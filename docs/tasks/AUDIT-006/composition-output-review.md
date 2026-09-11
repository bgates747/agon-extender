# AUDIT-006 W6 — Composition and output comparison

Status: source audit at Extender commit
`047ffe8caade708a4b867381fff7e8f0023f3782`; proposed dispositions, not an
implementation or performance qualification. This review covers palette/Copper,
sprite/cursor composition, readback versus presentation, and browser-output
handoff. The main video-backend audit combines it with storage, primitives,
mode/facade and execution reviews. No firmware, game, media or running-device
state was changed for this review.

## References and actual build selection

1. Official documentation was read first: `docs/vdp/Copper-API.md`,
   `docs/vdp/Bitmaps-API.md`, and the cursor, pixel/palette and VSYNC sections of
   `docs/vdp/System-Commands.md`, selected documentation commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Copper belongs to output palette
   selection, software sprites belong to drawing storage, and hardware sprites
   belong above the recoloured scanline. Nonzero alpha means opaque, not alpha
   blending. Rendering completion does not prove monitor/browser presentation.
2. Official VDP was verified clean at tag `v2.16.0`, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Official `context/cursor.h`
   versus the project copy differs only in include selection; `agon_palette.h`
   is byte-identical. This is source comparison, not a new stock firmware build.
