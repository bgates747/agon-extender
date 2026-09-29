# AUDIT-010 RP03 — Mutable font bounds, lifetime and fixed scratch

## Result

`A10-RP03-S01` [x] Accepted by the Author on 2026-09-29; implementation commit
`c789d45a`. RP04 was then authorized.

The selected VDP compatibility layer now gives every application-defined font
one `ManagedFont` owner containing its FabGL metadata, source `BufferStream`
owner and optional character-pointer `BufferStream` owner. Font deletion,
buffer deletion and saved-context lifetime can no longer leave the selected
P4 renderer with an unowned raw font-data or character-pointer address.

Width and height commands commit only when the retained font backing remains
large enough and every retained offset still names a complete glyph. Rejected
mutations leave the prior geometry intact. The selected VDP continues to reject
variable-width fonts. Per the official API, the reserved character-pointer
property is retained and validated as metadata but does not select FabGL's
variable-width renderer.

Screen-character capture now scans pixels once while eliminating candidates in
a fixed 256-bit set. It no longer multiplies the application-controlled glyph
size into eight bits or creates a variable-length stack array. FabGL's full
glyph path now selects doubled-height source rows directly instead of copying
an application-sized glyph with `alloca` on the 8,192-byte P4 drawing-task
stack.

Finding: `AUDIT-010-F006`. Plan item: `A10-RP03`. Upstream publication remains
a separate decision and is not part of this candidate.

## Official contract and lineage

`A10-RP03-C01` [x] Official Agon documentation commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` remains the semantic authority.
[Font-API.md](../../../../../agon-docs/docs/vdp/Font-API.md) specifies 256 byte-aligned fixed-width glyphs, mutable
width/height properties, one source block, variable-width fonts as unsupported,
and the character-pointer property as reserved with no rendering effect.

`A10-RP03-C02` [x] Official VDP tag `v2.16.0`, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, remains the read-only source
baseline. The unsafe `createFontFromBuffer`, `setFontInfo`, `getCharPtr`, context
capture VLA and FabGL glyph `alloca` are inherited code under `A10-LIN06`; the
Extender correction is isolated in the selected compatibility layer and
vendored FabGL copy. The official checkouts were not altered.

The source comparison used official
[`agon_fonts.h`](../../../../../agon-vdp/video/agon_fonts.h),
[`context/fonts.h`](../../../../../agon-vdp/video/context/fonts.h) and the local
selected [`agon_fonts.h`](../../../vdp/video/agon_fonts.h),
[`context/fonts.h`](../../../vdp/video/context/fonts.h) and
[`displaycontroller.h`](../../../vdp/vendor/vdp-gl/src/displaycontroller.h).

`A10-RP03-C03` [x] Existing local include selection and the accepted
transparent-text reset correction remain distinct from this repair. No second
font implementation or replacement renderer was introduced.

## Ownership and mutation contract

`A10-RP03-O01` [x] `AgonManagedFont` owns the `fabgl::FontInfo`, exact source
`BufferStream` and optional offset `BufferStream`. Every active, text-cursor,
graphics-cursor and saved-context reference owns that complete record.

`A10-RP03-O02` [x] Fixed-width creation rejects zero dimensions, unsupported
variable-width flags, multi-part buffers and a source size other than
`256 * height * ceil(width / 8)`, preserving the official create contract.

`A10-RP03-O03` [x] Width and height mutation calculate in `size_t`, reject zero
or insufficient backing, revalidate all attached offsets and publish the new
value only after validation succeeds. Maximum 255-by-255 glyph arithmetic is
8,160 bytes per glyph and 2,088,960 bytes per font without wrap.

`A10-RP03-O04` [x] Character-pointer mutation requires one buffer of at least
1,024 bytes and validates all 256 little-endian offsets against a complete
current glyph in the retained source. The owner is retained after the caller
or buffered-command registry releases its reference. `FontInfo::chptr` remains
null because the official selected API does not support variable-width
rendering.

`A10-RP03-O05` [x] Font clear/reset removes registry ownership but does not
invalidate a font retained by an active or saved `Context`. The selected
canvas receives the address of the owned `FontInfo`, and system-font behavior
remains the existing static `FONT_AGON` path.

`A10-RP03-O06` [x] Screen-character capture uses a fixed 256-bit candidate set
and `size_t` row/byte indices. The stock match priority remains characters
32–255 followed by 0–31. The FabGL double-height path preserves the original
top/bottom row mapping without temporary glyph storage.

## Regression manifest and evidence

| Check | Contract protected | Candidate result |
|---|---|---|
| `tests.font_safety_test` under ASan/UBSan | Maximum and short backing, rejected geometry, short/invalid offset tables, owner lifetime, offset revalidation and screen-character priority | PASS; 17 C++ checks plus source assertions |
| `tests.native_p4_build_test` | Maintained native profile/source authority remains coherent | PASS; 11 tests |
| `tests.visible_text_capture_test` | Existing visible-text transcript/capture oracle | PASS; three tests |
| `tests.visible_text_hardware_test` | Repeated visible-text orchestration and failure recovery with fake hardware | PASS; one test with three scenarios |
| `tests/numeric_renderer_test.py` | Neighboring exact renderer bodies and guarded/stock sampling | PASS; common sampling hash `12193972632595109770` |
| Fresh unversioned `p4-console` build | Actual selected P4 source compiles, archives and links; excluded display family remains absent | PASS; 33 selected and eleven forbidden sources |

The ignored candidate build is
`agents/builds/a10-rp03-final-20260929`. It is explicitly
`UNVERSIONED-DO-NOT-DEPLOY`, uses dirty source rooted at commit `fc670450`, and
was not flashed.

| Native artifact | Evidence |
|---|---|
| Profile manifest | SHA-256 `a4c487bd1857db07936fa01c1183cea8c662b26d60e8a7a12591d2dfb8d4bdf4` |
| Application image | 1,574,752 bytes; SHA-256 `408d84eae79512b2f498849464c3f08e4a6838e72bc0fb3dc7970283663d2a8c` |
| Offset-zero factory image | 1,705,824 bytes; SHA-256 `4770847413d259cb47c212597bf7f30ff5e2a84a25d5ff4aa480c121a7122176` |
| Linked ELF | 34,191,948 bytes; SHA-256 `93c77577c6f617fa2166aca7226c7137f7726670ad160496048333d3eb9d49c5` |
| Actual-action validator | PASS; 1,842 compile actions, 33 selected sources compiled once, eleven forbidden sources absent, selected archive on the ELF edge |

`A10-RP03-T01` [x] The first full compile exposed stale direct dimension reads
in `Context::readVariable`; those reads now use the owned `FontInfo`. The failed
output was ordinary development feedback and is not retained as diagnostic
evidence.

`A10-RP03-T02` [x] The Author accepted the candidate and authorized RP04. No P4
flash, reset, Agon/EMOS operation, SD mutation, production promotion or upstream
submission occurred as part of RP03.
