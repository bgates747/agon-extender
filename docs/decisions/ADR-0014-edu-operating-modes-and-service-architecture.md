# ADR-0014 — EDU operating modes, state ownership, and service architecture

- Status: Accepted
- Completeness: Partial
- Date: 2026-08-20
- Last amended: 2026-08-22
- Related tasks: SETUP-004, SETUP-005
- Open-decision tracker: SETUP-005

## Context

Extender needs an application-facing command path distinct from the stock VDU
path. Some operations can be performed synchronously by code linked into the
calling application, but persistent or asynchronous facilities may require an
eZ80-side program that remains resident after its installer or original caller
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

The intended EDP-exclusive compatibility behavior is asymmetric rather than a
complete removal of the onboard VDP. All applications, whether EDU-aware or
not, use the EDP for audio and video output. The onboard VDP remains the
physical keyboard and mouse controller, but Extender becomes the logical
compatibility gateway for its input. MOS must observe one coherent stream of
stock-compatible responses and input events and update its canonical sysvars
accordingly. Extender controls that logical stream; MOS should continue to own
and mechanically update its own sysvars wherever the selected routing mechanism
permits reuse of the stock parser.

Untouched legacy applications reach VDU output through fixed low-ROM restart
handlers. A normal resident service cannot replace those handlers through MOS's
documented interrupt-vector API. Hardware interposition could provide complete
transport control but would impose board modification or additional switching
hardware. A narrow MOS change could instead preserve the restart entry points
and select a different transport in the routines behind them. The routing
mechanism is not yet accepted and remains in the linked open-decision tracker.

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
   independent of whether its implementation is linked into an application or
   supplied by a resident program.
4. Make the resident EDU service an explicit, opt-in facility. Its absence must
   not alter stock MOS, onboard VDP, or ordinary VDU behavior.
5. Require applications to discover and explicitly open the EDU service before
   using it. Absence or incompatibility must be reported cleanly rather than
   causing implicit interception or partial activation.
6. Permit a directly linked EDU implementation for synchronous foreground
   operations. Applications may use that implementation when residency is not
   required.
7. Use the resident implementation for capabilities that require persistent
   ownership, asynchronous reception, interrupt servicing, shared transport
   state, queues, or work that survives the initiating call or program.
8. Keep application-visible EDU operations consistent across linked and
   resident implementations. At minimum, the eventual API must cover service
   discovery, session open and close, block transfer, and reception or polling.
9. Do not let an optional resident EDU service opportunistically hook or replace
   `RST.LIL 10h` or `RST.LIL 18h`. Any transparent legacy routing used by
   exclusive compatibility mode must be an explicit system-mode facility with
   defined activation, fallback, and ownership rather than an incidental TSR
   side effect.
10. Keep transport and resident-program mechanics behind the EDU API. A future
   official MOS integration may provide another backend without requiring EDU
   applications to adopt a different application protocol.
11. Define **EDP-exclusive compatibility mode** as selection of the EDP as the
    authoritative audio/video processor and compatibility interface. The EDP
    owns stock-compatible command processing, responses, completion flags, and
    canonical MOS VDP sysvars through the selected routing mechanism.
12. Permit EDP-exclusive mode to claim complete compatibility for the declared
    normal application-facing surface only after ordinary legacy VDU traffic
    and responses can be routed transparently. Explicitly exclude the v1
    maintenance/operator carve-outs named in the Context from that claim.
13. Define **extended cooperative mode** as simultaneous, explicitly addressed
    use of the onboard VDP through VDU and the EDP through EDU. The processors
    may perform coordinated work, but their command and response channels remain
    distinguishable.
14. Give VDU and the onboard VDP exclusive ownership of canonical MOS VDP
    sysvars in extended cooperative mode. EDU must retain EDP results in
    EDU-owned registers, structures, flags, queues, or resident-service state
    and must not impersonate a MOS VDP response.
15. Do not guarantee arbitrary unmodified legacy software in extended
    cooperative mode. Project-owned wrappers and abstraction layers may operate
    one or both processors on behalf of software that is not itself EDU-aware,
    but each supported compatibility profile requires explicit qualification.