3. The five vendored `vga{2,4,8,16,64}controller.cpp` files,
   `vgapalettedcontroller.{cpp,h}`, `vgabasecontroller.h`,
   `displaycontroller.{cpp,h}` and `fabutils.{cpp,h}` were compared byte-for-byte
   against Git object `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. All match.
   The vendor directory is an ordinary tracked directory, not an independent
   checkout: running `git rev-parse` there reports Extender's HEAD, not the
   vdp-gl identity. Exact upstream object comparison establishes the identity.
4. [The selected console manifest](../../../vdp/pio/p4-console-source-selection.json)
   compiles only `canvas.cpp`, `codepages.cpp`, and `displaycontroller.cpp`
   from vdp-gl. None of the five concrete depth controllers or
   `VGAPalettedController` executes in this P4 build. The project compiles
   `palette_state.cpp`, `presentation_compositor.cpp`,
   `presentation_snapshot_pool.cpp`, `p4_display_controller.cpp`, the frame
   service, browser provider, video service core and wired-network service.
   Portable code merely present in the vendor tree is not actual reuse.

## Execution and storage map

1. **Stock drawing:** VDU/Canvas code queues primitives; the vdp-gl worker
   renders into native drawing rows. Shared software-sprite logic saves and
   restores backgrounds and draws sprites. A double-buffer swap chooses which
   native row table is visible.
2. **Stock output:** an I2S DMA EOF interrupt selects the next visible row.
   Paletted controllers select a precomputed table once for that row, unpack
   multiple pixels through table lookups, then call the shared hardware
   sprite/cursor decorator. The 64-colour controller copies the native row
   with `memcpy` before decoration. DMA consumes a small rolling set of output
   rows. The drawing worker's queue need not become empty to produce them.
3. **P4 drawing:** retained common drawing/software-sprite logic calls project
   depth accessors against `PlaneStorage`. The frame-service worker drains
   drawing work, calls `showSprites`, then composes a snapshot.
4. **P4 output:** the compositor walks the fixed-order visible plane, decodes
   each pixel, resolves its presentation palette, writes RGB888, then overlays
   text cursor, hardware sprites and mouse cursor. The pool repacks the entire
   RGB888 image to RGB222 in place. A network worker leases that immutable image
   and queues header and payload for the HTTP task. The browser uploads RGB222
   to an R8 texture and expands channels in a fragment shader. Its next frame
   credit follows presentation.

The stock path already produces the final 64-colour image in byte-per-pixel
output rows. A different sink does not require reimplementing palette, sprite
or cursor semantics, nor fixing drawing rows at `base + y * stride`.

## Coverage ledger

Stock line locations below refer to the exact vdp-gl object above, available
unchanged in `vdp/vendor/vdp-gl/src/`. Unless prefixed otherwise, P4 locations
refer to `vdp/video/extender/display/` at the audit baseline. Restore/retain
dispositions are proposed for PORT-003 review, not implemented here.

| ID | Stock source and behavior | Selected P4 counterpart and difference | Dependency assessment and disposition |
|---|---|---|---|
| CO-01 | `dispdrivers/vgapalettedcontroller.cpp:214–227`, `setItemInPalette`: wrap index, mutate primary palette only for ID 0, update a precomputed output table. | `palette_state.cpp:164–177` stores compact RGB222 entries instead. Ordinary wrapping/creation and primary-versus-secondary split are retained; output preparation is replaced. | Sync values and output byte order are sink-specific; palette ownership/table generation are portable. Restore upstream table arrangement unless a concrete target constraint is established. |
| CO-02 | `vgapalettedcontroller.cpp:232–258`, `updateRGB2PaletteLUT`, and `fabutils.cpp:443`: HSV squared distances truncated to integers, `<=` tie comparison, early exit at exact zero. | `palette_state.cpp:28–49,179–203` copies/re-expresses both routines. Original HSV is absent from `fabutils_port.cpp`'s closure. | No processor/output reason requires duplicate HSV code. Retain original functions at their existing ABI in the portable closure; preserve exact arithmetic. |
| CO-03 | `vgapalettedcontroller.cpp:261–318`: output tables in a map; secondary creation copies table 0; deletion redirects affected signal pointers to table 0. | `palette_state.cpp:105–162` uses linked secondary palettes, copied 16-entry arrays and span IDs. Allocation/failure handling is independently implemented. | Allocation capability flags may change. Map ownership, ID rules and tables do not inherently need replacing. Restore with narrowly recorded inherited defect remedies. |
| CO-04 | `vgapalettedcontroller.cpp:321–393`: cumulative boundaries and resolved table pointers; scanline lookup advances one current cursor, reset once per frame by each ISR. | `palette_state.cpp:205–239,263–269` restarts span scanning at 0 for **each pixel**, then searches secondary palettes by ID. `composeBase:73–79` invokes this inside its pixel loop. | Avoidable algorithmic departure. Restore once-per-row table selection and sequential Copper traversal; preserve zero spans, last-span continuation and unknown-ID fallback. |
| CO-05 | `vga2controller.cpp:113–125,744–770`: 256-entry `uint64_t` table expands eight indices per lookup; sixteen pixels per loop; decorate row afterward. | `presentation_compositor.cpp:70–80` invokes checked codec, palette lookup and RGB888 expansion per pixel. | Restore portable bulk expansion; adapt only output order/sync and proven alignment/compiler requirements. |
| CO-06 | `vga4controller.cpp:141–153,773–804`: 256-entry `uint32_t` table expands four indices per lookup; sixteen pixels per loop. | Same scalar project compositor. | Same disposition as CO-05; preserving packed drawing storage does not justify dropping packed expansion. |
| CO-07 | `vga8controller.cpp:152–161,727–769`: six native bytes yield sixteen pixels using eight pair-table lookups and explicit destination word order. | Same scalar compositor/native codec. | Restore packed 3-bit path. Verify source word-load alignment and little-endian assumptions for P4; these are bounded dependencies. |
| CO-08 | `vga16controller.cpp:133–142,768–812`: pair-table lookups expand eight bytes into sixteen pixels using 16-bit writes. | Same scalar compositor. | Restore stock pair-table path, with the same bounded ordering review. |
| CO-09 | `vga64controller.cpp:730–736`: `memcpy(dest, visibleRow, width)`, then decorator; base row is already packed colour. | `composeBase` calls the codec, expands RGB222 to RGB888, then the pool repacks it. | Retain row copying. Normalize signal/lane representation at the sink boundary if necessary. RGB round trip has no physical necessity. |
| CO-10 | `vgapalettedcontroller.cpp:409–478`, `rawDrawSpriteScanline`: clip row; quantize RGBA8888 directly to RGB222; alpha test; signal-byte write. RGBA2222 supports XOR; unsupported formats are ignored. | `PresentationCompositor::applyOverlay:85–184` independently validates and clips an entire rectangle with 64-bit coordinates, iterates pixels, expands results to RGB888 and repacks destination for XOR. | `x ^ 2` and `m_HVSync` are narrow output seams. Prefer stock decorator operating on stock-format output rows, with an explicit inherited both-edge clipping correction (CO-F05). |
| CO-11 | `vgapalettedcontroller.cpp:480–499`, `drawSpriteScanLine`: text cursor, ascending eligible hardware sprites, then mouse cursor. | `p4_display_controller.cpp:590–613` reproduces order but traverses whole overlay rectangles after the whole base frame. | Visual order retained; implementation duplicated. Reuse stock decorator/order. Different traversal could reduce off-row sprite checks, but that unmeasured convenience is not an accepted departure reason. |
| CO-12 | `displaycontroller.cpp:652–758`, `setSprites/hideSprites/showSprites`: background allocation, reverse restoration, forward redraw, double-buffer distinction and static-sprite bookkeeping. | Byte-identical common functions execute, with P4 depth callbacks. `getBitmapSavePixelSize()` remains 1. `executeFrameWork:205–209` shows sprites before composing. | Retain common code. Backend equivalence still requires save/restore and clipping verification. Software sprites must stay in native drawing storage. |
| CO-13 | Official `context/cursor.h`, `updateTextCursorBitmap/doCursorFlash`: RGBA2222 XOR hardware sprite; FreeRTOS tick clock. `displaycontroller.cpp:762–789`: mouse hotspot and positioning. | Official text-cursor bodies retained; only includes differ. P4 uses common mouse methods. Output uses duplicate compositor; `cursor_position_adapter.cpp:22–30` clamps before calling retained position method. | Retain cursor construction/flash/hotspot methods; restore output decorator. Hardware mouse input availability is outside this display review. |
| CO-14 | `vga2controller.cpp:563`, `vga4controller.cpp:593`, `vga8controller.cpp:540`, `vga16controller.cpp:587`, `vga64controller.cpp:552`, `readScreen`: drawing rows, palette 0, no hardware overlays/Copper. | `p4_display_controller.cpp:515–522` retains that observable split through project accessors; presentation separately reads the visible plane. | Preserve split. Never substitute snapshot pixels for stock readback. Restore concrete read routines where native row access permits. |
| CO-15 | Paletted `rawCopyToBitmap`, e.g. `vga16controller.cpp:669–677`, exports RGB222 plus sync bits; software-sprite save callbacks instead save underlying per-pixel logical/native values. | `p4_display_controller.cpp:645–731` separates `nativeSavePixel` for explicit copy from sprite callbacks using `readLogical`. | Distinction is intentional and stock-backed. Storage audit must verify byte order/sync values rather than equating all native saves. |
| CO-16 | `vgapalettedcontroller.cpp:63–78,122–128,142–188`: small rolling DMA row set, descriptor/EOF schedule; concrete ISRs decorate independently of queue drain completion. | `p4_display_controller.cpp:184–211,616–633` composes/publishes only after a drain completes, on the drawing/frame worker. | I2S wiring must change; output independence must survive. This is measured AUDIT-006-F001, not a micro-optimization. |
| CO-17 | Stock output uses a small rolling row window, not three complete RGB888 images. | `presentation_snapshot_pool.hpp:20–26`, constructor `cpp:52–73`: three 1024×768×3 slots, **7,077,888 bytes (6.75 MiB)**, even for RGB222 output. P4 allocation requires PSRAM. | Immutable asynchronous ownership is justified. RGB888, maximum capacity and precisely three full slots are choices, not physical requirements; reassess behind stock row producer. |
| CO-18 | Stock row expansion/decorating directly writes packed final colours. | `composeBase/applyOverlay` write RGB888; `presentation_snapshot_pool.cpp:225–245` reads three bytes and writes one byte per pixel in a second full-image pass. Compaction allocates no extra image but performs extra work. | RGB222 sink already exists. Restore packed composition and eliminate the intermediate where upstream rows can supply it. |
| CO-19 | Stock scanout runs independently of monitor observation or image demand. | Pool `tryBegin:183–205` requires browser demand; `tryAcquireLatest:270–280` requests a new snapshot only when no producer is active. Selected minimum interval is zero. Producer transitions try-lock once and skip/defer. | Demand is a justified sink policy; it must not alter logical frame/callback timing. Keep immutable leases while uncoupling output from queue-empty completion. |
| CO-20 | Stock has no WebSocket equivalent; physical output consumes rows on its signal cadence. | `web/browser_video_provider.cpp:43–118` encodes a header and references leased payload as second segment without copying it. `network/browser_video_service_core.cpp` admits one client/credit/send. `wired_network_service.cpp:161–168,412–476` polls at 10 ms, queues HTTP work, sends segments and releases lease. | Necessary new sink code. Retain bounded lifetime and complete-or-error sends. Two application segments do not prove zero-copy through socket/Ethernet/browser internals. |
| CO-21 | Final stock colours are RGB222; lane ordering/sync bits concern electrical output. | `web/webgl2_presenter.js:21–39,113–178` uploads R8 and expands channels in shader. `web/app.js:101–127` sends next credit after animation-frame presentation. | Genuine output adaptation. Browser need not know native row layout, palettes, Copper or sprites. Keep wire protocol stable while restoring P4 internals. |

## Findings and reuse direction

### CO-F01 — Portable scanout was replaced along with physical output

The five concrete ISRs contain hardware scheduling **and** portable colour
expansion. Their table lookups, row copying and sprite decoration cannot be
classified wholesale as obsolete GPIO/I2S code. P4 instead has a second
all-depth compositor and palette implementation. Existing provenance labels
describe the adaptation choice but do not prove it necessary.

The smallest faithful direction is to preserve stock native rows, palette
tables, selected depth expansion and overlay functions, then bind the output
rows to P4 ownership. Before changing word ordering inside each function,
assess retaining stock signal-row layout and doing one narrow normalization
when writing the browser payload. The old registers need not execute to reuse
the C++ loops. A complete browser image can be assembled from these rows without
changing the existing EVF1 protocol or introducing scanline network messages.

### CO-F02 — Copper selection moved into the pixel loop

P4 starts from span zero and resolves its palette ID on every pixel. For width
W, height H, S spans and P secondary palettes, worst-case lookup work includes
O(W×H×(S+P)), aside from pixel decoding. Stock advances its current span and
selects a table once per row, then uses constant-time packed lookups. This is
source-proven repeated work, not a measured explanation of the Nurples hang;
Nurples' 64-colour mode bypasses paletted Copper selection.

### CO-F03 — RGB888 is an unnecessary selected-output intermediate

At 640×480 P4 writes 921,600 bytes of RGB888 base pixels, then reads those
pixels and writes 307,200 packed bytes during compaction; overlay work is
additional. These are source-level byte counts, not bus measurements: cache,
compiler access width and other work affect actual memory traffic. The pool
reserves 6.75 MiB despite transmitting one byte per pixel.

The browser already accepts the packed colour a stock scanline producer emits,
subject to lane/sync normalization. The repair should preserve independent
immutable browser ownership without retaining unnecessary colour expansion or
making the network own native drawing rows.

### CO-F04 — Publication independence is a semantic requirement

Stock output rows and frame counter advance in the output interrupt independently
of the drawing worker's eventual empty queue. P4 publishes only after that
worker completes a drain. The preserved 41.758495 s observation establishes the
resulting starvation. Faster drawing alone cannot prove independent output for
all continuously replenished workloads. Storage restoration must carry this
requirement while preserving FIFO/flush/swap, without a new drawing quota.

### CO-F05 — Reuse needs explicit inherited-defect dispositions

Two source concerns were found in the reuse surface. Neither is a new bench
failure report; no executable reproducer was run during this source audit.

1. `rawDrawSpriteScanline:428–431` computes right-clipped width as
   `scanWidth - spriteX` without subtracting left clip offset. For x = -5,
   sprite width = 20 and scan width = 10, it writes 15 pixels starting at
   position 0 instead of the 10-pixel intersection. Current P4 clips both edges.
   Reuse needs a narrow, attributed correction and boundary validation; byte
   identity is not a reason to regress to output-row overflow.
2. `deletePalette(65535):290–294` iterates the map and recursively erases its
   current iterator through `deletePalette(it->first)`, then increments the
   invalidated iterator. The destructor above uses erase-return iteration
   correctly; P4's linked deletion avoids that map iteration. Confirm and
   narrowly remedy this inherited path when selecting stock palette ownership.

These isolated concerns do not justify replacing all palette/sprite code.

## Real seams and remaining evidence

1. **Target-specific:** classic I2S1 status/clear registers, EOF descriptor
   address, `lldesc_t` linkage, GPIO, APLL/VGA timing and interrupt allocation.
   Stock `PSRAM_HACK` is documented in `fabutils.h:71–90` as an old
   ESP32/compiler workaround. Do not inherit it blindly on P4.
2. **Portable with narrow representation seams:** row selection, palette IDs
   and tables, Copper cursor, packed decode, sprite order/alpha/XOR,
   software-sprite save/restore and text-cursor construction. `pos ^ 2` and
   sync OR operations identify the lane/signal boundary; they do not require
   RGB888 processing.
3. **Justified browser additions:** immutable send lifetime, header, credit
   control, network transmission, texture upload and statistics. None dictates
   native framebuffer layout. The browser wire protocol can remain unchanged.
4. **Needs concrete binding evidence:** P4 alignment/cache requirements for
   retained word loads/stores, supported width quanta, source ownership during
   swaps, palette/sprite destruction while output reads, and callback timing.
   Current flat storage/single frame worker are not constraints on the answer.

## Validation limits and handoff

1. This is source inspection and exact reference-byte comparison. No new
   runtime performance, image parity, hardware stability or bandwidth claim
   follows. Earlier measurements remain in [the preserved findings](findings.md).
2. Published-slot immutability protects the network reader; it does not prove
   the producer saw an atomic combination of rows, palettes and sprite state.
   Parser paths can mutate cursor/palette metadata. The public
   `composeVisibleRegionQuiescent` requires caller ownership of overlay mutation;
   internal frame-boundary composition bypasses that misuse check. The main
   lifetime review must trace mutation, suspension and destruction before a
   new independent output reader is added. This is not attribution of the hang.
3. Ordinary text/Teletext remains owned by official context/VDU code and uses
   the selected depth output. It does not need a browser-side text renderer.
   Mode/facade and complete Teletext behavior are covered by the main audit.
4. Reuse validation should compare normalized stock/P4 row bytes across all
   depths, Copper boundaries/zero spans/palette deletion, alpha/XOR, sprite
   overlap/both-edge clipping, cursor order, single/double-buffer readback and
   active swaps. Continuous drawing must separately preserve output progress.
   Matching screenshots alone cannot establish layout or scheduling fidelity.
5. W7 should choose an upstream-derived row producer and narrow P4 binding,
   account for CO-01 through CO-21, and retain existing browser protocol and
   immutable ownership where compatible. This review does not authorize new
   core placement, a replacement generic compositor or the held benchmark.
