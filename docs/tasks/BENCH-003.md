# BENCH-003 — Paced Nurples application and web cadence

## Executive summary

Author authorizes the next bounded timing investigation after freezing the
production/test split. Measure whether the remaining choppiness originates in
application frame spacing or web capture/delivery/presentation. Do not infer
realized game fps from the EVF logical period, request rate, or a standalone test.
Production applications stay untouched after BENCH-002's requested consolidation.
No Golem, firmware experiments, compression or scheduler changes.

## Frozen work contract — 2026-09-16

1. [x] Finish BENCH-002 consolidation: repair assets; normal production pacing;
   independent 30fps Nurples and current Rally bundles beneath `/test`.
2. [x] Prepare a task-owned diagnostic derivative of the current repair source:
   retain two-vblank pacing; bounded in-RAM frame timestamps and phase records,
   no per-frame serial logging. Automate loading prompts only in this derivative;
   stop safely at the bounded frame limit or game over. Record every source edit
   and binary identity. Keep production and ordinary test binaries intact.
3. [ ] Record paired same-fixture Legacy/no-web and ExCom/no-web controls, then
   ExCom/web with host requests capped at30Hz. Use the existing browser protocol
   and presenter; record message arrival and WebGL submission intervals, sequence
   gaps and identical image observations. No serial opening or firmware flashing.
4. [ ] Read application timing records after exit, preserve raw evidence, and
   compare median/p95/max intervals and effective fps. MOS time is quantized;
   WebGL submission is not physical monitor scanout. No unsynchronized clock
   subtraction and no claim to observe native rendering completion from a game
   loop timestamp. Repeat one informative case if the initial contrast warrants.
5. [ ] Write executive summary/table, limitations and the next concrete avenue.
   Restore ordinary test build/readiness, preserve startup, then accepted hardware
   voice notification and visible completion message. Stop for Author review.

## Gates and limits

Use verified native keyboard and SD service with durable deployment receipts.
Keep diagnostics and measurements in this task's silo and `/test/nurples`.
Do not erase historical benchmark fixtures merely because their names contain
Nurples. Clear previous notification at an admitted prompt before test work.
If byte correctness, application termination or control health fails, preserve
failure and stop performance interpretation. Native game loop timing is only
submission/pacing evidence, not per-primitive graphics timing.

The accepted30Hz web ceiling applies to output requests and resulting snapshot
admission. This diagnostic may enforce it in its host client without claiming the
ordinary firmware/browser's production limiter is implemented.

## Agent-assigned preparation adjustment

The per-entry remote directory API re-enumerates from zero and incurs a network
round trip per entry. Replace the slow host walk with a tiny task-owned read-only
MOS3 directory walker, writing a new `/test/nscan.tsv` report. It traverses the
card and emits Nurples/Rally paths plus root entries, an entry count and terminal
status. No delete capability, firmware changes, or SD transport redesign. This
support step is self-assigned under the Author's execution authorization.
