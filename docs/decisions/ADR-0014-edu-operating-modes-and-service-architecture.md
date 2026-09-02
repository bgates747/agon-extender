# ADR-0014 — EDU operating modes, state ownership, and service architecture

- Status: Accepted
- Completeness: Partial
- Date: 2026-08-20
- Last amended: 2026-09-01
- Related tasks: SETUP-004, SETUP-005
- Open-decision tracker: SETUP-005

## Context

Extender needs an application-facing command path distinct from the stock VDU
path. Applications may link an EDU client binding for convenient synchronous
calls, but Extender requires EMOS to own activation, transport, lifecycle, and
shared state. Persistent or asynchronous facilities may additionally require
eZ80-side code that remains resident after its installer or original caller
exits.

Potential resident responsibilities include persistent Extender session and
configuration state, ownership of transport hardware and interrupt handling,
reception and routing of asynchronous UART traffic from the P4, buffering, and
coordination of background network, storage, or media services. Applications
that only issue synchronous foreground requests should not be forced to install
or depend upon such a service.

Legacy planning established that the documented MOS interrupt-vector machinery
does not replace the fixed low-ROM `RST.LIL 10h` and `RST.LIL 18h` VDU paths.
It also found no implemented TSR to carry forward. An ordinary MOSlet is loaded
into reusable memory and therefore does not by itself provide a safe resident
lifecycle. MOS modules remain a proposed rather than presently available
mechanism.

Stock VDP queries return protocol packets that MOS translates into canonical
sysvars and completion flags. If both the onboard VDP and EDP attempted to own
those fields, responses could race, overwrite one another, or describe
different device state. Full binary compatibility therefore requires exclusive
ownership of the stock-compatible command and response path, while simultaneous
use of both processors requires separate state domains.

The two P4-exclusive operating modes share one asymmetric ownership model. All
applications, whether EDU-aware or not, use the EDP for audio and video output.
The onboard VDP remains the physical keyboard and mouse controller, but
Extender becomes the logical compatibility gateway for its input. MOS must
observe one coherent stream of stock-compatible responses and input events and
update its canonical sysvars accordingly. Extender controls that logical
stream; MOS should continue to own and mechanically update its own sysvars
wherever the selected routing mechanism permits reuse of the stock parser.

Untouched legacy applications reach VDU output through fixed low-ROM restart
handlers. A normal resident service cannot replace those handlers through MOS's
documented interrupt-vector API. Hardware interposition could provide complete
transport control but would impose board modification or additional switching
hardware. The accepted EMOS direction instead preserves the restart entry
points and selects one committed backend through the routines behind them.
Exact response delivery, parser integration, transition-carrier mechanics,
remaining activation/lifecycle implementation, and qualification remain in the
linked open-decision tracker.

Not every VDU command that produces output participates in the VDP response
protocol. Buffered command 128 is an operator diagnostic: official VDP
`v2.16.0` writes buffer information directly to its local debug serial console,
returns no packet to MOS, and updates no sysvar. Diagnostic output therefore
needs its own ownership boundary distinct from VDU responses, EDU results,
network media output, and application-visible state.

Official printer/USB-serial output, console and terminal modes, ZDI, Intel HEX,
YMODEM, firmware updating, and local debug output are maintenance or operator
facilities rather than the normal application-facing audio/video contract.
Extender v1 does not implement those facilities. They remain available through
the onboard VDP whenever the selected operating mode leaves ordinary VDU with
that processor.

## Decision

1. Adopt **Extended Display Unit (EDU)** as the official project term for the
   Extender facility exposed to eZ80 software, including its command set and
   application-facing API.
2. Adopt **Extended Display Processor (EDP)** as the official project term for
   the ESP32-P4 processor and firmware that execute Extender display and service
   operations.
3. Define EDU as a stable, versioned application-facing API whose contract is
   independent of the application language or linked client binding. Every
   binding invokes EMOS; application code does not become a substitute
   transport or lifecycle owner.
4. Make optional resident EDU facilities explicit and opt-in. Their absence
   must not alter EMOS Legacy behavior, the onboard VDP, or ordinary VDU.
5. Require applications to discover and explicitly open EDU through EMOS before
   using it. Missing EMOS support, absence, or incompatibility must be reported
   cleanly rather than causing implicit interception or partial activation.
6. Permit directly linked EDU client code only as an application-facing EMOS
   binding for synchronous foreground operations. It may not activate EDP,
   claim transport hardware, install a private persistent receiver, or operate
   Extender independently of EMOS.
