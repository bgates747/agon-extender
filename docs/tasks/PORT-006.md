# PORT-006 — Implement the Extender network foundation and update service

## State

- Status: Keyboard transport plan accepted for freeze, 2026-09-08. Earlier browser-video bench path accepted; initial-tranche resilience
  item 6 remains open.
- Started: 2026-08-27 19:13 EDT
- Finished: --

## Current priority — focused keyboard transport

The next tranche supports REMOTE-001's browser keyboard session over existing
wired networking. Documentation is accepted for freeze; implementation has not
started. Keep P4 UART keyboard packets stock-compatible: network event/session
encoding terminates on P4 and is not copied as a new UART envelope.

1. [ ] Define a bounded input endpoint and session ownership, with explicit
   opt-in/admission, Origin/cross-site checks and revocation for the selected
   bench scope. Focus gates key capture but does not authenticate a client.
   Retain the existing service's broader-exposure restrictions. Enforce
   REMOTE-001 K004: one controlling browser, explicit takeover, old-session
   revocation and held-key release before new input, with stale events rejected.
   Viewing alone does not grant keyboard control.
2. [ ] Deliver ordered browser event messages to PORT-005 through REMOTE-001's
   interface. Bound size, queueing, backpressure, disconnect and stale-session
   handling while browser video is active; notify release/revocation reliably.
3. [ ] Keep keyboard semantics in REMOTE-001/PORT-005 and EMOS source authority
   in SETUP-005/INTEG-009. Do not turn this endpoint into a structured remote
   command/update service or require Wi-Fi/OTA completion first.
4. [ ] Test the affected connection and failure paths, including applicable
   F003/F012 containment. The earlier video tranche remains evidence, not a
   proof that a writable input endpoint is already authorized or implemented.

The full network/update roadmap below remains later work. This keyboard slice
has priority over its unrelated services.

## Intent

Implement the project-owned Extender networking layer. Native wired Ethernet
on the P4 DevKit is the primary Rev 1 backend. The Olimex MOD-WIFI-ESP8266 on
the Extender's dedicated header is an optional Rev 1 backend implemented
through an explicitly selected P4-to-module protocol and module-firmware
contract.

Provide common services required by browser video/audio, status and management,
and safe network firmware updates without inheriting the dormant vdp-gl ICMP
helper or the defective stock VDP serial updater transaction.

The Author selected the P4/EDP itself as the HTTP and browser-video endpoint.
The P4 serves its own browser assets and media endpoint through the DevKit's
onboard Ethernet; no Pi or external web server is a product runtime dependency.
The accepted first-tranche boundary assigns Ethernet, addressing, HTTP,
connection lifecycle, and generic bounded network backpressure to PORT-006.
PORT-003 owns framebuffer handoff, video framing and encoding, browser assets,
presentation code, and video-specific diagnostics. PORT-006 treats video as
opaque bytes; PORT-003 does not control Ethernet hardware. OTA, optional Wi-Fi,
management, and unrelated network services remain outside this tranche.

For the new keyboard slice, PORT-003 retains video/presentation ownership in
the shared browser page; REMOTE-001 owns its keyboard event and focus controls.
PORT-006 supplies their bounded network connection. Full display-backend
completion is not a prerequisite for adding input to the existing page.

The first bench tranche uses ordinary DHCP. The router's existing MAC-based
reservation is expected to supply the stable bench address, but firmware does
not embed it and reports link and lease state through USB serial diagnostics.
Friendly-name discovery, persisted user configuration, and multi-device naming
are deferred beyond the first forward test.

## Authority and inputs

Under PORT-008-D003, the browser/network service is a dependency only for r02
stages that actually select it as an observation or application path. Power,
bias, and isolated UART/parallel checks may keep it inactive and use their
reviewed direct evidence method under the
[staged process](../qualification/staged-circuit-validation.md). These checks
do not qualify network behavior or close this task's resilience findings.

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

## Initial browser-video tranche

This accepted tranche is the only PORT-006 work on the immediate critical
path. It supports PORT-003 Phase F without prematurely absorbing the remainder
of PORT-006. The Author accepted the joint Phase F plan on 2026-08-27.

