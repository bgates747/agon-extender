# INPUT-001 — PC game controllers over Extender's network input path

Connect a controller to an external PC such as Oryx, use its operating-system
controller support, and send axes/buttons to Extender over the existing network
control infrastructure. Preserve analogue input through to the application.
Direct P4-PC USB HID troubleshooting is outside this work.

## Origin and ownership

Fsim motivates this capability, but the generally applicable PC-controller
bridge and Extender service belong to agon-extender. The Author transferred
this full task here on2026-10-14 for Extender to register in its own TODO.
Fsim-specific mappings and consumer changes remain separate consumer work.

## State

- Status: Eventual — new task/design recorded; transport ownership review needed
- Started: --
- Finished: --
- Authority: Author requests a new game-controller task, 2026-10-14, selecting
  external-PC capture and HTTP delivery to P4 instead of direct P4 USB.

## Proposed path and ownership

Controller → PC HID/controller stack → PC capture bridge → HTTP P4 endpoint →
bounded controller-state owner → agreed P4/Agon interface → consuming application.

Extender owns reusable HTTP admission/session handling, P4 state storage and the
P4-to-mainboard interface. The agon-fsim project can own the flight-controller mapping,
pygame prototype and fsim consumer. Coordinate that boundary before implementation;
do not edit Extender's working tree or silently create a private competing ABI.
No Extender message or request has been sent by this task-registration action.

Prior art read locally: Extender `docs/decisions/ADR-0022-browser-keyboard-capture.md`
specifies explicit browser ownership, release/reconnect behavior and keyboard
WebSocket delivery. `scripts/keyboard.py` uses HTTP `/keyboard/status` and
`/keyboard/rpc` for host automation. Neither proves that analogue controller
state is already supported. Reuse the network/server mechanisms, not keyboard
event payloads or reserved keycodes to disguise axis values.

## Stable subtasks

1. [ ] **IN001-01** Review the current Extender production/network-input contracts
   with its owner. Establish reusable generic-controller endpoint, admission,
   session/owner and P4/Agon delivery contracts. Identify required Extender/EMOS
   work separately from fsim; record agreed responsibilities and target gates.
   No direct USB HID fixes or firmware changes merely to register this task.
2. [ ] **IN001-02** Prototype PC capture on Oryx using a maintained OS-backed
   controller library (existing pygame/SDL is a natural first candidate). Audit
   browser capture as an optional frontend if it supports the needed devices;
   browser availability must not be assumed equivalent to native HID support.
   Enumerate/select controllers by stable identity, support hotplug and inspect
   actual axes/buttons/hats without requiring guessed mappings. Expose a readable
   configuration for mapping, inversion, calibration, dead zones and sensitivity.
3. [ ] **IN001-03** Define bounded, versioned input messages: controller/session
   identity, monotonic sequence, signed normalized axis values, button state and
   ordered button transitions as required. Distinguish centered sticks from
   unipolar triggers/throttles. Keep values integer on the wire. Establish
   supported device/count limits, reconnect behavior and rejection of stale/
   displaced-owner data; do not let a queued old input replay after reconnection.
4. [ ] **IN001-04** Implement the approved PC HTTP bridge with connection reuse,
   bounded queues, latest-state coalescing for axes and heartbeat. Select and
   measure a practical update rate against the30Hz physics consumer rather than
   flooding the server with one request per raw HID event. Preserve short button
   presses through ordered events/latches; coalescing axis snapshots alone must
   not lose an entire press/release between packets. Avoid blocking PC input or
   the P4 render owner on slow network I/O.
5. [ ] **IN001-05** Define and test loss behavior: unplug, bridge exit/crash,
   network stall, timeout, server restart and ownership transfer. Release held
   buttons and prevent indefinitely stuck surface commands. Recommend neutral
   centered control axes plus an explicit lost-input indication; separately
   decide whether fsim pauses and whether throttle holds its last setting.
   Do not interpret zero throttle as “neutral” or silently cut power on loss.
   Require deliberate rearming/calibrated reacquisition before resuming control.
6. [ ] **IN001-06** Prototype fsim mapping in pygame: analogue elevator/aileron/
   rudder and throttle where hardware provides them; configurable buttons for
   existing pause/reset functions. Retain keyboard operation and current flight
   dynamics. Resolve keyboard/controller arbitration explicitly: absolute stick
   input must not compete with retained incremental keyboard positions. Surface
   indicators must show actual applied values. Provide a playable Oryx review
   and stop for Author handling/loss-policy acceptance.
7. [ ] **IN001-07** After approved contracts and host acceptance, register/promote
   separate reusable Extender and fsim target counterparts. Specify the actual
   bounded P4-to-eZ80 controller API; HTTP delivery to P4 alone is not end-to-end
   Agon input. Preserve explicit operator route selection and existing keyboard
   services. Measure UART packet/poll costs; no per-axis expensive remote math.
8. [ ] **IN001-08** Qualify end-to-end physical input after fresh handoff: latency,
   jitter, stale-sample age, delivered rate, button loss, reconnect and safe loss
   behavior under the full cockpit/rendering/file-loading workload. Compare full
   game-loop FPS/input responsiveness with keyboard baseline on the same route.
   Publish supported-device/config/run instructions and record Author acceptance.

## Constraints and acceptance

1. Target uses the external PC's controller stack. P4 receives logical inputs,
   not USB traffic or raw device-specific HID descriptors.
2. Preserve analogue values; synthetic keyboard-only controller emulation may
   serve an explicitly selected compatibility mode but is not the primary goal.
3. Keep generic controller transport distinct from flight-specific mapping and
   physics. Keyboard admission/ownership is prior art, not permission to revoke
   unrelated inputs without an explicit controller-arbitration contract.
4. Use existing project ownership, pinned builds and fresh hardware handoffs.
   No network discovery recipes, private host identities or endpoints are copied
   into this task. Canonical connection guides remain authoritative.
5. Host prototype first, target counterparts second. Emulator checks can prove
   interfaces, not physical latency or sustainable performance. Generated logs,
   captures and diagnostic artifacts stay ignored; retain reusable tools/tests.

## Dependencies and exit

Current accepted fsim controls/30Hz flight model and Extender network keyboard
infrastructure supply input contracts to research. This does not depend on
TERRAIN-015/016 and does not authorize their execution. Current AIRPORT-003
cockpit is the candidate fsim review surface; its hardware gate is independent.
Exit requires approved ownership/protocol, Author-accepted host controller
mapping and separately qualified end-to-end target support. Task registration
does not select firmware, modify Extender or reserve the bench.
