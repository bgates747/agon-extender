# BENCH-002 — Nurples two-vblank review

## Executive summary

Nurples now waits two distinct vblanks between main-loop frames. At60Hz this
caps frame-based updates at30fps (slower if rendering overruns), deliberately
slowing gameplay. Rally already gates rendering by four MOS clock ticks,
equivalent to two vblanks; no Rally source modification was necessary.
Hardware visual smoothness and realized frame rate remain for human review.

## Changes and evidence

1. Nurples dev commit `2f0f095` adds one adjacent `call vdu_vblank` at the existing
   pacing point. Existing bounded wait/timeout behavior is retained. Timestamp
   timers remain real-time; not every game event necessarily takes twice as long.
2. Assembly-only build succeeded and generated matched binary/symbols. Existing
   dirty UI/starfield work was neither committed nor regenerated. Installed art
   is retained for a pacing-only comparison. Required runtime file sizes checked.
3. Rally `rally-game/src/main.cpp` schedules `next=now+4`. Stock MOS
   `src/interrupts.asm::_vblank_handler` increments the clock by2 each vblank.
   Current release rebuild passed identity/CRT/fixture-separation checks.
4. [Build checks](BUILD-CHECKS.json) retain source revisions and artifact hashes.
   Nurples executable replacement uses staged CRC, independent stage readback,
   activation and active-file readback. Previous file remains `.p17bak`.
5. Standalone P4 research image was replaced with saved r43. Application bytes
   independently flash-verified; boot observation confirmed full build identity,
   native USB keyboard and Ethernet readiness. MOS/mainboard VDP were not flashed.
   Boot readiness initially required an explicit P4 run/reset and mainboard
   input readmission. A redundant guarded deployment invocation stopped before
   any write; this was an operator correction, not a MOS or application defect.
6. A local artwork mismatch was found during comparison. Its staged transfer
   was cancelled before activation; installed file boundary blocks stayed
   unchanged. No artwork replacement is part of the final change.

## Scope limits

This is application-loop pacing. The30fps web snapshot/output limiter is still
separate work under QUAL-003 P06e-30; no production web firmware change is claimed.
No Golem work, performance instrumentation or physics compensation added.
Hardware command acknowledgements are not proof of human visual acceptance.
Deployment/notification receipts are appended after completion.
