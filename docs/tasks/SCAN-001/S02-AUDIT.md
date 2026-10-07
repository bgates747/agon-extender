# SCAN01-S02 — Rendering, scrolling and output ownership audit

## Executive summary

**S02 complete; pause before S03.** The strongest optimization target remains
Nurples' partial vertical scroll. The panel-direct RGB888 implementation does
**nine times the pixel-exchange work** of the native algorithm for its playfield,
before sprite work or HDMI traffic. This is a source-derived operation count,
not a measured ninefold slowdown. It also exposes the drawing surface directly
to HDMI DMA while software sprites are hidden and redrawn. Together these are
credible explanations for the reported flicker and load-dependent input delay;
their actual game-time durations remain unmeasured.

The stock clipping algorithm still limits Nurples' tile plots to one scanline.
Stock's drawing timeout is explicitly disabled by VDP, and the P4 retains its
parser/drawing priority relationship. Neither a new drawing budget nor a core
rewrite follows from this audit. The next approved-plan step is to establish
whether segmented DMA can support the required mapping **and pixel lifetime**.
Changing descriptors alone cannot make a row safe to overwrite while DMA reads it.

This was source inspection and source-integrity verification only. No source
changes, compilation, emulator run, hardware access, card operation, commit or
push. All 5,510 frozen Extender source inputs and 81 repaired-Nurples inputs
still match S01. Existing unrelated work remains intact.

## References and comparison scope

1. [S01](S01-BASELINE.md) pins the ordinary r03 image, failed direct image,
   matched instrumented native image, repaired game and card contents. Its
   recorded source-to-binary reproducibility and live-attestation limits remain.
