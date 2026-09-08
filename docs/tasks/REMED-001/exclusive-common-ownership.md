# Exclusive-mode common ownership inventory

- Parent task: [REMED-001](../REMED-001.md), Work 2.a
- Scope: Exclusive Compatible and Exclusive Extended modes
- State: Accepted task-local ownership boundary
- Prepared: 2026-08-23
- Accepted: 2026-08-23

## Purpose

Define the hardware-independent ownership contract shared by the two exclusive
modes. This inventory separates four concepts that must not be collapsed:

- **semantic authority** — the component whose state and behavior an operation
  describes;
- **storage authority** — the component that owns the canonical memory holding
  a result or status;
- **mechanism authority** — the component permitted to perform a routing,
  parsing, or memory-update operation; and
- **physical authority** — the component directly attached to a device or
  signal.

“The EDP has logical reach into MOS effects” means that EDP behavior must cause
the same MOS-visible result through an accepted MOS-owned mechanism. It does
not grant the EDP, an application, or a resident EDU service ownership of MOS
memory or permission to write it directly.

This is an accepted task-local boundary, not yet normative architecture. It
becomes an input to ADR-0014 and `docs/architecture.md` under REMED-001 Work
2.m after the remaining SETUP-005 decisions.

## Common boundary

Above their transport adapters, Exclusive Compatible and Exclusive Extended
have one compatibility implementation and one ownership contract:

```text
application / MOS VDU entry points
        -> selected exclusive command transport
        -> EDP stock-compatible command parser and device state
        -> EDP stock-compatible response producer
        -> selected exclusive response transport
        -> MOS-owned packet parser
        -> MOS-owned canonical VDP state, flags, and hooks
```

The two modes may differ in framing, pacing, buffering, flow control, physical
endpoints, and enhanced reverse features. Those transport differences must not
change the stock-visible command semantics, response packets, or MOS effects
within the declared compatibility surface.

## Keyboard-source amendment — 2026-09-08

SETUP-005 K001 and amended ADR-0014 select browser → P4 → existing r03 UART1
→ EMOS for the next keyboard increment. Physical onboard devices remain
onboard where used; they are not prerequisites or relays for browser keys.
The inventory below reflects that distinction. K002/K003 retain session,
parser-state and input-source selection choices. The full exclusive-mode
contract remains a destination beyond the first bounded keyboard test.

## Ownership inventory

