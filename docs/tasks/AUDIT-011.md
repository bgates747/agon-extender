# AUDIT-011 — Hardware fitness of upstream code reuse

## Executive summary

Audit the project-owned codebase for stock MOS/VDP/FabGL assumptions retained
because the code compiles, without establishing that those assumptions suit
the P4. Preserve application-visible stock behavior; adapt implementation when
the original processor or output hardware explains a design that costs the P4
unnecessary work. Compilation establishes neither hardware fitness nor speed.

**State: proposed audit contract, not started.** Created 2026-10-11 at the
Author's request. This authorization covers writing the task only. Stop before
source review, implementation, builds or device operations. The indexed/PPA
integration under [RESEARCH-007](RESEARCH-007.md) remains paused for discussion.

## Review principle

Reuse proven upstream code when its assumptions and costs fit the destination.
Do not preserve hardware-specific layout, scheduling or peripheral mechanisms
solely for source similarity. Conversely, do not replace proven code merely
because a P4 alternative exists. The reviewer must identify the original
constraint, the P4 constraint, preserved observable behavior and comparative
cost before recommending an adaptation. Lack of evidence means unassessed,
not equivalent, defective or slower.

This refines the reuse rule, not the no-upstream-bug-fixes rule. Separate
intentional upstream hardware choices from inherited defects and local port
errors. No upstream bug fixes, new application semantics or transport redesign
are authorized by this audit.

## Scope and boundaries

1. Review maintained P4 code in `vdp/`, including vendored code actually linked
   into current board profiles, compatibility layers and local replacements.
   Include build selectors and host-tool interfaces where they enforce or
   conceal hardware assumptions. Inspect EMOS and MOS build integration in
   their owner checkouts only where they constrain these P4 contracts.
2. Prioritize video storage, drawing, partial scrolling, software and hardware
   sprites, palette handling, composition, cache/DMA handoff and output. Nurples
   remains the main gameplay performance target. Broaden the census to parser,
   task/interrupt, synchronization, input and peripheral paths without silently
   expanding into unrelated feature implementation.
3. Cover both maintained P4 board profiles. Distinguish P4 versus mainboard
   differences from board-specific wiring, silicon revision and SDK limits.
4. Official reference checkouts remain read-only. Review relevant contracts in
   `../../agon-docs` first; consult `../../agon-vdp` and `../../agon-mos` when
   implementation details matter. Pin exact source commits and official tags.
5. Reuse evidence from [AUDIT-006](AUDIT-006.md), [AUDIT-010](AUDIT-010.md),
   [SCAN-001](SCAN-001.md), [SPRITE-001](SPRITE-001.md),
   [RGB-001](RGB-001.md), [HDMI-002](HDMI-002.md) and RESEARCH-007. Those reviews
   answer different questions; do not reopen completed work without a concrete
   hardware-fit question or repeat measurements with equivalent evidence.
6. No flashing, resets, bench reservation, SD changes, emulator deployment,
   SDK modifications, production selection or automatic repair. A later
   implementation/test tranche requires its own reviewed scope.

## First candidate: VGA byte-lane ordering

The current stock-compatible VGA64 output adapter reads a signal row using
`signal[x ^ 2]` in
[`hdmi_geometry.hpp`](../../vdp/video/extender/display/hdmi_geometry.hpp).
PPA L8 consumes linear pixel order. Preserving that stock storage layout can
therefore impose a reorder pass before PPA expansion. RESEARCH-007's
[physical comparison](RESEARCH-007/PHYSICAL-RESULTS.md) separately measures
linear PPA and reorder-plus-PPA; it does not establish whole-renderer costs.

The audit must trace the original VGA hardware reason and every producer and
consumer of this layout before recommending linear storage. Identify drawing,
readback, bitmap, sprite-background, palette and output dependencies. Do not
assume that removing one output expression suffices, or confuse pixel order
with RGB channel order. Preserve stock-visible semantics while comparing the
total work required by the original layout and a P4-native layout.

## Discrete work plan

### A11-01 [ ] Freeze the review baseline and bounded source census

