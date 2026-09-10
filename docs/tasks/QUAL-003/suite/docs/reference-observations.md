# Shapes reference observations — 2026-09-08

The 24-page application has been compiled and exercised with official Fab
1.2.4 and pinned MOS 3.0.2 in the project profile. All 24 pages finish in the
full tour and independently after a fresh boot. The selected pixel checks
report **237/244 correct, seven mismatches, no query timeouts**. Successful
samples do not constitute whole-page visual acceptance or Extender hardware
qualification.

The Author explicitly requested retaining documented VDU calls regardless of
current Extender support. The tests therefore expose the differences below;
they do not change command meaning to hide them. Extender's agent owns its
implementation decisions and any explicit local skips.

## 1. SHP-11/12 — Arc point order

The official local `agon-docs/docs/vdp/PLOT-Commands.md` describes the first
point as the start, the second as the centre, and the third as an end-direction
point for arcs, segments, and sectors.

The reference implementation's `Context::plotArc`, `plotSegment`, and
`plotSector` pass `(p3,p2,p1)` to Canvas routines whose first pair is the
centre and second pair is the start. Thus the implemented order differs from
the documentation. This observation does not resolve which contract Extender
should adopt.

SHP-11 displays quarter, half, and major arc cases in two rows. `DOC` uses
start/centre/end; `REFERENCE` uses centre/start/end. A yellow cross marks the
intended centre. End-direction points lie beyond the intended radius. The
reference-order row draws around the intended centres, while the documented
row produces displaced/different geometry.

SHP-12 compares segments and sectors with both point orders and both minor
and major sweeps. Grey radius guides are separate from tested geometry.

The failing samples are:

| Page | Sample | Coordinate | Expected RGB | Observed RGB |
| --- | --- | --- | --- | --- |
| SHP-11 | Documented quarter arc top | 80,124 | 255,255,255 | 0,0,0 |
| SHP-11 | Documented half arc top | 248,124 | 255,255,255 | 0,0,0 |
| SHP-11 | Documented major arc top | 416,124 | 255,255,255 | 0,0,0 |
| SHP-12 | Documented minor sector interior | 390,106 | 0,255,255 | 0,0,0 |
| SHP-12 | Documented major segment interior | 182,170 | 0,255,255 | 0,0,0 |
| SHP-12 | Documented major sector interior | 390,170 | 0,255,255 | 0,0,0 |

SHP-11 passes 3/6 samples and SHP-12 passes 5/8. All centre-first control
samples pass. One documented-order segment sample coincidentally falls in
the displaced fill; that sample does not establish that the shape is correct.

Reference source, relative to the installed official Fab checkout:

1. `src/vdp/vdp-console8/video/context/graphics.h`: `plotArc`,
   `plotSegment`, `plotSector`.
2. `src/vdp/userspace-vdp-gl/src/canvas.h` and `canvas.cpp`: `drawArc`,
   `fillSegment`, `fillSector` and their centre/start/end parameter contracts.

## 2. SHP-23 — Direct bitmap drawing and clipping

`agon-docs/docs/vdp/Bitmaps-API.md` states that `VDU 23,27,3,x;y;` draws at
pixel coordinates without obeying the graphics viewport.

The test first uses PLOT to establish active clipping, then issues direct
bitmap drawing outside that viewport. The expected white shaft pixel at
`196,292` reads black in this reference emulator. After resetting viewports,
the identical direct drawing command at the labelled `CONTROL` location
works; its white shaft pixel at `276,292` passes. The ordinary bitmap PLOT
clipping sample also passes. The page therefore reports 2/3 samples correct.

The uploaded RGBA2222 arrow, transparent corners, and absolute/relative
foreground/background/inverse bitmap variants remain in the test.

## 3. SHP-05 — Thickness observation

The diagonal lines visibly widen for thickness 1, 2, 4, and 8. Circle outlines
remain thin in this reference renderer. The page's eight pixel checks cover
filled controls and their exterior; they do not certify curved-outline
thickness. This remains a visible observation for review.

## Reproduction and artifacts

From the repository root:

```sh
make -C examples/extender check
make -C examples/extender review
make -C examples/extender run PAGE=11
```

`review` deliberately returns nonzero when samples disagree, including the
seven recorded here. It does not mark them as successful or skip the commands.
`build/review/results.json` records each expected/observed RGB value, while
`build/review/shpNN.bmp` contains pixel-for-pixel captures of the real SDL
render output. `debugger.log` records page results and the successful return.
These generated files are ignored by Git and can be recreated.

The application retains four bytes per page at the `results` symbol:
`total, correct, wrong, timeouts`. The current page's RGB replies are retained
at `observed_pixels`; generated probe manifests associate these bytes with
sample names and coordinates. On a query timeout, later queries are skipped
to prevent a delayed reply being attributed to the next request. This never
turns an incomplete page into a pass.

The final reviewed-build candidate is 31,065 bytes, SHA-256
`5c386b1edb1252aca6780a2d45fc6eea9a8daf4f1dd37d8f7ab8d0a30b536abd`.
