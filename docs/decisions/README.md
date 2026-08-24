# Architecture decision records

Architecture decision records (ADRs) preserve accepted project architecture
and its rationale. Open questions and actionable work remain in the
authoritative `TODO.md` and corresponding files under `docs/tasks/`.

## Required metadata

Every ADR begins with these fields immediately below its title:

```markdown
- Status: Accepted
- Completeness: Complete
- Date: YYYY-MM-DD
```

Add `Related task` when a task owns the decision. An ADR with partial
completeness must also name its authoritative tracker:

```markdown
- Open-decision tracker: SETUP-NNN
```

## Status

- **Proposed:** presented for review but not authoritative.
- **Accepted:** authoritative current architecture.
- **Rejected:** considered and explicitly declined.
- **Superseded:** no longer authoritative; the ADR identifies its replacement.

Status describes the authority of decisions already recorded. Qualification,
implementation, and testing state do not change an accepted decision's status;
record those separately in its task and evidence.

## Completeness

- **Partial:** accepted decisions exist, but known architectural decisions
  remain unresolved inside the ADR's declared scope.
- **Complete:** no known architectural decisions remain unresolved inside the
  declared scope.

Complete does not mean immutable, implemented, tested, or eternally final. New
evidence may amend or supersede any ADR. Partial ADRs contain only accepted
decisions and link to a task that owns the unresolved questions; they do not
duplicate open questions or actionable checklists.

When the final tracked question is resolved, incorporate the accepted result,
change completeness to `Complete`, and update the task and development log.

## Design audit records

Files named `AUDIT-YYYY-MM-DD-NNN-<subject>.md` record a bounded review of
current architecture, tasks, implementation, generated data, and evidence.
They identify contradictions, omissions, stale assumptions, and affected
authorities without making new architecture authoritative merely by finding a
problem.

Every audit begins with `Status`, `Date`, `Trigger`, `Scope`, and `Owning task`.
Findings use stable IDs and record severity, observed state, required
disposition, and affected artifacts. Status is `In progress` while coverage is
being gathered and `Complete` when the declared scope has been reviewed and
every finding has an owner or explicit deferral.

Accepted architectural corrections are promoted into the applicable ADR and
normative architecture document. Actionable work remains in the owning tracked
task and `TODO.md`; generated outputs are regenerated from their corrected
authorities. An audit is evidence and a correction map, never a competing
architecture specification or task list.