1. [x] Freeze the opaque network-service API, DHCP/link lifecycle, one-client
   WebSocket credit boundary, diagnostics, failure behavior, exact ESP-IDF
   authorities, and exclusions before implementation.
2. [x] Reconcile the legacy hardware-qualified Ethernet/HTTP proof with the
   pinned current Olimex board, ESP-IDF 5.5.5, and P4 build. Reuse current
   maintained facilities and exact board facts; do not copy example-only
   configuration machinery into product code without review.
3. [x] Implement ordinary DHCP and observed link/lease reporting for the
   onboard Ethernet. The router reservation may produce the stable bench
   address, but no address enters firmware.
4. [x] Implement embedded static-asset HTTP routes and one video WebSocket
   connection. Accept and transport opaque immutable buffers through a bounded
   interface; do not include pixel or VDP semantics in PORT-006.
5. [x] Implement one outstanding client credit, send completion, disconnect
   cleanup, second-client refusal, and bounded error reporting. Never call
   PORT-003 from an Ethernet callback while holding network-internal locks.
6. [ ] Run host/state tests where separable and pinned-P4 compile/link tests.
   Confirm absent browser, failed DHCP, link loss, malformed client messages,
   slow sends, reconnect, and repeated server lifecycle cannot create an
   unbounded queue or block logical VDP execution.
7. [x] After the joint predeployment gate is approved, qualify DHCP, direct P4
   asset serving, one WebSocket client, disconnect/reconnect, and USB serial
   diagnostics on the named bench. Do not expose the test service to the public
   internet or claim production security.
8. [x] Return accepted evidence to PORT-003 Gate F, then pause PORT-006. Wi-Fi,
   audio transport, OTA, status/management, authentication, discovery, and
   broader qualification remain in this task for later tranches.

### Initial-tranche execution record

1. Item 1 is frozen in
   `docs/tasks/PORT-003/phase-f/network-service-contract.yaml`, beside the joint
   implementation that consumes it. The contract selects the maintained
   Arduino-ESP32 3.3.11 `ETH`/`Network` wrapper for explicit IP101/RMII startup
   and DHCP events, ESP-IDF 5.5.5 `esp_http_server` for HTTP/WebSocket work, and
   a fixed two-segment opaque lease API. It records the DevKit's ten active
   Ethernet GPIO roles, six embedded routes, one client and credit, exact
   actor/task ownership, reconnect cleanup, USB diagnostics, and trusted-bench-
   LAN security boundary. The deterministic validator passes without exposing
   machine-local values.
2. Item 2 reconciled the legacy `NET-00` and `NET-01` evidence rather than
   importing their examples. Those runs physically qualified the same Olimex
   Rev D1 IP101GRR path with ESP-IDF 5.5.5: explicit PHY address 1, MDC GPIO31,
   MDIO GPIO52, reset GPIO51, external RMII clock input, DHCP, ping, and direct
   HTTP all passed. The later legacy AGM/browser service proved feasibility but
   retained fixed addressing, fixed video dimensions, mutable globals, and
   example-specific ownership that do not satisfy the current contract.
   Current code therefore uses the maintained Arduino-ESP32 3.3.11 `ETH` event
   wrapper and ESP-IDF 5.5.5 HTTP server directly, with current project-owned
   lifecycle and bounded ownership.
3. Item 3 added `wired_network_service.hpp/.cpp`. The P4 setup owner starts a
   dedicated PORT-006 worker, registers a bounded Arduino network-event
   callback, and explicitly starts the onboard IP101/RMII wiring. Arduino's
   event task only records coalesced state and wakes the worker. The worker
   queries current `ETH` state, starts or stops HTTP idempotently, and reports
   observed link, IPv4 lease, netmask, gateway, and DNS through ESP logging.
   No address, reservation, or machine-local network value is compiled in.
