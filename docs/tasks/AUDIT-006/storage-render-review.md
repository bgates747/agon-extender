# AUDIT-006 W6 — Native storage and concrete rendering review

Status: source audit, 2026-09-10; proposed dispositions await the integrated
W7/W8 review. No executable change, build, hardware operation or performance
claim accompanies this report. This is the storage/concrete-depth portion of
[AUDIT-006](../AUDIT-006.md), not a replacement task or a new backend contract.

## Reference and coverage boundary

The comparison uses Extender checkpoint `047ffe8`, stock VDP v2.16.0
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, and its selected vdp-gl
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Git-object comparison verified that
the vendored `displaycontroller.{h,cpp}`, `vgabasecontroller.{h,cpp}`,
`vgapalettedcontroller.{h,cpp}` and all ten headers/sources for VGA2/4/8/16/64
are byte-identical to that selected graphics-library commit. Their presence
does not mean the P4 builds compile the concrete controllers: the current
P4 controller explicitly replaces them.

Official documentation reviewed first:

1. [VDU commands](../../../../../agon-docs/docs/vdp/VDU-Commands.md), scrolling
   at line 270 and graphics viewports at line 410: viewport coordinates are
   inclusive; a one-pixel-high viewport has equal top/bottom coordinates.
2. [Bitmap API](../../../../../agon-docs/docs/vdp/Bitmaps-API.md), capture at
   line 61 and formats at line 96: screen captures have used RGBA2222 since
   VDP 2.6.0; internal native sprite backgrounds are a different representation.
   The old direct bitmap draw command ignores the graphics viewport; bitmap
   PLOT obeys it. Mask/RGBA2222/RGBA8888 and native must not be conflated.
3. [Screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md), lines
   25–27, and [system commands](../../../../../agon-docs/docs/vdp/System-Commands.md),
   line 440: drawing/visible buffers and VSYNC-governed swaps remain required.

The integrated audit covers mode selection, generic primitive algorithms,
palette/Copper ownership, sprites, frame scheduling and output. This review
examines the storage and concrete pixel-access seams that those facilities use.

## Coverage ledger

| Region | Stock source/symbol anchors | P4 source/symbol anchors | Disposition established here |
|---|---|---|---|
| Five depth layouts | [VGA2](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga2controller.cpp):58; [VGA4](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga4controller.cpp):58; [VGA8](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga8controller.cpp):58; [VGA16](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga16controller.cpp):57; [base macros](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.h):63 | [NativePixelCodec](../../../vdp/video/extender/display/native_pixel_codec.cpp):62,90,112 | Two physical byte-layout departures; three within-byte layouts match |
| Dimensions, allocation, row ownership, double planes | [VGABaseController](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp):395,442; [VGAPalettedController](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp):114,122,142,396 | [PlaneStorage](../../../vdp/video/extender/display/plane_storage.cpp):70,119; [P4 controller](../../../vdp/video/extender/display/p4_display_controller.cpp):31,89,288 | Row-pointer tables removed; PSRAM preference and transactional allocation added |
| Pixel and row paint selection | VGA2/4/8/16/64 `getPixelLambda`, `setPixelLambda`, `setRowPixelLambda`, `fillRowLambda`; VGA64:82–158 | P4 controller:308–370 (`writePainted`, writers/fillers) | All depths replaced by runtime codec/paint dispatch; exact stock arithmetic is reusable |
| Fill, copy, clear, vertical scroll | VGA2:262,324,345,407,419; VGA4:294,354,375,437,449; VGA8:302,349,358,406,421; VGA16:283,343,364,426,438; VGA64:216,287,341,352 | P4 controller:368–382,444–462; codec:137 | Stock bulk paths and row-pointer scroll overload omitted |
| Horizontal scroll and overlap direction | VGA2:429; VGA4:459; VGA8:432; VGA16:448; VGA64:366 | P4 controller:464; [generic helper](../../../vdp/vendor/vdp-gl/src/displaycontroller.h):3002 | Stock specialized paths replaced by generic pixel walk; direction logic remains upstream |
| Glyphs, inversion, FG/BG exchange, rectangles | Five depth controllers `drawGlyph`, `invertRect`, `swapFGBG`, `copyRect` (VGA64:511–550) | P4 controller:475–513 | Same generic algorithm families, different concrete accessors |
| Lines, ellipses, arcs, segments, sectors, scan/flood fill | Five depth controllers `setPixelAt`, `absDrawLine`, `absFillRowScan`, `absFloodFill`, `drawEllipse`, `absDrawEllipseSheared`, `drawArc`, `fillSegment`, `fillSector` | P4 controller:384–442, later `absFillRowScan`/`absFloodFill` wrappers | Generic geometry is reused; all primitive pixels/rows pay the substituted depth seam |
| Ordinary and transformed bitmap writers | Five depth controllers `rawDrawBitmap_*`, `rawDrawBitmapWithMatrix_*`; VGA64:564–704; VGA8:552–693 | P4 controller:657–788 | Common traversal retained; packed conversion/paint paths rewritten |
| Readback, capture and native backgrounds | Five depth controllers `readScreen`, `rawCopyToBitmap`, `rawDrawBitmap_Native`; VGA64:552,564,635; VGA8:540,552,622 | P4 controller:515,645–665,722; codec:164 | Logical readback/capture generally preserved at selected mode descriptors; physical plane export is not stock framebuffer bytes |
| Physical row serialization | VGA depth `ISRHandler`, palette signal packers; base `VGA_PIXELINROW` | [Compositor](../../../vdp/video/extender/display/presentation_compositor.cpp):43 | Output can adapt to stock row tables/native order; flat drawing memory is not a browser requirement |