7. Make EMOS own persistent activation, interrupt servicing, shared transport
   state, queues, and lifecycle. Optional resident facilities may provide
   capabilities or work that survive an initiating call or program, but remain
   subordinate to EMOS ownership and arbitration.
8. Keep application-visible EDU operations consistent across linked bindings
   and optional resident facilities. At minimum, the eventual EMOS API must
   cover service discovery, session open and close, block transfer, and
   reception or polling.
9. Make EMOS the only supported authority that may redirect ordinary VDU,
   claim Extender transport hardware, or change committed mode. No application,
   linked client, TSR, MOS Module, or resident service may do so except through
   an explicit documented EMOS operation. This is a supported-software contract,
   not a security claim against deliberate unrestricted eZ80 register or GPIO
   manipulation.
10. Keep transport and resident-program mechanics behind the EMOS-owned EDU
    API. A future upstream MOS or MOS Modules integration may replace internal
    ownership machinery without requiring EDU applications to adopt a
    different application protocol.
11. Define **Exclusive Compatible mode** as selection of the EDP as the
    authoritative audio/video processor and compatibility interface over the
    stock VDP UART transport contract. The EDP owns stock-compatible command
    processing and supplies the corresponding response stream. MOS retains
    ownership of canonical VDP sysvar storage, completion flags, and the
    mechanism that updates them; neither the EDP nor an application or resident
    service may write that MOS-owned state directly.
12. Permit Exclusive Compatible and Exclusive Extended modes to claim complete
    compatibility for the declared normal application-facing surface only
    after ordinary legacy VDU traffic and responses can be routed
    transparently. Explicitly exclude the v1 maintenance/operator carve-outs
    named in the Context from that claim unless a later accepted decision
    restores them.
13. Define **Dual mode** as simultaneous, explicitly addressed
    use of the onboard VDP through VDU and the EDP through EDU. The processors
    may perform coordinated work, but their command and response channels
    remain distinguishable.
14. Give VDU and the onboard VDP exclusive ownership of canonical MOS VDP
    sysvars in Dual mode. EDU must retain EDP results in EDU-owned registers,
    structures, flags, queues, or resident-service state and must not
    impersonate a MOS VDP response.
15. Do not guarantee arbitrary unmodified legacy software in Dual mode.
    Project-owned wrappers and abstraction layers may operate one or both
    processors on behalf of software that is not itself EDU-aware, but each
    supported compatibility profile requires explicit qualification.
16. Never mirror ordinary application VDU traffic to both processors. Legacy
    and Dual route it only to the onboard VDP; both exclusive modes route it
    only to the EDP. Targeted private input/bootstrap control, recovery
    diagnostics, and separately identified qualification traffic are not
    mirrored application output. Divergent state and competing return packets
    make ordinary-VDU duplication unsafe and outside the supported architecture.
17. Require EMOS for every active Extender mode, including Dual. EMOS alone
    activates EDP, owns the EDU transport and result/event ingress, arbitrates
    clients, and commits the EDP-service plane. A linked client is only an EMOS
    API binding.
18. Limit stock MOS to Legacy operation. If EMOS is absent, Extender is outside
    the supported system and an Extender-specific command or API may fail as
    unavailable without changing stock behavior. Direct application ownership
    of Extender hardware under stock MOS is explicitly out of scope.
19. Do not implement the upstream local USB/UART maintenance and operator
    facilities in Extender v1, including printer output, console/terminal
    modes, ZDI, Intel HEX, YMODEM, firmware updating, and buffered-command debug
    output. Handling attempts is mode-contract dependent: strict compatibility
    preserves stock-observable behavior, including undesirable failures, while
    non-strict operation should improve failure and recovery. Exact behavior
    and the strict-mode boundary remain in the linked task rather than this ADR.
20. Define **Legacy mode** as the stock-machine mode in which Extender is
    electrically and logically absent from the Agon interface even when it is
    connected and powered. The onboard VDP owns ordinary VDU, responses,
    sysvars, input, and maintenance facilities without Extender interception.
21. In Dual mode, ordinary VDU continues to reach the onboard VDP, so its
    maintenance facilities may remain available through that stock path. Their
    availability does not make them Extender-supported features.
