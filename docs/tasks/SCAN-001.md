# SCAN-001 — Segmented HDMI scanout and transparent partial scrolling

## Executive summary

Prepare a feasibility and architecture handoff for making the P4's HDMI DMA
follow independently mapped RGB888 screen regions. The intended benefit is
vertical scrolling without repeatedly moving the scrolling pixels or copying
a whole image into HDMI memory. Existing Agon applications must retain their
VDU commands and EMOS routing. The initial direct renderer removes conversion
but regresses large writes and fails Author gameplay acceptance; its scrolling
implementation physically exchanges whole rows and sidebars. Stock's pointer
method still moves sidebar pixels during partial-width scrolling. Independent
region mapping could remove both costs, but DMA feasibility, renderer addressing
and coherent presentation remain unproven.

**State: S01–S05 complete; S06 remedy passes Author Nurples playtest; closeout pending.** The
authorized S06-R01 copy-scroll remedy is implemented, host-checked, flashed and
physically compared. [Remedy results](SCAN-001/S06-COPY-REMEDY.md) record 13 clean
case executions: short Nurples returns to 60 updates/s; scrolling with 32 software
sprites rises from about 26 to 54–55. Startup/configurations are restored and the
candidate remains installed. The Author accepts Nurples behaviour and reports
Rally input still fails as before, outside this remedy. Broader qualification and
production closeout remain pending; see the remedy report. No descriptor experiment
or general architecture adoption is authorized.
[First short hardware baseline](SCAN-001/S06-BASELINE.md) records five matched
mainboard/ordinary-P4 smokes. [Correlated windows](SCAN-001/S06-WINDOWS.md)
record the native/mainboard r02 tranche, the Author-approved longer Nurples pair,
and the short direct comparison. The original direct scrolling/tiles plus 32 software sprites
reaches only 26 updates/s, versus 60 without scrolling; short direct Nurples
reaches 36–40 with long drawing tails. One no-PRT finalization control is retained
as failed. Hook-free controls and visibility/input/mechanism gates remain;
S07 is not authorized.
The Author directs one subtask at a time, with discussion and fresh authorization
before each next subtask. S01 local input verification is recorded in
[S01 baseline](SCAN-001/S01-BASELINE.md), including fresh mounted-card hashes.
[S02 audit](SCAN-001/S02-AUDIT.md) records the stock comparison, addressing and
ownership inventory, ranked hypotheses and minimal observation points. It confirms
ninefold pixel-exchange work in the direct Nurples scroll, not a measured ninefold
slowdown; sprite exposure and input delay still need game-time measurement.
[S03 feasibility](SCAN-001/S03-FEASIBILITY.md) identifies a four-bit DSI bridge
block-count obstacle to the 1,010-block Nurples mapping. Small-list experiments
are specified; full-field segmented scanout is not yet established as feasible.
[S04 test contract](SCAN-001/S04-TEST-CONTRACT.md) freezes the Author-approved
nine-case mode20 comparison: a progressive scroll/tile/software-sprite ladder,
32 sprites on a static background, and deterministic repaired Nurples. This
replaces the proposed automatic 22-point resident performance sweep.
[S05 fixtures](SCAN-001/S05-FIXTURES.md) are built, emulator-validated and deployed
to the Author-mounted card. S06 now records the first physical timings; moving-image
acceptance remains incomplete. No bench device was changed in S05.
Nurples is the primary performance acceptance target. Preserve all existing work.

## Deferred Extender-specific exploration

SCAN01-X01 [ ] **Deferred: investigate an explicit accelerated scrolling-region
feature.** The Author wants to explore capabilities that exploit P4 hardware
even when their application interface extends beyond stock VDP. A persistent
scrolling region with stationary surroundings is a candidate for Nurples-like
games. Research whether explicit region lifetime, layout/alignment constraints
and an application-requested presentation boundary can simplify P4 rendering
and safe DMA publication. Identify the actual hardware mechanism, measurable
benefit, supported geometry and fallback before proposing an API.

This is a bookmark, not implementation authorization or a proven hardware hack.
An Extender-only API does not remove the four-bit DSI bridge block-count obstacle;
the S03 four-row specimen cannot establish full-height game scrolling. Separate
what an explicit interface simplifies from what the hardware can actually emit.
Any future extension must retain EMOS ownership of command routing and transport.

Keep this exploration outside the current S01–S12 acceptance path: existing
Nurples must benefit through its existing VDU commands without a rewrite.
The Author's willingness to explore extensions does not relax that compatibility
target. Resume X01 only on explicit direction after reviewing the feasibility
evidence; command encoding and architecture remain undecided.

## Why this is a separate task

