> Upstream single-display documentation. For paired builds and review, use
> [the owning task instructions](../README.md). Deployment commands below are
> historical and are disabled in the paired Makefile.

# Extender VDU demos

Small eZ80 applications exercising the VDU surface intended for Extender's
Exclusive Compatible mode.

`bitmaps.bin` implements the approved
[bitmap, matrix, and sprite suite](docs/tasks/EXT-004.md): 32 pages with 123
keypress stages using the 34 × 34 Blender axes artwork in RGBA2222 and
RGBA8888. It covers loading, alpha masks, compositing, all 13 documented 2D
matrix operations, baked transforms, and software/hardware sprites.

Build from the agon-utils repository root:

```sh
make -C examples/extender
```

This uses `ez80asm` and the repository's `.venv/bin/python` to produce
`tgt/hello.bin`, `tgt/shapes.bin`, and `tgt/bitmaps.bin`, with assembler listings, symbols, and
generated VDU streams in `build/`. `make -C examples/extender clean` removes
those generated files. The build does not require the Nurples checkout.

Bitmap assets are generated from the preserved PingoASM inputs under
`assets/bitmaps/source/`. The original RGBA8888 file already existed; this
build reproduces it exactly from the PNG. Twenty-four deterministic raw assets
and their manifest deploy under `/extender/assets/bitmaps/`, including cutout,
alpha-band, frame, mask, and pattern controls. The original artwork is opaque;
transparent derivatives are explicitly labelled. Both formats display in
mode 20's 64 colours.

```sh
make -C examples/extender run
make -C examples/extender run PAGE=26
make -C examples/extender check
make -C examples/extender review
```

The default app is Bitmaps. Select mode 20 before launching: 512 × 384,
64 colours, 60 Hz. Each key advances one stage or page; Escape removes live
sprites, releases owned resources, clears the display, and returns to MOS.
Movement and animation are stepped for inspection. At a mode-20 MOS prompt,
use `load bitmaps.bin`, then `run` or `run . N` for page N=1–32.

| Pages | Bitmap suite coverage |
| --- | --- |
| BSP-01–10 | Asset loads, addressing, alpha, PLOT variants, GCOL, compositing, clipping, capture, byte operations, masks |
| BSP-11–19 | Identity, scale/reflection, rotation, pivots, shear/skew, composition/inverse, number formats, baking, context state |
| BSP-20–25 | Software sprite lifecycle, positioning, deferred refresh, frame animation/replacement, GCOL, overlap |
| BSP-26–32 | Hardware sprites, mixed layers, XOR exception/demotion, transformed frames, bounded population, sharing, reset/rerun |

The application executes generated stage programs containing VDU packets,
audited API calls, and checked SD loads. The file loader reads the expected
length plus one byte into its own 32 KiB staging area and verifies the exact
length before uploading anything. Missing, short, or oversized files produce
a recoverable error page. Chunks are consolidated before bitmap creation.
The preserved vendor snapshot is supplemented by four exact-width sprite
adapters under `src/asm/bitmap_adapters.inc`.

`check` independently decodes stage programs/packets and validates assets,
compiled tables, memory extent, and command coverage. `review` captures every
stage through the actual SDL presentation and collects bounded pixel replies;
hardware sprites are assessed from presentation images, since framebuffer
queries do not include them. More focused qualification commands are:

```sh
.venv/bin/python examples/extender/tests/review_bitmaps.py --isolated-all
.venv/bin/python examples/extender/tests/review_bitmaps.py --page 32 --repeat 2
.venv/bin/python examples/extender/tests/review_bitmaps.py --page 22 --escape-stage 2
.venv/bin/python examples/extender/tests/review_bitmaps.py --fault truncated
.venv/bin/python examples/extender/tests/validate_bitmap_frames.py examples/extender/build/bitmap-review
```

The headless harness restores startup after each run. Fault injection restores
the deployed asset in a `finally` block. Presentation comparisons include
software deferred refresh, hardware movement and XOR, matrix equivalence,
frame wrap, and background stability. See the
[bitmap implementation and reference observations](docs/bitmap-reference-observations.md)
for the API contracts and renderer interactions found during review.

`shapes.bin` implements all 24 pages of the
[Shapes test plan](docs/tasks/EXT-003.md), covering all 28 defined PLOT families:

| Pages | Coverage |
| --- | --- |
| SHP-01–05 | Movement, points, line directions/endpoints, patterns, thickness |
| SHP-06–12 | Triangles, rectangles, parallelograms, circles, ellipses, arcs, segments, sectors |
| SHP-13–18 | Horizontal/flood/path fills, paint variants, all GCOL operations, 64-colour mapping |
| SHP-19–22 | Origins, scaling, viewports, clears, rectangle copy/move, scrolling |
| SHP-23–24 | Bitmap plots, graphics text, command buffers, contexts, affine transforms |

Shapes requires mode 20 (512 × 384, 64 colours, 60 Hz), selected before
launch. Each completed page waits for a keypress. Any key other than Escape
advances to the next test; after the last test it returns to MOS with the
picture intact. Escape clears the screen and returns to MOS from any page.
Individual-page runs use the same controls. Each page displays a command
description and selected pixel-query results. These samples supplement visual
review. Missing query replies are bounded and reported. Drawing and probe
streams are embedded, so neither app needs assets.

