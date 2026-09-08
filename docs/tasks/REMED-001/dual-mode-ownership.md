# Dual-mode ownership inventory

- Parent task: [REMED-001](../REMED-001.md), Work 2.b
- Scope: Dual mode (`mode:extender:dual`)
- State: Accepted task-local ownership boundary
- Prepared: 2026-08-23
- Accepted: 2026-08-23

## Applicability amendment — browser keyboard, 2026-09-08

The browser-keyboard direction in [SETUP-005](../SETUP-005.md) K001 and
amended ADR-0014 supersedes the earlier assumption that all input starts on
the onboard VDP. P4 sends browser keys to EMOS as stock packets over UART1.
This inventory retains Dual's ordinary onboard state domain; K002/K003 own
the source/session/receiver choices for the first bounded keyboard test.

## Purpose

Expand the accepted Dual-mode boundary into explicit ownership classes. This
inventory answers `MODE-AUDIT-F003`; it does not design the EDU API, select a
transport, resolve lifecycle or synchronization, or promise compatibility for
non-EDU-aware software.

Dual means that both display processors are active and separately addressed:

```text
ordinary VDU -> onboard VDP -> stock VDP packets -> EMOS stock-compatible VDP state
explicit EDU -> EMOS        -> EDP/EDU results   -> EMOS-owned EDU state
```

Dual does not mean mirrored VDU, shared display state, duplicate stock response
packets, or competing ownership of MOS sysvars.

## Identity rule

Every stateful object in Dual mode belongs to a processor and interface domain.
The full identity is therefore conceptually:

```text
<domain, owner, object type, local identifier>
```

The onboard VDP and EDP may use identical command encodings, callback numbers,
buffer IDs, channel numbers, bitmap IDs, variable IDs, or other local values
without referring to the same object. An EDU operation may deliberately carry
stock-compatible VDU bytes to reuse the faithful EDP parser, but the explicit
EDU address and EDU result domain keep that operation separate from ordinary
VDU.

## Onboard-VDP-only stock domain

| Asset or behavior | Dual-mode ownership rule |
|---|---|
| Ordinary VDU byte stream | `RST.LIL 10h`, `RST.LIL 18h`, BASIC `VDU`, MOS `VDU`, and other unmodified stock output continue to the onboard VDP only. |
| Stock VDU parser and device state | The onboard VDP is authoritative for all state produced by ordinary VDU, including screen mode, contexts, graphics, palette, cursor, fonts, bitmaps, sprites, tiles, copper, buffers, audio, and VDP-local variables. |
| Stock response producer | The onboard VDP alone emits VDP protocol packets intended for the stock-compatible VDP parser retained by EMOS in Dual mode. |
| Stock General Poll | Ordinary `VDU 23,0,&80,n` tests and initializes the onboard VDP. It does not establish EDP or EDU availability. |
| Physical keyboard and mouse | The onboard VDP owns the attached PS/2 devices, physical acquisition, and stock input packets. |
| Stock input configuration | Ordinary keyboard/mouse configuration commands describe and control the onboard VDP path. They do not configure EDP-local input state unless an explicit EDU operation separately does so. |
| Stock RTC command surface | Ordinary `VDU 23,0,&87` and its stock response describe the onboard VDP RTC domain pending the wider RTC policy. |
| Stock maintenance/operator facilities | Printer/USB serial, console/terminal, ZDI, Intel HEX, YMODEM, updater, and local debug behavior remain reachable only as ordinary onboard-VDP facilities where upstream supports them. Their availability is not an Extender implementation claim. |

## EDP-only Extender domain

| Asset or behavior | Dual-mode ownership rule |
|---|---|
| EDU command endpoint | Only an explicit EDU call through EMOS addresses the EDP. Linked code is an EMOS API binding and an optional resident facility is subordinate to EMOS; merely emitting ordinary VDU does not address EDP. |
| EDP parser and device state | The EDP owns all state created through EDU, including any reused stock-compatible parser state, display contexts, graphics, palette, cursor, fonts, bitmaps, sprites, tiles, copper, buffers, audio, callbacks, variables, and Extender additions. |
| Extender presentation | EDP-generated network/browser video and audio and any later explicitly supported P4 sink describe EDP state only. |
| Extender services | P4 Ethernet, optional ESP8266 networking, P4 microSD, media, update, status, management, and installed-application services are EDP/Extender facilities. They do not become onboard-VDP or MOS services merely because an EDU client can call them. |
| EDP callbacks and events | Registrations and callback execution are local to EDP. A result requiring eZ80 delivery enters the EDU asynchronous domain, never the stock VDP packet domain. |
| EDP liveness | EDU discovery/open or another future accepted EDU operation establishes EDP availability. The stock General Poll remains onboard-owned. |
| EDP failure and diagnostics | EDP crashes, resets, diagnostics, and service errors remain in the Extender domain and must not corrupt the stock VDP packet stream. Exact recovery and reporting remain unresolved. |

