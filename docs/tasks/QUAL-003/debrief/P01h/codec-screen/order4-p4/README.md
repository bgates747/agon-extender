# Full-block order4 SRLE2 on P4

## Executive summary

Author authorizes silicon tests and hardware spoken notification. Compare order4
with order3 and RLE2 on one isolated firmware, with identical rendering/scheduling.
Preserve and restore the current P4 image and Agon startup. Do not flash mainboard
VDP or change EMOS. The host-mounted MOS-suite card is out of scope.

## Frozen contract

1. [ ] S01 — Verify current stable P4 identity, baseline/startup and controller
   readiness; preserve rollback; clear mainboard screen through admitted CLI.
2. [ ] S02 — Clone retained qualified SRLE2 r03 into this task's private candidate.
   Add explicit order4 encode entry and query selection alongside unchanged
   order3/RLE2 controls; use full-input blocks and record1/no differencing.
   Retain stack sizes, priorities, codec ownership and rendering. Build and verify
   exact before/after firmware hashes when deploying. No small-block experiments.
3. [ ] S03 — Exact original-derived golden inputs and outputs for both orders on
   P4, including browser decode. Then matched deterministic fixed-mode Nurples
   runs, three trials per RLE2/order3/order4, plus informative static scenes.
   Record encoding time, bytes, delivered/submitted cadence and fixture timing.
   Stop and diagnose boundedly on corruption, reset or unresolved test failures.
4. [ ] S04 — Verdict and tables, restore verified original P4/startup, neutral keys
   and Legacy prompt; accepted hardware voice receipt, emulator voice fallback
   only if hardware cannot notify. Commit discrete work; no push/promotion.

Original reference tests: ../../srle2/hardware/README.md. Current local bench
state and identities: HARDWARE.local.md. All operations use the card in the Agon.
No Golem, EMOS, mainboard VDP, production games or graphics scheduling changes.
