# BENCH-002 — 30 fps Nurples and Rally human smoothness review

## Current-state clarification — 2026-09-20 queue review

The production/test separation accepted later in this record supersedes the
initial production slowdown: normal Nurples is single-vblank, while the
independent test build is two-vblank. The Author supplied qualitative game
feedback; final task disposition still needs review. No deployment changes here.


## Executive summary

Author requests Nurples wait two vblanks per game-loop frame, deliberately
slowing frame-based gameplay, and Rally be capped at30fps if not already so.
Use current nurples-repair code, preserve installed artwork and unrelated dirty work;
Rally's maintained full game is rally-game, never Golem/historical rally.
Restore the saved normal P4 firmware, deploy verified game bytes, and notify
with the standard hardware spoken cue. Human smoothness assessment remains open.

## Frozen execution contract

1. [x] B01: Inspect game pacing and authoritative MOS timing. Record branch,
   dirty-work boundary and exact change. No physics compensation in Nurples.
2. [x] B02: Add a second main-loop vblank wait in Nurples; build without asset
   regeneration or emulator deployment. Check Rally's four120Hz-tick scheduling;
   change it only if it does not already cap rendering at30Hz.
3. [x] B03: Restore saved P4 r43 application with stable USB identity checks and
   independent flash readback; mainboard reset/readmission if needed. Clear
   previous completion banner once admitted. No MOS/mainboard VDP flashing.
4. [x] B04: Deploy the narrow Nurples executable plus verify required runtime
   data; preserve/read back any replaced files. Compare deployed current Rally
   with maintained binary/build before declaring its cadence. Preserve autoexec.
5. [x] B05: Record build/deployment evidence and scope limits, send hardware
   voice and visible review banner, leave safe CLI readiness and stop for review.

## Scope and acceptance

Two sequential waits preserve existing bounded fail-open behavior on missing
vblank; no new IRQ implementation. Normal60Hz interrupts permit at most30 game
loop renders/s, slower under load. Wall-clock-based timers may not halve with
frame-based motion. Rally retains elapsed-time physics if already capped.
Game-frame pacing and web snapshot/output pacing are separate; ADR-0020's
production output limiter remains its own work. No new performance qualification
claim from assembly/build/readback alone. No experimental push.

## Agent-assigned scope correction during deployment

Installed artwork differs from dirty local artwork. A staged game.agnb upload
was cancelled before activation; original first/last blocks verified unchanged.
Keep existing assets and check required sizes, replacing only executable bytes.
This narrows the change to the Author-requested pacing comparison. Do not
claim full asset hash equality with the dirty tree.

Rally already uses next=now+4 on the MOS clock, which advances2 per vblank;
no Rally source change. Nurples dev commit2f0f095 adds the second existing
vdu_vblank call; real-time timestamp timers deliberately unchanged.

## Review stop

Hardware voice stage6/audio_commands=pass verified with fresh service receipt;
autoexec unchanged. Nurples ExCom launch commands acknowledged. Human hearing,
visual smoothness and realized frame rate remain unconfirmed. Rally binary
already matched the rebuilt maintained release and was not replaced.

## Author-directed deployment correction — 2026-09-16

The Author reports consistent but still choppy Nurples output under busy scenes,
and good Rally presentation. These are qualitative observations, not measured
frame intervals. The Author then requests the latest `nurples-repair` version,
removal of duplicate Nurples installations from the physical SD card, and one
canonical runtime at `/mystuff/nurples`.

The earlier executable came from repair dev, but retained SD artwork differed
from repair's current dirty runtime assets. This follow-up explicitly includes
that complete repair runtime (binary, game/UI containers, required font), keeps
the two-vblank pacing, and preserves unrelated applications/fixtures and startup.
Use an explicit SD inventory and exact paths for deletion; retain host evidence
of identities and validate the canonical runtime by complete readback. No firmware
or rendering changes. Private automation/evidence: `agents/nurples-cleanup/`.

### Production/test separation approved

Author selects `/test/nurples` and `/test/arcade/rally` for test installations,
with independent assets. Production `/mystuff/nurples` restores single-vblank
pacing; the two-vblank build is test-only. Preserve existing production Rally.
Subsequent testing/deployment must explicitly target `/test`, not production.
The canonical production Nurples repair bundle is updated once as requested
above; subsequent experiments leave it alone. Preserve unrelated deterministic
fixture evidence rather than classifying every Nurples-named test as a game.
