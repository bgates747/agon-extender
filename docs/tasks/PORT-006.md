# PORT-006 — Implement the Extender network foundation and update service

## State

- Status: Not started — registered from SETUP-004 Work 1.g
- Started: --
- Finished: --

## Intent

Implement the project-owned Extender networking layer. Native wired Ethernet
on the P4 DevKit is the primary Rev 1 backend. The Olimex MOD-WIFI-ESP8266 on
the Extender's dedicated header is an optional Rev 1 backend implemented
through an explicitly selected P4-to-module protocol and module-firmware
contract.

Provide common services required by browser video/audio, status and management,
and safe network firmware updates without inheriting the dormant vdp-gl ICMP
helper or the defective stock VDP serial updater transaction.

## Authority and inputs

- [SETUP-004 Work 1.g](SETUP-004.md#work-1g-execution-record) and its generated
  network/transfer inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decision 29.
- [ADR-0007](../decisions/ADR-0007-flash-partition-strategy.md).
- [Current architecture](../architecture.md).
- [PORT-003 display backend](PORT-003.md) and
  [PORT-004 audio scheduler](PORT-004.md).
- [PORT-002 source-selection work](PORT-002.md).

## Required outcomes

1. Define a project-owned network-service boundary that does not couple video,
   audio, update, status, or future file services directly to one physical
   network backend.
2. Bring up and qualify the P4 DevKit's native wired Ethernet as the primary
   Rev 1 backend, including addressing, link-state, reconnect, DNS, throughput,
   concurrency, and failure behavior.
3. Select and document the MOD-WIFI-ESP8266 module firmware and P4-to-module
   protocol; implement and qualify the optional dedicated-header backend
   without assuming that P4-local Arduino WiFi or lwIP APIs control it.
4. Supply the browser-facing transport used by PORT-003 and PORT-004, with
   bounded buffering and backpressure that cannot redefine logical video or
   audio state.
5. Implement status and management services with explicit authentication,
   authorization, exposure, and recovery policy.
6. Implement a network update transaction over the retained ESP-IDF OTA,
   image-validation, rollback, boot-partition, and restart substrate. Define
   image authenticity/integrity, authorization, progress, interruption,
   power-loss, rollback, and user-visible failure behavior.
7. Keep the stock serial updater, Intel HEX/YMODEM maintenance bridge, and
   dormant vdp-gl ICMP helper excluded from the P4 build. Add project-owned
   diagnostics only when a product or qualification requirement selects them.
8. Add deterministic host tests where practical and qualified target tests for
   each backend and service under disconnect, reconnect, congestion, malformed
   input, interrupted update, and concurrent media traffic.

## Dependencies and gates

- Complete SETUP-004 before implementation so storage/filesystem boundaries are
  settled.
- PORT-002 must represent the omitted upstream network and maintenance sources
  and the selected project-owned closure.
- QUAL-001 must retain network/browser/update qualification as secondary
  product-capability evidence that cannot satisfy stock-compatibility rows by
  itself.
- Work with the Author to select the ESP8266 host protocol and module firmware
  before implementing that backend; do not infer an AT command set or custom
  module image from the hardware alone.
- Define the service, security, buffering, and qualification design before
  writing production network or updater code.