| Asset or behavior | Semantic authority | Storage or physical authority | Common exclusive-mode contract | Open mechanism or owner |
|---|---|---|---|---|
| Application-facing VDU ABI | MOS | MOS low-ROM restart entry points and calling convention | Existing `RST.LIL 10h` single-byte and `RST.LIL 18h` stream calls remain the untouched-application entry points. | Transparent selection behind those entry points is D001 / REMED-001 2.c. |
| Outbound VDU byte stream | EDP once an exclusive mode is active | Selected transport backend | Exactly one EDP command parser consumes ordinary application audio/video VDU traffic; the onboard VDP must not consume a competing copy. | D001 selects routing; Works 2.k and 2.l freeze the distinct transports. |
| VDU parser state, partial commands, timeouts, and malformed-stream state | EDP | EDP firmware | Preserve upstream parser behavior within the accepted compatibility surface. Transport adapters deliver bytes and do not become a second semantic parser. | D006 / Work 2.h resolves carve-outs and strict malformed behavior. |
| Display state and visible output | EDP | EDP RAM and selected Extender video sinks | EDP is the sole authoritative display processor. Screen mode, contexts, graphics, fonts, bitmaps, sprites, tiles, copper, buffers, plotting, cursor, and visible results describe EDP state. | Sink-specific work remains with the corresponding PORT tasks. |
| Audio command and channel state | EDP | EDP RAM; guaranteed Rev 1 sink is network/browser audio | EDP retains the complete stock audio command surface and produces its acknowledgements. | D005 / Work 2.g decides whether a mode may delegate playback to onboard VDP hardware. |
| VDP-local variables | EDP | EDP RAM | Variables documented in the VDP variable blocks are part of the VDP implementation, not MOS named system variables. EDP holds the canonical values associated with its parser, display, audio, buffers, callbacks, and other retained behavior. | Physical input-backed and RTC-backed subsets follow the input and RTC rows below. |
| Stock response packet contents and emission conditions | EDP | EDP firmware and response queue | EDP computes the authoritative response bytes and stock-observable emission or suppression behavior for its state, including General Poll, cursor, screen character, pixel, audio, mode, RTC, keyboard-state, echo, and retained callback effects. | D006 governs carved-out diagnostics; D007 and D008 govern input- and RTC-derived contents. |
| Response framing and delivery | EDP supplies payload semantics; MOS consumes the resulting stock packet | Mode-specific return transport | Stock response frames retain the official header, length, payload, ordering, and application-visible timing contract as far as required for compatibility. | D003 / Work 2.e selects the MOS ingress path; Works 2.k and 2.l separate the transports. |
| VDP response parser | MOS | MOS firmware | A MOS-owned parser validates packet framing, dispatches packet types, and performs all canonical eZ80-side effects. Reuse of the stock parser is preferred; an equivalent MOS-owned route is permissible only if explicitly accepted and qualified. | D003 / Work 2.e selects the exact parser route. |
| Canonical MOS VDP sysvar block | EDP supplies its result and browser-key semantics; onboard VDP supplies selected physical-device semantics | MOS RAM | MOS alone owns and mechanically updates cursor, screen-read, pixel, audio, mode, RTC, keyboard, mouse, General Poll, and related canonical fields. P4 code and application/resident EDU code never write these fields directly. | D003, D007, and D008 select the source routes for their respective fields. |
| MOS VDP completion flags | EDP is the source event for EDP queries | MOS RAM | MOS sets and clears the official completion bits through its response handling. EDP emits the packet that causes the corresponding flag; it does not set the flag itself. | D003 / Work 2.e selects ingress and qualification. |
| MOS keyboard map, key event counter, keyboard handler, and user keyboard vector | Selected P4 browser session or onboard physical source supplies events; EMOS owns host behavior | MOS RAM, MOS code, and application hook | P4 emits stock keyboard packets over UART1 for browser keys. EMOS alone owns handler effects, map and callbacks; neither P4 nor an application writes replacement state. | D003/D007 K002/K003 resolve ingress/session/source selection; INTEG-009 implements it. |
| MOS mouse sysvars and mouse completion flag | Onboard VDP supplies physical events; MOS owns host-visible state | MOS RAM | The onboard VDP remains the physical event source and MOS remains the canonical eZ80 state owner. | D007 / Work 2.i resolves EDP-local mirroring and configuration routing. |
| Physical keyboard and mouse acquisition | Onboard VDP where those devices are used | Onboard VDP PS/2 hardware and firmware | Existing physical-device ownership remains. Browser keys originate on the browser host and need no physical onboard keyboard or new P4 device. | REMOTE-001/PORT-005 own the browser path; D007 retains physical/mouse composition. |
| EDP display-local keyboard and mouse state | EDP | EDP RAM | P4 processes original browser keys and emits stock keyboard packets once. A later copied Agon-originated event retains non-echo behavior. EDP owns local variables, callbacks and display effects; mouse scope is separate. | PORT-005 implements keyboard state; D007 retains broader input composition. |
| Keyboard/mouse configuration commands consumed in the exclusive VDU stream | EDP for browser-keyboard semantics; selected onboard VDP for physical-device effects | EDP-local state or selected onboard device | Browser keyboard configuration/query and stock replies use the EMOS/P4 UART. Physical-device effects, when selected, require explicit delegation. No physical LED/device success is inferred from stored settings. | PORT-005 scopes keyboard commands; D007 retains remaining configuration routing. |
| General Poll | EDP for request handling and returned byte; MOS for host-visible result | EDP General Poll VDP variable; MOS General Poll field | EDP must execute the stock General Poll callback point, return the resulting byte in a stock packet, and become observably alive through the MOS-owned result path. MOS stores the returned byte. | D003 selects response ingress; PORT-008/QUAL work qualifies the end-to-end path per transport. |
| Buffered-command callbacks and callback-modifiable VDP state | EDP | EDP RAM and firmware | Registrations, removals, callback execution, and VDP-local state mutation remain EDP-internal. A callback that changes a stock response changes the packet the EDP supplies; MOS still owns any resulting host-memory effect. | Callback transport and timing are qualified with the associated interface; no separate owner decision is presently required. |
| Buffered-command channels, status, and returned values | EDP | EDP RAM until an explicit result is returned | EDP owns buffer/channel lifecycle and status. Stock-compatible return packets enter MOS through its parser; EDU-specific results, if any, require a separately namespaced EDU domain and must not masquerade as stock VDP packets. | D003 owns stock return routing; EDU result design remains outside this common stock contract. |
| RTC command surface and RTC-backed VDP variables | EDP must implement the stock surface in both exclusive modes | EDP RAM and an RTC source not yet selected; MOS owns canonical RTC packet fields | Retain `VDU 23,0,&87`, the official packed packet, VDP variables, callbacks, and MOS-visible response effects. This row does not select which physical clock is authoritative or how clocks synchronize. | D008 / Work 2.j resolves authority, set/read routing, synchronization, persistence, timezone, conflict, and failure. |
| MOS named variables such as `Sys$Date`, `Sys$Time`, and `Sys$Year` | MOS | MOS variable system and RTC integration | These are not VDP-local variables. Extender cannot claim or modify them merely by implementing VDP variables or emitting an RTC packet. | D008 / Work 2.j must establish any relationship explicitly. |
| Mode selection, entry, exit, restart, reset, failure, and fallback | System integration layer | MOS, EDP, onboard VDP, and transport hardware within their own domains | Once either exclusive mode is active, its single-owner rules apply. This inventory does not select how that state is entered, preserved, recovered, or abandoned. | D002 / Work 2.d owns the lifecycle contract. |
| Onboard VDP while an exclusive mode is active | Physical keyboard/mouse owner and possible explicitly delegated service only | Onboard VDP hardware and firmware | It is not an audio/video compatibility authority, command-stream peer, response peer, or canonical display-state owner. Any use beyond physical input requires an explicit accepted delegation. | D005, D006, and D007 own the only presently contemplated delegations. |
| Maintenance/operator facilities and local debug | Component-specific, outside the normal application surface | Onboard VDP in Legacy; otherwise mode-contract dependent | Extender v1 does not inherit upstream printer/USB serial, console/terminal, ZDI, Intel HEX, YMODEM, firmware-update, or local debug facilities merely because their source exists. Their bytes must not contaminate stock response framing. | D006 / Work 2.h resolves exclusive-mode handling and strict-fidelity limits. |
| EDU-owned state and results | EDU/EDP | EDP, linked-client, or resident-service storage with an explicit EDU namespace | EDU extensions may coexist with the exclusive stock-compatible surface, but they do not become MOS VDP sysvars or stock packets unless a separate accepted mapping says so. | EDU API and resident-service tasks own the extended domain. |