The Author considers useful video acceleration the reason to retain the P4:
network access, file transfer and keyboard input alone could be provided by the
earlier WROOM arrangement. See the [Author's rationale and design discussion](SCAN-001/AUTHOR-OBSERVATIONS.md#motivation-and-handoff).
This is a larger renderer/scanout addressing proposal than tuning one scrolling
function. Do not promise that it is the only viable solution or that descriptor
mapping alone fixes all rendering and input defects.

[RGB-001](RGB-001.md) retains the direct-rendering experiment, its measurements
and unresolved gameplay/input diagnosis. [HDMI-001](HDMI-001.md) owns the working
720p output, geometry and fidelity limits. [BENCH-009](BENCH-009.md) owns the
deterministic fixtures and paused long campaign. [PPA-001](PPA-001.md) remains
deferred; no PPA or asset-cache implementation is selected by this handoff.

## Pickup context and authority

The current experimental target is Olimex ESP32-P4-PC Rev C, with P4 silicon
v1.3 established by the earlier reset capture in [P4PC-001](P4PC-001.md#accepted-timing-experiment--r06).
The Pi 5 ARM64 hosts this checkout and tools. `HARDWARE.local.md` owns exact
device identities, network endpoints, wiring and current access restrictions;
read its later updates rather than treating its historical opening sections as
the present topology. The Pi and Lenovo have distinct evidence/card roles.
Machine-specific paths and receipts are indexed in ignored
`agents/scan001/HANDOFF.local.md`.

Read the canonical and local AGENTS instructions, [handbook](../README.md),
[production selection](../../production/README.md), [building guide](../building.md)
and relevant task records before choosing source or tools. Selected production
remains the separate v0.1.0 DevKit bundle; it does not identify this bench's
experimental P4-PC image. Preserve the extensive existing uncommitted work.
Maintained P4 changes belong under `vdp/`, host tools under `scripts/`; reference
checkouts and archived build snapshots are read-only.

The last recorded Author installation is ordinary native-rendering HDMI
`hdmi-001-r03-b2026-10-05-01-47-13Z`, restored after the direct trial. Reverify
installed state before later bench work. The failed gameplay image is
`rgb-001-r01-b2026-10-05-23-30-11Z`. Retain both exact images, source closures,
receipts and meaningful failures. Do not create another device-firmware backup
by habit: the Author rejected that standing practice; retained source/build
artifacts and existing factory rollback remain available.

## Author observations and accepted constraints

The [observation transcript](SCAN-001/AUTHOR-OBSERVATIONS.md) preserves relevant
messages with stable local anchors. It links the existing contemporaneous task
records and distinguishes human observations from measurements. Original chat
message URLs are unavailable; no invented chat links are supplied.

| Observation / requirement | Evidence and consequence |
|---|---|
| Ordinary HDMI initially makes Nurples appear near full speed, with more sprite flicker than mainboard | [Initial review](SCAN-001/AUTHOR-OBSERVATIONS.md#initial-ordinary-hdmi-review); bounded visual acceptance, not a measured 60-update/s result |
| Direct RGB888 makes Nurples sprites flicker almost every frame and controls fail until scrolling stops | [Direct trial](SCAN-001/AUTHOR-OBSERVATIONS.md#direct-rgb888-gameplay-regression); direct gameplay acceptance failed |
| Ordinary rollback restores playable Nurples and responsive keys; skips/flicker remain | [Rollback](SCAN-001/AUTHOR-OBSERVATIONS.md#ordinary-hdmi-rollback-comparison); substantial additional direct regression, plus ordinary limitations |
| Rally steering fails on ordinary too; Escape works there | Same rollback; do not assign the whole Rally failure to RGB888 or infer a Legacy/ExCom comparison the Author did not report |
| Aginvadors is similar across variants/routes; held-fire slowdown is an application bug | Same rollback; exclude that slowdown from Extender regression attribution |
| 60 Hz is the target for compatibility with Agon and monitors | [Output requirements](SCAN-001/AUTHOR-OBSERVATIONS.md#output-and-validation-requirements); distinguish DMA refresh from coherent application updates |
| Preserve aspect ratio with centered unscaled content; crop oversized modes for now | Same requirements and [ADR-0024](../decisions/ADR-0024-centered-unscaled-hdmi.md) |
| Preserve stock vblank behavior and double buffering when the VDP mode requests it | Same requirements; no new application API or application-specific scrolling commands |
| Hold a visual experiment until the Author replies | Same requirements; a serial counter is not visual acceptance |

## Research baseline and source map

These are the already inspected dependencies, rechecked while preparing this
handoff. They bound the starting research, not a completed DMA feasibility audit.

| Reference | Exact baseline / relevant contract |
|---|---|
| Official Agon docs | Commit `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; [VDU scrolling](../../../../agon-docs/docs/vdp/VDU-Commands.md#vdu-23-7), graphics/text viewports, [PLOT](../../../../agon-docs/docs/vdp/PLOT-Commands.md), [bitmaps/sprites](../../../../agon-docs/docs/vdp/Bitmaps-API.md), [system/swap commands](../../../../agon-docs/docs/vdp/System-Commands.md) |
| Official VDP | Clean at v2.16.0, commit `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; read-only |
| Official MOS | Clean at v3.0.2, commit `8336409351ee5314e02801a7b72a4f1bb5282519`; read-only |
| Extender | HEAD `abb8ea995d7ebaff06db687d0cdff7e9a60967d3` plus substantial uncommitted work; HEAD alone does not identify experimental bytes |
| ESP-IDF | **5.5.5**, pinned commit `b774170ff46c393eeb5e495ea37936038d3f4f4f` in `agents/build001/native-tools/esp-idf`; do not substitute latest/stable/master or the separate SDK checkout |

The six inspected renderer/scanout source files match the failed direct image's
`source-inputs.json` hashes at handoff preparation. The local index records those
checks and exact build/report paths. Recheck source state at pickup.

| Responsibility | Source |
|---|---|
| EMOS-admitted VDU scroll interpretation | [vdu_sys.h](../../vdp/video/vdu_sys.h), `vdu_sys_scroll`; [context/graphics.h](../../vdp/video/context/graphics.h), `Context::scrollRegion` |
| Primitive dispatch, sprites, queue blocking | [displaycontroller.cpp](../../vdp/vendor/vdp-gl/src/displaycontroller.cpp), `addPrimitive`, `execPrimitive`, `hideSprites`, `showSprites` |
| Stock row rotation and sidebar compensation | [displaycontroller.h](../../vdp/vendor/vdp-gl/src/displaycontroller.h), three-callback `genericVScroll`; [vga64controller.cpp](../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp), `VScroll`, `swapRows` |
| Experimental RGB888 storage and physical row exchanges | [p4_rgb888_controller.cpp](../../vdp/video/extender/display/p4_rgb888_controller.cpp), `allocateViewPort`, `VScroll`, `swapRows`, `prepareForDrawing`, `composePanelOverlays`, `swapBuffers` |
| Renderer factory and execution exclusion | [stock_runtime_controller.cpp](../../vdp/video/extender/display/stock_runtime_controller.cpp), [stock_runtime_controller.hpp](../../vdp/video/extender/display/stock_runtime_controller.hpp), [stock_native_access.hpp](../../vdp/video/extender/display/stock_native_access.hpp) |
| Physical output and ownership | [hdmi_output.cpp](../../vdp/video/extender/display/hdmi_output.cpp), [hdmi_buffer_ownership.hpp](../../vdp/video/extender/display/hdmi_buffer_ownership.hpp), [rgb888_panel_storage.hpp](../../vdp/video/extender/display/rgb888_panel_storage.hpp) |
| Drawing/frame scheduling | [stock_p4_service.cpp](../../vdp/video/extender/display/stock_p4_service.cpp) |
| Keyboard forwarding shares VDU processing | [vdu_stream_processor.h](../../vdp/video/vdu_stream_processor.h), `processNext`, `handleKeyboardAndMouse`; [video.ino](../../vdp/video/video.ino), `processLoop` |
| IDF DSI DMA configuration / callback order | [pinned DPI driver](../../agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c), `dpi_panel_create_dma_link`, `dpi_panel_init`, `mipi_dsi_dma_trans_done_cb`, `dpi_panel_draw_bitmap` |
| Descriptor API and hardware restrictions to investigate | [DW-GDMA API](../../agents/build001/native-tools/esp-idf/components/esp_hw_support/dma/include/esp_private/dw_gdma.h), plus pinned P4 HAL/LL definitions and silicon applicability |

## Current rendering and output path

The eZ80 application emits ordinary VDU commands through EMOS. EMOS owns routing
to the onboard VDP or P4 VDP over its admitted transport; this proposal changes
neither endpoint protocol nor harness. The P4 CPU interprets primitives, renders
pixels and composes sprites. P4 DSI DMA feeds a pixel stream to the LT8912B
MIPI-to-HDMI bridge, which emits HDMI. The bridge does not interpret renderer
pointers, VDU viewports or sprite objects.

Ordinary P4 output renders a mode-native logical image, reads/composes rows and
expands them into centered RGB888 panel memory. The direct experiment writes
modes 20/8/136 directly into those panel allocations. Bitmap/software-sprite
pixels still expand when drawn; overlays called hardware sprites in the VDP
API are CPU-composed before scanout, not a P4 hardware sprite plane. Public
RGBA2222 bitmap semantics are distinct from stock framebuffer lane/storage
encoding and must remain intact.

The current IDF path consumes a linear 1280×720 framebuffer, stride 3,840 bytes.
One allocation is 2,764,800 bytes; two are 5,529,600 bytes. Direct logical row
descriptors address centered pixels inside those fixed physical rows. Merely
rotating the C++ row pointers changes rendering/readback, but the current DMA
still reads physical rows in their original order.

The earlier separate RGB888 drawing-plane experiment retained a presentation
copy: mode 20 static preparation was 23.19 ms (43.1 equivalent fps), including
19.41 ms (51.5 equivalent fps) for row copy/composition. The Author explicitly
requested direct writes to HDMI memory. Its measurements remain historical
context, not a fresh matched baseline; see [ADR-0025](../decisions/ADR-0025-rgb888-rendering-experiment.md).

## How partial scrolling actually works

Viewport coordinates persist until changed. A scroll command chooses the
current text, graphics, whole-screen or active viewport; `Context::scrollRegion`
enqueues its bounds and the requested movement. Setting bounds does not allocate
row storage. Each scroll must advance the contents or their address mapping.

Nurples changes the graphics viewport each update: first the playing field,
then a one-scanline strip for incoming tiles. Its request is extent 2, direction
2, movement 1: scroll the graphics viewport down one pixel. Reviewed source:
[tiles.inc](../../../nurples/src/asm/tiles.inc),
[screen.inc](../../../nurples/src/asm/screen.inc),
[state_game_playing.inc](../../../nurples/src/asm/state_game_playing.inc).
The field is 256×336 within mode 20's 512×384 image, starting at (128,48).

Stock exchanges row pointers covering the whole logical width. For a partial
width, it exchanges the left/right sidebar pixels before each pointer exchange,
compensating for their otherwise unwanted movement. It then fills the exposed
strip. Full-width scrolling is mostly pointer exchanges; partial scrolling
still physically exchanges pixels outside the moving region.

The direct `P4Rgb888Controller::VScroll` reuses this algorithm, but its panel
rows have fixed physical addresses. Its whole-row callback therefore exchanges
512×3 bytes instead of pointers, in addition to sidebar exchanges. For Nurples,
each adjacent-row step passes `(512 + 256) × 3 = 2,304` pixel bytes through the
swap loops, versus 256 one-byte sidebar pixels in the native implementation.
That is roughly nine times as many pixel bytes exchanged, not a measured
ninefold runtime/bus-traffic ratio. Native exchanges also use 32-bit groups;
the direct helper exchanges individual bytes.

The simpler direct-copy alternative would copy only the scrolling rectangle in
overlap-safe row order and clear the exposed strip. It still moves
`256 × 335 × 3 = 257,280` bytes per one-pixel scroll: 15.44 MB/s of destination
data at 60 updates/s, plus source reads, clearing, cache and other work. This is
an arithmetic estimate, not measured bandwidth or a claim that P4 cannot sustain
it. It removes redundant exchanges but does not recover pointer-based movement.

## Latest performance evidence

Primary sources are the [bounded report](../../agents/rgb001/panel-report-2026-10-06-03-08-04Z/index.html),
[machine-readable results](../../agents/rgb001/panel-report-2026-10-06-03-08-04Z/results.json),
[static controls](../../agents/rgb001/panel-report-2026-10-06-03-08-04Z/static-controls.json)
and [RGB-001 interpretation](RGB-001.md#qualified-results-and-resident-closeout-2026-10-05).
There are 88 valid matched measurements: 22 mode/case combinations across native
and direct renderers, each NORMAL and OFF. Four missing-window faults are
retained and excluded; the four valid no-probe controls and visual checks are
additional evidence. Historical mainboard results are separate context, not
fresh paired controls.

### Command completion

NORMAL includes active scanout. OFF suppresses presentation/cache submission
and DSI DMA while retaining comparable allocations and a software frame clock;
it is not a DMA-only subtraction. Timings are median command-to-completion-fence
wall time with the nominal 72,000-count/s eZ80 PRT calibration. Rates are
`1000 / milliseconds`, **completion-equivalent fps**, not observed video fps.
The 60-update/s budget is 16.67 ms. The benchmark includes command/transport and
completion costs; it is not an isolated CPU rasterizer measurement.

Selected NORMAL comparisons, ranked by largest percentage time regression.
Baseline is the matched native P4 path; difference is
`(direct_ms / native_ms − 1) × 100%`.

| Mode / case | Workload | Native ms / eq fps | Direct RGB888 ms / eq fps | Time difference |
|---|---|---:|---:|---:|
|8 / 9|Large filled area|1.875 / 533.3|6.264 / 159.6|+234.1%|
|20 / 9|Large filled area|5.667 / 176.5|13.319 / 75.1|+135.0%|
|8 / 41|64 bitmaps, 32×32|21.347 / 46.8|24.028 / 41.6|+12.6%|
|20 / 41|64 bitmaps, 32×32|22.236 / 45.0|24.056 / 41.6|+8.2%|
|136 / 41|64 bitmaps, 32×32; double buffer|33.319 / 30.0|32.986 / 30.3|−1.0%|
|20 / 46|16 software sprites; paced|5.889 / 169.8|4.903 / 204.0|−16.7%|
|20 / 15|16 lines|8.833 / 113.2|5.819 / 171.8|−34.1%|

Selected OFF controls, ranked by largest percentage time regression against
native OFF; the same percentage definition applies.

| Mode / case | Native OFF ms / eq fps | Direct OFF ms / eq fps | Time difference |
|---|---:|---:|---:|
|8 / 9|1.319 / 757.9|4.625 / 216.2|+250.5%|
|20 / 9|3.847 / 259.9|9.014 / 110.9|+134.3%|
|20 / 41|16.597 / 60.3|22.181 / 45.1|+33.6%|
|20 / 15|5.750 / 173.9|5.792 / 172.7|+0.7%|

Large writes regress even OFF, locating substantial extra cost in rendering/
storage rather than requiring active HDMI DMA. NORMAL sparse-line gains with
nearly unchanged OFF timings are consistent with removing concurrent conversion
pressure. Exact cache/bandwidth/locking contributions remain unmeasured.

### Fixed-source preparation and expansion

The colour chart is loaded once and unchanged during three ten-second windows.
These are presentation phase means, not active drawing or animation throughput.
Ranked by native preparation cost, worst first.

| Mode | Native preparation + cache ms / eq fps | Direct preparation + cache ms / eq fps | Native submissions/s | Direct submissions/s |
|---|---:|---:|---:|---:|
|20|35.29378 / 28.3|0.06193 / 16,147.3|27.57|59.94|
|8|15.29373 / 65.4|0.04457 / 22,434.1|59.94|59.94|
|136|15.24327 / 65.6|0.01428 / 70,046.6|39.76|60.04|

The tiny direct values establish removal of the repeated image conversion/copy;
their large reciprocal rates do not imply HDMI displays thousands of frames/s.
The previous five-mode native expansion controls are separately documented in
[BENCH-009](BENCH-009.md#completed-supplemental-results).
Mode 20 expansion alone was 27.28 ms (36.66 eq fps) with scanout and 23.60 ms
(42.37 eq fps) without. Modes 21/149 were similar at 512×384; modes 8/136 cost
about 10.9 ms (about 92 eq fps) with scanout at 320×240. The early CONVERT-OFF
branch incorrectly cleared all 720p pixels every pass: those controls are invalid
and excluded. That mistake did not apply to the earlier NORMAL drawing runs.

### DMA, image submission and double buffering

All matched NORMAL DMA counters lie between 59.86 and 60.09 Hz. These count
hardware scans, including repeats, not unique complete pictures.

| Mode 136 case | Native app updates/s | Native image submissions/s | Direct app updates/s | Direct sampled marker transitions/s | Direct submissions/s |
|---|---:|---:|---:|---:|---:|
|46 — software sprites|59.85|0.149|60.00|60.13|119.81|
|9 — large fill|60.00|0.291|60.00|60.13|119.96|
|41 — 64 bitmaps|29.93|29.89|30.00|30.13|89.96|

Native cases 9/46 complete logical updates near 60/s while accepting very few
converted images. The generation guard rejects a row pass spanning a logical
swap; this is a supported explanation but its rejection count was not recorded
in those windows. Direct submissions include repeats of the same image: 120
submissions/s with 60 Hz DMA is not 120 displayed fps. Marker transitions sample
one part of the image, not independent proof of a whole coherent physical frame.

An earlier ordinary r03 passive capture counted about 19.2 complete submissions/s
with about 60 DMA scans/s; conversion wall means were 50.05–50.37 ms (about
19.9–20.0 phase-equivalent fps). Its exact game scene was not identified. See
[HDMI-001](HDMI-001.md#r03-author-gameplay-review-and-passive-timing--2026-10-04-local);
do not call it a controlled Nurples result.

## Diagnosis carried into this handoff

The slow static charts and familiar-art visual checks passed modes 20/8/136.
The corrected mode 136 art fixture matched mainboard visually; its original
missing-sprite result was a fixture error because CLS disables sprites. These
passes do not qualify continuous scrolling with sprites or input under load.
The selected benchmark omitted scrolling and deferred hardware-overlay cases.

The command-completion table uses matched instrumented native/direct benchmark
variants. The Author's failed direct NORMAL gameplay image is instrumented,
whereas the ordinary r03 rollback is hook-free. The retained no-probe controls
do not constitute matched continuous-game trials. Preserve that distinction;
do not attribute every observed game difference solely to pixel storage without
separating instrumentation and game-time scheduling effects.

The strongest source-based explanation for Nurples is expensive row movement
combined with exposure of intermediate sprite/background states. Reviewed
Nurples uses ordinary software sprites. `genericVScroll` calls `hideSprites`;
the P4 worker redraws software sprites after draining pending primitives. The
direct single-buffer path exposes that same memory to DMA. Slow scrolling or a
continuously replenished queue can extend sprite absence. Ordinary output also
lacks a universal atomic whole-frame boundary, consistent with residual flicker.
Actual game-time absent durations and scanout visibility have not been captured.

P4 `processNext` forwards keyboard events to EMOS and interprets VDU commands on
the same processing path. Primitive admission can block on a full queue; immediate
drawing and native exclusion can also delay progress. The eZ80 game can then
wait sending output or reach its next input poll late. Controls recovering when
Nurples scrolling stops supports load-dependent backpressure/input delay, but
the exact accumulation point is unresolved. A post-game mode 0 status sample
with no pending host keys is not a failing-game capture.

Rally's maintained source draws filled road bands in double-buffered mode 136,
samples held keys once per rendered update and advances physics by elapsed
time. Low update rates can weaken frame-coupled steering relative to physics.
This does not establish the cause of its ordinary-r03 steering failure. Both
Rally's VDP-named `vdp_getKeyMap` helper and Nurples' `mos_getkbmap` read the EMOS
map; their left/right indices agree. Rally's Escape also uses that map, so its
working Escape does not establish a separate working ASCII-event path. Exact
on-card game binaries have not been matched to the reviewed source during this
diagnosis. The receiving agent must not substitute the historical root Rally or
abandoned Golem worktree for the current game by assumption.

## Proposed approaches and their actual costs

| Approach | P4 CPU / DMA behavior | Benefit and remaining cost |
|---|---|---|
| RGB888 logical rows, copied to linear HDMI | P4 CPU rotates renderer pointers; CPU or copy engine assembles panel rows | Retains stock scroll semantics, removes colour conversion but restores a presentation copy |
| Optimized direct rectangle copy | P4 CPU copies only the requested scroll region in overlap-safe order | Smallest correction to current waste; still moves scrolling pixels every update |
| Whole-row DMA mapping | P4 DMA follows a descriptor row order; P4 CPU retains stock sidebar compensation | Removes whole-row movement and presentation copy, but still exchanges sidebar pixels |
| Independent region mapping / segmented DMA | P4 renderer retains separate region rows; DMA assembles stationary and scrolling segments | Could avoid moving both scrolling pixels and sidebars; requires broader addressing/ownership work |

The Author's proposed clean arrangement is the last row: organize a stable
scrolling region once, then advance a circular row offset and clear/redraw the
exposed strip on each scroll. The CPU may still update descriptor addresses or
select another prepared list; this is not a claim of zero per-scroll work.
Repeatedly selecting a one-scanline drawing viewport must not unnecessarily
destroy the useful scrolling mapping.

The pinned IDF driver allocates DW-GDMA linked lists but currently configures a
whole-frame source transfer. This makes custom descriptor mapping a credible
research direction, not a demonstrated supported row-table interface. The
statement in ADR-0025 that DMA cannot follow logical pointer rotations describes
the current linear driver path; this handoff has not established a universal
hardware impossibility or amended that accepted experiment's architecture.

Feasibility must account for legal transfer widths/lengths, arbitrary RGB888
pixel boundaries, alignment, descriptor count and fetch cost, DSI bridge flow
control/underflow, PSRAM/cache maintenance, frame restart behavior and the
supported internal driver seam. Merely finding a linked-list type is insufficient.
On this pre-v3 silicon, the current DMA completion callback restarts DMA with
the selected list before the client callback. The callback used as a frame
boundary proxy is not an independent hardware VSYNC interrupt. Never mutate a
list or row allocation while DMA may still reference it; mapping publication
and pixel lifetime both require ownership, including mode teardown/cancellation.

## Compatibility and evaluation boundary

The P4 implementation must remain transparent to legacy applications. EMOS
continues to own ordinary VDU routing, activation and committed mode. No game
patch, fixed-region application API, new transport or direct-register bypass
is the compatibility solution. Preserve logical pixel coordinates, origins,
clipping, colours/paint modes, bitmap transparency, sprite restoration/layering,
readback and command order. Preserve single/double-buffer mode behavior and
stock vblank/swap expectations. A 60 Hz signal alone is insufficient.

Arbitrary changing, overlapping and disjoint viewports, cross-region primitives,
text scrolling, clearing and mode changes are architectural obligations. A
bounded first feasibility specimen may use Nurples' stable geometry, but a
special case silently accepted as general support is not an acceptable result.
Fallback/materialization and its cost remain a decision; indexed modes and
Copper retain existing behavior rather than being silently reinterpreted.

The intended evaluation separates mapping/scroll CPU cost, rendering/sprite work,
cache and memory traffic, descriptor preparation/publication, command completion,
keyboard-to-EMOS/game latency, DMA cadence and complete-image coherence. Use
matched workloads and a retained native/direct baseline, with output present
and absent when the comparison genuinely preserves the work. Static held images,
repeatable scroll-plus-sprite traffic and familiar games serve different roles.
Nurples is the primary performance acceptance target; Rally's independent baseline
problem must not disappear inside an aggregate score. Author visual comparisons
are held for a reply. Report milliseconds with equivalent fps and measured
update rates separately; record duration and avoid another unbounded campaign.

## Decision register and receiving-agent remit

SCAN01-D01 [x] **Author instruction:** plan approved. Execute exactly one subtask
at a time, then pause for discussion and explicit authorization for the next.
S01 is the current authorized step; this is not unattended execution approval.

SCAN01-D02 [x] **Required compatibility:** existing applications and EMOS routing
remain unchanged; improved scrolling is internal P4 implementation work.

SCAN01-D03 [x] **Inherited accepted contract:** fixed 720p RGB888, centered
unscaled image/cropping, nominal 60 Hz and mode-dependent buffering/vblank.

SCAN01-D04 [ ] **Proposed, unproven:** independent region mapping with segmented
DSI DMA is the principal investigation; whole-row mapping and optimized copying
remain alternatives, subject to the S08 selection gate.

SCAN01-D05 [ ] **Unresolved:** legal P4 v1.3 / IDF 5.5.5 descriptor arrangement,
supported driver integration seam and safe mapping/pixel handoff; S03/S07.
S03 specifies the project-owned seam and small-list proof, but finds a four-bit
bridge block count versus 1,010 blocks for the direct Nurples mapping. Long-list
DSI framing and physical pixel retirement remain unproved; no architecture
decision follows from the source study alone.

SCAN01-D06 [ ] **Unresolved:** general renderer addressing, changing/overlapping
regions, materialization/fallback and bounded memory/descriptor costs; S02/S08.

SCAN01-D07 [x] **Accepted with Author emphasis:** Nurples is the main performance
target. Partial vertical scrolling must match mainboard performance, or be close
enough to retain headroom for sprites without flicker and snappy input. Supporting
benchmark numbers alone are insufficient. Retain the measurable criteria below;
do not promise 60 game updates/s for every workload.

SCAN01-D08 [x] **Accepted:** keep the performance suite tightly focused, within
five to ten cases. The Author approves nine: static/polling, partial scroll,
scroll plus clipped tiles, then 4/8/16/32 software sprites on that background,
32 software sprites on a static background, and deterministic repaired Nurples.
Compare matched mainboard/P4 workloads in mode20. The earlier mainboard limit
near32 sprites without scrolling is a hypothesis, not a qualified threshold.
No hardware-sprite cases; S04 owns the exact measurement and repeat limits.

The receiving agent should first critically assess these hypotheses against the
pinned source/hardware contracts, then propose its own bounded plan and decision
sequence for Author review. The plan below is accepted subject to one-subtask authorization gates. Later executable
work requires a selected scope and artifact identities. Current records retain
Author-controlled flashing: build/verify and provide the Pi shell command at a
flash boundary unless subsequent Author instructions change that arrangement.
Read current bench constraints and SD layout before any fixture/deployment;
use verified fast transfers and keep representative resident fixtures on-card.
No production promotion, commit, tag or push is authorized by this handoff.

## Approved execution plan — 2026-10-06, one subtask per authorization

Investigate segmented DMA first, but prove the complete renderer-to-display
addressing and ownership scheme before adopting it. Reuse the resident tests,
add the missing continuous scroll workload, and compare a deterministic repaired
Nurples run on mainboard, ordinary HDMI and the selected candidate. Do not restart
the paused full benchmark campaign. The Author approved the plan and authorized S01 first; pause after each subtask
for discussion and permission to proceed.

### Pickup findings that change the plan

1. The handoff's source walkthrough used `../nurples`, whose current HEAD is a
   2026-08-02 checkpoint labelled known non-working. The requested modern game is
   `../nurples-repair` (currently HEAD `0c741d5`, 2026-09-16). Both trees have
   local changes, including repaired-tree assets. Freeze exact source/asset hashes
   before drawing conclusions; neither HEAD alone nor the old source walkthrough
   identifies the tested game. Do not edit or reset either game checkout.
2. The existing [Nurples builder](../../tests/performance/builders/nurples.py)
   already bypasses prompts/joystick, centers an invulnerable ship, records PRT
   timing and supports a finite run. It polls MOS, then substitutes a private
   all-released key map. That is useful for repeatable rendering but cannot prove
   P4-to-EMOS input delivery. Its source replacements and timing placement also
   need review against the repaired game; reuse is not permission for blind patching.
3. Its old /16 PRT timer saturates after approximately 56.9 ms. The recent
   [r04 timing contract](../testing/render-load-contract-r04.md) uses /256,
   approximately 13.889 microseconds/count and 910 ms range. Use the recent
   convention for comparable stall-sensitive reporting, with explicit saturation.
4. The [resident selection](../testing/resident-render-suite.md) supplies
   valuable fill/bitmap/sprite controls but does not reproduce Nurples' continuous
   partial scrolling, one-line clipped tile plotting and sprite restoration.
   Fencing every draw/update can also hide the natural queue backlog. Both
   unfenced gameplay and separate completion-fenced controls are required.

### Investigation and experiment contract

SCAN01-S01 [x] **Freeze the actual comparison inputs.** Record source closures,
compiler/SDK configuration, board/silicon, EMOS and mainboard VDP identities,
ordinary r03 rollback, direct experiment and fixture/assets hashes. Reconcile
on-card Nurples/Rally with maintained sources without modifying `/mystuff`.
Recheck current local bench ownership; the earlier topology and USB keyboard
assumptions are historical. Preserve existing dirty work and frozen artifacts.
Output: a compact baseline manifest and a current path/ownership map, including
which diagnostic facilities are actually present. No fresh ROM backup by habit.
**Complete:** local artifacts/source freeze and fresh mounted-card hashes verify,
including current `nurples-repair` runtime and all 12 resident files. See
[S01 findings](SCAN-001/S01-BASELINE.md). No firmware change or performance run.

SCAN01-S02 [x] **Audit the complete affected path against stock.** Trace VDU
viewport/scroll through logical row addressing, clipping, bitmap paths, software
sprite save/hide/restore, primitive draining, mode/buffer swaps, pixel readback,
cache publication and DMA restart. Check all direct-row/contiguous-memory users,
not just `VScroll`. Reuse upstream code unchanged wherever its contract fits;
record necessary processor/output adaptations, with no unrelated upstream fixes.
Resolve the official semantics of zero movement (character-size scroll), all
extents/directions, origin transforms and mode-dependent buffering. Audit input
forwarding/queue blocking as a possible consequence of drawing load, without
starting an unrelated RTOS/core-affinity rewrite.
Output: evidence-backed hypotheses and minimal observation points; distinguish
measured costs from inferred mechanisms and transfer bytes from memory traffic.
**Complete:** [S02 findings](SCAN-001/S02-AUDIT.md) cover retained clipping and
scroll semantics, direct-memory consumers, sprite/output lifetime, buffering,
cache/DMA restart and input service. Stock disables the optional drawing timeout;
no new budget is proposed. Fifty-eight selected function bodies match stock and
all S01 source hashes remain unchanged. No implementation or device operation.

SCAN01-S03 [x] **Establish whether segmented DMA is legal and useful.** Inspect
pinned IDF 5.5.5 and the P4 v1.3 hardware reference for source alignment, permitted
burst/transfer sizes, RGB888 segment ends, row stride, descriptor memory/count,
cache coherency, DSI flow control, restart ordering and underrun reporting. Work
through actual 720p margins and the 256×336 Nurples field, then odd X coordinates,
one-pixel strips and region boundaries that do not align to a DMA transfer.
Define a project-owned driver seam, not an unrecorded SDK edit. Calculate and
bound descriptor storage, PSRAM use and per-update descriptor/cache work.
Output: feasibility note and a small standalone descriptor specimen design.
If arbitrary segmentation is illegal, costed aligned-edge scratch copies are an
option to evaluate; do not quietly turn them into a full-frame copy.
**Complete as a source investigation:** [S03 findings](SCAN-001/S03-FEASIBILITY.md)
pin IDF and the v1.3 TRM, cost aligned/edge layouts, define the driver seam and
specimen, and retain pixel/descriptor lifetime requirements. The bridge's
four-bit count blocks an unqualified 1,010-node implementation; full-Nurples
feasibility remains conditional. No code, build or device operation.

SCAN01-S04 [x] **Freeze the small measurement/fixture contract.** Reuse
`render_load.py`, `rgb888_compare.py`, the resident catalogue, readback collector
and offline report machinery where their assumptions apply. Keep frozen r04
bytes unchanged. Freeze only the nine cases accepted in D08, with a separately
identified finite synthetic companion for missing coverage and the repaired-game
derivative. The downward partial-scroll/tile/sprite ladder is the performance
workload; upward/odd-edge cases remain correctness checks rather than additional
performance cases. Compare the same command stream on mainboard and P4.
Add optional aggregate diagnostic scopes for scroll, sprite-absent time, queue
backpressure, mapping publication and descriptor work; preserve old field meanings.
No serial logging, HTTP polling, SD writes or per-draw callbacks in timed loops.
Output: exact case selection, source inputs and executable identity requirements,
timing scopes/schema requirements, controls, finite run bounds and perturbation
checks. S05 produces the new executable/data identities. No broad new framework.
**Complete:** [S04 contract](SCAN-001/S04-TEST-CONTRACT.md) fixes T01–T09,
mode20, per-sprite software selection, 600-update synthetic and 3,600-update game
runs, matched endpoints, percentage headroom reporting and bounded repeat/control
rules. It separates fenced synthetic completion from unfenced gameplay pacing.
No code, build, device operation or result is implied by this contract freeze.

### Deterministic Nurples requirement

SCAN01-S05 [x] **Prepare the nine-case fixtures and repaired-game derivative.**
Adapt the existing r04 timing/command-stream machinery into the finite T01–T08
companion defined by S04, preserving the original r04 files and evidence. Freeze
new artifact identities, generated payloads, familiar16×16 game art, exact
software-sprite setup, timing records and safe RAM bounds. Keep this a bounded
reuse of the existing harness, not a replacement benchmark framework.
Export the pinned
`nurples-repair` source into an isolated fixture build; reuse its AGNB assets and
existing builder/provenance machinery. Assert every source transformation and
review the resulting diff. Start directly in gameplay, ship centered and immune
to damage, joystick disabled, no title/confirmation prompts. Keep ordinary
scrolling, clipped tile insertion, sprite work, MOS key polling and one-vblank
pacing. The derivative must contain no mode switch, including exit restoration;
startup/cleanup owns mode selection. Store it under `/test/nurples`, leaving
production game bytes unchanged.

S02 confirms that repaired Nurples' `vdu_vblank` polls MOS `sysvar_time`, updated
by mainboard vblank, and can fail open after a finite polling budget. Preserve
that helper and record its timing-fault flag; do not replace it with a P4 drawing
fence or describe it as an HDMI completion wait. Normalize MOS clock deltas using
the retained calibration; PRT remains the elapsed active/wait measurement.

Use a fixed initial state/seed/map and an update-indexed movement/fire schedule
that visits low and high sprite loads. Inspect game timers: elapsed-real-time
spawning/cooldowns must not silently create different work on a slower renderer.
Where necessary, drive those gameplay decisions from a recorded synthetic
60-update/s game clock **in the derivative only**; PRT, MOS elapsed clock and
vblank pacing remain real. Record seed, input script, phase/update IDs and
checkpoint state hashes (map progress, actors/projectiles and RNG). Repeated
runs must match these states before their performance is paired. Verify that the
selected map/script spans the full run without death, a prompt or an unplanned
level transition; if it does not, freeze an explicitly identified extended map
or repeatable phase sequence before comparing endpoints, not midway through tests.

The primary repeatability test may reuse the private scripted key map after the
ordinary MOS poll. Label it **rendering/pacing**, never input-delivery evidence.
A separate short transport check injects identified press/release events through
the admitted P4 keyboard path and records their arrival in the real MOS map and
consumption by the game, with no private-map substitution. Keep this outside the
primary matched workload; late delivery must not change what is called identical
rendering work. Do not subtract unsynchronized P4/eZ80 timestamps. Use local
intervals and event IDs; add a bounded logic-analyzer capture only if needed to
locate a remaining delay. Respect admitted input ownership and spacing.

Proposed run length: **3,600 gameplay updates**, nominally one minute at 60 Hz,
after a fixed untimed warm-up. Stop by update count so each renderer receives the
same work; a slow renderer takes longer than one minute and that is a result.
Record real elapsed seconds and updates/s. First use a 120-update smoke, then
three full repetitions for mainboard Legacy, ordinary native HDMI and the selected
candidate. Retain the failed direct implementation as a short diagnostic control,
not an automatic fourth full campaign. A five-minute per-run host deadline marks
an incomplete run and requests recovery; it does not automatically reset Agon or
turn a partial run into a pass. Record actual progress and saturation separately.

Primary records: per-update elapsed active work before pacing, deliberate wait,
total loop time, update/phase ID and real MOS clock; fixed-size RAM recording with
capacity checked against application/asset memory. PRT1 uses the r04 /256 convention,
leaves PRT0/interrupt vectors untouched, refuses conflicting ownership and restores
its state on exit. Saturated rows are long-interval failures/lower bounds, never
wrapped fast samples or silently omitted. Load/save/retrieval occur outside timing.

P4 uses the existing correlated begin/end windows to collect render/output phases
and DMA counts. Primary gameplay adds **no completion fence per update**. A short,
separate run uses one completion fence per whole update to measure application-
visible completion and fence overhead; never insert one per primitive. Keep
unfenced active time, fenced completion and physical output as different columns.
Run a timing-disabled control and a genuinely hook-free ordinary/candidate pair
before attributing changes to the renderer rather than instrumentation.

**Complete:** [S05 results and deployment](SCAN-001/S05-FIXTURES.md) record the
nine built fixtures, matched game-source rebuild, complete emulator smokes,
two identical3600-update game trajectories, short controls and pixel checks.
Startup and production games are preserved. One timer-contract precision:
PRT1's unused control state is restored to0; its write-only reload remains65535,
not an asserted restoration of an unknowable prior reload. The occupied-timer
check remains. Bench input delivery, flicker and physical timings await S06.

### Bounded implementation and tests

The Author defers segmented-DMA investigation and dependent integration
(S07–S12) after accepting the transparent copy-scroll remedy. Retain those
steps as a future optimization path, not the next automatic work. Acceptance
closeout for the tested remedy remains separate.

SCAN01-S06 [ ] **Measure the failing mechanism before replacing it.** Use short
S04 T01/T03/T07/T08 controls and a T09 Nurples smoke on mainboard, ordinary native
and current direct paths with matched scopes/hooks, followed by bounded controls
without hooks. These are the same nine workload identities, not another suite. Measure
queue/drain stalls, sprite absence and scroll costs while the failure is active;
post-game empty queues are not evidence. Reuse resident machinery for collection,
not its broader case list. OFF/held-output experiments are not automatic additions
to the agreed scope; propose a bounded replay only if one unresolved mechanism
requires it. Existing OFF removes cache/presentation and substitutes a clock,
so it must not be described as a pure DMA subtraction.
Output: a short comparison and a ranked explanation, including any unproved link.

#### S06-R01 — First copy-scroll remedy, authorized 2026-10-06

The Author directs trying S06 finding F08 and releases the unchanged bench.
This is a bounded experiment within S06; unresolved hook-free, sprite-visibility
and input observations remain open. No commit/push or production promotion.

S06-R01-A [x] Reuse the existing stock two-callback `genericVScroll` without
editing its body. For panel-backed RGB888 rows only, supply a physical row-span
copy and the existing brush-fill adapter. Preserve hide/show ordering, viewport
coordinates, clipping, RGB222 colour semantics, row stride, double buffering and
EMOS routing. Owned/native pointer-swapping storage remains unchanged. No new
clamp, upstream bug fix, scheduler policy, cache policy or DMA change.

S06-R01-B [x] Extend the existing RGB888/native golden comparison for partial
up/down scrolling, odd edges, full-height moves, one-pixel regions, repeated
one-row tile clipping, sprite background restoration and panel margins in both
buffering modes. Run existing related host checks; freeze new `rgb-001-r02`
experimental bytes with the same normal-output diagnostic build configuration
as the failed direct control. Preserve exact r01 and ordinary rollback images.

S06-R01-C [x] The Author's instruction to try this remedy with the bench
"all yours" delegates this bounded candidate deployment/testing to the agent.
Flash and independently verify the concrete candidate. After installation, run the same five short r02
cases and matched bounded controls; no new workload or extended direct run is
implied. Restore original startup/configurations and leave a verified candidate
available for the Author's ordinary Nurples playtest if the checks permit it.
Report active-budget percentages, completion and final-drain costs separately
from HDMI publication and actual visible/input behaviour. Pause after this remedy;
do not continue to S07 or another optimization without discussion.

Completed: 13 short case executions / 1,560 retained updates, no recorded faults
or aborts, all simulation trajectories matching. Four-segment installation and
whole-file restoration verify. Candidate `rgb-001-r02-b2026-10-07-00-49-06Z`
remains installed at the normal startup boundary with input ready and no active
listener/window. The short Nurples smoke has no enemy-table actors; its 60/s
result does not establish busy-game flicker/input acceptance. Natural T07 still
finishes with a 133.5 ms drawing tail. Pause here for the Author's real playtest;
S06's broader open gates are not closed by the completed remedy subsection.

Research basis: official [scroll command](../../../../agon-docs/docs/vdp/VDU-Commands.md)
at `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, and the unchanged copy/fill helper
in stock VDP v2.16.0's selected vdp-gl (`ac2dd5986daf496c43ae8e7fe41836274aec54a0`).
S02 records the stock oversized-movement limitation; this remedy does not change
that contract. Fixed panel rows cannot use native pointer rotation, but the stock
copy helper already supplies direction-safe row order. Each valid source and
destination row span is disjoint, allowing a library byte copy of only the field.

SCAN01-S07 [ ] **Deferred by Author after the Nurples pass: prove descriptor scanout independently of the renderer.** After
the S03 small-list source gate, compile an isolated, reversible output candidate
with the known-good HDMI signal timing. Follow the bounded specimen stages in
[S03](SCAN-001/S03-FEASIBILITY.md): first 1/3/15 blocks, then a four-row partial
scroll using 14 blocks. A representable small-list success does not establish
long-list support. Do not silently truncate the bridge count or proceed to the
1,010-node Nurples mapping without a justified, separately demonstrated framing
method; if none exists, report that boundary for the S08 decision.
Reorder uniquely numbered rows, then stationary
sidebars plus a circular middle region. Verify stream length, colour byte phase,
edge pixels, margins and complete descriptor traversal. Test repeated wraps and
bounded handoffs with CPU writes/cache flushes; stop on underrun or ownership
failure. Two descriptor lists alone are insufficient: prove pixel lifetime when
clearing/reusing a row that an older list can still reference. Test mode teardown
and recovery as well as steady state. The Author flashes the verified image using
the supplied command; hold each requested visual check until the Author replies.
Output: measured feasibility and safe publication rules, or a specific rejection.

SCAN01-S08 [ ] **Select and record the architecture before integration.** Resolve
D05/D06 with measured evidence. Preferred: persistent region row mappings with
segmented DMA. Logical clipping is separate from storage mapping, so temporarily
selecting the tile strip must not repartition/materialize the whole field.
Define cross-region pixel/bitmap/span operations, row retirement, descriptor-list
publication, bounded fragmentation, fallback and allocation failure. Full-width
row mapping remains an alternative with sidebar compensation; an overlap-safe
rectangle copy is the minimal control/fallback, not successful zero-copy scrolling.
If segmentation fails, present that evidence and alternatives for Author choice
before switching to a substantially different architecture. Update the ADR and
normative architecture only after the decision is accepted.

SCAN01-S09 [ ] **Implement the selected P4 adaptation in small increments.**
First full rows, then a stationary/scrolling split, then changing regions and
fallback; qualify each before the next. Share stock clipping/painting/sprite
logic rather than creating a second incompatible implementation. Keep one
logical addressing contract for rendering, saved backgrounds, readback and
presentation. Reused rows must not leak stale pixels. Honor single-buffer and
explicit double-buffer visibility and swap semantics; do not invent a frame
boundary from every VDU command, add a drawing budget, or silently double-buffer
all modes to conceal flicker. Address sprite lifetime/publication coherently.
Any remaining input delay requires its own measured cause and narrow correction.
Output: a separately selectable candidate, compile checks and bounded unit/
native tests for addressing, ownership, cache ranges and teardown.

SCAN01-S10 [ ] **Check compatibility and integration before performance claims.**
Reuse existing scroll/sprite/clipping checks and resident colour/familiar-art
fixtures. Add only missing cases: repeated region wrap; opposite scrolls;
zero/large movement; odd edges; changed/overlapping/disjoint viewports; a bitmap
larger than its one-line clip; boundary-crossing draws/sprites; text scroll;
origins/paint modes; clear; pixel readback; buffer swap and mode teardown.
Require unchanged sidebars and correct cleared/new rows. Reuse existing host
checks for20/8/136 and relevant fallback paths where shared code changes. Physical
performance stays with the nine mode20 cases; propose any additional physical
compatibility coverage explicitly before expanding the bench scope. Record
exclusions. Exact completed-image checks establish
logical correctness; moving-image coherence still needs output/Author evidence.
Treat capture-induced failures under the existing capture-failure protocol:
mark, recover, continue independent tests, then run uninstrumented controls.
Emulator/native tests cannot qualify P4 DMA or display timing.

SCAN01-S11 [ ] **Run the finite comparison and Author gameplay review.** After
correctness gates, execute only S04's nine cases on mainboard, ordinary native
and the chosen candidate. Start with one complete pass per endpoint/variant;
T09 and the decision-critical threshold/control cases need three matched
repetitions as defined by S04. Do not run the old 22-point resident selection or
resume BENCH-009's paused campaign. Keep failures and bounded repeats explicit.
Use mainboard as the Nurples compatibility reference and ordinary HDMI as the
P4 regression baseline. Keep browser video disconnected and streaming counters
checked; browser keyboard control is separate from video traffic. Freeze clock,
cache/PSRAM config, compiler, workload and assets across paired candidates.
Restore normal gameplay and leave a familiar scene for the Author to assess
scrolling, sprite flicker and controls; hold it for their response. Rally's
separate steering defect is recorded independently, not repaired by assumption.

SCAN01-S12 [ ] **Report, restore and close only the proven scope.** Reuse the
recent self-contained HTML/CSV/JSON report style, with raw hashes/provenance and
invalid/missing runs visible. Separate preparation, execution and retrieval
elapsed times. Results and startup backups go under `/agents/extender/results`;
fixtures remain resident; fast deployment uses one independent file readback.
Prefer mounted-card collection for bulk data. Restore startup byte-for-byte and
the agreed ordinary firmware unless the Author accepts the candidate. Preserve
meaningful failures and rollback; no blind reset/retry. Update task/handbook and,
after explicit tested acceptance, follow production version/bundle/tag rules.

### Accepted success criteria and reporting (D07)

| Question | Required evidence / reporting |
|---|---|
| Does the mapping remove the intended cost? | On a stable region, no per-scroll whole-field/sidebar exchange or full-frame presentation copy; count actual bytes moved, descriptor changes, cache work and fallbacks. Edge copies, if necessary, are reported. |
| Does Nurples meet the main target? | Partial vertical scrolling at mainboard speed, or close enough to retain sprite/input headroom; same deterministic state/command workload; per-run median/p95/max active and total ms, updates/s, pacing wait, saturation and intervals exceeding16.67ms. Improvement must exceed observed repeat-to-repeat spread; show all three runs. |
| Does it retain 60Hz opportunities? | Target60Hz scanout/logical vblank and mode-correct swap behavior; separately report completed game updates and fresh image submissions. Never infer displayed game FPS from DMA alone. |
| What is the monkey-friendly budget? | Active budget use = active ms /16.667ms ×100%; remaining budget =100% minus that value (negative means overrun). Show median and p95, plus percentage of updates over budget. Active includes output blocking; it is not pure eZ80 CPU computation. |
| What is faster/slower than baseline? | Side-by-side mainboard, ordinary HDMI, failed direct diagnostic and candidate, where comparable. Difference=(candidate time/baseline time−1)×100%; name the baseline and rank largest regressions first. Report1000/ms only as phase/completion-equivalent fps, never observed display fps. |
| Are correctness and usability retained? | No new failed pixel/clip/ownership tests, no silent lost keys or new hangs, and Author acceptance of ordinary-game scrolling/sprites/input. Flag fill/bitmap or tail-latency regressions beyond measured noise even if average scrolling improves. |

A candidate that only emits a60Hz signal, passes static pictures, or reduces
scroll cost while making sprites/input worse has not met this task. Exact 60 game
updates/s is a target to measure, not a promised result or a reason to alter the
application workload. If bounded tests fail these criteria, report the remaining
bottleneck and stop rather than expanding into a general renderer rewrite.

### Review and execution boundaries

Execute **one subtask per Author authorization**, then stop for discussion. S01 is
complete, as are S02–S05; S06 is authorized and incomplete. The sequence
remains S01–S04 input/audit/test-definition work, S05–S07 reproducer and physical
proof, S08 architecture selection, then S09–S12 implementation and qualification.
A phase grouping is not permission to execute all its subtasks. Preserve the
Author-controlled flashing and visual-review gates. Tie completed checkboxes
to evidence; keep an incomplete step open rather than moving its missing proof
into an unrecorded assumption. No commit/push or goal is implied by approval.