2. Official [VDU commands](../../../../../agon-docs/docs/vdp/VDU-Commands.md),
   [system commands](../../../../../agon-docs/docs/vdp/System-Commands.md),
   [bitmaps/sprites](../../../../../agon-docs/docs/vdp/Bitmaps-API.md),
   [screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md) and
   [MOS API](../../../../../agon-docs/docs/mos/API.md) were consulted first at
   documentation commit `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
3. Official VDP remains clean at v2.16.0,
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Its installed library reference
   under `.pio/libdeps/esp32dev/vdp-gl` is clean at
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. This is the actual selected
   library reference, not a claim that every current vendored file is untouched.
4. Fifty-eight selected function-body comparisons match that stock reference:
   viewport/scroll dispatch, clipping and untransformed bitmap helpers, Canvas
   scroll/wait operations, and VGA64 methods excluding its constructor/physical
   ISR. Local evidence `agents/scan001/s02/source-check.json` records each match
   and S01 hash reconciliation. Read-only library diffs sit beside it.
5. Existing P4 changes outside those matching bodies include synchronization,
   allocation/lifecycle checks, diagnostic hooks, direct-panel preparation,
   earlier glyph stack reduction and numeric-transform checks. S02 neither
   removes them nor introduces upstream fixes. Historical claims that the whole
   common library is byte-identical must not be applied to today's source.
6. Pinned IDF 5.5.5 is still `b774170ff46c393eeb5e495ea37936038d3f4f4f`.
   S02 inspected its current DPI submission/restart path only; transfer alignment,
   descriptor construction and hardware feasibility belong to S03.

Source locations below refer to the S01-frozen working tree. Function names are
the durable anchors; line numbers aid this review and may move after edits.

## Command and game contracts

| ID | Contract verified | Consequence for this work |
|---|---|---|
| S02-C01 | `VDU 23,7,extent,direction,movement`: extent 0 text, 1 entire screen, 2 graphics, 3 active viewport. Unknown extent currently falls back to default. | Preserve context selection; no Nurples-specific command or fixed playfield in the renderer. |
| S02-C02 | Directions 0–3 are physical right/left/down/up. Directions 4–7 use cursor axis inversion and XY exchange. Movement 0 becomes font width/height for the resulting axis; positive values are pixels. | Zero on the wire is **not** a no-op. Preserve horizontal operations, upward scrolling and transformed coordinates. |
| S02-C03 | `Context::scrollRegion` installs the selected scrolling rectangle and text-background brush/options. `Canvas::scroll` queues vertical then horizontal operations. | The exposed strip uses stock's brush, not an assumed black pixel. Scrolling region and drawing clip are different state. |
| S02-C04 | Graphics coordinates pass through scaling/origin before viewport/plot use. `VDU 24` accepts a one-row rectangle (`Y1 == Y2`); invalid bounds are rejected. PLOT-derived viewport commands have their separate clipping rules. | Keep logical coordinates, negative bitmap positions and inclusive rectangle endpoints. A temporary one-row clip must not dismantle a persistent storage mapping. |
| S02-C05 | `absDrawBitmap` computes source offsets and clipped X/Y counts before its format-specific loops. Nonzero alpha means opaque, not blended. Sprite save/restore ignores the graphics clip but still clips to screen bounds. | The tile trick does not require drawing and then discarding 15 complete rows. Keep ordinary bitmap clipping distinct from sprite restoration. |
| S02-C06 | Single-buffer drawing normally queues; double-buffer drawing is immediate into its back plane, except queued `SwapBuffers`, whose caller waits for notification. Single-buffer software sprites save backgrounds; double-buffer software sprites do not. | Do not fix flicker by silently changing the application's buffering mode. Preserve stock double-buffer semantics and the existing fixture's redraw requirements. |
| S02-C07 | `VDU 23,0,&CA` and pixel queries flush pending drawing. `&C3` uses swap/wait behavior; stock's single-buffer implementation queues a no-op and polls queue occupancy. | A pixel reply is a drawing-completion observation, not proof HDMI displayed a coherent frame. Queue-empty alone is not a general tagged fence for an already dequeued primitive. |

Contracts C01–C04 follow [scroll dispatch](../../../vdp/video/vdu_sys.h)
(`vdu_sys_scroll`, 822), [graphics context](../../../vdp/video/context/graphics.h)
(`scrollRegion`, 404/941), [viewport context](../../../vdp/video/context/viewport.h)
(17/67/125/202) and [Canvas](../../../vdp/vendor/vdp-gl/src/canvas.cpp)
(85/131/148). C05–C07 follow
[common drawing](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp)
(541/664/731/759/967/1679), [common templates](../../../vdp/vendor/vdp-gl/src/displaycontroller.h)
(`genericRawDrawBitmap_RGBA2222`, 2700), and
[screen facade](../../../vdp/video/agon_screen.h) (676/683).

The generic vertical-scroll helpers do not clamp a movement larger than the
selected region's height. Their fill loops can extend beyond that region; the
new direct horizontal implementation does clamp its amount. This is a source
boundary requiring stock comparison, not a newly reproduced hardware defect or
authorization to fix upstream. Nurples uses movement 1 in a 336-row field and
does not reach that case. Keep oversized/degenerate cases in bounded host
compatibility tests before attempting potentially unsafe hardware inputs.

### What repaired Nurples actually submits

1. [screen.inc](../../../../nurples-repair/src/asm/screen.inc) defines a
   512×384 screen, origin (128,48), and inclusive local playfield (0,0)–(255,335):
   **256×336**, with two stationary 128-pixel sidebars.
2. [tiles.inc](../../../../nurples-repair/src/asm/tiles.inc),
   `tiles_scroll_background`, sets that viewport and sends extent 2, direction 2,
   movement 1. It then selects local (0,0)–(255,0), draws background and plots
   the tile row. Tile Y advances from −15 through 0, revealing one successive
   source scanline per update. The scrolling region remains the full field until
   the next scroll; changing the graphics clip does not allocate new storage.
3. [sprites.inc](../../../../nurples-repair/src/asm/sprites.inc) resets,
   defines and activates ordinary sprites, then changes their frames/positions.
   The game does not select hardware sprites. The fresh-default path is software
   sprites; record/reset VDP feature flags in the later fixture, since stock
   `resetSprites` can inherit the optional auto-hardware-sprite flag.
4. [nurples.asm](../../../../nurples-repair/src/asm/nurples.asm), `main_loop`
   (118), calls `do_game`, then [vdu.inc](../../../../nurples-repair/src/asm/vdu.inc)
   `vdu_vblank` (213). Despite its name, that helper sends no VDU command: it
   polls MOS `sysvar_time` until it changes, with a finite polling escape that
   records a timing-fault flag. [EMOS's interrupt handler](../../../../agon-emos/src/interrupts.asm)
   increments that clock by 2 on mainboard vblank. This is not a wait for P4
   drawing or HDMI completion and not a centisecond-accurate elapsed-time source
   at 60 Hz. Preserve it in S05, report its timeout flag, and use the planned PRT
   measurements for actual active/wait intervals. The two display clocks are
   not thereby phase-locked.

## Ranked findings

Ranking is by relevance to the reported Nurples regression, not by an invented
percentage attribution of runtime.

| Finding | Stock/mainboard and ordinary native P4 | Panel-direct RGB888 | Evidence status |
|---|---|---|---|
| **S02-F01: excessive scroll movement** | VGA64 exchanges sidebar bytes, then swaps logical whole-row pointers. Ordinary P4 retains those same method bodies. | Keeps fixed panel-row addresses; replaces the pointer swap with physical whole-row byte swaps, while still doing sidebar swaps. | Confirmed source difference and operation count; game-time duration unmeasured. |
| **S02-F02: intermediate sprite states reach output** | Mainboard copies logical rows into four rolling output rows, decorating two per ISR. Ordinary HDMI converts logical rows into separate panel storage after a drawing notification, with only per-row CPU exclusion. | CPU restores sprite backgrounds, scrolls/draws and redraws sprites in the very storage DMA scans. A CPU mutex does not stop DMA. | Confirmed ownership/exposure; its contribution to observed flicker needs measurement. Ordinary HDMI is also not an atomic single-buffer snapshot. |
| **S02-F03: rendering can stall input service** | Stock and P4 both give drawing priority 5 and parser priority 3 on the drawing/parser core. | Slow scroll holds native exclusion for the primitive and occupies the higher-priority drawing task. Console input/VDU interpretation/reply staging share the parser owner. | Confirmed blocking paths; no failing-game trace yet locates delayed keys or proves overflow. |
| **S02-F04: overlays have changed storage ownership** | Hardware sprites, text/mouse cursors and indexed Copper are composed into output rows, separate from the persistent logical background. | In eligible 64-colour modes, hardware overlays are composed into panel rows, with saved background rows restored before drawing/readback. | Confirmed adaptation and extra row work; not evidence of a wrong-colour or clipped-tile defect. |
| **S02-F05: timing/fences can disguise the workload** | Nurples submits an unfenced stream paced by the mainboard MOS clock. | Existing frame-fenced and slow art checks allow work to finish before observation. Direct diagnostics and ordinary r03 also differ in hooks. | Existing passes do not measure hidden-sprite duration, active input service or coherent gameplay updates. |

### Scroll cost, with units

[Native VGA64](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp)
`swapRows`/`VScroll` (297/352) and
[RGB888](../../../vdp/video/extender/display/p4_rgb888_controller.cpp)
`swapRows`/`VScroll` (297/350) both use the stock three-callback
`genericVScroll` (common header, 2972). For a one-pixel downward scroll they
perform **335 adjacent row exchanges**. Native sidebar swaps use aligned
32-bit groups plus edge bytes; the direct routine loops over individual bytes.

| Per Nurples scroll, excluding fill/sprites/metadata | Native VGA64 algorithm | Current panel-direct RGB888 | Difference relative to native |
|---|---:|---:|---:|
| Bytes exchanged per row pair, counting one side of each exchange | 256 | (256 + 512) × 3 = 2,304 | +800% (9×) |
| Bytes exchanged across 335 pairs | 85,760 | 771,840 | +800% (9×) |
| Algorithmic byte reads + writes, two reads/two writes per exchange | 343,040 | 3,087,360 | +800% (9×) |
| Same access volume at 60 scrolls/s, decimal MB/s | 20.5824 | 185.2416 | +800% (9×) |

These are **not PSRAM bus measurements**. Caches, writeback, memory placement,
word width, compiler code generation and repeated accesses change external
traffic and elapsed time. Mainboard's native framebuffer requests internal RAM;
ordinary P4 normally requests PSRAM. Clearing the new strip adds 256 logical
pixels (256 or 768 physical bytes), while sprite/tile accesses add separate work.

For scale only, an overlap-safe direct copy of just the field would copy
256 × 335 × 3 = 257,280 bytes, with 514,560 algorithmic read/write bytes. That is
one-sixth of the current exchange volume, **not** a measured sixfold speedup or
a selected implementation. Pointer/region mapping could avoid that field copy
too, subject to S03/S07 proving feasibility and lifetime.

HDMI's 1280×720×3 active payload is 2,764,800 bytes/frame, or 165.888 MB/s at
exactly 60 frames/s. That separate DMA payload is not UART traffic and must not
be added to CPU access counts and labelled measured memory bandwidth. The
five-byte VDU scroll command remains small regardless of the pixel movement.

The [prior matched measurements](../RGB-001.md) independently establish that
large writes already regressed: mode20 case9 median completion 5.667→13.319 ms
(+135.0%); mode8 case9 1.875→6.264 ms (+234.1%). They do **not** measure this
scroll. Static mode20 preparation/cache dropped from 35.29378 to 0.06193 ms,
which explains the experiment's attraction but does not establish gameplay
performance. Retain those different measurement scopes.

## Complete addressing and ownership boundary

The following inventory is the change surface for a later implementation, not
permission to edit every item. `m_viewPort` is the drawing table;
`m_viewPortVisible` is the visible table. In single-buffer mode they alias.

| ID | Current consumer / source | What mapping must preserve |
|---|---|---|
| S02-A01 | RGB888 macros and pixel/set-row lambdas, lines 68–190; [pixel proxy](../../../vdp/video/extender/display/rgb888_pixel.hpp) | Every `(x,y)` resolves through the logical mapping. Preserve six-bit GCOL operations, HDMI B,G,R byte order and existing one-byte Native assets/saved backgrounds; RGB888 storage is not a new VDU colour ABI. |
| S02-A02 | Raw fills/OR/AND/XOR/invert, 231–288; horizontal `memmove`, 369; clear, 341 | These assume contiguous `row + 3*x`. A split row requires span-aware fills and overlap-safe horizontal movement across segment boundaries. Merely changing the row pointer is insufficient. |
| S02-A03 | Lines, ellipses, flood/row-scan fill, glyphs, copyRect and swapFGBG, 195–227/305–335/387–431 | Most generic algorithms already accept pixel/row callbacks. Reuse their geometry/order and adapt the addressing seam; flood tests and overlapping copy source/destination must see the same logical pixels. |
| S02-A04 | Raw Native/Mask/RGBA2222/RGBA8888 plots, bitmap capture and transformed plots, 448–587 | Source bitmap rows remain ordinary contiguous assets. Destination callbacks must span mapped regions; clipped source offsets, alpha and one-byte background save/restore remain intact. |
| S02-A05 | Common `hideSprites`/`showSprites`, 731/759, and [sprite mutations](../../../vdp/video/sprites.h) | Restore in reverse order, redraw/save in forward order; saved coordinates are logical screen positions. Scroll must remove old software sprites before moving background. Do not scroll the saved-background allocation or constrain restoration to the tile clip. |
| S02-A06 | RGB888 `readScreen`, 435; common `copyToBitmap`; Canvas pixel read; VDU pixel reply | Read logical drawing pixels, not blindly linear HDMI storage. Current direct readback retires hardware overlays first; it can change what a live DMA scan sees. Keep timed runs free of per-draw capture/readback. |
| S02-A07 | RGB888 allocation/binding/free, 600–641; [VGABase](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp) allocate/free/swap | Current rows borrow centered panel storage with 3,840-byte stride; descriptor arrays are separately owned. Panel owner retains pixels. Free lists must own allocations, not whichever pointers currently represent logical rows. |
| S02-A08 | `panelIndex`, overlay row save/restore, 643–679 | Current code identifies a whole physical buffer using row0 and indexes saved overlays by physical buffer plus logical y. A mixed-region mapping invalidates that assumption; explicit ownership is required. |
| S02-A09 | RGB888 swap/prepare/encode/copy, 681–745; [runtime binding](../../../vdp/video/extender/display/stock_runtime_controller.hpp) | Keep logical drawing/visible selection, palette/cursor state and output selection consistent. Row memcpy and `signal[x ^ 2]` decoration expect a complete logical row. |
| S02-A10 | [Native scanline code](../../../vdp/video/extender/display/stock_scanline.cpp), paletted controller and native depth classes | Other colour depths retain stock packed layouts and ordered Copper lookup. RGB888 is selected only for 64 colours at 512×384/320×240 (single or double buffered). Preserve fallback modes and crop traversal; do not reinterpret native packed pixels as RGB888. |
| S02-A11 | [HDMI publisher](../../../vdp/video/extender/display/hdmi_output.cpp), 267–420, [ownership](../../../vdp/video/extender/display/hdmi_buffer_ownership.hpp), direct submitter 428–502 | Descriptor publication, cache-clean ranges, border bytes, last DMA reader and mode lifetime all belong to output. The current API only selects whole panel-owned linear images; logical row-pointer edits do not redirect its DMA. |
| S02-A12 | [Mode transaction](../../../vdp/video/agon_screen.h), 299–412; [service detach](../../../vdp/video/extender/display/stock_p4_service.cpp), 230 onward | Join drawing/output owners, cancel waiting swaps, retain old resources through required readers, restore aliases/fallback correctly. Direct-mode preparation already detaches earlier because candidate initialization writes shared panel pixels. New descriptors cannot outlive their pixel allocations. |

The inventory includes direct memory consumers, not just the two scroll methods.
Older `p4_display_controller`/flat-plane code is not the selected stock-runtime
renderer and is not evidence that ordinary r03 lost row-pointer scrolling.

### Output and sprite lifetime

1. Mainboard VGA64's ISR copies/decorates two of four rolling output rows,
   independently of the drawing task. It increments `frameCounter` and wakes
   drawing at its frame boundary. Software sprites still live in drawing memory;
   stock does not provide a universal single-buffer atomic-frame guarantee.
2. Ordinary P4 HDMI keeps native row storage, composes one logical row at a time
   under native exclusion, then expands outside that row lock into panel memory.
   Single-buffer output writes the scanned front; double-buffer output stages
   a separate panel back. A visible-generation check rejects a conversion that
   crossed a logical buffer swap. This does not detect arbitrary single-buffer
   drawing changes between rows.
3. Direct single-buffer RGB888 aliases drawing/visible rows to the scanned panel
   front. `hideSprites` restores backgrounds before scrolling; `showSprites`
   happens on refresh or at drain completion. The native mutex excludes another
   CPU accessor, **not DMA**. Explicit cache clean at a publication or ordinary
   cache eviction can expose intermediate state. The current publication can
   also run between primitives of a subsequent drain. Short completed-frame
   comparisons do not measure this exposure.
4. Direct hardware overlays use a different mechanism: save the entire affected
   logical row in one-byte colour form, decorate it, expand back into the panel,
   then restore it before a later primitive/readback. These saved rows are not
   the software sprites' per-sprite backgrounds. Segment mapping must handle both.
5. Direct double buffering composes the back, asks a separate core1 submitter
   to clean/select it, waits for DMA acknowledgment, then exchanges native aliases.
   The old front is not returned for drawing before that boundary. Synchronous
   swap cancellation and mode detach remain required.
6. IDF `esp_lcd_panel_dpi.c::dpi_panel_draw_bitmap` recognizes pointers into its
   framebuffer allocation, cleans complete requested rows and sets `cur_fb_index`.
   It does not wait for scanout. `mipi_dsi_dma_trans_done_cb` samples that index,
   restarts the selected DMA list, **then** invokes the frame-buffer callback.
   The P4 service advances its clock independently there. On this silicon that
   callback is a whole-frame DMA proxy, not a physical pixel/VSYNC timestamp.

Two alternating descriptor lists protect metadata only. If an old list still
references a circular row, clearing that row for the new image can corrupt the
ongoing old scan. S03/S07 must address that lifetime without silently converting
all single-buffer modes into mandatory double buffering. Source inspection has
not selected the answer.

### Queue, input and pacing consequences

Stock [mode setup](../../../../../agon-vdp/video/agon_screen.h), line230,
explicitly calls `enableBackgroundPrimitiveTimeout(false)`. The retained worker
drains available commands and shows sprites; the P4 runtime deliberately mirrors
that unbudgeted inner loop. Stock's library contains optional timeout arithmetic,
but it is **not enabled by this VDP**. A new drawing budget is not a stock fix.

[P4 service](../../../vdp/video/extender/display/stock_p4_service.cpp) uses
parser core0/priority3, drawing core0/priority5 and output core1/priority6 in the
selected configuration. The shared [native mutex](../../../vdp/video/extender/display/stock_native_access.hpp)
is recursive and supports priority inheritance. One costly scroll excludes
other native operations and occupies the drawing core until it finishes. A
cross-core output waiter can add inherited priority, not make the parser faster.
Because parser and drawing share a core, an endlessly replenished queue must
not be asserted without evidence of actual interleaving/blocking; the slow
primitive and accumulated queue alone are credible delay paths.

[runConsole](../../../vdp/video/extender/transport/console_hardware.inc),
lines109–318, owns USB report pumping, remote key selection, retained VDU parser
calls and UART reply FIFO refill. USB/network producers may collect input
independently, but forwarding it through this owner still requires progress.
`processNext` checks events/keys before a command; that does not preempt a long
previous command or a high-priority drawing operation. Single-buffer queue
admission blocks when full; double-buffer drawing executes on the parser;
sprite mutations/readback also acquire native exclusion.

EMOS sends ordinary ExCom VDU to P4 over UART1 at 1,152,000 baud, 8N1, RTS/CTS;
P4 sends admitted key/reply packets back over the same duplex link. Board-selected
signals remain the authority for wiring. Long parser service gaps can postpone
TX FIFO refill and consume RX capacity, eventually applying backpressure to
eZ80 output. The eZ80 game can consequently reach its next key poll late too.
This is not proof that UART wire speed itself is the bottleneck. No interrupt
vector change or new keyboard protocol is justified by these source findings.

Nurples' nominal one-mainboard-vblank pace, P4 drawing batches and HDMI frame
boundaries are distinct. Faster scrolling may restore headroom without making
those clocks phase-identical. Input delivery and game input consumption must
remain separate measurements in the already planned S05 check.

## Minimal observations for S04/S06

These refine the existing subtasks; no new benchmark campaign or task is started.

| ID | Measurement owner and boundary | Question answered / reuse |
|---|---|---|
| S02-O01 | P4 aggregate duration/count for vertical scroll, including separate software-sprite hide/show intervals | How much of a 16.667 ms frame the actual partial-scroll workload consumes; how long sprites are absent. Record region/amount once outside the hot loop. |
| S02-O02 | P4 parser service-gap maximum, primitive-admission wait, native-lock wait and queue high-water at existing owner boundaries | Distinguish CPU scheduling, lock exclusion, queued drawing and UART backpressure; reuse existing optional owner/native-wait tracing where adequate. |
| S02-O03 | P4 drain/publish/cache timings, frame counter, coherent update/marker counts | Reuse `render_benchmark.hpp`; do not add overlapping phase sums as CPU utilization. DMA frames may repeat or expose partial application state. |
| S02-O04 | eZ80 PRT active-before-wait / pacing wait / total, MOS clock delta and timing-fault flag | Preserve real Nurples pacing and quantify headroom. Use S05's fixed work/state checks and /256 saturation-aware timer; no SD writes in the measured loop. |
| S02-O05 | Separate bounded identified input injection, P4 forwarding and real MOS-map/game observation | Establish whether keys are delayed before transmission, reception or consumption; no cross-clock subtraction or private-map substitution in this check. |

Reuse [RGB888 golden checks](../../../tests/display/rgb888_renderer_test.cpp):
they already cover owned and borrowed rows, both physical-front choices,
single/double buffering, clipping, horizontal/vertical scroll, background
restoration, overlay exclusion and delayed swap acknowledgment. Their synchronous
64×32 commands and mock panel do not reproduce concurrent real DMA, PSRAM cache
publication or continuous 256×336 scroll plus sprites. Add the missing one-row
tile insertion and region-crossing cases only in S04's identified supplement.

Reuse the [resident suite](../../testing/resident-render-suite.md) for fixed
fill/bitmap/sprite controls. Its 22 combinations omit scrolling; software-sprite
case46 in double-buffer mode deliberately lacks a back-plane redraw and is not
a clean-animation parity test. The corrected familiar-art mode136 fixture supplies
that separate visual control. Keep unfenced Nurples primary, completion-fenced
controls secondary and instrumented/hook-free comparisons explicit.

## Next boundary

S03 is a source/hardware-contract feasibility study, not a flash. It must prove
whether the pinned driver/hardware can consume a full 720p stream assembled
from margins, stationary sidebars and independently rotated field rows, including
unaligned edges, cache publication, descriptor count/cost and safe reuse. The
addressing inventory above prevents a descriptor-only proof being mistaken for
a complete renderer solution. The SD card can remain on Lenovo for that step.
Pause here for Author discussion and authorization.
