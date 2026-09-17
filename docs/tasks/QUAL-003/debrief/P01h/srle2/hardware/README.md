# SRLE2 physical P4 qualification

## Executive summary

Author releases the bench and authorizes restoring the saved EMOS image, keeping
mainboard VDP stock, and testing SRLE2 on the P4. Determine whether reduced wire
traffic compensates for entropy-encoding cost under actual rendering load. The
browser candidate passed host tests; no hardware performance conclusion follows
from that pass. This is a new goal; the preceding browser-only hour has ended.

## Frozen execution contract

1. [ ] H01 — Re-establish the bench baseline. Preserve current SD startup and actual
   P4 state; restore the exact pre-stock-test EMOS ROM through the maintained ZDI
   programmer and independently verify it. No EMOS source edits. Leave mainboard
   VDP release2.16.0 untouched. Restore the known P4 product baseline, enable its
   admitted keyboard/SD path through startup, verify readiness and clear the
   mainboard screen. Physical card movement is a human assistance gate when needed.
2. [ ] H02 — Build a corrected isolated SRLE2 candidate from retained RLE2 r06.
   Integrate the tested EVS1 browser decoder and explicit raw/RLE2/SRLE2 negotiation.
   Reuse one-frame credits/30Hz output ceiling. Keep immutable compressed snapshot
   ownership separate from graphics locks; do not change scheduling or rendering
   to manufacture a codec improvement. Bound allocations, concurrent admission,
   failures and raw fallback. Record build and rollback manifests before flashing.
3. [ ] H03 — Qualify device codec and asset paths first. Original CLI golden corpus
   → P4 decode and P4 encode → independent host decode, exact bytes. Cover tiny/
   stored data, alpha assets, command65 two-layer unpack, fragmented buffers,
   in-place destination, retained destination after bounded invalid input, and
   bitmap pixels versus raw upload. Record memory/stack and codec time where
   measurable. Stop on corruption/watchdog/unknown correctness faults; diagnose
   in the task silo, not by modifying EMOS or mainboard VDP.
4. [ ] H04 — Matched performance controls. Begin with informative synthetic regular,
   sprite-heavy and noise scenes; separately measure encoding cost, message bytes,
   and delivered browser cadence. Then reuse the identical deterministic Nurples
   single-vblank fixture for output-disabled, raw, RLE2 and SRLE2 conditions at the
   existing30Hz web cap. Use three matched RLE2/SRLE2 trials where stable, retain
   actual fixture/build identity, application timing and browser receipt/submission
   separately. Historical results are context, not replacements for a current
   same-candidate control. No Golem, game-logic or EMOS changes.
5. [ ] H05 — Review the evidence and perform bounded P4-only corrections if a clear
   defect or avoidable codec overhead is exposed. Change one cause at a time and
   repeat affected controls, keeping failed evidence and rollback points. Do not
   chase parity indefinitely or broaden into scheduler/transport rewrites. Label
   any self-assigned additions prominently and record their justification.
6. [ ] H06 — Write the assessment with tables and a keep/reject/conditional verdict
   in its first sentences. Restore the known-good product P4 image/startup unless
   a fully tested candidate is deliberately retained for Author review, with that
   state explicit. Leave restored EMOS and stock mainboard VDP in place. Return
   neutral keys and a usable foreground; hardware spoken notification, then stop.
   Use accepted emulator voice fallback if hardware cannot deliver the cue.

## Limits and provenance

No experimental push. Commit discrete changes/evidence; source stays within P01h
until acceptance. Preserve original szip source and historical command65 CmpS wire
contract. Mainboard VDP flashing, new EMOS hacks, Golem and production application
replacement are excluded. See ../web/RESULTS.md, ../PORT-NOTES.md and the enduring
../../../../../../mos-recovery.md procedure. Host and P4 allocation limits are
not interchangeable, and host timing is not P4 timing.

The SD card is presently mounted on the Linux host with the Author's MOS-suite
startup. Preserve it before staging; do not mistake a missing card for MOS failure.
Inspect actual P4 state because the intervening MOS test may have used a programmer
image. Machine identities, fresh receipts and controller ownership live in the
ignored hardware record and agents/srle2-hardware.
