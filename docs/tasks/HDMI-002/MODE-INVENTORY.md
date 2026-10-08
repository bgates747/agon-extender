# HDMI mode inventory — 2026-10-07

Subsequent implementation: the Author selected full-width 480p first. Experimental
modes 96–99 are tracked under HDMI02-W in [the owning task](../HDMI-002.md).
The stock-mode inventory below remains the dated pre-implementation evidence.

## Executive summary

The maintained VDP retains stock's **54 mode numbers, nine pixel geometries and
Teletext special case**. The installed automatic HDMI build has two working
carriers, 684×384 and 848×480. Six geometries fit without cropping; three do not:
640×512, 800×600 and 1024×768. Fitting does not establish performance, stock
display proportions, double-buffer behavior or complete sprite qualification.

This is a source/evidence inventory only. No firmware, bench, SD, mode selection
or test fixture was changed. The next implementation choice remains with the
Author: a smaller widescreen carrier for 320×240, or integer enlargement inside
the existing 848×480 signal. The current centered, unscaled policy is unchanged.

## Complete ordinary-mode inventory

Numbers in parentheses are background color counts. DB means double-buffered;
only the explicitly listed DB IDs exist in the stock dispatch table. Origins
are output pixels measured from the HDMI image's top-left corner. Crops are
removed source pixels **on each named edge**, not total loss.
These are the adapter's geometry results assuming logical-mode initialization
succeeds; untested entries are not proof of allocation or hardware operation.

| Logical geometry | Single-buffer mode IDs | DB mode IDs | Stock nominal Hz | Current HDMI carrier / origin | Current geometry and evidence |
|---|---|---|---:|---|---|
| 1024×768 | 18(2), 19(4) | 146(2) | 60 | 848×480 / 0,0 | Crops 88 left/right and 144 top/bottom; not reviewed on this build |
| 800×600 | 16(4), 17(2) | 145(2) | 60 | 848×480 / 24,0 | Crops 60 top/bottom; not reviewed on this build |
| 640×512 | 24(16), 25(4), 26(2) | 153(4), 154(2) | 60 | 848×480 / 104,0 | Crops 16 top/bottom; not reviewed on this build |
| 640×480 | 0(16), 1(4), 2(2) | 129(4), 130(2) | 60 | 848×480 / 104,0 | Fits; current single-buffer sprite checks pass; mode0 upper text confirmed by Author |
| 640×256 | 27(64), 28(16), 29(4), 30(2) | 156(16), 157(4), 158(2) | 60 | 684×384 / 22,64 | Fits unscaled; proportions and mode-specific behavior unreviewed |
| 640×240 | 3(64), 4(16), 5(4), 6(2) | 132(16), 133(4), 134(2) | 60 | 684×384 / 22,72 | Fits unscaled; stock vertical repetition is not reproduced by this HDMI mapping |
| 512×384 | 20(64), 21(16), 22(4), 23(2) | 149(16), 150(4), 151(2) | 60 | 684×384 / 86,0 | Fits; ordinary software/hardware Nurples in mode20 pass; other depths and DB not qualified on this build |
| 320×240 | 8(64), 9(16), 10(4), 11(2) | 136(64), 137(16), 138(4), 139(2) | 60 | 684×384 / 182,72 | Fits; mode8 Nurples title works; no 240-line physical carrier or current full gameplay/DB qualification |
| 320×200 | 12(64), 13(16), 14(4), 15(2) | 140(64), 141(16), 142(4), 143(2) | 70 | 684×384 / 182,92 | Fits; HDMI remains approximately 60 Hz, not stock 70 Hz; proportions unreviewed |

Mode **7** initializes a **640×480, 16-color** controller and then Teletext.
The ordinary documentation deliberately calls its pixel geometry n/a; its
underlying HDMI carrier is 848×480. Teletext operation is a separate unperformed
check, not established by mode0's pass. There is no mode135 in this dispatch.

Mode136 is **320×240, 64 colors, double-buffered**. It is not 512×384.
Mode148 (mode20+128) is absent: adding128 to an arbitrary ID does not make it
implemented. No new IDs or extra buffering combinations are proposed here.

## Compatibility remapping

`VDU 23,0,&C1,n` selects the old pre-1.04 mode-number interpretation. This is
**not EMOS Legacy/ExCom routing**. In the maintained stock dispatch it changes
only these four IDs; the rest of the switch, including DB IDs, remains unchanged.

| Old ID | Logical image | Colors / nominal Hz | Current HDMI result |
|---|---|---|---|
| 0 | 1024×768 | 2 /60 | Cropped as above |
| 1 | 512×384 | 16 /60 | Fits 684×384, native indexed compositor |
| 2 | 320×200 | 64 /75 | Fits 684×384; physical cadence remains approximately 60 Hz |
| 3 | 640×480 | 16 /60 | Fits 848×480 |

