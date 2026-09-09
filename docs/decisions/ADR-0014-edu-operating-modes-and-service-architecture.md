# ADR-0014 — EDU operating modes, state ownership, and service architecture

- Status: Accepted
- Completeness: Partial
- Date: 2026-08-20
- Last amended: 2026-09-09
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
The onboard VDP retains physical keyboard/mouse acquisition where used.
Browser-originated and directly attached USB keyboard input instead enter P4
and reach EMOS over UART1; neither requires an onboard-VDP relay. MOS must
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
    API. Extend resident EMOS through ordinary compile-time linking with clear
    internal ownership boundaries and upstream-reviewable changes. No module
    loader or runtime relocation is required for this implementation.
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
20. Define **Legacy mode** as mainboard ordinary-VDU routing with the ordinary
    EDP/EDU service inactive. The separately selected keyboard source is
    preserved: explicitly selected browser or P4 USB keyboard input may continue
    over P4 UART1.
    This is the accepted keyboard exception to total Extender absence. EMOS
    retains canonical sysvar ownership; mainboard display and maintenance
    behavior remain on the onboard VDP.
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
23. Select mainboard/Extender keyboard choice as the immediate input goal,
    with directly attached USB as the Extender acquisition source. Focused
    browser input retains its contract but is deferred until explicitly
    reprioritized. P4 processes selected input and emits stock-compatible VDP keyboard packets
    over existing r03 UART1 to EMOS. EMOS owns packet reception, canonical key
    sysvars, keymap and application hook effects. Applicable configuration and
    queries use the same UART in the forward direction. No proprietary UART
    keyboard/state envelope, parallel transfer or direct onboard link is needed.
    The earlier aware-application forwarding proof of concept is later scope;
    its non-echo rule applies to forwarded copies, not browser-originated keys.
    An explicit CLI or autoexec command enables EMOS input
    reception; EMOS selects P4 keyboard events exclusively while retaining
    other onboard VDP communications. For the deferred browser source, on focus loss or browser disconnect, P4
    sends stock key-up packets for held keys, then stops keyboard packet
    delivery to EMOS. Native USB device lifetime is independent of browser
    focus, leases and network connectivity.
24. Keep mainboard-connected keyboard/mouse acquisition on the onboard VDP
    where used; it is not a mandatory source or relay for P4-originated input.
    Permit a directly attached USB keyboard through the P4 DevKit's native USB
    host and the required connector/power assembly. This brings forward the
    physical Extender input source while retaining the selected onboard VBlank
    clock. It does not enable the retained physical PS/2 drivers or select
    wider P4-owned peripheral hardware.
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
    for mainboard VDU routing with the keyboard-source exception in decision 20.
    **ExCom** is accepted conversational shorthand for **Exclusive Compatible**
    (Author-approved 2026-09-08); it does not change the formal name or stable
    mode identity.
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
    invalid. The accepted keyboard-source amendment below adds an independent
    input selection; keyboard-only activity does not set this ordinary EDP/EDU
    service plane active or commit Dual. EMOS alone derives formal mode from the
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
9. Browser-keyboard configuration and replies belong to the selected P4/EMOS
   UART path. Physical onboard-device configuration, when selected, needs its
   explicit controlled route rather than mirrored VDU. SETUP-005 D003/D007
   track source selection and exact parser/session integration.
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
14. The focused keyboard increment uses ordinary MOS keyboard interfaces at
    the application boundary. EMOS derives local sysvars/keymap from stock
    packets; P4 does not send a replacement memory image. Session admission
    remains explicit and Legacy follows decision 20's keyboard exception. A separately
    identified bounded test does not claim complete exclusive-mode activation.


## SD-loaded qualification samples — 2026-09-08 clarification

The Author accepted moving the visible-text sample into an SD-loaded C
application. This uses decision 16's separately identified qualification-traffic
exception: the application supplies a bounded text buffer to resident EMOS;
EMOS owns validation, UART transport, completion and release. P4 admits a
bounded text grammar and executes it through retained EDP. Sample text is
independent of both firmware images. The diagnostic does not activate a mode
or redirect ordinary application VDU, and establishes no supported application
bypass of EMOS ownership. PORT-014 owns its bounded implementation and evidence.

## CLI and keyboard selection — 2026-09-08

1. Use `EMOS <subcommand>` for EMOS-specific control at the MOS CLI and in
   `autoexec.txt`. Command names, subcommands and named selectors are
   case-insensitive. The namespace reduces command collisions; it cannot
   guarantee that upstream will never introduce an `EMOS` command.
2. Keep `VDU` as ordinary display commands routed by EMOS to the selected
   display authority. Use `EDU` for explicitly Extender-specific commands;
   ordinary VDU remains VDU when its destination is EDP in ExCom.
3. Select destination modes with `EMOS EXCOM` and `EMOS LEGACY`, rather than
   `ON`/`OFF` toggles. They request Exclusive Compatible and Legacy respectively.
   Report success only after transition completion; requesting the current
   mode is a harmless no-op. These names do not implement or qualify mode
   transitions by themselves.
4. Keep `SET KEYBOARD n` as the separate runtime keyboard-layout setting,
   with the same effect in Legacy, ExCom and later mixed modes. EMOS owns the
   setting and applies it to the selected keyboard path. Source selection is
   not encoded in that number. A future dual-keyboard design may extend this
   model, but is outside the first increment.
