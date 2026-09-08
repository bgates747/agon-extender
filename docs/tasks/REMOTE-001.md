# REMOTE-001 — Develop browser keyboard and remote EMOS control

## State

- Status: Browser-keyboard plan accepted for freeze, 2026-09-08; implementation not started.
- Started: 2026-09-08 (scope reconciliation only).
- Finished: --

## Current increment

The Author selected keyboard capture while the browser display has focus as
the next feature. Browser events travel through the existing P4 network
service; P4 processes them into stock-compatible VDP keyboard packets and
sends them to EMOS over the existing r03 UART1 connection at 1152000/8N1 with
RTS/CTS. EMOS owns reception and all canonical keyboard/sysvar effects.
This path needs neither parallel transfer nor an onboard-VDP/EDP direct link.

The current bench keyboard circuit is inoperative. Browser input is the chosen
next input source; diagnosing or repairing that circuit is not a prerequisite.
BC-001 remains active while this alternative is unqualified. This amendment
updates the original 2026-08-28 intake; its direct-link-first sequence is
superseded for focused keyboard input.

## Actor and ownership boundaries

1. REMOTE-001 owns browser focus, key-down/up, modifiers, repeat, layout,
   visible session state and focus-loss/disconnect release behavior. The
   browser describes events; it does not construct VDP wire packets or modify
   MOS memory. Browser/P4 event encoding is separate from the stock UART wire.
2. PORT-006 owns the input endpoint, connection lifecycle, bounded transport
   and session-access/Origin policy. Focus alone is not network authorization.
3. PORT-005 owns P4 processed-keyboard state, stock event/virtual-key mapping,
   relevant retained callbacks/control-key behavior and stock packet creation.
   Browser-originated input is emitted once toward EMOS. Non-echo protection
   applies to any later Agon-originated forwarded copy, not to browser keys.
4. PORT-008 owns UART transport and cross-component receiver qualification.
   EMOS implementation lives in agon-emos task INTEG-009. EMOS selects the
   accepted input source/session, owns receive/parser state, keyboard sysvars,
   the virtual keyboard map and the existing application keyboard APIs/hooks.
5. The onboard VDP keeps its existing physical-device and clock roles. It is
   not a relay for these browser keys and requires no firmware replacement.
6. Keyboard authority is meaningful operator authority: normal stock key
   behavior can reach the MOS command line and reset-key handling. Session
   admission/revocation must be explicit. This is not an implementation of
   a structured agent-command, updater or privileged automation API.

## CLI coordination

SETUP-005 K004 and ADR-0014 define case-insensitive `EMOS KEYINPUT browser`
and `EMOS KEYINPUT mainboard`, with a bare command reporting the source.
`extender` is reserved for future physical input and is unavailable. Keep
`SET KEYBOARD n` layout separate from source selection. K005 preserves the
keyboard source across mode changes, including returning to Legacy. K006
starts with mainboard input and restores preferences only through autoexec;
this increment adds no separate saved configuration.

## Single controlling browser

For the first version, P4 admits keyboard input from exactly one controlling
browser session at a time. Other browser sessions may view the display within
the video service's supported connection limits. Taking keyboard control is
explicit; focus alone does not take it from another session. P4 revokes the
old session, emits stock key-up packets for its held keys, then admits the new
session's input. Reject stale events from the previous owner so the two input
streams cannot mix. The UI identifies whether this browser has control.

This controls browser-session ownership without changing the stock UART packet
format or the selected EMOS keyboard source. No multi-player keyboard scheme
is implied. Qualify takeover with held modifiers and queued old-session events.

## Stock compatibility reference

Use the accepted AUDIT-004 inventory P013/P014 and A003–A005, and its
[primary packet trace](AUDIT-004/trace-primary-protocol.md) and
[MOS API trace](AUDIT-004/trace-mos-interfaces.md). Official references are
MOS v3.0.2 at `8336409351ee5314e02801a7b72a4f1bb5282519` and VDP v2.16.0 at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Both remain clean read-only sources.

P4 sends normal VDP packets, including key events and applicable keyboard
settings replies. EMOS derives its sysvars and 16-byte virtual keyboard map
from those packets. No new UART keymap download, raw memory write, diagnostic
ACK per key, or proprietary keyboard envelope is selected.

## Resident EMOS integration

INTEG-009 extends resident EMOS with normal compile-time linking and explicit
ownership boundaries. The Author rejected the proposed module loader and
runtime relocation; MOS-001 is cancelled in favor of resident EMOS extensions.
P4/browser work retains its existing ownership and stock UART contract.

