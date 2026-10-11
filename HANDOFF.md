# Current checkpoint — matched stream timing complete; UART pair restored

The bounded comparison is complete. All 48 selected samples have exact full-buffer
proof. The current parallel path wins only for a full 4096-byte batch’s wire-drain
endpoint; small/residual streams and ordered replies are substantially slower.
The original UART pair/startup is restored and verified; the bench is released.
The broader eight-hour goal remains paused. Stop for Author discussion before
profiling or optimizing; no production promotion or new version acceptance.

## Start here

1. Read `AGENTS.md`, the handbook, production selection and `HARDWARE.local.md`.
   The Author requires all work to stop at an unanswered question. Current
   device identity, ownership and receipts belong in ignored local records.
2. [Completed bounded contract](docs/tasks/PORT-008/STREAM-TIMING-R01.md) and
   [physical results](docs/tasks/PORT-008/STREAM-TIMING-R01-RESULTS.md) own the
   measured endpoints, clocks, sample provenance, limits and verified handback.
3. [Paused broader work](docs/tasks/PORT-008/EXEXT-STREAM-R01.md) and its
   [results](docs/tasks/PORT-008/EXEXT-STREAM-R01-RESULTS.md) retain gameplay
   regression and uninstalled r15 boundaries. Do not resume that goal implicitly.

## Installed pair and handback

1. P4 `port-008-data-r20-b2026-10-11-09-07-32Z`; all four flash segments verify.
   Application SHA256:
   `01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
2. EMOS `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`; all 128 KiB ROM bytes verify.
   Full ROM SHA256:
   `69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
3. Mainboard fsim custom VDP unchanged. Original 38-byte startup restored/readback;
   card in Agon. Actual Legacy CLI input and five seconds of neutral readiness
   pass. No listener/transaction/test/collector/reset hold or pending/held keys.
4. Mixed-pair admission failed during restoration; matching stream-r14 restored
   input, then old EMOS was submitted once followed by old P4. Final ROM proof
   is obtained only after the complete original pair returns. Broader warm-reset
   and mixed-pair admission qualification remain open, not fixed by this run.
5. Final receipts: ignored `agents/stream-timing-r01/bench-r01/final-handback.json`
   and `restore-p4-r02/restoration/receipt.json`. All three installed-current
   local records refreshed. Source HEAD and production selection do not identify
   the currently installed bench pair by assumption.

## Results and next discussion

1. M02 parallel/UART elapsed ratios:256 B 6.57×; 4097 B 2.30×; 8192 B 1.37×; 4096 B 0.83×.
   Adding one byte at the boundary changes parallel drain from 30.6 to 84.8 ms.
   M04 ordered replies are slower for every length; these are not rendering FPS.
2. Forty comparison samples plus eight excluded warm-ups verify 393,216 buffer bytes.
   Twelve complete invocations retain 72 raw rows; five individual USB dumps lose
   bytes. Four corresponding fresh-repeat samples fill original gaps under an
   integrity-only rule; original indices/timing fields and source hashes remain.
3. PRT1 /256 gives 72,000 nominal counts/s. Stock MOS increments its coarse clock
   by two per VBlank: at 60 Hz about 120 units/s. Corrected initial timeout descriptions;
   frozen firmware, fixture constants and measured intervals are unchanged.
4. Proposed next focus is bounded attribution of block reservation/offer,
   UART parking, byte loop, receipt/release and real VBlank return service.
   No additional profiling or optimization has been started.

Unrelated HOST-001 relocation edits and EMOS application_peer.py remain untouched.
