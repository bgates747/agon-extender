# Nurples single-vblank follow-up

## Executive summary

Author requests a 60fps-paced Nurples run and hardware completion notification.
Measure application cadence separately from browser delivery. Keep the existing
30fps web credit cap: this changes application pacing, not the output guarantee.
Use candidate r06 and a one-vblank derivative of the exact retained repair-based
1800-cycle fixture. Production applications remain untouched.

1. [x] Build isolated fixture by removing only its second vblank wait; preserve
   source/binary hashes and compare against the retained two-vblank fixture.
2. [x] Clear the hardware screen, deploy/readback r06 reversibly, upload the new
   fixture under /test/nurples, and run output-disabled then RLE2 web controls.
3. [x] Validate trace count and faults; report application intervals and browser
   receipt cadence separately. Record receiver network and single-run limits.
4. [x] Restore prior P4 firmware, confirm original startup unchanged, retain
   evidence, commit results and deliver the hardware spoken notification.

No mainboard firmware changes, Golem, production default changes or remote push.
Stop for an unexpected fault; do not silently repair the renderer in this test.

Completed: see [RESULTS.md](RESULTS.md). Baseline restored; hardware voice
commands acknowledged with fresh receipt. Human hearing remains unverified.

## Missing raw control — Author authorized

Run only the missing raw-streaming condition with the identical r06 firmware,
cadence60 binary, assets, Linux receiver and nominal30Hz browser credit cap.
Do not rerun off/RLE2 conditions. Validate1800 cycles and faults, add its row to
the same results, restore baseline and notify. Single sequential trials remain
subject to changing network conditions.

Raw-control amendment complete:1800 cycles, exact fixture readback, EVF1 receipts
confirmed. Results now include all three conditions; no prior condition rerun.