## MOS-owned stock assets

| Asset or behavior | Dual-mode ownership rule |
|---|---|
| Low-ROM VDU restart entry points | MOS owns the ABI and routing. In Dual mode they continue to target the onboard VDP and are not intercepted by an optional EDU service. |
| UART0 VDP response parser | MOS owns packet framing, validation, dispatch, and every eZ80 memory effect produced by the onboard VDP response stream. |
| Canonical VDP sysvar block | MOS owns the memory. In Dual mode its display, audio, RTC, keyboard, mouse, General Poll, and related values describe the onboard VDP only. |
| VDP completion flags | MOS owns the flags and changes them only through stock response handling. EDP operations cannot set or clear them. |
| Keyboard map and input hooks | MOS owns its keyboard map, event count, keyboard handler, user keyboard vector, mouse fields, and associated host behavior. Their canonical event source is the onboard VDP. |
| Other MOS memory, APIs, vectors, and named system variables | MOS remains authoritative. EDP and EDU clients obtain only explicitly documented or allocated access; they acquire no general memory ownership from Dual mode. |

EMOS owns both the retained stock VDP domain and the separately namespaced EDU
domain. Stock MOS cannot activate Extender and supports only Legacy. Linked EDU
client code is an EMOS API binding, and optional resident facilities remain
subordinate to EMOS transport, lifecycle, and mode arbitration.

## Separately namespaced assets

| Asset class | Stock namespace | EDU namespace requirement |
|---|---|---|
| Commands | Ordinary VDU stream | Explicit EDU operation; a VDU-compatible payload is still EDU-addressed. |
| Results and errors | MOS VDP sysvars and completion flags | EDU-owned result structures, registers, return values, queues, or service memory. |
| Asynchronous messages | Stock VDP packets parsed by MOS | Versioned EDU event/message framing delivered only to an EDU client or service. |
| Session and lifecycle state | Onboard VDP/MOS stock lifecycle | EDU discovery, compatibility negotiation, open sessions, handles, and recovery state. |
| Graphics and display objects | Onboard VDP object IDs and contexts | EDP object IDs and contexts, even when numeric values and semantics match. |
| Audio objects | Onboard VDP channels, samples, and status | EDP channels, samples, status, and sink routing. |
| Buffers and callbacks | Onboard VDP buffer IDs, callback IDs, and registrations | EDP IDs and registrations. Numeric equality never aliases an onboard object. |
| VDP variables | Onboard VDP-resident variables | EDP-resident variables reached through EDU; neither set is a MOS named variable. |
| RTC state | Onboard VDP/MOS stock RTC domain | EDP clock and synchronization status until D008 defines any controlled relationship. |
| Input-derived display state | Onboard VDP state and canonical MOS input | EDP-local injected or relayed state, with no duplicate stock packet emission. |
| eZ80 memory | MOS and application-owned stock memory | Explicitly allocated client or resident-service memory with a documented owner and lifetime. |
| Transport state | UART0 stock VDP path | EDU transport driver buffers, framing, queues, interrupts, and errors. |

## Safely shareable information and coordination

Sharing means copying or coordinating explicitly; it does not create two
canonical writers.

| Shareable item | Safety boundary |
|---|---|
| Processed keyboard/mouse events | An aware application may read canonical stock input and explicitly inject a copy into EDP. The copy updates EDP-local behavior and does not generate a duplicate stock packet. Automatic v1 relaying remains D007. |
| Application data and media | An EDU-aware application may deliberately transfer data between eZ80/MOS storage and Extender services. Each endpoint retains its own storage, locking, durability, and error ownership. |
| High-level application intent | A program or abstraction layer may issue separate VDU and EDU operations to make the processors work in concert. Each operation remains addressed and its result domain remains identifiable. |
| Immutable resources | Fonts, images, palettes, geometry, or other data may be loaded into both processors as independent copies. Mutation in one copy does not silently mutate the other. |
| Time observations | One clock may be sampled to synchronize another only under the future D008 policy. Sharing a timestamp does not make the clocks one writable object. |
| Capability and status observations | EDU may report Extender capabilities to its clients without changing stock MOS VDP fields. A wrapper may combine separately labeled observations for an application. |
| Physical buses and pins | Electrical sharing is safe only where a reviewed transport/hardware profile assigns ownership, idle state, isolation, and transitions. Logical Dual-mode permission does not itself authorize concurrent drive. |