`scripts/build_shapes.py` and `scripts/shapes_pages.py` generate exact-width
VDU packets and JSON command/probe manifests in `build/shp01.*` through
`build/shp24.*`. The assembly uses a generated descriptor table. Bitmap data,
captured endpoint magnifications, matrices, and a reusable motif use only
buffer IDs 60000–60003, released before each page's key wait. The vendored API
snapshot is unchanged. Documented commands remain included irrespective of
current Extender support.

Reference checks currently report **237/244 correct, no reply timeouts**.
SHP-11/12 expose a disagreement between documented arc point order and the
reference implementation; both orders are labelled and exercised. SHP-23
exposes direct bitmap drawing retaining a graphics clip. These mismatches
remain visible and are described in the
[reference observations](docs/reference-observations.md). The emulator result
is not a physical Extender qualification.

```sh
make -C examples/extender check
make -C examples/extender review APP=shapes
```

`check` independently decodes every packet and verifies the binary header,
embedded data, descriptors, and PLOT-family coverage. `review` deploys/selects
the tour and runs the stock emulator headlessly with simulated SDL key events.
It captures actual frames and RGB replies under `build/review/`, including
`results.json` and `debugger.log`. It exits nonzero for pixel mismatches,
including the documented reference discrepancies. Review additionally needs
GCC and the installed SDL3 headers; the normal build does not.

`hello.bin` is a normal MOS ADL executable loaded at `0x040000`. It selects
text-cursor output, prints `Hello World!` followed by CR/LF, and returns to
MOS with status zero. It requires no assets or keyboard input. Video-mode
selection belongs in the SD card's `/autoexec.txt` before the program runs;
the application does not select a mode. EMOS owns the VDU route to the EDP.

`src/asm/api.inc` includes the entire imported API set, so this build checks
that all its dependencies resolve. Applications define `origin_left` and
`origin_top` for the inherited fixed-point sprite positioning helpers; Hello
World uses zero for both. Vendored source, license, and hashes are under
[`vendor/nurples/`](vendor/nurples/README.md).

Shapes sends literal VDU streams through MOS. Bitmaps exercises the imported
bitmap and sprite routines and the new adapters; audio, font management, and
direct timer/interrupt helpers remain dormant.
Inherited implementation findings and validation evidence are recorded in
[`docs/development/2026-09-08.md`](docs/development/2026-09-08.md).

The local emulator is generated by the canonical `agon-dev-env` setup tool:

```sh
make -C examples/extender emulator-setup
make -C examples/extender deploy
make -C examples/extender run
```

`emulator-setup` builds and provisions the profile; `deploy` performs the same
refresh and copy while preserving startup. `run` deploys, selects Bitmaps in
startup, and launches using `cd .emulator && ./fab-agon-emulator`.
To select one page or return to Hello World:

```sh
make -C examples/extender run APP=shapes PAGE=1
make -C examples/extender run APP=shapes PAGE=24
make -C examples/extender run APP=hello
```

`select` performs the same deployment/startup selection without launching.
Selection keeps the previous different startup in `.emulator/autoexec.previous.txt`.
To launch the existing deployment without rebuilding or copying, use
`cd .emulator && ./fab-agon-emulator` from this directory.

The ignored profile contains visible runtime links and its own virtual SD:

```text
.emulator/
  fab-agon-emulator       generated executable launcher
  fab-agon-emulator.bin   link to the official Fab runtime
  firmware/              link to the runtime firmware
  mos_platform.bin       pinned MOS image link
  mos_platform.map       matching symbol-map link
  sdcard/
    autoexec.txt
    bin/                 shared utility links
    extender/
      hello.bin
      shapes.bin
      bitmaps.bin
      <other apps>.bin
      assets/
        <shared supporting assets>
```

All deployable applications belong directly in `tgt/` as `.bin` files.
Supporting assets belong under `tgt/assets/`, with subdirectories allowed.
Deployment replaces only the profile's `/extender` application tree with
copies of that payload, removes stale deployed files, and ensures the shared
`assets` directory exists even when empty. Generated listings and source files
do not belong in `tgt/`. Apps run with `/extender` as their working directory
and reference shared files as `assets/...`. Rebuilding alone does not update
the deployed copies.

Initial CRLF startup selects video mode 3, changes to `/extender`, loads
`hello.bin`, and runs it. Subsequent setup/deployment preserves `autoexec.txt`.
Explicit Shapes selection uses mode 20, loads `shapes.bin`, and invokes `run`
for the full tour or `run . N` for an individual page, N=1–24. At a mode-20
MOS prompt, the equivalent commands are `load shapes.bin` followed by `run`
or the selected-page variant.
The canonical setup currently selects the installed official Fab 1.2.4 runtime
and verified stock MOS 3.0.2; its runtime location and override are maintained
in `agon-dev-env/profiles/README.md`. This is a stock VDU reference profile,
not an ESP32-P4 or EMOS emulator. The Author visually validated Hello World
and its return to the `/extender` MOS prompt on 2026-09-08.

The Extender command-disposition authority remains
`../../../agon-extender/docs/tasks/SETUP-004/VDU-inventory.md` relative to this
directory. Its supported-command scope is broader than the convenience
wrappers currently present in the imported API files.
