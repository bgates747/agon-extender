# Indexed framebuffer research — current pipeline inventory

R07-01 complete, 2026-10-11. Source inspection only: no new build, benchmark,
emulator run, device access or firmware change. This is a bounded précis for
[RESEARCH-007](../RESEARCH-007.md), not a storage architecture decision.

## Findings in plain English

1. Extender already has compact stock storage: packed palette indices in
   lower-colour modes and one-byte physical RGB222 in ordinary 64-colour modes.
   Selected HDMI 64-colour geometries instead use three-byte B,G,R pixels so
   the P4 can draw directly into an HDMI output image. These three bytes still
   express stock six-bit colour semantics; they do not provide arbitrary
   24-bit drawing colours.
2. Software sprites save **one byte per background pixel**, including on the
   three-byte controller. Their saved backgrounds did not become three times
   larger. Bitmap assets retain their own formats independently.
3. The current rolling HDMI path still owns full RGB888 output images in PSRAM.
   DMA2D copies strips into SRAM, where the P4 CPU adds hardware sprites before
   DSI scanout. Compact drawing storage alone would not remove those images or
   the output expansion work. Whether a different pipeline can do so remains
   for R07-03–05.
4. A programmable palette index is different from a byte containing RGB222.
   Stock palette changes recolour existing pixels in lower-colour modes, but
   stock 64-colour logical remapping affects subsequent drawing. A common
   indexed representation must preserve that distinction; custom 256 colours
   remain an unaccepted extension.

## Exact baseline and selection

The inventory follows Extender source commit
`188a45715144208d222b26dff5f56f52b7890eef`; the scope freeze is `01923768`.
All **5,501** retained r17 source-input entries match the inspected checkout by
SHA256. The retained build was made from commit
`0982d5678f0307d3fe2a6bc0b280cb295c0a27d2` plus an explicit dirty source snapshot,
subsequently committed in `188a4571`. Do not relabel its original manifest.

| Reference or dependency | Selected identity |
|---|---|
| Official Agon documentation | `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` |
| Official VDP | v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3` |
| Official MOS | v3.0.2, `8336409351ee5314e02801a7b72a4f1bb5282519` |
| Vendored vdp-gl import baseline | `all-the-plots`, `ac2dd5986daf496c43ae8e7fe41836274aec54a0` |
| ESP-IDF | 5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f` |
| Arduino dependency | 3.3.11, retained dependency lock |
| OLIMEX LT8912B component | ESP32-P4-PC `04032d68e5c727870f9d40beb9e37b7ab3a66916`, provenance below |

Official MOS/VDP checkouts were clean at their exact local release tags. The
documentation checkout had no tracked changes and one preserved untracked
Finder metadata file. No remote release survey or reference mutation occurred.
The vdp-gl revision identifies the import, **not an unmodified current vendor
tree**. [Reviewed baselines](../../dependencies/reviewed/source-baselines.yaml)
and [LT8912B provenance](../../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json)
identify those owners; [source hashes](SOURCE-BASELINE.json) pin inspected files.

The retained compilation evidence is P4-PC HDMI build
`port-008-stream-r17-b2026-10-11-22-37-46Z`, app 1,780,560 bytes, SHA256
`963737f032817cfa97af12ed4d4466d6f4748d8800305a9ce05b469c32ae6c2e`.
Its compile commands select stock runtime, direct RGB888, automatic HDMI carrier,
rolling scanout and PPA 320×240. The source/config/graph are retained under the
ignored `agents/completion-removal-r01/p4-r17/`; the normalized baseline records
their hashes without machine-specific paths. This inventory checks that graph
and input identity; it does not rerun compilation or claim installation.

**Production is separate:** [current selection](../../../production/current.yaml)
remains v0.1.0 / `extender-installation-r02`, the approved DevKit bundle.
Neither current source nor r17 becomes production through this review. The
bench's installed image was not observed; fsim retains the bench.

## Contracts read before implementation details

1. [VDU commands](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md):
   VDU 17/18 select colours and plotting operations; VDU 19 has the depth-dependent
   palette behaviour above. Public physical colour numbers use RRGGBB.
   The retained official
   [setLogicalPalette](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h)
   applies underlying palette changes only below 64 colours, as does the port.
2. [Screen modes](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Screen-Modes.md):
   stock mode 8/136 is 320×240×64, mode 20 is 512×384×64, mode 0 is 640×480×16.
   The geometry predicate, rather than a mode-number assumption, selects storage.
3. [Bitmap API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Bitmaps-API.md):
   RGBA8888, RGBA2222, mask and Native are distinct formats; alpha is an opacity
   test rather than blended translucency. Captured-screen RGBA2222 is distinct
   from logical palette indices and saved Native sprite backgrounds.
4. [Copper API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Copper-API.md):
   drawing uses the primary palette; output may select different palettes by
   scanline. Stock 64-colour modes do not use this paletted scanout mechanism.
   This makes the point where indices become physical colours material.

