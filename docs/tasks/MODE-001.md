# MODE-001 — Develop state-preserving operating-mode transitions

## State

- Status: Not started — aspirational v1 target; firm v2 requirement
- Started: --
- Finished: --

## Current bounded implementation

[EMOS console switching](../protocols/excom-console.md) already implements
bounded Legacy/ExCom transitions, including explicit `--keep-display` to retain
each processor's own scene. It does not migrate graphics assets or implement
this task's general four-mode, in-flight quiescence and recovery guarantees.
The remaining work begins from that implementation, not from an absent switch.

## Namespace

`MODE` identifies work whose primary subject is operating-mode lifecycle,
including selection, transition, preservation, rollback, failure, and
qualification across MOS, onboard VDP, and EDP. Product-version scope remains
explicit in each task rather than being encoded as a vague future-work class.

## Prompting decision

This task was created from
[`REMED-001` Work 2.d, `W2D-Q02`](REMED-001/mode-lifecycle-analysis.md#w2d-q02--rev-1-transition-classes).
That decision permits live Legacy↔Dual activation but adopts disruptive,
restart-mediated ordinary-VDU route changes as the proof-of-concept/beta
baseline and an acceptable v1 fallback.

The Author set state-preserving route changes as an aspirational v1 target and
a firm v2 requirement.

## Intent

Design and qualify quiesced operating-mode transitions that preserve the
loaded eZ80 program and data and preserve resident onboard-VDP/EDP state where
safe and useful. Do this without weakening transactional activation, parser
integrity, ownership boundaries, graceful fallback, or the four-mode truth
table.

The accepted baseline uses Legacy as the mandatory transition hub. Any later
proposal to add a direct transition between two non-Legacy modes requires
separate architectural review and qualification; state preservation alone does
not authorize expanding the transition graph.

State preservation is not state migration. This task does not presume that
onboard-VDP display assets become EDP assets, or vice versa. It must state what
survives in place, what becomes inactive or stale, what is discarded, and what
an aware application must rebuild for every transition.

[LINK-001](LINK-001.md) owns the v2 aspiration for a direct bidirectional
VDP/EDP link. Direct transfer of compatible display state and buffers is a
minimum aspirational use case if that link proceeds. MODE-001 must consume any
accepted link design but does not design the link, require it for Rev 1, or
presume that all processor state is transferable. No v1 state-preserving
transition may depend on direct VDP/EDP communication or state/buffer transfer.

## Work

M01-W01 [ ] Inventory every reset, restart, dispatcher, parser, queue, sysvar, callback,
   transport, and processor initialization effect used by the beta transition.
M01-W02 [ ] Produce a per-transition preservation matrix for eZ80 execution state,
   eZ80 RAM, MOS state, onboard-VDP state, EDP state, transport state, and
   externally visible application behavior.
M01-W03 [ ] Define a bounded quiescence protocol that stops new VDU/EDU work, drains or
   cancels owned operations, proves a safe boundary, and cannot deadlock the
   running application.
M01-W04 [ ] Determine whether Exclusive Compatible↔Exclusive Extended can change only
   transport machinery while preserving EDP device and asset state.
M01-W05 [ ] Define prepare, commit, rollback, timeout, failure reporting, and recovery
   when either source or destination cannot quiesce or initialize.
M01-W06 [ ] Define explicit application/operator consent and reporting for transitions
   that preserve eZ80 execution but clear, stale, or hide display-side state.
M01-W07 [ ] Build deterministic host tests, emulator tests where representative, and
   qualified bench tests for successful transitions, in-flight traffic,
   malformed traffic, timeouts, resets, unavailable processors, and rollback.
M01-W08 [ ] Determine which guarantees are safe for v1 and record every remaining
   requirement as mandatory v2 work.

## Gates

- PORT-008-D005 (accepted 2026-09-09) permits the bounded idle-CLI
  Legacy↔ExCom console increment without first implementing restart mediation.
  It preserves keyboard selection/layout with fresh destination screens and
  does not claim this task's broader application/display-state preservation.
  Other replacements of the restart-mediated fallback retain their review and
  qualification requirement.
- Consume the final SETUP-005 D002, D003, D007, and related ownership
  decisions rather than inventing transition-local alternatives.
- Do not implement transparent display-state migration without a separately
  reviewed representation, ownership, capacity, and compatibility design.
- A failed state-preserving attempt must leave the system no less recoverable
  than the accepted restart-mediated baseline.

## Completion criteria

1. Every formal transition has an accepted preservation and loss contract.
2. The eZ80 program/RAM survival guarantee and its exceptions are explicit.
3. Quiescence, commit, rollback, reset, timeout, and recovery are implemented
   and qualified against deterministic procedures.
4. VDP/EDP resident-state behavior is observable and documented without
   implying unimplemented migration.
5. The accepted v1 subset and mandatory v2 remainder are separately visible.
