# Reproducing the order4 silicon comparison

## Executive summary

This is a hardware qualification recipe, not an unattended default deployment.
Obtain bench ownership, read HARDWARE.local.md and bench constraints, preserve
current firmware/startup, and establish exact before-images before flashing.
Use the SD card physically in the Agon; the host-mounted MOS-suite card is excluded.

1. `prepare.py BASE OUT --wasm WASM_DIR` clones retained qualified SRLE2 r03,
   adds a per-call selected-order entry while preserving `p4_szip` as order3,
   exposes `op=encode4` for the test RPC and `srle2=4` for the browser request.
   Both orders use one full-input block. Decoder accepts orders3/4; the qualified
   generalized Worker Wasm handles the same EVS1 envelope. Never patch a source
   checkout belonging to another task or an official reference.
2. Build using the existing `srle2/build.py OUT --revision r04` command from the
   repository root and `.venv/bin/python`. Build identity/hash is recorded in
   evidence/candidate.json; compile time was approximately102 seconds on this
   workstation. PlatformIO/package paths are machine-local.
3. Reuse the identity-checking deployment helper from the previous SRLE2 hardware
   qualification. It reads/preserves the installed prefix, asserts application
   and partition bytes against the expected baseline, writes the candidate and
   independently verifies flash. Re-establish mainboard keyboard/SD admission by
   a normal reset after the P4 flash. Do not change EMOS or mainboard VDP firmware.
4. Reuse `srle2/hardware/codec_check.py` with the pinned corpus for order3. For
   order4, regenerate CmpS goldens with the original CLI `-b41o4` over the exact
   same RLE2 bytes, and invoke `op=encode4`. Decode/unpack operations remain the
   same. Both passes use one warmup plus three measured calls, exact output,
   short/truncated/wrong-version rejection and recovery. See tracked golden
   hashes and device receipts.
5. Stage the retained cadence60 fixed-mode fixture under `/test/szip4`, verifying
   uploads. Temporary startup selects mode20 on both devices and launches the
   admitted SD service. The fixture's mode setter is RET, so it cannot override
   startup. Production Nurples and Rally are untouched.
6. Run interleaved RLE2/order3/order4 three times each. Each run records1800 game
   cycles then returns to the SD service with trace/telemetry files. Browser
   request query is `rle2=1`, `srle2=1` or `srle2=4`. Retain frame geometry, byte
   sizes, receive/request/submission timestamps, codec counters and browser errors.
   Use the previous fixed-mode analyzer's central15-second output window.
7. Repeat static scenes after that mode20 startup, asserting every received frame
   is512×384. Use bitmap_raw, raw_sprites and incompressible task-owned streams
   through the ordinary EMOS VDU route;20 receipts per codec. Do not accept
   inherited mode3/640×480 as a compressed-output comparison.
8. `report.py RUN_DIR` consumes completed game analysis, codec3/codec4 receipts and
   synthetic02 rows. It writes tables and compact evidence. Raw run/restore logs
   and machine-specific runners remain in ignored `agents/order4-p4`; source and
   fixture hashes are retained publicly. This script does not contact hardware.
9. Restore the actual preserved startup and original P4 prefix with independent
   verification. Normal mainboard reset; check keyboard/SD readiness. Invoke the
   accepted hardware attention batch, verify a fresh successful audio receipt,
   return to Legacy prompt, neutral keys and stop. Emulator spoken cue is fallback.