## Prohibited collisions

The following are outside supported Dual mode:

1. mirroring one uncontrolled ordinary VDU stream to both processors;
2. routing an EDP response into MOS's stock VDP parser or setting stock VDP
   completion flags for an EDU operation;
3. direct EDP, application, or resident-service writes to canonical MOS VDP
   sysvars to impersonate an onboard VDP response;
4. allowing both processors to emit canonical keyboard or mouse packets for
   one physical event;
5. treating identical numeric IDs in onboard and EDP buffers, callbacks,
   variables, graphics objects, or audio channels as one shared object;
6. exposing EDU asynchronous bytes on the stock VDP packet stream without a
   separately accepted, unambiguous protocol and MOS owner;
7. an optional EDU service intercepting VDU or activating Extender implicitly;
8. sharing mutable parser, command, graphics, audio, RTC, or callback state
   without an explicit single writer and synchronization contract;
9. treating maintenance facilities available through the onboard VDP as
   implemented or owned by Extender; and
10. representing an EDU operation as qualification of the analogous ordinary
    VDU interface unless an explicit reviewed mapping exists.

## Unresolved Dual-mode assets

| ID | Unresolved boundary | Existing owner |
|---|---|---|
| `DUAL-U01` | Exact EDU command, result, error, event, and capability namespaces and their version negotiation. | EDU API and later implementation tasks; affects REMED-001 2.e and 4.f. |
| `DUAL-U02` | eZ80-side owner, memory layout, interrupt ownership, queues, reentrancy, and lifecycle for a resident EDU service. | ADR-0014 follow-on service work and D002. |
| `DUAL-U03` | Physical and link-layer transport used by EDU in Dual mode, including UART1/parallel ownership, framing, pacing, and concurrent electrical behavior. | D002, PORT-008 reconciliation, and hardware/qualification tasks. |
| `DUAL-U04` | Which non-EDU-aware software can be supported by wrappers/loaders and what each profile guarantees. | D004 / REMED-001 2.f. |
| `DUAL-U05` | Whether EDP audio may be explicitly delegated to onboard VDP hardware without confusing ownership or acknowledgements. | D005 / REMED-001 2.g. |
| `DUAL-U06` | Whether and how input is automatically relayed to EDP, which fields are copied, and how configuration commands are divided. | D007 / REMED-001 2.i. |
| `DUAL-U07` | RTC authority, synchronization, read/set direction, MOS named variables, persistence, timezone, conflict, and failure. | D008 / REMED-001 2.j. |
| `DUAL-U08` | Discovery, entry, exit, reset, Extender failure, recovery, and fallback while preserving ordinary onboard-VDP operation. | D002 / REMED-001 2.d. |
| `DUAL-U09` | Exact asynchronous reverse transport and whether any Extender-enabled MOS facility participates without entering the stock VDP parser domain. | D003 / REMED-001 2.e and later EDU transport design. |
| `DUAL-U10` | Concurrency, locking, and arbitration for multiple EDU clients using network, storage, media, transport, and resident-service resources. | PORT-006, PORT-007, and the resident EDU service design. |

These unresolved mechanisms do not weaken the top-level non-collision rule:
ordinary VDU remains onboard-VDP-authoritative, its canonical eZ80 state remains
MOS-owned, and explicit EDU operations and results remain EDP/EDU-owned.

## Reviewed authority

- [Operating-mode audit](../../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md),
  especially `MODE-AUDIT-F003`, `F011`, and `F013`.
- [ADR-0014](../../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md),
  decisions 3–18, 21, 23–24, and 26.
- [Current architecture](../../architecture.md), operating-mode and EDU service
  sections.
- [SETUP-005](../SETUP-005.md), decisions D002–D008.
- [Exclusive-mode common ownership](exclusive-common-ownership.md), used only
  to distinguish the exclusive MOS integration domain from Dual.
- Official Agon VDP documentation and official VDP `v2.16.0` / MOS `v3.0.2`
  source findings already bounded in Work 2.a.

## Work 2.b disposition

The Author accepted this inventory on 2026-08-23 as the explicit Dual-mode
ownership boundary. The acceptance classifies current assets and prohibits
collisions; it does not resolve the ten named mechanisms above, define the EDU
wire/API contract, implement EMOS or an optional resident facility, or qualify
Dual-mode operation.
