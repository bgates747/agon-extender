# Preparation validation

## Executive summary

The task-owned diagnostic builds successfully from the repair source. It adds no
per-frame transport. Hardware results remain pending until the paired runs finish.

1. Repair dev `0c741d5` restores normal production pacing; exact production binary
   SHA256 `63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088`.
   The two-vblank test executable is retained from `2f0f095`, SHA256
   `e7850b78db8c3c5ae1a232836f58f68dcbd56af3066049be8ee335325909b3b0`.
2. Diagnostic timestamp record is 10,812 bytes: magic,24-bit sample count, ABI1,
   and1,800 slots of24-bit MOS time plus24-bit global state. The buffer is placed
   before runtime sprite/tile allocation. Symbols confirm no overlap.
3. Source RNG reset is retained; no keyboard/joystick gameplay input. Elapsed-time
   game logic can still diverge between processors: this is a same-program
   comparison, not a claim of identical per-frame drawing lists.
4. Host trace parser passed synthetic24-bit wrap with33.333/50ms intervals.
   Browser parser passed duplicate DOM updates without counting them as presents.
5. Browser requests use an exact1000/30ms minimum interval with timer rechecks,
   one existing protocol credit and no catch-up queue. Headless WebGL submission
   is measured separately from message arrival. Physical panel timing is unknown.
6. Native MOS clock units are1/120s, normally advanced two per60Hz vblank: effective
   sample granularity is16.667ms. These records cannot resolve individual draw
   operation costs or certify pixel-render completion. Final telemetry is retained
   and vblank timeout flags invalidate a timing control.
7. Full on-card read-only directory scan completed15,515 entries, status0. One
   obsolete playable installation exists at `/nurples`; source-only historical
   `/mystuff/agon-testing/nurples` is preserved. Current repair artwork deployment
   and independent test copies are verified before destructive cleanup.
