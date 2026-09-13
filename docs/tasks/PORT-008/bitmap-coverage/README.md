# Ordinary bitmap and affine command coverage — 2026-09-13

This continues the Author's faithful VDP coverage request after the bounded
video and font checks. PORT-008 owns command integration, PORT-003 the retained
renderer. No new rendering algorithm, Golem work, timing hook, firmware flash
or resumption of the held QUAL-003 graphics tranche is required by this case.
All changes remain local; human review and commit/publication gates stay open.

## Bounded plan

1. [x] P008-B01: Read the official bitmap, PLOT, buffer and affine contracts;
   inspect retained dispatch/sampling where exact behavior matters. Define
   independent pixel patterns and bind the stock/P4 references before execution.
2. [x] P008-B02: Generate a finite ordinary MOS EXEC script. Cover RGBA8888,
   RGBA2222 and mono/mask input, 8/16-bit bitmap selection, screen capture,
   in-place source-byte adjustment, viewport clipping, affine reflection,
   scaling and a generated transformed bitmap. Keep all VDU commands complete
   and below MOS's line limit; select mode outside the script.
3. [x] P008-B03: Check headless stock output against the independent pixel
   oracle, including transparency and surrounding untouched pixels. Distinguish
   documentation/stock discrepancies from port defects. Do not alter upstream.
4. [x] P008-B04: Transfer exact input through the existing SD service and invoke
   it using EMOS CLI on the already installed P4. Compare identical regions,
   then verify neutral keyboard, Legacy/SD and unchanged startup recovery.
5. [x] P008-B05: Record exact tested behavior, unsupported cases and evidence
   limits. Any needed port repair gets a separate bounded diagnosis before
   implementation. Do not mark the general command suite qualified.

## Source précis

Read-only official VDP v2.16.0 is
c7ac293d2aa81ddfa693390549bcd909069c8fc3; MOS v3.0.2 is
8336409351ee5314e02801a7b72a4f1bb5282519. The documentation checkout remains
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. Relevant paths in agon-docs:

1. docs/vdp/Bitmaps-API.md: 8-bit bitmap ID maps to buffer64000+ID; buffers
   contain contiguous row-major RGBA8888 or RGBA2222 pixels, or byte-aligned
   mono rows. Zero alpha is invisible, nonzero alpha is documented as opaque.
   Mono on-pixels use the creation-time graphics foreground. Screen capture
   uses the inclusive rectangle from the last two MOVE positions and creates
   RGBA2222 data in this VDP version.
2. docs/vdp/PLOT-Commands.md: bitmap PLOT232–239 uses selected bitmap, graphics
   coordinates, GCOL and viewport. Use foreground absolute237 for the primary
   cases, physical coordinates and single-buffer mode8. Direct bitmap command3
   has different documented clipping/painting behavior; do not silently equate
   those APIs or extend this case to double-buffer software sprites.
3. docs/vdp/Buffered-Commands-API.md: ordinary buffer write/adjust/clear;
   affine32 creates a3×3 matrix; operation11 accepts six row-major values;
   format192 is signed16-bit integer input. Command40 creates a transformed
   RGBA2222 bitmap. Explicit dimensions avoid automatic bounding-box rounding
   in this first coverage slice.
4. docs/vdp/System-Commands.md: enable the affine feature via23,0,248,1;1;,
   select bitmap transform via23,0,150,1,id;, disable with65535. Transform origin
   is the source bitmap's top-left. Integer reflection and2× scaling give
   independently computable expected pixels without trigonometric tolerance.

Retained vdu_sprites.h, vdu_buffered.h, context/graphics.h and
vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp are the implementation
boundaries. Actual Context::drawBitmap also checks bitmapTransform for direct
command3, despite older prose claiming transforms are ignored there. The
primary transformed cases deliberately use PLOT; no correction follows from
that documentary discrepancy. Stock read-pixel commands join preceding drawing
before buffer mutation/retirement. Returned MOS sysvars are not asserted here.

The installed P4 is the already recorded optional DSP-cleanup/poll1/TCP32768
r17 build; exact physical identity/admission/rollback stay in HARDWARE.local.md.
Use synthetic project-owned pixel arrays. No external artwork is needed.
Generated input is a source-hashed exploratory case, not a new released utility
or silently incremented firmware lineage. The old qualification mode matrix
remains unpromoted; SETUP-004/VDU-inventory.md owns command disposition.

## Stock reference result and preserved edge discrepancy

The generated script has93 complete MOS command lines and SHA256
5898b77a2ba46fa5aa4a9ccf7027bb0d59937b09b276b7b5e01623c6af06bc18.
The stock native capture matches12 of13 independent ideal tiles exactly.
Direct live reflection alone differs: its final destination column is blank,
omitting source column0's red/yellow/magenta pixels. The source array and ideal
oracle remain unchanged; the three missing pixels are retained as a failure of
the mathematical expectation, not erased to get a green test.

