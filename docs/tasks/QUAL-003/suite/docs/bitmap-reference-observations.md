# Bitmap suite implementation and reference observations

EXT-004 implements BSP-01–32 with 123 keypress stages. These observations
distinguish the test application's behavior from the VDP behavior under test.
The task's original command descriptions remain in `tasks/EXT-004.md`.

## Presentation and command completion

1. `CLS` deactivates sprites, including when clearing a small text viewport.
   The bitmap suite therefore clears headings and footers with filled vector
   rectangles. Stage changes retain active sprites. BSP-22 preprints all
   instructions and emits no heading updates during its deferred-move stages;
   otherwise label drawing would refresh the software sprite under test.
2. MOS VDU output can leave a few final bytes queued when a debugger stops
   immediately at `waitKeypress`. Normal stages end with a drawing flush;
   every stage then waits for three changes of the MOS clock, with a bounded
   CPU backstop. This allows transport to settle before observation. The
   quiet deferred-update stages emit no flush or other drawing commands.
   This short settle never advances a page; all progression requires a key.
3. Hardware sprites are captured from the real SDL presentation. The suite
   does not use framebuffer RGB replies to decide whether hardware sprites
   are visible. `tests/validate_bitmap_frames.py` independently checks
   selected display pixels and corresponding image regions, including hardware
   movement without sprite-update command 15.
4. BSP-07's direct-draw control currently matches the documented unclipped
   behavior. It does not reproduce the earlier SHP-23 clip observation.
   Those are separate fixtures; the historical Shapes record is preserved.
   Physical top/bottom edge samples occupy the narrow right corners, outside
   the heading/footer text. Their visible pixels have explicit query checks.

## Matrix contracts exercised

1. The VDP combines a new operation on the left: `new × existing`.
   A translate `(24,12)` followed by uniform scale 2 therefore has translation
   `(48,24)`. BSP-16 compares that composition with six explicit coefficients
   and checks the resulting pixels, then exercises inverse composition.
2. Centred transforms first translate the source centre to zero, then scale
   and rotate. BSP-14 pairs explicit pixel translation with bitmap-relative
   operation 12. Fixed-canvas sprite frames in BSP-29 translate `(-17,-17)`,
   rotate, then translate `(36,36)` into a 72 × 72 canvas.
3. Both argument encodings and matrix storage have explicit byte contracts.
   Matrix arguments cover float32, float16, fixed32, fixed16, negative shifts,
   buffer-fetched values, and individual argument formats. Stored matrices
   remain row-major float32. Baked bitmap command 40 always produces RGBA2222.
4. Changing the selected PLOT matrix does not transform ordinary sprite
   frames. BSP-29 leaves a 3× PLOT scale selected while stepping software and
   hardware sprite frames, providing a visible control for that distinction.

## Sprite backend transitions in the stock renderer

The first active hardware-to-software conversion experiment completed its
visible stage but the stock Fab process terminated when the next page removed
the sprites. The reference backend allocates software saved-background storage
when the active sprite set is installed; changing the hardware flag alone does
not allocate that storage. This is a renderer-lifecycle finding, not evidence
of an Extender failure.

BSP-26/27/28 explicitly deactivate the group before changing rendering type,
then reactivate it. That refreshes software background allocation and preserves
the commands being exercised. In particular, command 18 still demonstrates
hardware-to-software GCOL demotion, and command 19 still demonstrates the
RGBA2222-only hardware XOR exception. This lifecycle is visible in stage
descriptions and the generated manifests; no hardware test is replaced by an
unlabelled software fallback.

The bounded population test stops at 16 sprites. Its results describe this
mode and fixture, not a measured maximum for the emulator or physical Extender.

## Exercised library paths and widths

1. The Nurples import remains byte-for-byte preserved. Bitmap loading uses
   audited `vdu_clear_buffer`, `vdu_load_buffer`, `vdu_consolidate_buffer`,
   `vdu_buff_select`, and `vdu_bmp_create`. The old unchecked file loader and
   fixed `0xB7E000` scratch buffer are not called.
2. The inherited sprite entry points cover selection, frame lists, activation,
   navigation, show/hide, integer and fixed16.8 movement, update, reset, and
   GCOL. Four small adapters add hardware/software selection and 8-/16-bit
   frame replacement. BSP-20 includes an equivalent literal-packet software
   sprite beside the imported API controls.
3. Some imported builders deliberately write a 24-bit register across a word
   and adjacent padding or a field repaired before transmission. The stage VM
   supplies zero-extended IDs, dimensions, and upload lengths. The fixed16.8
   helpers receive deliberate 24-bit fixed-point values and restore the
   overwritten opcode before sending. New packet adapters write words
   bytewise; new application pointers/counts have explicit `dl` storage.
4. The stage VM serializes a raw VDU block, a call-table index plus A/BC/DE/HL
   arguments, or an asset-table index plus destination/mode. The independent
   validator verifies record widths and compiled pointers, rejects reserved
   bitmap formats, and decodes variable-length matrix/buffer packets.
5. Buffer IDs are listed in `build/bitmaps-catalog.json`. They are dedicated
   61000-range resources plus the explicitly tested legacy aliases 64000/64001.
   Cleanup deactivates and resets sprites before clearing those resources;
   it never clears all VDP buffers with ID 65535.

## Asset provenance

`assets/bitmaps/source/provenance.json` records the original PingoASM PNG,
RGBA2222, and existing RGBA8888 file hashes. The PNG and packed source are
preserved; the build regenerates RGBA8888 and verifies the raw reference
contract. The 24 generated fixtures include explicitly named opaque originals,
host enlargements, cutouts, alpha bands, frames, patterns, a mono mask, and
packed 1-/2-/4-bit sources. The deployed asset manifest records lengths,
dimensions, formats, descriptions, and hashes.

Fully transparent pixels retain RGB bytes deliberately. Alpha values above
zero are expected to be opaque in both supported RGBA formats; this suite does
not claim partial-alpha blending or more than 64 display colours in mode 20.