22. Retain the stock RTC command and state surface in both exclusive modes with
    as much fidelity as practical: `VDU 23,0,&87`, its
    six-byte packed payload and eight-octet response frame, RTC-backed VDP
    variables, and packet callbacks. Canonical RTC sysvar effects require the
    selected response to reach a MOS-owned parser; this decision grants the EDP
    no ownership of MOS memory. The strict-mode requirement is independently
    sufficient to retain this surface.
23. Use explicit aware-application input forwarding for the proof of concept.
    An EDU-aware eZ80 program reads processed keyboard and mouse input through
    the stock onboard VDP path and injects the events into the EDP through EDU.
    Injection updates EDP-local state and behavior and does not automatically
    emit the same stock input packets back to the forwarding application. This
    profile does not transparently support untouched applications and does not
    settle the more automatic input route that v1 may adopt.
24. Keep physical keyboard and mouse ownership on the onboard VDP through v1.
    V1 adds no P4-owned peripheral hardware beyond facilities already present
    on the selected P4 DevKit; any additional input hardware is post-v1 work.
25. Define **Exclusive Extended mode** as selection of the EDP as the same
    exclusive compatibility authority established for Exclusive Compatible
    mode, but with the eight-bit parallel Agon-to-EDP command path and the
    enhanced UART return contract. Transport enhancement does not reduce the
    EDP's logical reach into MOS-owned parser effects, completion flags,
    sysvars, restart routing, input integration, or related eZ80 state. Exact
    enhanced reverse capabilities remain open in SETUP-005.
26. Make **Exclusive Compatible mode**, **Exclusive Extended mode**, and
    **Dual mode** the formal names. “Compatible” and “Extended” are permitted
    short forms only where operating-mode context is unambiguous; “Exclusive”
    remains part of each exclusive mode's official name. Retain **Legacy mode**
    for the state in which an attached Extender is inactive and
    indistinguishable from absence.
27. Distinguish an application's entry point from the selected destination.
    `RST.LIL 10h`, `RST.LIL 18h`, and their C-runtime output paths remain VDU
    calls in every mode. EMOS routes those calls to the onboard VDP in Legacy
    and Dual, to the EDP stock-compatible backend in Exclusive Compatible, and
    to the EDP enhanced backend in Exclusive Extended. An explicit EDU call is
    a separate application interface and result domain even when both call
    classes ultimately reach the EDP.
28. Permit EDU-aware applications to combine conventional VDU calls with
    explicit EDU calls. This is a mixed-API application pattern, not another
    operating mode. In Dual the two call classes address different processors;
    in either exclusive mode they may address different interfaces of the same
    EDP.
29. Permit an application to require Exclusive Extended and deliberately use
    conventional VDU restart calls for its high-frequency compatible output,
    avoiding an EDU envelope around every transfer. Such software is
    intentionally mode-dependent and must verify or request the required mode
    before issuing output that would be unsafe or meaningless if EMOS routed it
    to the onboard VDP.
30. Treat direct Extender hardware access without an active EMOS transaction as
    unsupported caveat-emptor experimentation. Project carrier hardware must
    use fail-safe disabled P4-to-Agon driver defaults independently of P4
    firmware, and project EDP firmware must expose only a bounded EMOS
    activation exchange before commit—never ordinary VDU, EDU, update, or
    persistent-write operations. These are normative design protections for
    project-produced hardware and software, not a guarantee that arbitrary
    external eZ80 code violating the EMOS contract cannot corrupt, damage, or
    brick either system. Any best-effort warning uses only an Extender-owned
    out-of-band display or log and never drives the unactivated Agon interface.
31. Model formal mode as the committed combination of two EMOS-owned planes:
    ordinary-VDU routing and EDP service. The only valid combinations are
    onboard/inactive for Legacy, onboard/active for Dual,
    EDP-compatible/active for Exclusive Compatible, and EDP-extended/active
    for Exclusive Extended. An exclusive route with inactive EDP service is
    invalid. Adding a third independent state dimension requires a separate
    architectural decision. EMOS alone derives and names formal mode from the
    two committed planes; EDP firmware and applications may report only local,
    requested, pending, readiness, transport, or failure state.
32. Make each explicit activation request one bounded
    prepare/readiness/commit/recover transaction owned by the EMOS coordinator.
    EMOS validates prerequisites and initializes the complete target before
    publishing either committed plane, makes at most one transition attempt per
    request, and returns or reports a bounded prerequisite failure through an
    available accepted caller or diagnostic path. Any pre-commit failure
    restores the current stable mode and unchanged routing without partial
    publication. This coherence rule does not depend on preservation of the
    initiating program or other processor state.