## Findings

### SR-01 — The native-format claim is not byte-for-byte true

At equal valid stock dimensions, the format comparison is:

| Depth | Stock drawing memory | Current P4 drawing memory |
|---|---|---|
| 2 colours | Pixel 0 is bit 7; eight pixels per byte | Same bit order |
| 4 colours | Pixel 0 in bits 7–6; four pixels per byte | Same bit order |
| 8 colours | Eight pixels occupy three bytes; pixel 0 is bits 23–21 of the **little-endian 24-bit group** | MSB-first stream across increasing byte addresses; each three-byte group is reversed relative to stock |
| 16 colours | Pixel 0 high nibble, pixel 1 low nibble | Same nibble order |
| 64 colours | `row[x ^ 2]`; low bits `BBGGRR`, high bits VGA sync state | `row[x]`; low bits `BBGGRR`, high bits always absent from stored logical pixels |

An explicit eight-colour witness derived from the source formulas is pixel
values `0,1,2,3,4,5,6,7`: stock stores `77 39 05`; P4 stores `05 39 77`.
For four 64-colour pixels `0,1,2,3`, stock bytes are
`(2|sync),(3|sync),(0|sync),(1|sync)`; P4 bytes are `00 01 02 03`.
These witnesses describe storage, not a claim that current pixel readback
scrambles the visible image: P4 reads its own alternative layout consistently.

The codec's header comment cites avoiding VGA8's unaligned 32-bit access as
the reason for byte operations. That is a real access pattern to review:
stock loads/stores four bytes at each three-byte group and preserves the fourth
byte, potentially touching beyond the last logical group. But changing access
width does not require reversing the three meaningful bytes. Safe access can
retain their exact order and bit positions. Target unaligned-access behavior,
allocation padding and possible compiler lowering need an explicit decision;
they were not established by this read-only review.

The 64-colour permutation has a concrete VGA output origin: stock's header
documents the I2S-oriented pixel-to-byte order, and its optimized horizontal
scroll code is written for it. P4's output need not emit that physical ordering.
Nevertheless, retaining the drawing order would permit greater direct code
reuse; a final output adapter can decode it. Removing the order from the
drawing plane is a convenience choice, not a demonstrated requirement of P4
or the browser. The same distinction applies to retaining inert sync bits to
reuse stock drawing expressions while stripping them at output.

### SR-02 — Row indirection is useful renderer state, not a VGA peripheral

Stock allocates as few row-memory pools as available memory permits, then
constructs drawing and visible arrays of row pointers. Single buffering aliases
the arrays; double buffering keeps distinct arrays and swaps their identities.
Contiguous row allocation is already possible in this design: the indirection
does not imply one heap allocation per row or mandatory fragmentation.

