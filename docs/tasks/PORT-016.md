# PORT-016 — Add MicroPython scripting to EDP

## State

- Status: Planned long-term capability; implementation deferred.
- Recorded: 2026-09-10
- Started: --
- Finished: --
- Release placement: Undecided; v1 remains possible, not promised.

## Intent

The Author requests MicroPython support within EDP on the ESP32-P4 as a
long-term project goal. The discussion arose from scripting repeatable
movement and firing events for a Nurples benchmark; that use is a potential
consumer, not the limit of the capability. The current performance
investigation does not depend on introducing an interpreter.

EDP would host the interpreter alongside its existing services. The current
EDP firmware does not include MicroPython. This records future integration
work, not authorization to replace the running firmware with a standalone
MicroPython image. EMOS retains ownership of Agon-facing transports, ordinary
VDU routing and committed operating mode.

The P4 DevKit's own microSD service is tracked separately in
[PORT-007](PORT-007.md). Plan script storage/loading against that service;
EMOS read access to the same card is a required storage capability independent
of MicroPython. Physical card availability is recorded in `HARDWARE.local.md`.

## Work when prioritized

1. Establish intended script uses and the EDP APIs exposed to scripts; decide
   script loading from P4 microSD, execution, stopping and error recovery.
2. Assess a supported MicroPython integration with the selected P4 toolchain,
   including memory and scheduling costs while UART, input and display
   services remain responsive. The official
   [embedding example](https://github.com/micropython/micropython/blob/master/examples/embedding/README.md)
   is a starting reference, not a selected implementation.
3. Present a minimal integration and validation scope, then settle whether it
   belongs in v1 or a later release before implementation.