## Source findings supporting the split

The inventory uses the latest tagged project baselines selected for this port:
official VDP `v2.16.0` and MOS `v3.0.2`, together with current official Agon
documentation.

1. Official VDP documentation defines the VDP as the video, audio, keyboard,
   and mouse processor. It receives the eZ80 byte stream at 1,152,000 baud and
   returns keyboard and screen information through a custom serial protocol.
2. VDP `v2.16.0` defines packet types `0x00` through `0x0B` and constructs the
   packet header, length, and payload in `video/vdu_stream_processor.h`. The
   VDP runs callbacks before relevant responses, may alter VDP variables used
   in payloads, and applies the response-suppression variable before writing a
   packet.
3. MOS `v3.0.2` receives each UART0 byte in `src/interrupts.asm` and calls the
   MOS-owned state machine in `src/vdp_protocol.asm`.
4. That MOS parser owns packet validation and dispatch. Its handlers write the
   canonical VDP sysvar block, set completion flags, update keyboard and mouse
   state, invoke the keyboard vector and handler, and store General Poll and
   RTC results.
5. MOS `src_startup/globals.asm` allocates those fields and parser state in
   eZ80 RAM. The EDP therefore produces the semantic result but does not own
   the destination storage or write mechanism.
6. Official VDP-variable documentation describes a separate VDP-resident
   variable address space for communications, RTC, memory, keyboard, context,
   mouse, events, General Poll, graphics, bitmaps, sprites, last values, and
   VDU state. Those values must not be conflated with MOS named system
   variables or the MOS VDP sysvar block.

### Reviewed references

- Agon documentation: `docs/VDP.md`, `docs/mos/API.md`,
  `docs/mos/System-Variables.md`, `docs/vdp/System-Commands.md`, and
  `docs/vdp/VDP-Variables.md`.
- VDP `v2.16.0`: `video/agon.h`, `video/vdu_stream_processor.h`,
  `video/vdu_sys.h`, and `video/vdu_audio.h`.
- MOS `v3.0.2`: `src/interrupts.asm`, `src/vdp_protocol.asm`, `src/equs.inc`,
  `src/mos_api.inc`, and `src_startup/globals.asm`.

## Work 2.a disposition

The Author accepted this inventory on 2026-08-23 as the common ownership
boundary for both exclusive modes. The acceptance decides ownership only. It
does not select a MOS patch, transport, circuit, mode lifecycle, input bridge,
RTC authority, audio delegation, maintenance behavior, or enhanced reverse
protocol. Those choices remain with their explicit SETUP-005 decisions and
later REMED-001 work items.