All five colour-depth controllers use the three-callback `genericVScroll`
overload at `displaycontroller.h:2941`: exchange pixels outside the scrolling
viewport, swap the row pointers, then fill the exposed strip. No peripheral
register appears in that algorithm. Width-wide scrolls require no outside-pixel
exchange. A partial-width viewport does perform work on its exterior; its
cost advantage depends on viewport geometry and is not universally constant.

`PlaneStorage` instead allocates one full plane per buffer. P4 `row(y)` always
calculates `plane.data + y*stride`. P4 therefore chooses the two-callback
copy/fill `genericVScroll` overload at `displaycontroller.h:2898`, and its own
copy callback decodes and rewrites every moved pixel. This is an upstream
generic algorithm, but it is **not the overload selected by any of these five
stock controllers**. Exact common-template reuse did not preserve the actual
stock implementation path.

P4 can retain row tables over contiguous or pooled allocations. Browser
composition can read those tables into its independent snapshot. That would
preserve the existing browser wire format; the browser need not learn the
renderer allocation layout.

### SR-03 — Allocation policy and alignment need separate dispositions

Stock paletted-controller drawing planes use `MALLOC_CAP_INTERNAL | 8BIT`;
four physical scanline buffers use `MALLOC_CAP_DMA`. Every reviewed depth uses
a 16-pixel width quantum and four-row height quantum. Base mode setup also
establishes aligned viewport positions. The row lengths are width divided by
8, 4, or 2, width-times-3/8, and width respectively. Those restrictions help
the concrete access and output code meet alignment/group assumptions.

P4 prefers PSRAM for logical planes, falls back to any 8-bit-addressable heap,
accepts arbitrary positive dimensions, and uses a ceiling packed-row stride.
Its allocation is allocate-new/commit/free-old; failed second-plane allocation
keeps the old mode. Stock's memory-pool allocator can reduce allocated height.

Memory capabilities, DMA/cache ownership and physical scanline storage are
legitimate processor/output seams. **Neither removing the row table nor
rewriting the packed encodings follows from changing those capabilities.**
The allocation failure behavior is also a substantive policy difference, not
an ESP32-P4 register adaptation. Preserve its rationale for review rather than
silently treating it as stock. Current official-mode use should be distinguished
from odd-width synthetic tests that never represented stock mode layouts.

### SR-04 — Concrete bulk rendering paths were discarded

Stock 2/4/16/64-colour `rawFillRow` routines handle leading/trailing pixels and
fill the aligned body in bytes using `memset`. Their `clear` routines operate
on packed row patterns. Stock eight-colour clear writes one repeated 24-bit
pattern per eight pixels; its ordinary row fill and row swap are themselves
scalar. Do not claim every stock operation has a bulk fast path.

P4 row fills iterate pixels. Nonzero `NativePixelCodec::clear` first zeros the
whole plane and then writes every pixel; even an all-white 64-colour clear
therefore loses the stock row `memset`. The codec selects the format on each
read/write and loops over every component bit for packed depths. `writePainted`
reads the old pixel even for Set, where stock directly overwrites; P4 also
reselects the paint operation for each pixel. These are concrete additional
operations, although their timing contribution has not been isolated.

Stock horizontal scrolling has depth-specific aligned paths:

1. Two/four colours: whole packed-byte moves and packed residual shifts.
2. Eight colours: whole three-byte groups for suitably aligned multiples of
   eight pixels; scalar residual handling.
3. Sixteen colours: byte `memmove` for even shifts and four-pixel word handling
   for one-pixel residual shifts.
4. Sixty-four colours: 32-bit word moves plus specialized one/two/three-pixel
   cases honoring its byte permutation.

The source also retains slower unaligned fallbacks. P4 always selects the
generic pixel-walk horizontal helper. There is no processor register dependency
in the aligned copying/filling logic. Restoring stock storage/accessors makes
these exact bodies reuse candidates; target alignment/word-access checks are
required before selecting them.

### SR-05 — Bitmap clipping is reused, but colour conversion is heavier

