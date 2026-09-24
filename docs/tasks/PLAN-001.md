# PLAN-001 — Timing closeout and next-work selection

## Executive summary

Author approved the work contract on 2026-09-20, with stable subtask IDs and
completion checkboxes. Author authorized freeze and T01 execution. Close out the reusable timing package, reconcile the
unfinished-task queue, then select a bounded tranche of faithful VDP-to-EDP
implementation. Park further browser-performance experiments pending future
display hardware. Aginvadors optimization is deferred until the Author has more
tokens available; it is not a prerequisite or an active investigation here.
Approval does not mark the execution subtasks complete or authorize a new
hardware/implementation tranche beyond this closeout and planning contract.

## Frozen work contract — 2026-09-20

**PLAN-001-T01** [x] **Timing closeout.** The agent reviews BENCH-007 implementation, reusable
   documentation, results and firmware-restoration evidence. Identify owning
   repositories and separate scoped changes from unrelated browser/game work.
   Retain the unresolved mainboard sequential-run sprite/heap panic and Rally's
   fixture-versus-gameplay discrepancy as explicit follow-ups. After approval,
   commit the timing package and findings in discrete groups. Do not push without
   an instruction to publish.

**PLAN-001-T02** [x] **Queue reconciliation.** The agent checks every open TODO entry against its
   task record and evidence. Present a compact disposition table: genuinely
   unfinished implementation, completed work awaiting acceptance, superseded
   work, or deliberate deferral. Machine completion does not substitute for
   required human acceptance. Close accepted items in their task and development
   log before removing them from TODO. Preserve evidence and deferred tasks.
   Replace conflicting historical priority headings with one clear sequence.

**PLAN-001-T03** [ ] **Next implementation selection.** From the reconciled queue, the agent
   proposes a bounded faithful VDP-to-EDP tranche with acceptance criteria.
   Reuse stock implementations where applicable. Park browser transport and
   compression optimization; correctness regressions remain eligible. Planning
   does not itself start another hardware experiment or implementation tranche.

## Decision register

### D01 — Optimize Aginvadors before the next porting tranche?

**Resolved — deferred by the Author on 2026-09-20.**

Do not start Aginvadors profiling or optimization under this contract. Revisit
only when the Author chooses to spend tokens on it. The useful goal of a
dependable playable 320×240 reference remains recorded, without blocking T03.

Production Aginvadors selects mode 8: 320×240, 64 colours. The measured
one-vblank build averaged about 51 application updates/s on both routes;
20 of 120 active updates exceeded one 60-Hz interval. These short runs identify
deadline misses, not their cause. This is not evidence of an Extender-only
problem or a remaining 50-Hz cap. See [results](BENCH-007/RESULTS.md) and
[game baseline](QUAL-003/mode-transition/AGINVADORS.md).

**Retained rationale:** a playable 320×240 reference would help compare
resolution-dependent costs, but game optimization takes time and tokens away
from renderer coverage. Nurples remains the stronger current pacing reference.
If the Author resumes Aginvadors work, scope production improvements separately,
preserve representative gameplay and the requested 60-Hz target, and define
repeated workload, deadline-miss and human-playability acceptance before coding.

## Review gates and deliverables

**PLAN-001-G01** [x] Author reviewed and approved this contract, subject to
stable subtask identifiers and checkbox formatting; applied in this revision.

**PLAN-001-G02** [x] Author settled D01: defer Aginvadors optimization.

**PLAN-001-G03** [x] T01 produces scoped commit groups with retained limitations.

**PLAN-001-G04** [x] T02 produces a disposition table and proposed authoritative
order for Author review.

**PLAN-001-G05** [ ] Author approves the implementation contract proposed by T03
before that new tranche starts.

No firmware identity, emulator launch, bench operation or network change is
required for this documentation update.

## T01 execution receipt — 2026-09-20

Contract freeze: `01bd48a5`. Reusable timing package: `ba9dd47f` in Extender.
Existing production one-vblank pacing: `7321a0f` in Pynvaders. Results and
closeout records are committed separately. Review checks: four analyzer tests,
ASan/UBSan recorder, normal Aginvadors build and sanitizer-backed simulation,
85 evidence hashes, 18 CSV validations and 12 serial comparisons all passed.
No hardware change or push. Mainboard panic and Rally comparison limits remain
BENCH-007-F01/F02 for T02 disposition. T02 and T03 had not started at that receipt.

## T02 review delivery — 2026-09-20

Author authorized T02 after the T01 closeout. Reviewed all 45 incoming entries
against their task records and later linked evidence: one active planning task,
ten with remaining implementation/documentation, eleven review/disposition
items, twenty-two parked/unscheduled items, and one already-completed research
item. [Disposition table](PLAN-001/QUEUE-REVIEW.md) covers every original ID.

TODO now has one current sequence and separate candidate/review/parked groups.
RESEARCH-004's already-completed entry is removed with task/log closure; all
other acceptance gates remain. Targeted current-state notes distinguish old
recovery, installation, input and production-pacing claims from later evidence.
The existing 30-Hz ADR versus later higher-rate records is flagged for future
scope reconciliation, not silently resolved by this queue edit.

T02 was delivered for review; the Author subsequently authorized the bounded
AUDIT-007 first source pass for T03. Its contract was frozen in `db314dd6`.
[Findings](AUDIT-007/FINDINGS.md) now propose mode-transition lifetime work.
T03/G05 remain open pending selection and approval of that implementation
contract. No code, hardware operation or new benchmark was performed.