5. Use `EMOS KEYINPUT mainboard` for the keyboard connected to the Agon
   mainboard and `EMOS KEYINPUT browser` for focused browser capture. Use
   `EMOS KEYINPUT extender` for Extender-connected keyboard hardware, initially
   a directly attached USB keyboard as selected on 2026-09-09.
   `EMOS KEYINPUT` without an argument
   reports the selected source. Use readable named arguments, not numeric
   source codes or Unix-style option switches, for this selector.
6. Receive browser keyboard packets through an EMOS-owned interrupt-driven
   UART1 receiver with separate packet assembly from UART0, reusing stock MOS
   keyboard handlers and preserving their application-visible behavior. P4
   has no connection to the onboard MOS/VDP UART0 link in the current harness;
   the onboard VDP requires no firmware customization for browser input.

## Keyboard source independent of display mode — 2026-09-08

The Author accepted preserving the selected keyboard source across display-mode
changes. `EMOS LEGACY` restores mainboard display routing while selected
browser or P4 USB keyboard input continues. EMOS admits that input explicitly through KEYINPUT;
selecting Legacy is not an instruction to shut down the keyboard path.

This amends earlier total electrical/logical absence and quiescence requirements
for Legacy: they exclude the explicitly selected keyboard service and its
required UART traffic. Other EDP/EDU service remains inactive in Legacy;
keyboard-only activity does not imply Dual or permit unrelated EDP traffic.
Stock MOS gains no Extender capability from this amendment. Cold-boot input
selection is a separate setting from preservation across mode changes.

## Startup persistence — 2026-09-08

Restore command selections across boots only through `autoexec.txt` for this
increment. EMOS starts with mainboard keyboard input; autoexec may select
`EMOS KEYINPUT browser` and apply `SET KEYBOARD n`. Layout and source persist
in memory across mode changes, but these commands do not create a separate
state file, `.cfg` file or nonvolatile settings store. A command issued only
at the interactive prompt does not automatically become a saved preference.
This clarifies the earlier use of “persistent” for keyboard settings. A future
configuration store may be considered if an actual need arises; none is
selected now. Existing unrelated MOS facilities are outside this change.

## Resident EMOS extensions — 2026-09-08 clarification

After considering a minimal MOS Modules implementation, the Author rejected
moslet-space module loading and runtime relocation for this work. Extend
resident EMOS directly with ordinary compile-time linking. Preserve explicit
command, service, interrupt, state and transport ownership in the source;
do not introduce transient command modules, an SD module loader, relocation
machinery or a restriction to the 32 KiB moslet area.

This supersedes the briefly proposed Modules-foundation prerequisite. MOS-001
records the cancelled development path and preserves historical research only.
INTEG-009 owns the next resident keyboard increment. Upstream-reviewable
organization remains desirable, but is not a claim to implement the upstream
MOS Modules proposal or an authorization to submit changes upstream.

## Mainboard display during exclusive operation — 2026-09-08

The Author selected a static mainboard status banner with its text cursor
hidden while ExCom routes ordinary VDU output, including CLI echo, to EDP.
EMOS draws the notice and hides the cursor using stock mainboard VDP commands;
no double buffering or periodic software refresh is required. Mainboard video
scanout and the retained VBlank clock continue. The banner names the actual
exclusive mode and must not falsely claim that a failed transition succeeded.

This is EMOS-owned transition/status output, not mirrored application VDU.
Dual retains its two active display roles and is not assigned an inactive-screen
banner. No custom mainboard VDP firmware is required.

For the first implementation, returning to Legacy clears the mainboard display,
restores a visible text cursor and presents a fresh MOS prompt. The selected
keyboard source and layout remain unchanged. This initial behavior does not
require reconstructing the pre-switch screen and is not a permanent
requirement to clear user display contents; SETUP-005 retains the later
non-destructive notification refinement.

## Single controlling browser — 2026-09-08

When browser input is resumed, P4 accepts keyboard events from one controlling browser
session at a time. Other sessions may view within the video service's supported
limits. Keyboard takeover is explicit. P4 revokes the old session and emits
stock key-up packets for its held keys before admitting new-owner input;
stale events from the old session cannot enter the new stream. Focus gates
capture but does not itself take control. This session policy preserves the
stock UART format and EMOS keyboard-source ownership. REMOTE-001 K004 owns
implementation and qualification of the transition.

## Immediate keyboard priority — 2026-09-09

Following accepted native USB ordinary-CLI and gameplay results, the Author
selected `EMOS KEYINPUT mainboard` / `EMOS KEYINPUT extender` as the immediate
keyboard goal. Browser input is deferred until explicitly reprioritized, with
its implementation, session contract and diagnostic findings preserved. It is
not a required next step after USB bring-up. This does not defer browser video
as an output capability or change the four operating modes.

EMOS retains case-insensitive source selection, separate `SET KEYBOARD n`
layout, mainboard input at boot, and autoexec-only startup persistence. The
selected input source remains independent of display mode; no automatic
fallback or simultaneous keyboard-source mixing is selected. The P4 USB
connector/power addition is specified beside the r03 design. SETUP-005 K010
records acceptance; HW-002 owns incorporating it into the drawing.
