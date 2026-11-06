# Separate application progress from parallel transport qualification

- Status: Accepted
- Completeness: Complete
- Date: 2026-11-06
- Related task: NET-004

Smith selects one final parallel-pipe test for MechAgon. If that selected case
fails, MechAgon explicitly switches application networking back to the supported
UART1 carrier so renderer/application work can continue. This supersedes the
earlier parallel-only requirement for that application sequence. It does not
add an implicit fallback to `ext.netp` or reinterpret a failed transfer as sent.

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
