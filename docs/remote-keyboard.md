# Host-controlled keyboard input

This accepted contract is under implementation in REMOTE-002; it does not
describe an endpoint already present in the installed firmware.

The PC sends bounded, numbered keyboard requests to the P4 over Ethernet. A
separate automation input source joins the existing processed-key path after
USB acquisition. The P4 console owner uses the retained stock-compatible
serializer and existing UART1 wiring. EMOS admits the Extender keyboard source
and owns the keyboard map, sysvars and normal application/CLI behavior.

The physical USB keyboard remains available. Automation starts only while it
is neutral; a physical press cancels remote input and takes precedence. Remote
held keys, cancellation and disconnect releases are source-specific. Requests
are paced, bounded and idempotent within their admitted session; stale sessions
and conflicting duplicates are rejected. Layout/admission loss invalidates the
session. The host reports the difference between request acceptance, UART
emission and separately observed eZ80 command/application completion.

The network handler enqueues input; it never writes UART or MOS memory. This
does not restore browser keyboard focus/leases, add a remote shell to the SD
wire API, or grant the P4 independent mainboard-control authority. The PC is
the initiating operator. Ordinary application commands execute through MOS.

Bench reset is independent: the Pi drives the existing transistor actuator to
pull the mainboard reset signal low. The Extender does not reset the mainboard.
The Author may authorize unattended fixture commands and resets; the live
review demonstration remains gated by the requested spoken alert and chat reply.