The shared bitmap traversal clips before invoking concrete writers. A
one-scanline viewport does not cause the concrete RGBA writer to iterate an
entire source tile. The integrated generic-renderer audit retains responsibility
for direct-draw versus PLOT, transforms, clipping and sprite-hide side effects.

Stock paletted RGBA2222 writers index `RGB2222toPaletteIndex(src)` directly.
Stock VGA64 writes `(src & 0x3f) | m_HVSync`. P4 expands the incoming packed
channels into RGB888 and calls `colorToLogical`, which repacks the channels
and optionally consults its LUT, before the generic runtime paint/codec path.
Transformed RGBA2222 bitmaps repeat the same extra conversion. Stock VGA64's
RGBA8888 writer packs channels directly. The stock paletted RGBA8888 lookup
already constructs RGB888, so that intermediate is not itself a new P4
departure in the lower depths. The same visible colour can result; source
equivalence and operation cost are different claims.

The reusable code includes more than common templates: stock concrete
`getPixelLambda`, row/pixel paint selectors, bitmap writer adapters, row
accessors and clear/scroll routines contain useful portable behavior. Their
location in `vga*controller.cpp` does not justify replacing them wholesale.

### SR-06 — Physical plane bytes, native backgrounds and screen captures differ

Three separate contracts must survive restoration:

1. Drawing-plane packed storage, described in SR-01.
2. Internal software-sprite saved backgrounds: stock common helpers save one
   **unpacked** native pixel per visible pixel and restore through native
   writers. Palette modes save palette indices; 64 colours carry raw pixel
   colour/sync bytes. P4 saves its logical value and restores through its own
   codec. Current self-consistency is not byte identity with the stock plane.
3. Public screen capture via `rawCopyToBitmap`: current stock produces opaque
   RGBA2222, with `0xC0`, regardless of the plane's packed depth. P4 similarly
   expands palette-zero colours, and its actual screen facade selects `0xC0`
   in the mode descriptor. There is no demonstrated capture-format bug in that
   selected path. A more general descriptor can substitute another high-bit
   value, which would not match the current stock capture contract.

`NativePixelCodec::exportNativeSave` exports a packed P4 plane (adding configured
sync bits in 64 colours). Repository references show this API is called only
by Phase-B codec tests, not by production screen capture. Its name and passing
tests must not be used as evidence of stock-native bitmap or framebuffer
identity.

### SR-07 — Existing codec qualification misses the stock-byte distinction

[Phase-B contracts](../PORT-003/phase-b/contracts.md):24 claim upstream
packed-bit order is preserved. The eight-colour description gives a 24-bit
position without specifying memory endianness. Its
[fixture generator](../PORT-003/phase-b/scripts/generate-fixtures.py):59
explicitly models an MSB-first stream across increasing byte addresses.
Consequently its independent mathematical implementation agrees with the new
codec while disagreeing with the stock VGA8 byte layout. It also deliberately
models unpermuted 64-colour bytes.

Restoration evidence should compare to the selected stock accessor/row code
and explicit byte witnesses, not merely two implementations of the rewritten
contract. Existing logical rendering passes remain evidence for their actual
scope; they do not establish exact stock storage reuse.

### SR-08 — Exact reuse also exposes a stock boundary hazard

In stock VGA2/4/16/64 `swapRows`, the trailing loop restarts at the aligned floor
of `x2`, even if the leading loop already processed a very narrow interval.
For example, VGA64 `swapRows(...,5,6)` first exchanges pixels 5 and 6, then its
tail exchanges 4,5,6: two intended pixels are exchanged twice and pixel 4 lies
outside the requested interval. Similar loop structure exists in those depth
controllers' `rawCopyRow` routines; VGA64's copy method is empty/unused.
VGA8's scalar row swap does not have this particular shape.

This is a source-derived upstream edge-case defect candidate, not a claimed
explanation for the current P4 hangs or measured behavior on mainboard. A
future differential check needs narrow and unaligned outside-viewport spans,
not only full-width/aligned scrolling. If confirmed in a reachable stock
operation, identify the upstream defect and authorize a narrow correction
rather than concealing it inside a replacement backend.

## Reuse direction for W7

1. Restore row-indirected drawing/visible ownership and exact five-depth
   physical formats first, enabling reuse of the real stock concrete
   render bodies. Keep output conversion separate from drawing storage.