16. Do not support uncontrolled duplication of one ordinary VDU stream to both
    processors. Divergent state and competing return packets make such a shared
    VDU mode unsafe and outside the supported architecture.
17. Require baseline extended cooperative mode to operate with stock MOS. An
    EDU-aware application may communicate with the EDP through linked client
    code or the optional resident EDU service without requiring MOS to know that
    Extender exists.
18. Treat Extender-enabled MOS as a prerequisite only for capabilities that
    require system-wide integration, including any accepted implementation of
    transparent legacy VDU routing that depends on MOS. Modified MOS is not a
    general prerequisite for EDU-aware software or cooperative use.
19. Do not implement the upstream local USB/UART maintenance and operator
    facilities in Extender v1, including printer output, console/terminal
    modes, ZDI, Intel HEX, YMODEM, firmware updating, and buffered-command debug
    output. Handling attempts is mode-contract dependent: strict compatibility
    preserves stock-observable behavior, including undesirable failures, while
    non-strict operation should improve failure and recovery. Exact behavior
    and the strict-mode boundary remain in the linked task rather than this ADR.
20. Define **legacy mode** as the stock-machine mode in which Extender is
    electrically and logically absent from the Agon interface even when it is
    connected and powered. The onboard VDP owns ordinary VDU, responses,
    sysvars, input, and maintenance facilities without Extender interception.
21. In extended cooperative mode, ordinary VDU continues to reach the onboard
    VDP, so its maintenance facilities may remain available through that stock
    path. Their availability does not make them Extender-supported features.

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
9. Stock-MOS cooperative operation gives Extender a useful deployment path
   independent of the harder transparent-compatibility problem and avoids
   imposing a firmware replacement on applications that already use EDU
   explicitly.
10. Keeping diagnostics out of protocol return paths prevents console text from
    corrupting packet framing or being mistaken for application data.
11. A truly inert legacy mode provides an unconditional stock fallback for
    software and maintenance workflows outside the EDP-exclusive compatibility
    surface.
12. Explicit carve-outs make the compatibility claim testable and avoid
    importing high-risk operator transports that are not needed by normal
    applications.

## Consequences

1. EDU-capable programs use an explicit API rather than assuming that ordinary
   VDU output can be redirected to Extender.
2. Features requiring background or cross-program state depend on installation
   of a compatible resident service; foreground-only features may not.
3. Resident implementation work must establish safe memory ownership, service
   discovery, version negotiation, installation lifecycle, interrupt ownership
   and restoration, register preservation, reentrancy behavior, and interaction
   with application memory maps before it can be considered qualified.
4. A resident service consumes eZ80 memory and must remain optional for programs
   that do not need its facilities.
5. Future official MOS integration can replace or supplement the resident
   backend while retaining the EDU application contract.
6. Exclusive EDP compatibility cannot be delivered for untouched binaries until
   a transparent route exists for the fixed stock VDU restart paths and for EDP
   responses expected by MOS.
7. Extended cooperative applications must distinguish VDU state from EDU state
   even when an abstraction layer presents them through one higher-level API.
8. A compatibility claim must identify the operating mode and selected display
   authority; “compatible” without that context is insufficient.
9. In EDP-exclusive compatibility mode, input-device configuration still needs
   a controlled route to the onboard VDP even though ordinary audio/video output
   is consumed by the EDP. The onboard VDP remains the initial physical input
   owner and its packets to MOS remain canonical; `SETUP-005-D007` owns the
   unresolved route by which the EDP receives processed events needed for its
   display-local behavior.
10. Reusing MOS's normal packet parser would preserve sysvar semantics better
    than having the EDP or a resident service write MOS-owned memory directly.
11. Documentation, releases, and compatibility metadata must distinguish
    stock-MOS cooperative operation from features that require an
    Extender-enabled MOS build.
12. The P4 port must not inherit upstream `DBGSerial` or its UART0 mapping.
    Unsupported command paths must not block waiting for an absent external
    serial peer, corrupt parser framing, or enter a partially active mode.
13. Compatibility metadata must name the maintenance/operator carve-out when
    claiming EDP-exclusive compatibility. Legacy mode remains the fallback for
    those facilities.