4. Item 4 added six direct ESP-IDF HTTP routes: five immutable browser assets
   embedded by the application component and one WebSocket endpoint. The
   generic network code accepts a fixed two-segment opaque lease and never
   parses EVF1. `browser_video_provider.hpp/.cpp` is the sole PORT-003 bridge;
   it owns one snapshot lease and emits the exact 32-byte header plus immutable
   RGB888 payload.
5. Item 5 added `browser_video_service_core.hpp/.cpp` and the target adapter.
   One post-handshake client, one exact `frame` credit, one lease, and one
   queued HTTP-task send are the complete bounded state. A second client is
   refused with WebSocket 1013; malformed or duplicate credit closes with
   1002. Completion and socket-close paths release leases as sent, failed, or
   disconnected. Provider acquisition and release callbacks occur outside the
   short state mutex, and Ethernet callbacks never call the provider.

   Sanitized host tests pass second-client refusal, duplicate credit, pending
   credit with no new generation, exact header/payload segmentation, send
   completion, failure, disconnect, reconnect, and metrics. The
   `p4-network-service` diagnostic compiles and links against the pinned 360
   MHz P4 profile, Arduino-ESP32 3.3.11, and ESP-IDF 5.5.5. Its ELF contains all
   five embedded asset bounds and the network/provider service symbols. This
   diagnostic publishes no frames and is not a bootable retained-VDP image.

   Target integration exposed two build-system gotchas. PlatformIO had rebuilt
   its private environment while leaving a stale Arduino 2.0.14 package; the
   normal pinned environment package installation restored 3.3.11. Also,
   PlatformIO's generic text-embedding hook generated but did not link asset
   objects in this Arduino/ESP-IDF hybrid. `pio/select_sources.py` now renders
   the tracked source manifest's `embedded_text_files` through ESP-IDF's native
   application-component `EMBED_TXTFILES` facility. This keeps one tracked
   owner and avoids a hand-maintained linker workaround.
6. Item 6 remains open. Sanitized service-core tests and the pinned P4
   compile/link closure cover bounded malformed-client, slow-send,
   disconnect/reconnect, repeated-client, and absent-client behavior. Explicit
   failed-DHCP and physical link-loss recovery have not yet been exercised, so
   no broader PORT-006 resilience claim is made.
7. Item 7 passed in run `PORT-003-2026-08-28-15-28-59Z`. The exact P4 image
   acquired DHCP, served all committed assets and EVF1 frames directly,
   handled disconnect/reconnect, emitted continuing USB diagnostics, and
   remained stable through one warm-up and five measured client cycles on the
   trusted bench LAN.
8. The Author accepted that evidence at PORT-003 Gate F on 2026-08-28. The
   initial browser-video path is returned and PORT-006 pauses here. Item 6 and
   the later Wi-Fi, audio, OTA, management, authentication, discovery, and
   broader network tranches remain open.

## Accepted REMED-002 findings

The Author accepted the PORT-006 dispositions in
[REMED-002](REMED-002.md). The detailed evidence and upstream/local provenance
remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).

1. [ ] **F003:** Prevent a positive short TCP write from being accepted as a
   complete WebSocket frame. Use a defensive adapter or a pinned, re-audited
   upstream correction; preserve the immutable snapshot lease until the entire
   declared frame is transmitted or the connection is failed. Fault-inject
   short writes, congestion, disconnect, and retry. PORT-003 owns the
   browser-frame regression half of this split.
2. [ ] **F012:** Retain the live ESP-IDF HTTP server handle and callback
   ownership across failed stop and URI-registration rollback paths. Define
   retry and destruction behavior and fault-inject every partial-start and
   failed-stop path, including prevention of duplicate server instances and
   callbacks into a destroyed service.
3. [ ] **R003 dependency:** Before REMOTE-001 enables remote input or commands,
   define the authentication, Origin, cross-site WebSocket, privileged-service
   exposure, session-presence, and revocation contract. Do not reinterpret the
   accepted trusted-bench-LAN browser boundary as a remote-control security
   claim.

An upstream ESP-IDF origin for F003 or documentation inconsistency for F012
does not defer the local product containment. Any upstream-report task split is
pending REMED-002-D002.