## Work — keyboard slice

K002 now accepts explicit autoexec enablement and P4-only keyboard events for
the initial increment, with other onboard VDP communication retained. Focus
loss/disconnect makes P4 send stock key-up packets for held keys, then stop
keyboard delivery to EMOS. The Author accepted that cleanup for trial under
SETUP-005 K002; browser disconnect cleanup must also work without a final
browser message.

1. [ ] Resolve the remaining narrow SETUP-005 D003/D007 session, source-selection
   and receiver decisions. Record exactly which stock keys/configuration
   behaviors the first test covers and which remain unqualified.
2. [ ] Define focused display capture: key-down/up, modifiers and lock state,
   repeat ownership, locale mapping, browser-reserved shortcuts and unsupported
   input, with deterministic release on blur, hidden page, disconnect or reset.
   Do not consume keystrokes intended for other browser controls.
3. [ ] Consume PORT-006's bounded session transport and PORT-005's ordered event
   adapter. Bind the existing display UI without making full PORT-003
   completion or additional video routing a keyboard prerequisite.
4. [ ] Integrate with PORT-008/INTEG-009 and prove stock MOS-visible key reads,
   sysvars, virtual keymap and callbacks, including while no foreground UART
   transaction is running. Autoexec starts the identified test; applications
   must not configure UART1 or forward their own input back to P4.
5. [ ] Exercise focus/release/reconnect, held modifiers, repeat, rapid ordered
   transitions and reset recovery in host/emulator and paired hardware tests.
   Preserve ordinary boot/SD/clock and the currently selected VDU route. The
   first bounded qualification session does not silently activate an exclusive
   mode. Legacy accepts browser input only when explicitly selected under K005.

## Decision register

| ID | Decision | State / owner |
|---|---|---|
| REMOTE-001-K001 | Browser display focus is the keyboard capture boundary; P4 sends stock-compatible keyboard traffic to EMOS over existing UART1. No parallel or direct onboard link is needed. | Accepted by the Author, 2026-09-08; SETUP-005 owns the architecture. |
| REMOTE-001-K002 | On focus loss/disconnect P4 sends held-key releases, then goes quiet. Exact repeat, locale and browser-reserved-key mapping remain to be specified. | Release behavior accepted for trial, 2026-09-08; remaining mapping details open with PORT-005. |
| REMOTE-001-K003 | Input-session admission, source selection, revocation and first bounded test invocation. | Open; SETUP-005 with PORT-006 and INTEG-009. |
| REMOTE-001-K004 | One controlling browser; explicit takeover releases the old session's held keys before admitting new input. Other sessions may view within supported video limits. | Accepted by the Author, 2026-09-08; REMOTE-001/PORT-006 own session transfer, PORT-005 owns ordered key-up emission. |

## Later work retained

Structured agent control, a full remote-terminal product, broader network
exposure and optional direct-link research remain later use cases. LINK-001
owns any future link study; neither that research nor new circuitry gates this
keyboard increment. Mouse capture and Agon-originated EDU event forwarding
remain later PORT-005 scope. Full ordinary VDU routing to the browser is a
separate integration milestone; receiving keys does not redirect output.

## Accepted REMED-002 findings and retained risk

1. [ ] **F010:** REMOTE-001 owns remote product/session semantics. LINK-001 owns
   only optional direct-link research. A later new link needs its own accepted
   endpoint/hardware/qualification scope; this keyboard path uses existing
   hardware and the task owners above.
2. [ ] **F019:** Preserve remote-session provenance and EMOS authority at session
   admission and the selected UART1 ingress. The Author selected ordinary
   stock keyboard packets, so do not add remote-origin tags to those packets.
   Define the admitted keyboard session's authority before enabling it. Do not
   claim stock key packets can distinguish typed shell commands from other
   ordinary input, or that keyboard focus authorizes structured agent requests.
3. [ ] Keep any later structured command/result protocol and privileged agent
   permissions separate from this keyboard path; preserve existing agent flash,
   reset and deployment approval rules.
4. [ ] **R003:** With PORT-006, define access, Origin/cross-site WebSocket,
   session-presence and revocation behavior for the selected bench input
   endpoint. Broader/unattended exposure remains deferred and requires its own
   accepted policy and negative tests. Trusted LAN video acceptance alone does
   not authorize keyboard control.

## Review boundary

The Author approved freezing this documentation on 2026-09-08 and requested
a stop after committing. Implementation has not started. No new firmware,
fixture, protocol revision, deployment or hardware operation is authorized by
this documentation update. Existing artifact identities remain unchanged.
