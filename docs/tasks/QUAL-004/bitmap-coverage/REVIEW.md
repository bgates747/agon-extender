# Bitmap format and conversion coverage — review draft

## Executive summary

All three public bitmap storage formats already have passing evidence. The main
gap is evidence strength and selected conversion edge cases, not an entire
untested format. Existing suite code already exercises packed expansion and
baked transforms; reuse it before creating new fixtures. This is an inventory
and recommendation only. Author requested review before further implementation
or bench activity.

## Scope and references

Official documentation baseline: agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`:
[bitmap API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Bitmaps-API.md),
[buffer API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md).
No upstream checkout was modified. This is bounded test-evidence review, not a
new implementation audit or assertion that every format/path combination works.

Existing evidence classes must remain distinct:

1. **Paired physical pixels:** QUAL-004 mainboard capture versus P4 full image.
2. **Native reference versus physical P4:** earlier bitmap/affine tile checks.
3. **Author visual suite acceptance:** broad coverage, not per-pixel proof.
4. **Fixture/source exists:** capability of a test, not evidence it passed in a
particular frozen physical campaign. Match historical input hashes before reuse;
page numbering in current generators must not be used to reinterpret older runs.

## Coverage map

| Operation | Existing evidence | Remaining gap / recommendation |
|---|---|---|
| Public format0 RGBA8888, format1 RGBA2222 | [Bitmap case02](../../PORT-008/bitmap-coverage/README.md): native/P4 tiles; [palette generator](../../PORT-008/palette-coverage/make_case.py) and PAL16/PAL4/PAL2 physical comparisons cover both, including zero/nonzero alpha | Do not invent another basic format smoke. Channel quantization boundaries and exhaustive value combinations are not established |
| Public format2 mono/mask | Same palette tests include9-pixel-wide, byte-padded rows and creation-time colour; bitmap case02 also includes mono | Already covers an odd-width case; not an exhaustive width/stride matrix |
| Format3 native | Officially reserved for internal use, not a fourth public input format | No public compatibility test priority; controller internals belong to backend review |
| Direct streamed load, solid bitmap,8/16-bit selection | Case02 tests streamed RGBA8888; palette cases test solid bitmap/alias and buffered selection | Useful existing tests; no new general smoke needed |
| Screen capture to bitmap, then replot | Palette physical controls test capture/replot; case02 tests inclusive bounds. Older suite has both ID forms and one-pixel capture | Full paired pixel evidence for both ID forms and one-pixel boundary is not identified in the current exact-image corpus |
| Packed buffer expansion, command72 | Older [bitmap suite generator](../../QUAL-003/suite/scripts/bitmap_suite.py), “MASKS AND PACKED EXPANSION”:1/2/4bpp, width34 row alignment, inline mappings and a buffered2bpp mapping. Broad suite [visual acceptance](../../QUAL-003.md#graphics-suite-milestone-frozen--2026-09-10) exists | Not selected in QUAL-004 exact scene manifest. Best next bounded physical comparison; reuse existing inputs first |
| Expansion variants | Same generator covers only the combinations above | No targeted evidence found for3/5/6/7/8bpp, continuous bitstream without row alignment, or both mapping transports for every packing. Gaps are not implementation defects |
| Baked bitmap transform, command40, output RGBA2222 | Case02 explicit-size reflection matches native/P4, independent ideal. Older “BAKE TRANSFORMED BITMAPS” covers both colour source formats, fixed/auto/explicit sizes and auto-translation. Existing selected transformed-sprite scenes exercise a subset | Complete paired coverage of the options/source-format matrix is not established. Reuse the baked-transform page before writing another |
| Live transforms versus baked transforms | Case02 reflection/scaling coverage; inherited live-reflection last-column discrepancy retained | Preserve stock discrepancy. This is not authorization to fix it or equate live drawing with stored-format conversion |
| Copy/adjust source bytes | Case02 copy independence and source adjustment; older page covers further bitwise operations | Selected evidence, not exhaustive mutation/resource-lifetime qualification; lifetime bugs remain deferred |
| Hardware sprite format restrictions | Docs restrict hardware frames to formats0/1; software permits all public formats | Mono not displaying as a hardware sprite is a stock restriction, not automatically an Extender bug |

## Precise contracts relevant to a future tranche

1. Creating a bitmap from a buffer (`23,27,&21,w;h;format`) assigns interpretation;
it is not a generic format-to-format conversion command. Public formats are0/1/2.
2. Current documented screen capture produces RGBA2222 regardless of display depth;
old native-format capture behavior predates the selected release.
3. Buffer command40 creates a transformed RGBA2222 bitmap. Output bounds/options
are meaningful separate cases, not just a test of loading its source format.
4. Buffer command72 expands1–8-bit indices to bytes using a mapping; zero in the
bit-count field means8. It supports continuous packing or optional row alignment,
and inline or buffered mappings. The output must then explicitly become a bitmap.
5. Transparency is binary: zero alpha invisible, nonzero opaque. Do not impose
alpha blending as an expected result of these formats.

## Bounded next scope

**QUAL-004-BM01** [x] Inventory public formats and existing evidence. This document.

**QUAL-004-BM02** [x] Author authorized execution: selected a bounded packed-expansion comparison
using existing1/2/4bpp inputs. Mainboard VDP and P4 render identical frozen bytes;
host compares captures and a small independent expected-pixel pattern. Use the
accepted capture-failure/control protocol. No renderer changes.

**QUAL-004-BM03** [ ] Only if later selected: fill packing/mapping edge cases or
promote existing baked-transform/capture-boundary cases to exact paired evidence.
Do not automatically execute a comprehensive matrix or reopen lifetime/Copper work.

No fixture generated, firmware built/flashed, emulator started, or hardware tested
for this review. Sprite results were committed separately as `04ec865c`.

Execution checklist: [BM02 contract](../packed-expansion/CONTRACT.md).

BM02 completed: [three paired cases pass](../packed-expansion/RESULTS.md); BM03 remains parked.
