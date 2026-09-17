# Reproduction and evidence scopes

## Executive summary

This experiment is isolated from product source. prepare.py clones the retained
order4 candidate source into a new private directory, then adds the image codec,
selected HTTP controls and browser-native image decoding. Build/deploy artifacts
must retain hashes, identity and exact restoration payloads.

1. Obtain PNGenc commit23e97d1c146ef572fb9e073bbcafd2fbf212a57a with license.
2. Run project .venv/bin/python prepare.py BASE OUT PNGENC_CHECKOUT. BASE is the
   retained order4-p4/candidate01, whose preparation is preserved in that task.
3. Run project .venv/bin/python build.py OUT --revision r01. New timestamps
   identify every build. Retain manifest plus exact source hashes. No automatic
   flashing occurs in either script.
4. Use established independently verified P4 deployment with expected before
   application/partition hashes and full-prefix preservation. Mainboard stock
   VDP and EMOS must not change. Local endpoint/serial/SSH values are private.
5. Run check_images.py --url URL --corpus CORPUS --out NEW_DIR --modes 80,90,95
   and later --modes 1,3. It posts bounded raw final-colour indices, records one
   warmup plus three measured encodes, tests browser decoded pixels separately,
   retains reference/decoded images and malformed-input recovery. Dimensions
   are padded to8-pixel boundaries for shared JPEG/PNG corpus compatibility.
6. Game controls reuse unchanged mode-free cadence fixture, fixed-mode startup,
   SD retrieval, browser credit cap30Hz and central15-second measurement window.
   Raw controller scripts and screenshots are retained in private task evidence;
   compact measurements are copied into tracked evidence at closeout.
7. Native browser decoding uses ImageBitmap rather than CPU canvas readback for
   game timing. Corpus verification intentionally reads back pixels, outside
   timing of native decode. JPEG pixels are lossy; PNG must be exactly equal.
8. Retain original startup bytes and flash prefix, restore independently, then
   use accepted hardware attention batch and verify a fresh receipt.
