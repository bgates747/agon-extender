# Use Eirene as the future EMOS foundation

- Status: Accepted
- Completeness: Partial
- Date: 2026-11-04
- Related task: EMOS-001
- Unresolved decision tracker: [EMOS-001](../tasks/EMOS-001.md)

## Decision

The Author selects Eirene as the future base for Extender MOS, including its
asynchronous UART and OTIRX improvements. EMOS remains the complete
backward-compatible MOS replacement and retains ownership of ordinary VDU
routing, Extender transports, activation and committed mode. Existing unaware
applications retain synchronous output ordering and source-lifetime behavior;
asynchronous operation is explicit under the selected integration contract.

## Rationale and boundaries

Reuse the maintained Eirene foundation and UART innovations while preserving
EMOS integration and minimizing resident eZ80 flash, RAM and processor cost.
Keep policy and diagnostic algorithms in applications/utilities where practical.

This records the base direction, not an implemented rebase, selected async ABI,
UART1 qualification or approval to replace installed firmware. The task owns
integration choices and migration gates. Runtime RST hooks remain a separate
possible experiment. Current production/component selections, frozen evidence
and rollback identities remain unchanged.