These remappings were inspected, not run on hardware in this inventory.

## Important distinctions for the next decision

1. **Rendering speed is not selected solely by HDMI size.** The current direct
   RGB888 renderer admits only 64-color 512×384 and 320×240 images. Other depths
   and geometries use the existing native compositor. Thus mode21 is not the
   same performance path as mode20, even though both fit the same carrier.
   The geometry predicate also admits mode136, but that is not a current-build
   double-buffer validation. The latest 480-line sprite checks produced about
   19 new images/s while DMA scanned out about 60 times/s.
2. **All ordinary sprite paths remain present.** Carrier selection does not
   disable software or hardware sprites in any color depth. Retained stock
   scanline code writes hardware sprites' RGB222 after expanding the background
   palette; this may already permit 64-color hardware sprites over a lower-color
   background. No new color semantics or exhaustive physical sprite claim is
   made. Software sprites paint into the background's representation.
3. **Stock VGA repetition is different from today's HDMI pixel mapping.**
   Stock modelines use DoubleScan for 640×240, 320×240, 320×200, 512×384 and
   640×512, and QuadScan for 640×256. VGA timing and monitor geometry also matter:
   these flags are not a universal instruction to double every HDMI image.
   In particular 640×240 mapped one-for-one has an 8:3 pixel rectangle, whereas
   repeating its rows once would give 640×480. Our accepted square-pixel 512×384
   presentation must not be doubled vertically just because stock uses DoubleScan.
4. **Refresh compatibility remains separate.** Both installed carriers run at
   calculated 60.069438 Hz. Stock 70/75-Hz declarations still exist, but there
   are no corresponding physical HDMI carriers. Mode metadata must not be read
   as evidence of 70/75-Hz output or identical application pacing.
5. **Previously tested 720p is not an automatic fallback today.** A separately
   built 1280×720 output exists in the earlier evidence, but the installed
   selector chooses only 684×384 or 848×480. Reintroducing 720p could fit 640×512
   and 800×600 unscaled; it would still crop 1024×768 by 24 rows at each end.
   Integration, memory, sprites and mode transitions would need fresh checks.

## Discussion options — not an implementation contract

| First 320×240 approach | Benefit | Cost / unresolved point |
|---|---|---|
| New roughly 427–428×240 widescreen carrier, 320×240 centered | Preserves one-to-one pixels and reduces output pixels; follows the successful 384-line approach | Actual aligned width, monitor acceptance, clock/porches and rolling-strip layout must be established; no working timing claimed |
| Enlarge pixels 2× in each direction into the proven 848×480 carrier | Produces centered 640×480 gameplay using an already accepted physical signal | Requires a new integer-scaling output path and sprite-coordinate handling; current full-frame compositor is slow, so performance cannot be assumed |
| Retain current unscaled image in 684×384 | Already works for the title and needs no new code | Leaves substantial surrounding black area and does not advance native 240-line output |

Recommendation for discussion: try the small widescreen **static timing pattern
first**, before integrating games, if native low-resolution output remains the
priority. Keep 2× output as the fallback if the monitor rejects that carrier.
The current rolling layout uses 32-row strips and a four-bit block count; a
240-line image does not divide into those strips. A new carrier therefore also
needs an explicit strip-layout review, not just different width/height constants.
Any new full-width logical game mode is a separate API decision, not an automatic
consequence of selecting a wider HDMI carrier.
The 2× alternative would amend ADR-0024's current unscaled presentation rule;
this inventory does not change that rule.

## Sources and verification

1. Official [screen-mode documentation](../../../../../agon-docs/docs/vdp/Screen-Modes.md),
   reference commit `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
2. Official [mode dispatch](../../../../../agon-vdp/video/agon_screen.h),
   clean local tag **v2.16.0**, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; latest tag present in the local
   reference checkout. No remote release query or reference edits were performed.
   The 54 IDs and `changeResolution` calls match the maintained dispatch.
3. Maintained [dispatch](../../../vdp/video/agon_screen.h),
   [stock modelines](../../../vdp/vendor/vdp-gl/src/fabglconf.h),
   [RGB888 eligibility](../../../vdp/video/extender/display/rgb888_pixel.hpp),
   [carrier selector](../../../vdp/video/extender/display/hdmi_timing.hpp),
   [centering/cropping](../../../vdp/video/extender/display/hdmi_geometry.hpp), and
   [hardware sprite scanline](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp).
4. Exact current build and limited physical evidence: [runtime results](RUNTIME-RESULTS.md).
   Older browser/emulator or other-carrier passes are not counted as current
   HDMI mode qualification. Geometry/crop arithmetic was independently checked
   against all nine width/height pairs without touching the bench.
