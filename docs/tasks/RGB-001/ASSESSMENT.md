# Direct RGB888 rendering — initial change assessment

## Executive summary

Direct rendering can remove the current full-image RGB888 expansion, but requires
a new experimental pixel-writing backend plus a shared renderer/HDMI ownership
contract. It is not a switch on the existing VGA64 byte layout. Reuse Canvas,
command parsing and the common geometry algorithms; replace their pixel access
and bind logical rows directly into panel-owned RGB888 memory. Start with
single-buffered64-colour modes20/8, then qualify double-buffered136 separately.
Keep PPA, indexed modes, Copper and hardware-sprite redesign out of this first
comparison. This document is a completed source assessment, not selected code
architecture or an implemented renderer.

The [owning task](../RGB-001.md) records22 shortlisted mode/case combinations.
The first18 are single-buffered; four136 follow-ups depend on the handoff design.
No source changes, build, flash, reset or new measurement occurred during this
assessment.

The Author's subsequent clarification retains rendering-time conversion for
plotted bitmaps and software sprites, and presentation/scanline-composition-time
conversion for hardware sprites. The P4 CPU owns that overlay processing before
DSI DMA reads the final image. Definition-time asset expansion is recorded under
RGB01-06 as a deferred optimization; transparency and cache-coherence concerns
must be resolved before it can replace the initial policy. This clarification
does not select a new production architecture or implement overlay support.

## Research baseline