33. Make Legacy the transition hub. Cold boot first reaches fully operational
    Legacy and contacts EDP only after an explicit late `autoexec.txt` or manual
    request. A successful explicit presence/version probe activates EDP and
    commits Dual; failure leaves Legacy. Exclusive entry also starts from
    Legacy. Live Legacy-to-Dual and Dual-to-Legacy transitions are contracted,
    but no direct transition between two non-Legacy modes is contracted; EMOS
    first commits Legacy before attempting a different non-Legacy destination.
34. Use pull discovery for Extender v1 and define no proactive EDP presence
    signal. EMOS selects a reviewed transport/wiring profile, arms the eZ80
    receiver, issues the activation request, validates EDP identity, protocol,
    and capabilities, and alone commits mode. The exchange proves protocol
    readiness, not electrical qualification. Asynchronous EDP traffic is
    permitted only through a negotiated, armed post-activation receiver; P4
    reset revokes that permission and EMOS quarantines stale traffic.
35. Keep one fixed set of EMOS reset-vector and C-runtime output handlers that
    call one semantic VDU dispatcher. Each invocation retains one snapshot of
    the committed backend; a mode change switches only that backend and never
    replaces the vector table. Before changing that backend, the EMOS coordinator
    blocks new invocations, waits for active calls and owned response work to
    finish or be abandoned, reinitializes affected parser state, and commits
    atomically. The beta adds no second semantic VDU parser and does not
    preserve a multi-call partial command across a disruptive transition.
36. Use a disruptive controlled restart for every ordinary-VDU route change in
    the proof-of-concept and beta, and retain it as an acceptable v1 fallback.
    Preservation of the loaded eZ80 program, data, and resident processor state
    is an aspirational v1 target and a firm v2 requirement under MODE-001; it
    never implies migration of display assets between processors. The exact
    actor and carrier for a disruptive restart remain an open decision rather
    than being inferred here.
37. Latch successful explicit EDP activation as system state: foreground exit
    or zero known callers does not deactivate EDP. Normal return to Legacy is
    an explicit EMOS-coordinated shutdown and may refuse or time out when
    registered work cannot quiesce. A separately explicit forced shutdown may
    invalidate work only after warning.
38. Do not make persisted preferred mode a v1 contract. A fixed-backend build
    still requires explicit activation after Legacy startup. Represent a
    conditionally pending mode across reset only if a selected implementation
    actually carries an attempt across that reset. Retained cross-boot circuit
    breaking is a regression-driven conditional v1 target under MODE-002, not
    a beta requirement. Exact lifecycle-state storage and session/shutdown APIs
    remain open in SETUP-005.
39. Treat reset of an affected component as invalidating that component's
    sessions, parsers, pending work, readiness, and authority even if its RAM
    bytes or another processor survive; invalidation need not erase storage.
    eZ80/MOS reset and whole-system reset return through Legacy. P4 reset in
    Dual causes EMOS to invalidate EDU work and commit Legacy while ordinary
    VDU continues through the onboard VDP.
40. After a detected EDP failure in Dual, EMOS invalidates EDU work and commits
    Legacy while onboard VDU remains available. In an exclusive mode, an EDP
    or transport failure blocks ordinary VDU and permits only bounded
    reinitialization before disruptive recovery to Legacy. Recovery must not
    claim that application, display, audio, buffer, or other EDP-visible state
    survived. EMOS may use the onboard VDP for a best-effort recovery report
    only after disclaiming that continuity.
41. Record requested, conditionally pending, committed, failure, and fallback
    information in the EMOS lifecycle state. Structured failure reporting is
    advisable during beta and mandatory for v1: it supplies best-effort
    descriptive display output plus durable machine-readable consequences and
    safely obtainable processor context. Reporting must not depend solely on a
    failed component when another accepted sink survives and must not delay
    safe recovery.
42. Require v1 to provide a bounded durable crash-log sink in P4 onboard flash,
    independent of optional microSD. The existing `coredump` partition is only
    the initial candidate; DIAG-001 owns its integrity, interrupted-write, wear,
    native-crash, retrieval, and evidence-scope decisions and qualification.
43. Treat EMOS as one complete backward-compatible replacement for stock MOS,
    not a side-by-side companion. Its dispatcher alone owns ordinary VDU
    routing, and its lifecycle/EDU machinery alone owns EDP activation and
    Extender transport through supported project interfaces.
