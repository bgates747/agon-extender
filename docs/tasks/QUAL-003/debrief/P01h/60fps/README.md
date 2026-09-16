# Nurples single-vblank follow-up

## Executive summary

Author requests a 60fps-paced Nurples run and hardware completion notification.
Measure application cadence separately from browser delivery. Keep the existing
30fps web credit cap: this changes application pacing, not the output guarantee.
Use candidate r06 and a one-vblank derivative of the exact retained repair-based
1800-cycle fixture. Production applications remain untouched.

1. [x] Build isolated fixture by removing only its second vblank wait; preserve
   source/binary hashes and compare against the retained two-vblank fixture.
2. [ ] Clear the hardware screen, deploy/readback r06 reversibly, upload the new
   fixture under /test/nurples, and run output-disabled then RLE2 web controls.
3. [ ] Validate trace count and faults; report application intervals and browser
   receipt cadence separately. Record receiver network and single-run limits.
4. [ ] Restore prior P4 firmware, confirm original startup unchanged, retain
   evidence, commit results and deliver the hardware spoken notification.

No mainboard firmware changes, Golem, production default changes or remote push.
Stop for an unexpected fault; do not silently repair the renderer in this test.