1. Official Agon docs: `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Reviewed
   [PLOT paint modes](../../../../../agon-docs/docs/vdp/PLOT-Commands.md),
   [logical colours](../../../../../agon-docs/docs/vdp/VDU-Commands.md),
   [bitmap/sprite formats and behaviour](../../../../../agon-docs/docs/vdp/Bitmaps-API.md),
   [swap/wait semantics](../../../../../agon-docs/docs/vdp/System-Commands.md),
   and [mode definitions](../../../../../agon-docs/docs/vdp/Screen-Modes.md).
2. Reference VDP is clean at tag v2.16.0, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; MOS is clean at v3.0.2,
   `8336409351ee5314e02801a7b72a4f1bb5282519`. No reference changes.
3. Project HEAD is `abb8ea995d7ebaff06db687d0cdff7e9a60967d3`; the working tree
   contains pre-existing experimental work. HEAD alone does not identify this
   assessment's code. The source hashes below identify inspected inputs.
4. ESP-IDF5.5.5 is pinned to `b774170ff46c393eeb5e495ea37936038d3f4f4f`, verified
   in the maintained local tools checkout. Reviewed its
   [DSI documentation](../../../agents/build001/native-tools/esp-idf/docs/en/api-reference/peripherals/lcd/dsi_lcd.rst),
   [callback API](../../../agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/include/esp_lcd_mipi_dsi.h),
   and [DPI driver](../../../agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c).
   The online version-specific DSI page was unavailable during this assessment;
   no latest/stable documentation was substituted.
5. Workloads are the frozen r04 contract and existing generator. Existing raw
   partial results supplied valid P4 cases0/1/7/9/15/23/39/41/46 in20/8,
   plus0/9/41/46 in136. Preserve raw evidence, missing-pass annotations and the
   ordinary r03 image; obtain fresh matched controls for later attribution.

## Current path and required seam

The current
[factory](../../../vdp/video/extender/display/stock_runtime_controller.cpp)
selects stock VGA2/4/8/16/64 depth classes. For64 colours,
[VGA64Controller](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp)
writes one-byte `SBGR2222` pixels in VGA lane order (`x ^ 2`). Its drawing
callbacks, fast row fills and readback assume that layout. Merely allocating
three times the memory would leave the renderer writing the wrong bytes.

[StockBoundController](../../../vdp/video/extender/display/stock_runtime_controller.hpp)
drains queued primitives and prepares visible rows with native exclusion.
[StockScanlineController](../../../vdp/video/extender/display/stock_scanline.cpp)
copies each64-colour row and decorates it with hardware sprites/cursors.
[HdmiOutput::publish](../../../vdp/video/extender/display/hdmi_output.cpp)
then expands every row into panel memory before cache writeback and submission.
That full-image pass repeats even on static content. Direct rendering must
replace it with submission of pixels already resident in panel memory.

## Change matrix

| Area / current source | Required change | Preservation or risk |
|---|---|---|
| Pixel backend: `vga64controller.cpp`, `vgabasecontroller.h` | New RGB888 pixel/row writers, fills and readers using physical byte stride and ordinary x coordinates; retain common rasterizer templates. | Existing one-byte methods are private and layout-specific. Do not branch every ordinary controller operation or quietly reinterpret its row aliases. |
| Common drawing: [displaycontroller.h](../../../vdp/vendor/vdp-gl/src/displaycontroller.h) and [displaycontroller.cpp](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp) | Bind generic line/circle/glyph/bitmap algorithms to the new accessors; implement the abstract surface required for a concrete controller. | High-level primitive colours already use RGB888. This helps reuse but is not an existing RGB888 framebuffer backend. Audit actual pixel-type assumptions before reusing each template. |
| Factory/API: `stock_runtime_controller.hpp/.cpp`, [agon_screen.h](../../../vdp/video/agon_screen.h) | Explicit experimental backend selection for20/8/136; expose configuration/lifetime hooks that do not assume native allocation. | Current API returns `VGABaseController`/`VGAPalettedController`; resolution setup and alias binding are coupled to stock rows. A narrow new controller can preserve these caller-facing types, but must override resolution/allocation/teardown rather than inherit byte clears unchanged. |
| Storage/lifecycle: [VGA allocation](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp), `HdmiOutput` | Borrow panel buffers through a lifetime-managed interface; build logical row descriptors pointing into their centered image regions. | IDF owns pixel allocation. Renderer teardown must release descriptors/leases, never free panel memory. Candidate mode preparation must not clear or rebind a live display; join old draw/output owners before commit. |
| Pixel geometry: [hdmi_geometry.hpp](../../../vdp/video/extender/display/hdmi_geometry.hpp) | Reuse centered geometry; each logical pixel addresses three bytes within a3840-byte physical row. | Mode20 offset is384,168;8/136 is480,240. Logical width remains512 or320, not1280. Initialize black borders once per mode/buffer, not every frame. |
| Readback and fences: VGA64 `readScreen`, [Canvas::getPixel](../../../vdp/vendor/vdp-gl/src/canvas.cpp) | Read logical drawing pixels from RGB888 memory in RGB component order; retain prior-command completion and MOS reply path. | Double-buffer pixel queries read the drawing buffer as today. A cache submission or DMA callback is not a drawing fence. |
| RGBA2222 assets and software sprites: VGA64 bitmap methods, `showSprites` | Expand only the bitmap pixels actually drawn; preserve nonzero-alpha-as-visible semantics, clipping and paint modes. Provide compatible saved-background restoration. | No bitmap fixture or wire-format changes. Wider framebuffer storage does not eliminate per-asset conversion. Preserve64-colour quantization, not new true-colour behaviour. |
| Hardware sprites/cursors: VGA paletted scanline decoration | Explicit handling for any direct mode because the row pass will be bypassed. | They are overlays, not pixels already in the drawing plane. First fixtures hide cursor and select software sprites. Hardware-sprite tests remain deferred; ordinary fallback modes retain their current composition. Missing overlays must never be advertised as supported direct behaviour. |
| Scheduling: [stock_p4_service.cpp](../../../vdp/video/extender/display/stock_p4_service.cpp), common `SwapBuffers` dispatch | Single-buffer submit follows drawing; double-buffer completion must distinguish requested, scanned and writable buffers. | Keep independent60Hz frame counting. In double modes ordinary commands execute immediately on the foreground path; the swap currently wakes its waiter as soon as row pointers exchange. That is too early to recycle a directly scanned buffer. |
| Build/telemetry: [build_p4.py](../../../scripts/build_p4.py), [profile manifest](../../../vdp/build/p4-profiles.json), benchmark header | Separate experimental selector, validated source closure and storage identity; adapt frame-marker sampling and phase counters to RGB888. | Ordinary backend must remain reproducible. Record direct drawing, asset work, cache and ownership waits; zero full-image conversion alone does not establish zero preparation overhead. |

## Recommended bounded implementation

1. Add a project-owned experimental RGB888 controller within the current
   stock-shaped execution family. Reuse common Canvas/geometry code and narrow
   execution guards, while providing a complete pixel-access implementation for
   admitted operations. Retain VGA64 and other depth classes unchanged for the
   baseline and fallback modes. Do not revive the older `P4DisplayController`:
   [current architecture](../../architecture.md) explicitly reserves that family
   for historical non-product qualification, and it is not the active backend.
2. Keep logical64-colour semantics distinct from physical storage. Quantize
   channels exactly as existing RGB222 paths do, then write expanded B,G,R
   bytes. Bitwise paint operations act on that quantized colour value. Preserve
   alpha's existing visible/transparent interpretation rather than introducing
   blending. Add meaningful golden pixel checks for those contracts.
3. Keep public native bitmap format3 as its existing one-byte data contract;
   [vdu_sprites.h](../../../vdp/video/vdu_sprites.h) currently assigns it one byte
   per pixel. Do not redefine it as three-byte data. Two viable saved-background
   choices are canonical one-byte RGB222 backgrounds, expanded only on restore,
   or a distinctly tagged internal RGB888 background representation. The first
   is a narrow recommendation while all drawn pixels remain64 colours; it avoids
   ambiguity between public native assets and internal sprite saves. Its pack/
   restore work still belongs in drawing measurements. Three-byte backgrounds
   require changing the current `PixelFormat::Native` restore construction and
   save-size handling explicitly.
4. Use the panel-owned RGB888 allocation as the drawing target. A separate
   logical-size RGB888 image copied into720p would remove colour conversion but
   leave another full-image copy; it would be a different experiment. IDF5.5.5
   recognizes a pointer inside panel framebuffer memory and takes its no-copy
   cache-writeback path. It still flushes whole physical rows in the requested
   y range. Retain that path initially before adding dirty-region optimization.
5. Start with single-buffer modes20/8 and the correctness chart, clears, text
   needed by fixture lifecycle, lines, circles and bitmap marker. Add software
   sprite save/restore before running case46. Direct single-buffer writes can
   overlap HDMI reads and may expose flicker/tearing more directly; successful
   timing is conditional on separate visible coherence checks. This experiment
   does not promise coherent60fps single-buffer animation.
6. Add double-buffered136 only after the handoff described below is implemented
   and checked. No new sprite count, test family or indexed mode is needed to
   establish this comparison.

## Double-buffer handoff is a separate correctness/performance problem

The VDP's "hardware sprite" terminology denotes an overlay composed separately
from the logical drawing plane. In the current P4 code, the CPU executes
`decorateScanLinePixels`/`rawDrawSpriteScanline` during output preparation; P4
has no dedicated sprite-plane engine performing these operations. PPA can
accelerate image blending but is not an autonomous sprite scanout engine; its
documented operation families are fill, blend and scale/rotate/mirror in the
[IDF5.5.5 PPA guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/ppa.html).
Any later direct-output overlay implementation must retain layering and remove
old overlay pixels without corrupting the logical background. Its conversion
remains in that presentation stage under the selected initial policy.

Today four distinct pixel planes can exist: two native logical buffers plus
two HDMI buffers. A logical swap exchanges native row pointers immediately in
the queued executor; HDMI conversion later uses an independently writable panel
buffer. Direct rendering would merge those responsibilities into the two panel
buffers. Returning the former front to the foreground renderer before DMA has
switched away from it would permit drawing into a still-scanned image.

The pinned IDF driver restarts DMA using its selected framebuffer index **before**
calling `on_frame_buf_complete`. Submitting a new index after that callback
does not retroactively change the DMA frame already started. The ordinary code's
submission metadata also has an interruption window; its same-core ownership
rules need a fresh state-machine proof when logical drawing owns these buffers.

A simple implementation that executes the logical swap after one hardware edge,
submits the new index, then waits for the following edge to recycle the old front
could introduce two-edge pacing and limit throughput to30fps. This is a risk
derived from the driver/executor order, not a measured direct-renderer result.

The recommended design must stage a completed back buffer **before** its intended
hardware boundary, have DMA adopt it at that boundary, and release/notify the
logical swap caller only once the old front is safe to write. Preserve the
official next-vblank swap behaviour and independent frame counter. Do not add an
extra full-frame copy or extra scanout wait to hide ownership uncertainty. The
current drawing worker only drains on hardware notifications, so swap staging
and acknowledgement need an explicit scheduling seam. Any required wait must
be interruptible during mode teardown and must not make the callback acquire a
native/foreground mutex. This design remains unselected at the assessment gate.

## Memory and performance bounds

| Storage item | Bytes |
|---|---:|
| One existing720p RGB888 panel framebuffer |2,764,800|
| Two panel framebuffers |5,529,600|
| Mode20 one-byte logical plane currently allocated separately |196,608|
| Mode8 one-byte logical plane currently allocated separately |76,800|
| Mode136 two one-byte logical planes currently allocated separately |153,600|

Borrowing the existing panel allocations would remove the separate logical pixel
planes for direct modes, rather than add another pair of720p images. Row tables,
assets and mode-transition resources still consume memory. Preserve two panel
allocations in matched single-buffer controls where the baseline does so; report
actual allocations rather than claiming a RAM benefit without measurements.

Direct RGB888 writes increase per-pixel byte traffic versus one-byte native
drawing. Sparse work should avoid the large unconditional conversion pass;
dense fills and bitmap batches might offset some of that saving with wider writes.
Source analysis alone cannot quantify the gain. Removing expansion cannot fix
transport or eZ80 command costs, repeated sprite save/restore, scheduling, cache
writeback or unsafe buffer reuse.

## Measurement preparation and implementation gates

1. Keep the same existing fixture binary, RGBA2222 assets and VDU bytes for each
   native/direct pair. The fixture marker changes even in the r04 static case;
   use the dedicated colour chart for truly fixed-source controls.
2. Compare mode20 first, then8, then the four136 cases once ownership passes.
   Use retained mainboard results as context; do not rerun mainboard or resume
   the long campaign as part of this subset automatically.
3. Future native/direct scanout-off controls must retain the same memory layout
   and admitted workloads. A direct backend cannot use the current `hold` control
   as-is: its drawing pixels would modify the very framebuffer being scanned.
   Any held-display control needs a separate design and label.
4. Instrument drawing on both the queued and immediate foreground paths;
   current `Drain` wall scope alone misses immediate double-buffer drawing.
   Report command/fence completion, renderer work, asset conversion, cache,
   swap wait, submitted image identity and DMA cadence separately. Rework marker
   decoding to read the equivalent RGB888 pixels, without restoring a whole-row
   conversion just for instrumentation.
5. Require exact colour/readback/clip checks, saved-background round trips,
   startup/mode fallback and ownership state-machine tests before deployment.
   Stage a stable visual state and wait for the Author before advancing. Keep
   indefinite fixture controls and fast transfer with untimed verification.
6. Next step is selecting the bounded backend and buffer design in RGB01-02,
   then CPU-only implementation. No PPA work or production architecture change
   is selected. The existing ordinary image and paused campaign remain intact.

## Inspected source identities

Hashes below capture the source state used for this assessment; future edits
require refreshing the assessment rather than assuming HEAD identifies it.

| Input | SHA256 |
|---|---|
| `vdp/video/extender/display/stock_runtime_controller.hpp` | `42c48052ba287b7816653753d300168c0acea54f72681645f40ee0f8f6a3f875` |
| `vdp/video/extender/display/stock_runtime_controller.cpp` | `e49909545ea2dc570ea7002b3eb53ba4193bb3cd2a85b2a78e872e7088b4d897` |
| `vdp/video/extender/display/stock_scanline.cpp` | `c2660e1b73f3437c84a8be22e8f8e7de79268d0ca478083b023a60c3b983d28e` |
| `vdp/video/extender/display/stock_p4_service.cpp` | `8dc25092cc9102921cb9a6b2f85d1f75e461d402b2a7e8ba55f179a38df35b36` |
| `vdp/video/extender/display/stock_native_access.hpp` | `57ace2a09e7db1ef64d887a08ea5ff63f9f8525ae61dfb2153a5e35b0e6dcff3` |
| `vdp/video/extender/display/hdmi_output.hpp` | `cb531b7d5196b7916d6e5fdd0fa797429efd8bb79dc876e83883c8a192092ba0` |
| `vdp/video/extender/display/hdmi_output.cpp` | `f6ec9b02e694096eef4b392bdd0d7b6746e15fa7f08964ceb34d9f379abfab59` |
| `vdp/video/extender/display/hdmi_buffer_ownership.hpp` | `31ffaa3a320c91c3bc8a5873cd496507d722d8f57159106548e9a1682d28c509` |
| `vdp/video/extender/display/hdmi_geometry.hpp` | `85886fc5519b03dd372d966afa8567179a5b9e064b9e1dee7d7c9212a70f2d3c` |
| `vdp/video/agon_screen.h` | `c63a36a80633be684d47241fa252f74117c0d4260f86ae6bd81340ccdf6a69d8` |
| `vdp/video/vdu_sprites.h` | `95aeb568f8ec1fad96ffe320e506c13be32b1fb0404dce5a072a26ca8041bb78` |
| `vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp` | `c106c53979d2dc1239636e2ccf98916944cac38d325b24b1e5fabdbb7bccd4ba` |
| `vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.h` | `ff9531dc3213e66507b7d691841d44371af6d5492c00ea6f206d9a0c2650a101` |
| `vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp` | `d2bd84041f9ee261484eb0b3fd66b91eb15cd238d28781b4969c757fa04a4801` |
| `vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.h` | `7d3832192cbe0f38f9ee8462a2b5748f135cd2b9cb4c1c369a470813db46c3e9` |
| `vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp` | `4447b81ad53a7dc262e782600259e18fcf866dafe7e64f2c239b35dc186141fa` |
| `vdp/vendor/vdp-gl/src/displaycontroller.h` | `c939cfc407f526f782ea88018c610f565113d62d968cb53e5da0cc4d24107754` |
| `vdp/vendor/vdp-gl/src/displaycontroller.cpp` | `07f6354bf63c8f497c698beabd4eadc702516b420bc3bf6b49da55aea1dfa3d2` |
| `vdp/vendor/vdp-gl/src/canvas.cpp` | `3626baa0df539ed5a8fde03d67d236c5a38636cd914764eca702b5310bde3271` |
| `vdp/build/p4-profiles.json` | `a4c487bd1857db07936fa01c1183cea8c662b26d60e8a7a12591d2dfb8d4bdf4` |
| `scripts/build_p4.py` | `a4dbbb23d18dd73458770239d719c5d897b98138a669f1136ad4b74beb318eb7` |
| `scripts/validate_p4_build.py` | `984d92e3abce9cb6fa25d216a5469c93c55b7ef2e2d97b17bc8689bc8f7aa697` |
| `vdp/video/extender/diagnostics/render_benchmark.hpp` | `525991b448f8b3deaaaf7c9c474a913bab04cce5a1c37de4d223f76860efdcf5` |
| `docs/testing/render-load-contract-r04.md` | `2e0061139a3f620481377c6089c51627c922bb66c5d2d5c9152f04fd02d46396` |
| `tests/performance/render_load/contract-r04.json` | `8843965a47b40e8571efb4efb0269b10ba8d8b6eff487953a5a729aec2dd177c` |
| `tests/performance/render_load/generate.py` | `02b1e33c63a3ded9eb46cb38793f6c88ab84988710fd744ec56be8b722c2d9f7` |
| `agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c` | `a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373` |
