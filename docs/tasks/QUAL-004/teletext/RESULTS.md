# Static Mode7 results — 2026-09-20

## Executive summary

The physical mainboard VDP and P4 EDP images match **all 307,200 pixels** of the
640×480 static teletext page. Two fresh-reset mainboard captures match; two
separate P4 generations (27/28) match. All structural checks pass on both
endpoints. No unexpected reset, incomplete capture or renderer change occurred.

| Tested static content | Mainboard versus Extender |
|---|---|
| Text, seven foreground colours and national symbols | Exact image parity |
| Contiguous/separated mosaics and held/released graphics | Exact image parity |
| Background colours, conceal and return to normal text | Exact image parity |
| Double-height top/bottom and normal-height restoration | Exact image parity |
| Entire raster, including five unused bottom rows | 0 differences / 307,200 pixels |

This is one static page, not exhaustive teletext compatibility. Flash timing,
scrolling, dynamic updates and all control-code combinations remain unqualified.

## Evidence and method

[Contract](CONTRACT.md) and generator/inputs were frozen in `7f7407c0`, with
structural checks frozen in `e7bcd3c9`, before bench mutation. Fixture identity
is `teletext-static-probe-r01`, registry r94. Mode7 was selected on each route
only in temporary startup. Existing scene player and all-depth diagnostic were
reused; deployed fixture bytes and sidecar were read back and hash-verified.

Mainboard capture taps the visible VGA16 scanout after palette expansion and
composition. P4 supplies immutable raw snapshots. No masking, resizing or colour
tolerance was used. P4 retained the preceding verified key-query candidate;
its flash was not reread/replaced during this run. EMOS was unchanged.

Independent checks establish a solid contiguous white mosaic cell, both white
and black in the separated cell, presence of each text colour, nonempty yellow
pixels in both double-height halves, and black unused bottom rows. They do not
constitute an independent font rasterizer; whole-glyph correctness here means
exact stock-reference parity. The check rejects deliberately altered mosaic
and bottom-row pixels. Existing five decoder and four comparator tests passed.

The descriptive byte strings on mosaic rows intentionally remain in graphics
mode: lowercase characters there render as mosaics, identically on both devices.
The page is not asserting that those byte strings display as ordinary captions.

1. [Comparison and structural checks](evidence/results.json).
2. [Mainboard/P4 images, zero-difference image and compressed captures](evidence/TTSTATIC/).
3. [Artifact and restoration receipt](evidence/receipt.json).
4. [Evidence hashes](evidence/SHA256.json).
5. [Immutable scene identity](manifest.json) and [generator](prepare.py).

Run `QUAL-004-2026-09-20-23-52-42Z` took **124.288 host wall-clock seconds** for
reset/startup, command entry, two serial captures, P4 snapshots, comparison and
return to SD service. Backup/install and final restoration are excluded; this
is acquisition duration, not rendering performance.

Artifact-registry validation passed. The broader version-record validator stops
on an existing `hardware/designs/light2-harness-r02/profile.yaml` connectivity
hash mismatch (expected `560ab589…`, actual `c68e4d4f…`). Those wiring files were
unchanged by this task; no blanket full-validator pass is claimed.

## Closeout

Original mainboard application sectors and startup were restored and verified.
Final MOS prompt, keyboard admission/release and closed SD/serial/video services
are recorded in the receipt and final image. No emulator or voice cue requested.

Cumulative retained static coverage is **71 scenes / 13,231,104 pixels** across
the recorded firmware campaigns. The four prepared Copper controls and existing
crash findings remain deferred/open. This result qualifies the demonstrated
teletext subset only.
