# Agon controller viewer in mode20

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-24
- Related task: [INPUT-001](../tasks/INPUT-001.md)

The first target-side controller viewer is an Agon/eZ80 application in mode20.
The Author permits AgonDev C++ for this application. This selects the viewer
processor, presentation and application toolchain; it does not select a new
EMOS controller API or establish a working end-to-end controller connection.

## Decision

1. Agon runs the viewer in512×384/64colours, showing both sticks, separate
   analog triggers, buttons, D-pad and observed press counts with readable text.
2. The application uses ordinary EMOS-owned display routing and the established
   appliance mode lifecycle. It switches only when necessary, allows monitor
   settling and restores a visible CLI. Escape exits; Alt-Tab does not exit.
3. The application may use AgonDev C++; this is not permission to change an
   EMOS firmware toolchain, bypass its gateway or access hardware directly.
4. Recorded-input visual review is explicitly labelled. It cannot establish
   Oryx→P4→Agon delivery, target timing or controller-loss behavior.

## Consequences

The standalone UI can be compiled and reviewed before the live EMOS service is
implemented. The [appliance source/guide](../../tests/fixtures/controller/README.md)
owns that bounded build. INPUT-001 retains the EMOS read/edge-consumption
decision and physical validation. The [LAN decision](ADR-2026-10-24-controller-udp.md)
continues to govern Oryx→P4; that LAN envelope is not an application ABI.