## Drawing storage and row tables

The selected [controller factory](../../../vdp/video/extender/display/stock_runtime_controller.cpp)
uses the [RGB888 geometry predicate](../../../vdp/video/extender/display/rgb888_pixel.hpp).
All other depths/geometries retain the stock-shaped controller family below.
Single/double buffering changes image count, not bytes per pixel.

| Selected controller | Pixel representation | Tight row bytes for width W | Example |
|---|---|---:|---|
| VGA2 | Packed 1-bit palette index | W/8 | 2-colour modes |
| VGA4 | Packed 2-bit palette index | W/4 | 4-colour modes |
| VGA8 | Packed 3-bit palette index | 3W/8 | 8-colour controller; not eight-bit storage |
| VGA16 | Packed 4-bit palette index | W/2 | Mode 0: 320 bytes/row |
| VGA64 | One-byte SBGR2222 physical signal colour | W | Ordinary 64-colour geometries outside the predicate |
| P4Rgb888 | Three bytes B,G,R, four levels/channel | 3W | 64 colours at 320×240, 512×384, and auto-carrier 848×480 |

Ratios come from constructors in the vendored
[2](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga2controller.cpp),
[4](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga4controller.cpp),
[8](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga8controller.cpp),
[16](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga16controller.cpp),
[64](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp) and
[RGB888](../../../vdp/video/extender/display/p4_rgb888_controller.cpp) controllers.
The stock native byte uses low R bits, then G, then B, plus sync bits; it is not
the public RRGGBB colour number. Stock signal rows also use the `x ^ 2` lane order.

[VGAPalettedController::allocateViewPort](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp)
selects PSRAM for this build. The base allocator creates pixel pools and separate
drawing/visible row tables through
[prepareViewport](../../../vdp/video/extender/display/checked_viewport_allocation.hpp).
Scrolling can move row pointers as well as copy pixels; storage is not safely
described as one universally contiguous image.

For larger direct RGB888 geometries, P4Rgb888 borrows the IDF panel images and
points logical rows into their centred rectangle, retaining carrier-width stride.
That layout cannot scroll by rotating the physical panel rows; the partial-scroll
copy remedy copies B,G,R spans. At 320×240 with PPA enabled, it instead owns
private logical front/back storage. [Rgb888PixelRef](../../../vdp/video/extender/display/rgb888_pixel.hpp)
converts between stored channel bytes and the six-bit value used by upstream
drawing/GCOL helpers. The unused non-rolling overlay-background allocation is
not part of this rolling build.

## Assets, saved backgrounds and palette owners

1. [createBitmapFromBuffer](../../../vdp/video/vdu_sprites.h) retains a buffer's
   selected RGBA8888 (4 bytes/pixel), RGBA2222 (1), mask (packed bits per row),
   or Native representation; changing drawing storage does not automatically
   convert those assets. [Sprite admission](../../../vdp/video/sprites.h) excludes
   Native frames. RGBA8888 assets do not establish full-colour framebuffer support.
2. [setSprites / hideSprites / showSprites](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp)
   allocate saved backgrounds for single-buffer software sprites, restore them
   in reverse order and redraw. Allocation uses the largest frame area times
   `getBitmapSavePixelSize()`, which is one in the selected controllers, including
   [P4Rgb888](../../../vdp/video/extender/display/p4_rgb888_controller.hpp).
   Its raw bitmap save/restore helpers translate between one-byte Native values
   and three-byte drawing pixels. Hardware sprites do not keep these saved areas.
3. [agon_screen.h](../../../vdp/video/agon_screen.h) owns the logical mapping to
   physical RRGGBB colours; [agon_palette.h](../../../vdp/video/agon_palette.h)
   owns the stock lookup tables. VGAPalettedController owns output palettes,
   RGB-to-index lookup and Copper signal selection. The
   [stock scanline adapter](../../../vdp/video/extender/display/stock_scanline.cpp)
   prepares physical signal rows from the selected paletted state. RGB888 storage
   still quantizes drawn channel values to four levels/channel.

## Output ownership and conversions

| Stage / owner | Selected HDMI behaviour | Storage / conversion |
|---|---|---|
| P4 drawing worker, StockRuntimeController | Drains retained primitives and software sprites; native guards protect row access | Packed/native or B,G,R drawing rows as selected above |
| P4 output worker, HdmiOutput | Publishes borrowed panel storage, or prepares/expands stock rows into an output image | RGB888 panel images; no full-image conversion for the borrowed direct path |
| P4 output worker, 320×240 scaler | Prepares an RGB888 source image, including row overlays, then submits PPA SRM | Blocking RGB888→RGB888 bilinear 2×; 640×480 centred in 848×480 |
| Patched IDF rolling driver, DMA2D | Copies one selected PSRAM background strip into a free SRAM slot | Three 32-row RGB888 slots, generation/ownership checks |
| P4 copy-completion callback, rolling Scene | Adds immutable hardware-sprite/cursor data to intersecting spans | Temporary native signal bytes → retained upstream sprite painter → B,G,R strip |
| DSI DMA, then LT8912B | Scans the completed SRAM strips; bridge emits HDMI | RGB888 input/output configured; no arbitrary palette-index output configured |