2. Retain the existing common renderer and choose the same stock overloads,
   concrete accessors and fast paths. Do not implement another generic codec
   as the presumed target architecture.
3. Limit initial processor adaptations to demonstrated allocation/capability,
   word-access, ISR/register and output ownership needs. VGA8's four-byte
   access across three-byte groups merits a narrowly defined access/padding
   decision that retains its bytes. Exact code reuse is the default; each
   altered body needs a source-specific reason.
4. Keep the browser's final RGB222 snapshot contract independent. A
   row-table-aware compositor can preserve browser compatibility without
   fixing drawing rows to `base + y*stride`.
5. Requalify byte layout, paint modes, clear/fill/copy/scroll boundaries,
   clipping, native background restore, screen capture and double buffers
   against stock-derived evidence. Then use the held workloads to measure
   throughput and sustained game behavior. This review does not predict the
   resulting frame rate or supersede the recorded publication-starvation
   finding.

Open implementation choices remain with AUDIT-006-D002. No claim here proves
that a full concrete-controller source file compiles unchanged on P4: physical
includes, static row globals, allocation and ISR coupling still need the
integrated binding review. Those dependencies justify investigating a narrow
platform boundary, not discarding the portable methods inside the file.

### Preferred binding to investigate before copying method bodies

The smallest source-reuse candidate is to keep the actual `VGA2Controller`,
`VGA4Controller`, `VGA8Controller`, `VGA16Controller` and `VGA64Controller`
rendering methods and their inheritance from the stock common renderer, while
providing a narrowly selected P4 lifecycle/output binding in their base layers.
It is preferable to extracting renamed copies into another large
`P4DisplayController`:

1. The existing concrete classes already contain matching pixel macros,
   native-format declarations, row-paint selectors, bitmap writers and fast
   paths. Retaining them preserves their mutual assumptions and leaves less
   independently maintained code. Many are private virtual overrides; a new
   subclass cannot substitute only row storage without addressing the base
   class lifecycle and globals.
2. Physical includes, classic ISR bodies and GPIO/I2S/DMA setup must be selected
   out or supplied through a real P4 output implementation. Do not emulate
   nonexistent registers with inert stubs merely to obtain a successful build.
   `VGABaseController`/`VGAPalettedController` bind allocation, resolution,
   row tables, static `s_viewPort`/`s_viewPortVisible`, synchronization, sync
   constants and frame state. These are explicit seams to divide; the classes
   are not indivisible hardware blobs.
3. The P4 lifecycle must preserve the selected controller's active row globals,
   drawing/visible pointer identity and packed-row alignment. If the lifecycle
   retains allocate-new-before-destroy-old behavior, class singleton/static
   effects must be reviewed: two live candidate objects cannot silently change
   the row globals beneath a rendering worker. Mode transition and allocation
   failure handling belong at that boundary.
4. Keep `VGA_PIXELINROW(row,x)=row[x^2]` and stock eight-colour three-byte order
   as the initial reuse target. The output reader alone translates these to
   ordered RGB222 snapshots. If processor evidence requires changing an access
   instruction, adapt the accessor while preserving its bytes; evaluate that
   precise exception separately from complete method extraction.
5. Sprite backgrounds must stay in their stock one-byte-per-pixel native
   logical order, even though destination framebuffer bytes are permuted or
   packed. Retained `genericRawDrawBitmap_*` get-pixel callbacks extract one
   value; retained `rawDrawBitmap_Native` puts it back through the corresponding
   depth accessor. Do not reinterpret the saved background as a raw row copy,
   apply the framebuffer permutation twice, or retain the present P4 codec's
   refusal of sync-bearing 64-colour native bytes after restoring stock save
   callbacks. Public RGBA2222 captures continue to use their separate opaque
   export path.

This candidate requires a bounded source/build feasibility review at W7's
authorized implementation boundary; it is not proven compilable by inspection.
If a particular method cannot remain in its original class/source because of
a concrete dependency, preserve its body verbatim in the narrowest extracted
unit and record that reason and source span. Copying all five method sets into
a new generic abstraction without first evaluating the original classes would
repeat the design departure this audit is intended to correct.
