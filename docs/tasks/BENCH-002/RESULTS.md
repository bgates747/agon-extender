# BENCH-002 — Nurples two-vblank review

## Executive summary

The retained test build waits two distinct vblanks between main-loop frames,
capping updates at 30/s under a 60-Hz vblank (slower when work overruns).
Production Nurples was subsequently restored to one vblank; the final deployment
is recorded below. Rally already gated rendering by four MOS clock ticks and
needed no source change. Earlier qualitative feedback did not identify the exact
Nurples installation, so it cannot qualify the later matched bundle. No fresh
performance or installed-state claim is made by this record.

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

## Deployment and notification complete

[Deployment receipt](DEPLOYMENT.json): only Nurples executable changed; Rally
matched byte-for-byte. Required assets retained, autoexec unchanged.
[Hardware notification](NOTIFICATION.JSON): fresh stage6/audio_commands=pass
receipt. [Launch record](LAUNCH.JSON): EMOS EXCOM, current Nurples path, LOAD/RUN
commands acknowledged. Human visual acceptance is pending; no ongoing driver
or SD service. Changes committed locally, unrelated dirty artwork preserved.

## Corrected repair installation and test separation — 2026-09-16

The Author identified the version ambiguity after the initial visual review.
A full read-only SD directory scan completed15,515 entries with status0. The
obsolete playable `/nurples` installation (40,707-byte executable,476 total
entries) was removed through an explicit MOS batch; subsequent STAT confirmed
its directory absent. Historical source under `/mystuff/agon-testing/nurples`
was preserved; its22-byte scratch binary is not a playable Nurples installation.

The normal repair build and current dirty repair assets now live in
`/mystuff/nurples`. Production uses one vblank; `/test/nurples` has the exact
previous two-vblank build with independent matching assets. All four runtime
files in both installations received full readback verification. Independent
Rally copies at `/test/arcade/rally` match the three production runtime files;
production Rally and autoexec were unchanged. Exact hashes and transfer duration
are in `REPAIR-DEPLOYMENT.json`. Verification/copy/deletion took2,305.933 seconds,
excluding earlier inventory and local preparation. This is deployment time,
not game or rendering performance.

The earlier observation—Nurples consistently choppy, Rally looking good—does
not identify which old installation the Author ran. Do not assign it to the new
fully matched bundle. BENCH-003 now measures an explicitly identified derivative.
