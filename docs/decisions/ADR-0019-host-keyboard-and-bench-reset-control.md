# ADR-0019 — Host keyboard input and independent bench reset

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-13
- Related task: REMOTE-002

The Author selected host-controlled typing over Ethernet through the P4's
existing native-keyboard delivery path. Host events have separate held state,
bounded queues, idempotent session requests and finite release/cancellation
behavior. Physical input takes precedence. EMOS remains the authority that
admits the input source and interprets stock key events.

The PC initiates automation; the P4 forwards admitted events through the
existing retained serializer. The P4 does not independently issue commands or
reset the mainboard. The mainboard may control the Extender, not the reverse.
Bench reset remains a Pi-controlled transistor pulling the mainboard reset
pin low, independent of P4 firmware and of the ZDI debug protocol.

This decision adds a host-tool input surface, not a remote shell/storage
command extension. Later [ADR-0022](ADR-0022-browser-keyboard-capture.md) defines
browser capture and arbitration over the same admitted input path. The current
[reset guide](../bench-reset.md) describes the Pi-backed browser control without
changing the physical reset owner. Original deployment and attended-review
authorization belongs to the dated REMOTE-002 record; this ADR grants no
standing permission to flash, reset or send demonstration input.
