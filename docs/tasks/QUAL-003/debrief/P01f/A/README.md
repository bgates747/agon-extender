# P01f A — graphics ownership and scheduling audit

## Executive summary

Author directed proceeding with greater scrutiny after the failed priority
experiment. This chunk traces ownership, blocking and handoffs from UART parser
to graphics execution, snapshot and HTTP output, against the retained mainboard
FabGL implementation and pinned ESP-IDF. Deliver a source-linked map, concrete
findings, uncertainty ledger and one bounded next experiment. Hardware actions
are limited to clearing the prior cue and the established completion voice/banner.
No firmware edits/build/flash, performance tests or broad redesign in this chunk.

## Frozen contract

1. [ ] A01: Freeze this scope, identify exact source snapshots/SDK and official
   references; clear mainboard through admitted CLI without reset.
2. [ ] A02: Trace real lock order and ownership across parser, foreground flush,
   drawing, row composition, snapshot leases, network worker, HTTP sender and
   SDK networking tasks. Identify waits/yields and allocation inside exclusion.
   Follow virtual overrides and build flags, not comments alone.
3. [ ] A03: Compare upstream VGA ISR/primitive execution constraints with P4
   replacements. Explain which locks are inherited or port-added and which
   original timing/exclusion guarantees survive. Reuse P00; only add findings
   that resolve a gap or re-check an assumption. AUDIT-007 remains separate.
4. [ ] A04: Reconstruct the S priority scope through pinned FreeRTOS priority
   changes, recursive mutex inheritance/disinheritance and scheduler yields.
   Look for concrete contradictions, cycles, starving loops and lost guarantees.
   Distinguish source-proven mechanisms, measured evidence and hypotheses.
5. [ ] A05: Review alternative explanations and negative evidence; produce an
   ownership diagram, indexed findings and one smallest discriminating next
   experiment with validity gates. No speculative fix by implication. If source
   inspection cannot establish cause, say precisely what observation is missing.
6. [ ] A06: Update parent plan/TODO/log, commit granular results, accepted hardware
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