Retained vendor/vdp-gl/src/displaycontroller.cpp computes the transformed
rectangle from source corners including x=width. For x'=-x+3 and width4, its
maximum X is3. In displaycontroller.h genericRawDrawTransformedBitmap_RGBA2222
the loop uses x<drawingRect.X2, excluding x=3 even though its inverse maps to
valid source x=0. The buffered command40 implementation loops x<explicitWidth
and therefore includes all four reflected columns. This explains the observed
difference without requiring an invalid matrix or P4 transport failure.

This slice will compare P4 against the unchanged native reference across all
13 tiles and halos while reporting the ideal mismatch separately. The checker
has an explicit --reference mode with the exact reference image SHA; it does
not silently replace the ideal oracle. A parity pass proves preservation of
these selected stock pixels, not mathematically perfect reflection. No renderer
or game workaround is authorized or needed by this finding. Rally's canvas
reflection uses the same width-minus-one convention, but this fixture does not
establish whether its transparent edge contains a visible affected car pixel.

The existing experimental P4 lifetime correction affects only a leaked DSP
temporary, not this sample/bounds algorithm. Physical comparison follows on
that exact already installed image. Native evidence is under the ignored
agents/video-throughput/bitmap-stock01; no public source/assets were downloaded.


Before physical execution, case02 strengthens the alpha checks: invisible source
pixels carry blue RGB, and both colour formats draw over a white backdrop.
This distinguishes transparency from painting black over an already black
background. It adds one tile, for14 total, while retaining the independently
specified ideal reflection and its already observed stock discrepancy. The
100-line command script SHA256 is
77aec770ee3c5e1f6fc731a086e63b4bcbd66dc6beb20a5b4fc22144c5b8d3cb.
Case01 and its informative native reflection failure remain preserved; it was
not transferred to hardware. The stronger input is checked natively first.

## Physical result and scope closure

Case02 is 2,700 bytes and contains 14 tiles, with 855 independently checked
logical pixels including their halos. Stock native and P4 match the ideal
expectation for 13 tiles. Both omit the same three pixels in the live reflection;
strict stock parity passes all 14 regions with zero differences. The unchanged
ideal oracle still reports that omission. Its explicit reference mode accepts
stock parity only, and records the exact reference image hash. A negative check
that overwrites a surviving white backdrop pixel is rejected, demonstrating
that this exception does not mask unrelated alpha regressions.

Native reference frame-000600.png SHA256 is
8153c42a6e6bbccffd48b784bf8cca2fe25be8e48fea73077cc71688741ab3cf.
The ordinary five-second P4 observation retains 299 snapshots: one previous
640×480 surface followed by 298 at 320×240, with no sequence gaps. These are
static image observations, not rendering or physical scanout measurements.
Exact inputs, EVF bytes, decoded pixels, checker output and admission journals
remain under ignored agents/bitmap-coverage; native evidence is under
agents/video-throughput/bitmap-stock02. No renderer or firmware changed.

Read-only inspection of Rally's actual build dependency,
rally-production/include/car.hpp, and rally-game/src/main.cpp establishes that
all 77 pixels in uploaded source column zero are transparent in each of its
five 102×77 player-car views. Therefore this specific reflected-column omission
removes no visible player-car pixel. The source-hashed inspection does not
establish fractional traffic-scaling bounds or general correctness of affine
clipping; those remain outside this case.

The same 2,700-byte input passed staged and active SD readback before execution.
After capture, ordinary EMOS commands return to Legacy and start sdserve;
startup and the exact script are independently read back, then the service
exits. The final SD journal has no pending request. Keyboard admission remains
ready, neutral and released under the same boot, with the owned session canceled.
No reset, flash, root-startup edit or accepted production-file change occurs.
HARDWARE.local.md records exact foreground and candidate identity. No observer
is left running. All changes remain local for human visual and commit review.

P008-B01–B05 are machine-complete. This evidence covers these mode8 pixels only,
not all colour depths, sprite animation, arbitrary affine matrices, malformed
buffers, deletion of active resources, all PLOT modes, or query return values.
No general command-suite qualification or release follows.

Reproduction from the Extender root:

```text
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/make_case.py agents/bitmap-coverage/new-case
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/check_pixels.py agents/bitmap-coverage/new-case/oracle.json <capture.png-or-evf> --reference <exact-stock.png> --output <result.json>
```

Select mode8 outside the generated script and EXEC bitmaps.txt through ordinary
MOS/EMOS. Omitting --reference checks the mathematical oracle and intentionally
reports the inherited reflection discrepancy. New runs must bind their own
runtime/input/reference identities and preserve the historical evidence.