Source owners:
[StockP4Service](../../../vdp/video/extender/display/stock_p4_service.cpp),
[native controller binding](../../../vdp/video/extender/display/stock_runtime_controller.hpp),
[HdmiOutput](../../../vdp/video/extender/display/hdmi_output.cpp),
[PPA scaler](../../../vdp/video/extender/display/hdmi_ppa_scaler.cpp),
[rolling driver](../../../vdp/video/extender/display/rolling/strip_runtime.inc),
[scene copying](../../../vdp/video/extender/display/rolling/scene.cpp) and
[scene composition](../../../vdp/video/extender/display/rolling/scene.hpp).
The bridge scene deep-copies selected visible hardware RGBA assets into one of
three PSRAM arenas; the callback never traverses live FabGL sprite pointers.
The retained upstream sprite body is in
[stock_sprite_body.inc](../../../vdp/dsi-strip-test/main/stock_sprite_body.inc).
Packed-controller and 320×240 paths compose row overlays before publication;
their rolling scene contains no second copy of those overlays.

The ordinary panel flag `use_dma2d=false` does **not** mean this composition
avoids DMA2D: the rolling derivative separately uses `esp_async_fbcpy`.
[strip_driver.cmake](../../../vdp/video/extender/display/rolling/strip_driver.cmake)
derives the selected DPI/DW-GDMA sources from pinned IDF inputs without editing
the SDK checkout. The current PPA configuration establishes no L8/CLUT capability
finding; that is R07-03.

## Allocated image inventory, not a runtime memory measurement

Payload arithmetic excludes row tables, alignment, palettes, assets, worker
stacks, allocator overhead and scene capacities. MiB means 1,048,576 bytes.
Rows below are not additive in every mode: direct larger modes borrow the output
images, while 320×240 owns separate logical images. The panel normally allocates
two images, with an explicit one-image allocation fallback.

| Allocation / owner | Source-established payload |
|---|---:|
| 848×480 RGB888 panel image, IDF | 1,221,120 bytes each; 2,442,240 for two |
| 684×384 RGB888 panel image, IDF | 787,968 bytes each; 1,575,936 for two |
| 320×240 RGB888 logical image, P4Rgb888 | 230,400 bytes each; two in double-buffered mode |
| 320×240 RGB888 PPA source staging, scaler | 230,400 bytes |
| Three maximum-width 848×32 RGB888 strips, rolling driver | 244,224 bytes internal SRAM, retained across carrier changes |
| Three 1024×768 one-byte snapshot slots, snapshot pool | 2,359,296 bytes PSRAM (2.25 MiB) |
| Single-buffer software-sprite saved area | Largest frame width × height bytes per sprite |
| Hardware-scene arenas | Up to three retained, asset-dependent PSRAM capacities; no fixed total inferred |

The last fixed allocation deserves explicit notice: [updateVGAController](../../../vdp/video/agon_screen.h)
constructs an RGB222 direct snapshot pool, and its
[constructor](../../../vdp/video/extender/display/presentation_snapshot_pool.cpp)
allocates all three maximum-size slots, including in this HDMI build.
`StockP4Service::publish` takes the HDMI branch and returns before browser
snapshot production. Thus browser publication is bypassed, **not the snapshot
allocation**. This is a source-observed review opportunity, not a measured
bottleneck or authorization to change allocation/lifecycle contracts.

For the non-HDMI source variant, StockP4Service prepares physical RGB222 rows
into these immutable slots on demand. The
[browser provider](../../../vdp/video/extender/web/browser_video_provider.cpp)
accepts RGB222/RGB888 snapshots; the stock producer selects RGB222. Subsequent
network compression does not make those bytes programmable palette indices.
This build's compiled browser/provider code is not evidence of simultaneous
HDMI and browser video publication.

## Inventory boundary and next question

The older `plane_storage.cpp`, `palette_state.cpp`, `p4_display_controller.cpp`,
`p4_frame_service.cpp` and `presentation_compositor.cpp` implementations are
absent from the retained product compile graph. Shared headers/types remain
referenced; their presence does not select those older execution paths.

R07-01 is complete. R07-02–07 and D01/D02 remain open. The next authorized
decision, if the Author selects it, is semantic review: what must remain an
index, what must become a physical colour, and when palette/Copper changes
must affect already drawn pixels. No hardware acceleration feasibility,
new allocation design, performance prediction or implementation is established
by this inventory.