Record exact project/component commits, board profiles, SDK and upstream
reference tags. Map linked source and local adaptations by subsystem. Start a
coverage ledger with file/function ranges, original hardware assumptions,
review state and evidence links. Exclude unlinked historical experiments from
the active census; record why each exclusion is valid. Reconcile dirty work
without discarding or silently incorporating it.

### A11-02 [ ] Trace framebuffer and pixel-format assumptions

Start with byte-lane ordering. Trace packed versus byte storage, stride,
alignment, colour meaning, transparency, row indirection and readback. Compare
P4 CPU, PSRAM, DMA, PPA and output requirements against original VGA demands.
Identify redundant copies, expansions or reorder passes and their callers.
Link any linear-byte recommendation into RESEARCH-007 before integration.

### A11-03 [ ] Trace drawing, scrolling and sprite assumptions

Review clipping, bitmap blits, partial vertical scroll, saved backgrounds,
software sprites, scanout sprites and Copper. Explain which operations depend
on original storage and scanout hardware, and which algorithms transfer well.
Assess complete-path costs and concurrency, particularly Nurples's scrolling
playfield plus loaded sprites. Preserve upstream edge behavior unless a
separate approved defect task changes it.

### A11-04 [ ] Trace execution, memory and output assumptions

Review task/core ownership, interrupt versus task execution, locks, busy waits,
queues, allocation capabilities, cache coherence and buffer publication.
Separate original VGA deadlines from HDMI/LCD requirements. Check DMA/PPA
restrictions using primary documentation; a successful compile is insufficient.
Do not propose an RTOS rewrite or assume that offloading always saves time.

### A11-05 [ ] Review remaining linked subsystems

Complete the census for VDU parsing, timers, keyboard/input, peripheral and
transport adapters and build configuration. Identify original CPU/peripheral
shortcuts, polling or emulation carried into the P4 unnecessarily. Preserve
EMOS routing/transport ownership and current application contracts. Record
cross-repository ownership without editing another owner's implementation.

### A11-06 [ ] Consolidate findings and discriminating validation proposals

Assign stable finding IDs `A11-F001`, `A11-F002`, etc. Rank actionable findings
by measured or plausible impact, compatibility risk and evidence confidence.
For each recommendation, identify the processor/software owner, exact source,
original rationale, P4 alternative, preserved contracts, total resource/cost
effects, dependencies, rollback and a small discriminating test. Reuse existing
colour, scrolling, sprite and deterministic Nurples fixtures. Separate drawing,
conversion, composition, transport and presentation measurements. Do not turn
proposed tests into authorized execution.

### A11-07 [ ] Report and pause for Author disposition

Deliver a concise findings table and completed coverage ledger. Distinguish
retain-as-is, adapt-for-P4, inherited-defect/separate-task and unresolved items.
Record justified exclusions and untested claims. Propose one bounded first
repair, link to its existing owner where possible, then stop for approval.
Update TODO and the development log; do not automatically create many repair
tasks or apply recommendations.

## Evidence and completion gates

1. Store the source census and coverage ledger under `docs/tasks/AUDIT-011/`
   when review begins. Freeze source identities before drawing conclusions;
   review later changes as explicit deltas rather than moving the baseline.
2. Each finding must cite exact local source lines/commits and primary
   contracts. Label source-derived expectations, measurements and hypotheses
   separately. No claim of P4 superiority without comparable evidence.
3. Completion requires accounting for the linked codebase, not only a list of
   suspicious examples. Record reuse judged appropriate as well as problems.
4. Report performance in side-by-side tables with units, baseline, percentage
   definition and comparability limits; prioritize worst cases. Include total
   memory traffic and setup/synchronization costs, not only kernel time.
5. Keep findings and proposals in this task. Promote approved implementation
   rules into maintained architecture/build guidance only after disposition;
   this proposed audit does not itself change product architecture.

## Decision register

### A11-D01 [ ] Audit execution — awaiting authorization

Recommendation: execute A11-01 first, then review video assumptions before the
remaining census. The Author requested the task and a stop, so no audit work
starts now. Indexed/PPA integration also stays paused until the current layout
discussion is resolved; this audit is not an automatic prerequisite to finishing
every unrelated active task.
