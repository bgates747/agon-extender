# Separate application progress from parallel transport qualification

- Status: Accepted
- Completeness: Complete
- Date: 2026-11-07
- Related task: NET-004

The November 6 decision selected one final MechAgon parallel-pipe test, then an
explicit supported UART1 binding on failure so application work could continue.
This superseded the earlier parallel-only application requirement.

On November 7 Smith explicitly retains UART1 for MechAgon until further notice.
Smith and Extender will revisit this choice through their joint assessment of
parallel performance for smaller batches, if worthwhile. The separate measured
large-buffer gain does not authorize an application carrier migration. This
choice adds no implicit fallback to `ext.netp` and never reinterprets a failed
transfer as sent. [COMMS-002](../tasks/COMMS-002.md) owns the separate performance
investigation; this accepted carrier choice has no unresolved decision within
its declared scope.

Extender continues investigating the parallel carrier with its own bounded
fixtures. Extender prepares source and tests while consuming agents hold the
bench, and uses normally admitted bench intervals while those agents write
code. Actual custody, cleanup and source ownership remain required; there is
no simultaneous target access or preemption. MechAgon remains first priority,
then Wolf, without making application development wait on parallel repair.

EMOS continues owning transport admission, UART serialization, shared-pin
handover and ordinary VDU routing. The application explicitly selects its
carrier using a matched supported SDK/component combination. MechAgon owns
application integration; Extender owns reusable carrier/firmware changes and
independent qualification. Mainboard UART0 rendering remains separate from
network payload carriage. This decision claims no new installed combination,
successful test, physical diagnosis or production acceptance.
