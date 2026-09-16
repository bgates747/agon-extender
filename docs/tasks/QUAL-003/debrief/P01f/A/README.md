# P01f A — graphics ownership and scheduling audit

## Executive summary

**Focused audit complete; no firmware change.** The port's snapshot task shares
native graphics exclusion with parser/drawing; immutable socket sending itself
is outside that mutex. Mainboard row preparation runs in an ISR. The failed S
experiment additionally requested a scheduler yield after each row pair:
192 requests, 384 priority changes and 768 priority queries per full snapshot.
Inherited priority can persist in another holder until its other mutexes release.
These are verified mechanisms, not a complete causal attribution of the failure.

[Findings, comparative tables and proposed next experiment](FINDINGS.md) and
[ownership/FabGL map](OWNERSHIP.md) contain the detailed audit. Recommend testing
the same ceiling once per admitted snapshot, with original row lock boundaries
and strict repeated correctness/pacing gates; no implementation before review.
This removes repeated priority transitions but also raises normalization priority,
so that confound is explicit. No deadlock cycle established in the inspected
steady-state path. Exhaustive AUDIT-007 remains separate; Golem excluded.

Standard hardware voice receipt and visible completion-banner input verified;
startup unchanged, input neutral, SD exited to Legacy MOS. Await Author review.

## Frozen contract

1. [x] A01: Freeze this scope, identify exact source snapshots/SDK and official
   references; clear mainboard through admitted CLI without reset.
2. [x] A02: Trace real lock order and ownership across parser, foreground flush,
   drawing, row composition, snapshot leases, network worker, HTTP sender and
   SDK networking tasks. Identify waits/yields and allocation inside exclusion.
   Follow virtual overrides and build flags, not comments alone.
3. [x] A03: Compare upstream VGA ISR/primitive execution constraints with P4
   replacements. Explain which locks are inherited or port-added and which
   original timing/exclusion guarantees survive. Reuse P00; only add findings
   that resolve a gap or re-check an assumption. AUDIT-007 remains separate.
4. [x] A04: Reconstruct the S priority scope through pinned FreeRTOS priority
   changes, recursive mutex inheritance/disinheritance and scheduler yields.
   Look for concrete contradictions, cycles, starving loops and lost guarantees.
   Distinguish source-proven mechanisms, measured evidence and hypotheses.
5. [x] A05: Review alternative explanations and negative evidence; produce an
   ownership diagram, indexed findings and one smallest discriminating next
   experiment with validity gates. No speculative fix by implication. If source
   inspection cannot establish cause, say precisely what observation is missing.
6. [x] A06: Update parent plan/TODO/log, commit granular results, accepted hardware
   voice and visible banner; verify unchanged startup and neutral input/SD state.
   Stop for Author review. No push, emulator experiment or delegation.

## Boundaries

Pinned archive r45 is the recovered baseline; r48 is the failed S intervention.
Current checked-in adapters are compared against those archives to avoid calling
an inactive diagnostic branch production behavior. r43 remains installed. Official
checkouts are read-only. No MOS/mainboard VDP changes. Golem excluded; interrupt
masking, chunk pacing, RLE and exhaustive FabGL coverage remain outside this chunk.

Host-side source inspection/calculation is allowed. Any model must be labelled
as a model, not proof of the bench schedule. New performance or firmware work
requires a frozen subsequent implementation/test contract after this review.

## A01 source admission

Scope frozen in commit `8d92f12`. Mainboard was cleared through freshly admitted
CLI without reset. Exact archived r45/r48/current source comparisons, retained
mainboard identities and pinned SDK hashes are in [SOURCES.json](SOURCES.json).
Official VDP checkout remains clean at v2.16.0. Online v5.5 ESP-IDF documentation
provides context; locally pinned 5.5.5 source controls precise behavior.

## Ownership and upstream comparison

A02/A03 completed in [OWNERSHIP.md](OWNERSHIP.md): actor/lock map, virtual
gate dispatch, original ISR versus scheduled task differences, immutable network
lease boundary, selected SDK send path, inherited allocation waits and scope
limits. No closed cycle established in the inspected steady-state path.

## Closeout

[Notification receipt](notification.json) records fresh stage6/audio success,
unchanged autoexec and neutral keyboard. Completion banner emitted without
clearing it afterward; human hearing remains unconfirmed. Previous verified r43
retained, no flash/reset/build/benchmark or active observer during this chunk.
Documentation/source calculations checked; no runtime test is claimed. All
changes committed locally in discrete documentation commits, no push.
