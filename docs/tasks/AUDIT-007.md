# AUDIT-007 — Exhaustive Agon FabGL port completeness audit

## Executive summary

The first graphics-backend source tranche is complete; see
[findings](AUDIT-007/FINDINGS.md). Its subsequent
[mode-startup investigation](AUDIT-007/MODE-LIFETIME.md) recorded an inherited
palette defect, with mainboard manifestation reported by the Author (not captured
by that investigation). The
[firmware bug register](../firmware-bugs.md) owns the current deferred-fix
disposition. The exhaustive audit remains incomplete; no new bench work or
upstream correction is authorized by this summary.

**Original exhaustive scope:** Audit the complete pinned
Agon FabGL/vdp-gl fork for code, dependencies and implicit contracts the P4 port
must retain or minimally adapt. Scheduling awaits findings from QUAL-003's
immediate focused timing research. This audit will happen whether or not that
research fixes the current Nurples performance issue; the dependency determines
sequence and starting points, not whether the audit is required.

Created: 2026-09-15. Owning queue: `TODO.md`. Bounded first-pass execution starts under the linked contract.
Predecessor: [QUAL-003 P00](QUAL-003/DEBRIEF-PLAN.md#p00--audit-inherited-fabgl-timing-before-selecting-scheduling-changes).
This task owns the exhaustive work formerly described under P00e.

## Purpose and scope

The Author reports that experienced maintainers of Agon's fork describe FabGL
as notoriously convoluted. Machine-assisted call-chain tracing does not ensure
recognition of implicit contracts or subtle cross-subsystem effects. Explicitly
look for those effects; successful compilation, visible output and a narrow
current feature set are insufficient evidence of a complete port.

Cover every subsystem in the selected fork, including code omitted from the
P4 build, stubs, alternative controllers, hardware-specific branches and
functions outside the current implementation scope. Trace dependencies into
Agon VDP and platform adapters where needed to explain behavior. Hardware
differences and deferred features are not, by themselves, reasons to discard
supporting code. The audit need not implement every deferred feature, but it
must identify its interactions and any present requirements.

Preserve the prime directive: use stock code where it compiles; otherwise make
the smallest necessary adaptation while retaining its logic and contracts.
Record upstream bugs separately, without opportunistic fixes or improvements.
Golem testing remains on hold. VGA output implementation is not authorized by
this task; identify reusable mechanisms without assuming VGA must be generated.

## Exhaustive work items — not completed by the bounded first pass

**AUDIT-007-F01** [ ] Review the focused research and preceding AUDIT-006/PORT-003 records.
   Pin exact upstream, fork, dependency and P4 revisions. Consult official
   documentation first. Preserve official checkouts as read-only references.
   Establish the full file/subsystem inventory, build selections and omission
   list before treating any area as covered.
**AUDIT-007-F02** [ ] Create an exhaustive coverage ledger. Include all subsystem files,
   relevant symbols and build branches, their upstream/P4 counterparts, prior
   audit evidence and unresolved questions. Expand coverage whenever tracing
   reveals another dependency; do not restrict it to currently exposed APIs.
**AUDIT-007-F03** [ ] Trace behavior across callers/callees, virtual dispatch, macros,
   compile-time selection and shared state. Explicitly examine initialization,
   teardown, ownership/lifetime, allocation and memory capabilities, locking,
   ISR/task boundaries, queueing, timing, notifications, completion and output
   side effects. Follow hidden dependencies through omitted and deferred code.
**AUDIT-007-F04** [ ] Compare the actual P4 port against those contracts. Assign each
   area a source-backed disposition: retained correctly; necessary adaptation
   verified; required port/adaptation missing; deferred with dependencies and
   consequences identified; or demonstrably unnecessary on this hardware.
   Unresolved relevance is an open finding, not permission to omit code.
**AUDIT-007-F05** [ ] Review the ledger for blind spots. Trace representative public
   operations end to end and audit the omitted/stubbed code in the reverse
   direction for dependencies on active paths. Check that prior hardware or
   feature-scope assumptions have not substituted for source evidence.
**AUDIT-007-F06** [ ] Produce an executive findings report, stock/P4 dependency maps and
   prioritized required port work with discriminating validation proposals.
   Link confirmed immediate-research findings rather than repeating experiments.
   Separate audit completeness, implementation completeness and test coverage.
**AUDIT-007-F07** [ ] Present the audit for Author review. Promote agreed implementation
   and validation work into the owning tasks/queue, with explicit contracts.
   Do not close this audit merely because the original performance issue was
   fixed or a game became visually acceptable.

## Completion evidence and execution boundary

Every inventoried subsystem and excluded build area must have a supported
disposition, traceable sources, and explicit unresolved dependencies or follow-up
owners. Findings must explain both what needs porting and why an omission is
safe where that is claimed. The final review must expose remaining uncertainty;
unknowns cannot be silently counted as verified coverage.

The original task definition authorized its durable record, not execution. The
2026-09-20 first-pass contract now authorizes bounded source investigation, not
flashing firmware, running hardware tests, changing upstream code, or publishing
experimental changes. Scheduling follows the immediate research and subsequent
Author direction. Future implementation and hardware validation need their own
bounded plans; the current bench remains undisturbed.

## First-pass delivery — 2026-09-20

The frozen bounded tranche is complete; [findings](AUDIT-007/FINDINGS.md)
recommend mode-transition lifetime investigation for review. This does not
complete the exhaustive audit or authorize hardware work.
