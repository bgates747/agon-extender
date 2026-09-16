# BENCH-002 — 30 fps Nurples and Rally human smoothness review

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
5. [ ] B05: Record build/deployment evidence and scope limits, send hardware
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