44. Before valid activation, supported pre-activation logic patterns or GPIO
    direction changes may be ignored or fail safely, but EDP must not expose
    ordinary VDU, EDU, updater, or persistent-write operations. Carrier
    hardware and EDP firmware remain quiescent while Legacy is committed or a
    transaction is uncommitted. QUAL-002 owns electrical and power/reset proof;
    the protocol and parser owners prove bounded handling.

## Rationale

1. An implementation-neutral API allows simple applications to avoid the
   memory, installation, and lifecycle costs of residency.
2. Explicit opt-in behavior prevents Extender from changing established Agon
   behavior merely because support software is present.
3. Persistent and asynchronous facilities need a single owner for interrupts,
   receive state, packet routing, and shared queues; duplicating that ownership
   independently in applications would be unsafe.
4. Keeping transparent routing out of an incidental TSR separates the stable
   EDU API from the system-level mechanism eventually selected for untouched
   legacy binaries.
5. Separating the public contract from its backend leaves room for later MOS
   support without making current applications depend on a facility MOS does
   not yet provide.
6. Exclusive ownership makes canonical MOS sysvars describe one coherent
   processor state and creates a defensible boundary for the full compatibility
   guarantee.
7. Separate VDU and EDU result domains allow both processors to work together
   without races or ambiguity over which device produced a response.
8. Compatibility wrappers provide a migration path for existing applications
   without making unsafe dual ownership part of the machine-level contract.
9. Requiring EMOS for every active Extender mode provides one durable owner for
   transport, discovery, sessions, result/event ingress, and recovery rather
   than treating a foreground application's private hardware access as a
   supported system mode.
10. Keeping diagnostics out of protocol return paths prevents console text from
    corrupting packet framing or being mistaken for application data.
11. A truly inert legacy mode provides an unconditional stock fallback for
    software and maintenance workflows outside the exclusive compatibility
    surface.
12. Explicit carve-outs make the compatibility claim testable and avoid
    importing high-risk operator transports that are not needed by normal
    applications.

## Consequences

1. EDU-capable programs use an explicit API rather than assuming that ordinary
   VDU output can be redirected to Extender.
2. Every EDU feature depends on EMOS. Features requiring optional background or
   cross-program facilities may additionally depend on installation of a
   compatible resident service; foreground-only features need not.
3. Resident implementation work must establish safe memory ownership, service
   discovery, version negotiation, installation lifecycle, interrupt ownership
   and restoration, register preservation, reentrancy behavior, and interaction
   with application memory maps before it can be considered qualified.
4. A resident service consumes eZ80 memory and must remain optional for programs
   that do not need its facilities.
5. Future upstream MOS or MOS Modules integration can replace or supplement
   EMOS's internal resident-service machinery while retaining the EDU
   application contract.
6. Exclusive EDP compatibility cannot be delivered for untouched binaries until
   a transparent route exists for the fixed stock VDU restart paths and for EDP
   responses expected by MOS.
7. Dual-mode applications must distinguish VDU state from EDU state
   even when an abstraction layer presents them through one higher-level API.
8. A compatibility claim must identify the operating mode and selected display
   authority; “compatible” without that context is insufficient.
9. In both exclusive modes, input-device configuration still needs
   a controlled route to the onboard VDP even though ordinary audio/video output
   is consumed by the EDP. The onboard VDP remains the initial physical input
   owner and its packets to MOS remain canonical; `SETUP-005-D007` owns the
   unresolved route by which the EDP receives processed events needed for its
   display-local behavior.
10. Reusing MOS's normal packet parser would preserve sysvar semantics better
    than having the EDP or a resident service write MOS-owned memory directly;
    direct writes by either are outside the accepted ownership model.
11. Documentation, releases, and compatibility metadata must state that every
    active Extender mode requires a compatible EMOS build; stock MOS supports
    only Legacy, in which Extender is inactive.
12. The P4 port must not inherit upstream `DBGSerial` or its UART0 mapping.
    Unsupported command paths must not block waiting for an absent external
    serial peer, corrupt parser framing, or enter a partially active mode.
13. Compatibility metadata must name the maintenance/operator carve-out when
    claiming compatibility in either exclusive mode. Legacy mode remains the
    fallback for those facilities.
14. The proof-of-concept input profile is intentionally application-mediated.
    It validates EDP-local input behavior without claiming transparent legacy
    compatibility or pre-deciding the v1 routing mechanism.
