# REMOTE-001 — Develop browser keyboard and remote EMOS control

## Current plan — browser capture over the working Extender input path

**Behaviour contract frozen by Author, 2026-09-19. B04 deployed; initial human typing review passed, UI corrections pending.** Add an explicit
Capture keyboard / Release keyboard toggle to the existing video page, backed by
the working processed-key input route used by Extender USB and host injection.
Retain installed video codecs, fullscreen controls and direct screen-text access.
The historical implementation below is evidence, not the new build baseline.

### Accepted behaviour

1. Start released. Clicking Capture keyboard explicitly requests ownership; show
   captured only after P4 admission succeeds. Display a clear active indicator.
2. While captured, send key-down/key-up events through P4's existing processed-key
   serializer to EMOS. Capture does not switch Legacy/ExCom or change VDU routing.
3. Release button, focus loss, hidden page or disconnect releases all browser-held
   keys. P4 handles expiry/disconnect even when the browser cannot send cleanup.
4. Returning focus or reconnecting leaves input released; capture must be explicit.
5. Place controls outside the video image. Screen-text HTTP reads remain independent
   of both video viewing and keyboard ownership.
6. Use a separate browser-to-P4 keyboard WebSocket. Capture requires input
   admission, not an active video connection. Input connection loss releases
   browser-held keys; video-only connection loss does not itself revoke capture.
7. With Extender input admitted by EMOS, browser keys work in both Legacy and
   ExCom. Legacy output remains on mainboard VDP; the browser retains P4's image
   rather than mirroring mainboard output. The operator can type `emos excom`
   at the MOS prompt to restore P4 output without visiting the bench.

### Itemized work

- [x] B01 — Inspect retained browser implementation/tests at 1ce96dc and current
  remote-keyboard/USB path. Map reusable key conversion and cleanup logic; preserve
  rollback. Do not reinstate the retired networking implementation wholesale.
  Completed 2026-09-19: [source review and checks](REMOTE-001/B01-review.md).
- [x] B02 — Specify browser transport and ownership alongside host injection and
  physical USB. Resolve competing captures, physical takeover and source-specific
  releases. Current host endpoint rejects browser Origin: define a deliberate
  browser-facing admission contract instead of merely removing that check.
  Behaviour settled in B02-D01–D06; B04 must define and test the browser-specific
  handshake/wire admission without weakening the host-only endpoint.
- [x] B03 — Specify key mapping, modifiers, locale, held keys, repeat ownership,
  browser-reserved shortcuts and fullscreen interaction. Document unsupported keys
  visibly. Reuse existing stock-compatible UART encoding and EMOS admission.
  Behaviour settled in B03-D01–D09. Browser/platform qualification remains B05/B06.
- [x] B04 — Implement toggle/UI and P4 adapter with bounded queues, orderly key-up
  cleanup, stale-session rejection and correct wrap-safe lease timing. Keep the
  video service independent of input session expiry and failed input requests.
  Implemented locally: [wire contract, tests and remaining gates](REMOTE-001/B04-implementation.md).
- [ ] B05 — Test mapping and state transitions: down/up, modifiers, held movement,
  release while held, blur, hidden tab, disconnected network, page reload, takeover,
  physical input and host-agent input. Reproduce the historical stale-time defect
  as a regression test. Confirm screen readback leaves browser control intact.
- [x] B06 — Build and stage on the existing bench; verify firmware and web assets.
  Check CLI typing/editing and game held-key input, with video active. Measure input
  delivery separately from visible response; compare against the current baseline.
  Deployed 2026-09-19: [bounded smoke receipt](REMOTE-001/B04-deployment.json).
  CLI marker verified; performance and broader human checks remain B07.
- [ ] B07 — Human browser acceptance, then document the selected interface and
  final bench state. Leave ExCom for remote review. Retain failed evidence and
  rollback; publication follows the Author's review.

### Human review — 2026-09-19

Author reports no perceptible typing latency and working keyboard Caps Lock
toggling. These are qualitative observations, not instrumented latency results.
Physical USB takeover is explicitly untested; Author will test it later. Overall
acceptance remains partial: focus decoration clips edge text, fullscreen no longer
enlarges the image correctly, and surrounding controls/diagnostics are distracting.

### UI follow-up — implemented locally, review pending

- [ ] C01 — Local UI implementation and Chromium checks complete under the [UI cleanup contract](REMOTE-001/C01-ui-cleanup.md); P4 deployed and CLI smoke passed; fullscreen capture/escape failures diagnosed, awaiting remaining Author feedback.

| Decision | State | Scope |
|---|---|---|
| C01-D01 — Presentation cleanup | Accepted 2026-09-19 | No inset focus border; enlarge fullscreen image with aspect preserved; one clear video surface; Capture replaces the URL slot; connection status below Connect; resolution and presented fps beside branding; remove ordinary debug clutter. |
| C01-D02 — Manual lock controls | Accepted 2026-09-19 | Remove manual lock selectors and software overrides entirely, including secondary menus. Host-reported state remains authoritative; preserve working keyboard Caps Lock and distinguish unknown from off through concise input status. Supersedes B03-D08. |

### Decision register — accepted behaviour

The Author settled the behaviour through one-at-a-time questions. B04 is deployed with partial human acceptance. This register owns the accepted decisions; historical policies
below do not override it. The decisions below remain accepted except B03-D08, superseded by accepted C01-D02. No UI contract decision remains open.

| Decision | State | Contract or question |
|---|---|---|
| B02-D01 — Transport | Accepted 2026-09-19 | Separate keyboard WebSocket; preserve video protocol and host-only RPC contract. Separate connections still share P4 resources, so this is not a latency guarantee. |
| B02-D02 — Display independence | Accepted 2026-09-19 | Browser input remains usable in Legacy and ExCom when EMOS admits Extender input; video connection is not a capture prerequisite. |
| B02-D03 — Physical USB takeover | Accepted 2026-09-19 | Physical USB keypress takes precedence: P4 discards queued browser input and releases browser-held keys before emitting the physical press; browser requires explicit recapture. |
| B02-D04 — Browser versus host automation | Accepted 2026-09-19 | Explicit browser Capture overrides host-agent input. P4 cancels pending agent events and releases agent-held keys before admitting browser input. Agent keyboard acquisition receives busy while browser capture is active; release permits a fresh agent session, not automatic replay. Physical USB precedence remains unchanged. |
| B02-D05 — Competing browsers | Accepted 2026-09-19 | Latest explicit browser Capture wins, subject to physical USB precedence and input admission. P4 revokes the previous browser, discards its queued input and releases its held keys before admitting the new owner. Stale events cannot regain ownership. |
| B02-D06 — EMOS source naming | Accepted 2026-09-19 | `EMOS KEYINPUT extender` admits the common P4 source for USB, browser and agent input. P4 owns provider arbitration; all use the same stock-compatible keyboard packet format without a provider identifier. Browser capture does not issue or require `EMOS KEYINPUT browser`. |
| B03-D01 — Repeat ownership | Accepted 2026-09-19 | P4 generates browser held-key repeats using the Agon's configured delay/rate, following the existing USB repeat policy. Browser sends press/release transitions and suppresses its automatic repeated key-downs. |
| B03-D03 — Interactive pacing | Accepted 2026-09-19 | Human keypresses are not subject to agent automation's fixed 20 ms spacing. P4 delivers browser transitions promptly through the existing owner path, retaining UART flow control, ordering and bounded queues. Agent automation pacing is unchanged; held-key repeat follows configured delay/rate. |
| B03-D02 — Locale | Accepted 2026-09-19 | Browser reports physical key positions; P4 translates using the Agon's selected `SET KEYBOARD` locale, consistent with USB. Initially support the existing UK/US mappings; do not silently substitute the Mac's character interpretation. |
| B03-D04 — Caps Lock ownership | Accepted 2026-09-19 | Follow the active input provider, not a global P4 override. Browser Capture supplies the browser host's Caps Lock state when available; subsequent browser key events keep it current. Physical USB takeover restores that provider's own state. Browser support is cross-platform, not Mac-only; indicated and effective state must agree. |
| B03-D05 — Captured application keys | Accepted 2026-09-19 | Tab and Escape are essential Agon application keys. While captured, forward their events and suppress browser default actions where the browser delivers cancellable events. Neither key intentionally releases capture. Explicit Release and actual focus/session loss retain their agreed behaviour. Browser/OS-reserved events that never reach the page cannot be promised; qualify fullscreen Escape behaviour and document limits. |
| B03-D06 — Caps state absent at Capture | Accepted 2026-09-19 | Show Caps Lock as unknown until the first reliable keyboard event supplies it; synchronize before translating/delivering that key. Never silently treat unsupported reporting as known off. |
| B03-D07 — Other locks and keypad | Accepted 2026-09-19 | Num Lock and Scroll Lock follow the active provider's state like Caps Lock; numeric-keypad behaviour follows Num Lock. Extend current limited mapping and USB indicator synchronization accordingly. Unknown reporting must not silently mean off. |
| B03-D08 — Unavailable lock reporting | Superseded by C01-D02 | Original manual fallback was withdrawn by Author on 2026-09-19 to reduce clutter and avoid software/keyboard state divergence. |
| B03-D09 — Fullscreen control access | Accepted 2026-09-19 | Mouse movement to the bottom edge reveals a normally hidden strip containing Release keyboard and Exit fullscreen, inside the fullscreen container and outside the Agon image. Do not use the top edge, avoiding browser fullscreen notices. Controls beside the video are the accepted fallback. Preserve Tab/Escape as application keys where supported. |

Fullscreen review: current `web/app.js` requests fullscreen on `#video-panel`,
which contains only the canvas; controls are siblings in `index.html` and so
are excluded from element fullscreen. A control strip must be inside the chosen
fullscreen element, outside the rendered image. Merely reusing the existing
button will not fix access. Browser-window fullscreen is a separate host mode;
`document.exitFullscreen()` controls page-requested element fullscreen only.
Keyboard Lock can help deliver reserved keys but support/secure-context
requirements vary; `preventDefault()` alone is not a universal guarantee that
Escape stays in fullscreen. Qualify supported modes and keep explicit mouse
access to release/exit. References:
[Keyboard Lock](https://developer.mozilla.org/en-US/docs/Web/API/Keyboard/lock),
[Fullscreen API](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API).
The bottom-reveal/side-fallback design is frozen; implementation is in progress.
Keyboard Lock/platform limits remain a
qualification requirement, not a promise that all browsers expose Escape.

Caps feasibility: W3C UI Events defines `getModifierState("CapsLock")` on
keyboard and mouse events; it is event-associated state, not an unrestricted
global keyboard query. Capture can sample its trusted activation event where
supported, then refresh from trusted keyboard events. Actual reporting differs
across browser/host combinations and must be tested; a returned false alone
cannot distinguish unsupported reporting from a known off state.
[UI Events](https://www.w3.org/TR/uievents/),
[MDN modifier-state support](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/getModifierState).

Physical USB detail: the current `usb_boot_keyboard.hpp` tracks its own Caps
state but implements no LED writes. USB boot input reports do not supply an
independent lock-state bit; the USB host maintains state and sends LED output
reports. Meeting B03-D04's indicator requirement therefore includes implementing
and qualifying physical LED synchronization, while keeping its state separate
from browser state. Do not claim the current keyboard already satisfies it.
See [USB HID 1.11, Appendix B](https://www.usb.org/sites/default/files/hid1_11.pdf).
Include opposite-state browser/USB handover, browser-to-browser handover,
Caps changes during capture, capture by mouse/keyboard, and USB reconnect in
B05/B06. This scopes future work; no keyboard or firmware was changed.

B02-D03 preserves the current physical/host takeover model. Its
prerequisite is source-specific cleanup before the physical event reaches the
shared processed-key queue; the tradeoff is that a bench keypress interrupts
remote control. B02-D04/D05 preserve that ownership rule. ADR-0022 is complete
for this behaviour scope; implementation and qualification remain outstanding.

### Implementation and acceptance boundaries

1. Preserve installed candidate provenance and rollback before producing a new
   build. Retain codecs, fullscreen display and screen-text access; do not restore
   the historical network service. No EMOS wire/receiver change is indicated.
2. P4 must bind each browser admission to a fresh session/generation and reject
   stale events. Define bounded message/queue sizes and lease timing before
   implementation; retain signed modular timer comparisons. Capture acknowledgement
   means input admission, not eZ80 execution. Network handlers never write UART.
3. Qualify priority transitions with held modifiers and queued input: USB over
   browser over agent, latest browser capture, no stale replay, clean release,
   reconnect and layout/admission loss. Agent pacing and journals must retain
   their existing guarantees.
4. Qualify browser input with no video connection, in Legacy, and after typing
   `emos excom` at a verified MOS prompt. Separately test live video load and
   screen-text reads without revoking browser control.
5. Qualify repeat, UK/US letters/editing/F keys, Tab/Escape, keypad and lock-state
   handover. Extend physical USB state/LED handling; test host-reported
   browser lock state and unknown initial state without manual overrides. Keep unavailable reporting
   distinguishable from off; do not silently translate a lock-sensitive key
   using a guessed state.
6. Test fullscreen bottom reveal and side fallback, release/exit accessibility,
   focus cleanup, and browser-reserved key limits. Record the actual browsers,
   operating systems and secure-context requirements tested. Do not claim broad
   cross-platform acceptance from a single browser or mocked DOM test.
7. Record product/host/emulator checks before staging hardware under the existing
   bench instructions. Contract agreement alone does not start implementation,
   authorize a flash or establish qualification. The Author froze the contract;
   execution authorization remains separate.

### Review progress — 2026-09-19

Author subsequently authorized B01 review. It is complete; implementation and
bench work have not started. Current processed-key mapping/serialization and
EMOS reception are reusable. Retired BrowserKeyboard still reproduces its
false-expiry defect; current host ownership fixes the arithmetic but retains
automation-only pacing/no-repeat policy. Preserve installed codec/source overlay
and rollback. Subsequent Author answers settled B02/B03 in the register above
and were promoted into ADR-0022; its scope is now complete, not implemented.

## Historical state and evidence (superseded priority)


- Status: Browser-input implementation deprecated by Author, 2026-09-09;
  future input work remains deferred in favor of selectable mainboard/Extender
  USB keyboard input. Active browser and network service are video-only.
  Resume only on explicit reprioritization. Retain the stale-time lease defect,
  video stalls, latency findings and wider qualification work.
- Started: 2026-09-08 (scope reconciliation); implementation 2026-09-09.
- Finished: --

## Retained browser increment — deferred

After the first ExCom hardware attempt, the Author explicitly requested rolling
back browser keyboard/release behavior before adding functionality. The shared
page, HTTP service and snapshot pool no longer carry this experiment. The
`p4-browser-typing` composition is retired and blocks new builds; historical
candidate `1ce96dc` retains the measured implementation and its UI tests for
reproduction. This does not repair or close I001/I002. The current video-only
rollback is tracked under PORT-008/PORT-006; the requirements below describe
the deferred input path rather than active product behavior.

The earlier increment selected keyboard capture while the browser display has
focus. It is no longer the immediate input goal. Browser events travel through the existing P4 network
service; P4 processes them into stock-compatible VDP keyboard packets and
sends them to EMOS over the existing r03 UART1 connection at 1152000/8N1 with
RTS/CTS. EMOS owns reception and all canonical keyboard/sysvar effects.
This path needs neither parallel transfer nor an onboard-VDP/EDP direct link.

The mainboard keyboard circuit remains inoperative; P4 native USB now supplies
the working replacement. Browser repair is not a prerequisite for selectable
mainboard/Extender input. This retained browser amendment
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
PORT-015 now implements `extender` in a separate native-USB composition; it is
not a second acquisition provider in the browser candidate. Keep
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

## Earlier review boundary

The Author froze the documentation on 2026-09-08. Subsequent explicit
authorization starts the implementation recorded below; the documentation
freeze alone did not authorize deployment. Human review of the new executable
behavior remains pending.

## Current implementation increment — 2026-09-09

Author authorized focused typing and preapproved versioning. Work now implements
an autoexec-launched SD typing program using public EMOS keyboard APIs and the
resident text gateway. EMOS v0.1.9 shares its UART1 IRQ receiver with foreground
text transactions; browser-keyboard-probe-r01 selects the paired P4 composition.
Registry r40 is draft. No ordinary CLI/ExCom routing is claimed. Bounded research
and implementation notes live in the ignored agents/precis/browser-typing.md.
Review and paired hardware acceptance remain pending; earlier freeze wording
above records the preceding documentation gate, not a current prohibition.

### Bounded r01 behavior under review

1. The browser explicitly requests control with **Capture keyboard / take
   control** (or a click in the live display). P4 accepts only while EMOS has
   selected browser input and completed locale/General Poll admission. Canvas
   focus gates subsequent keys; viewing alone sends no input.
2. `/keyboard` is a same-origin WebSocket on the existing trusted bench LAN.
   P4 checks Host and Origin against its current leased IPv4 address before
   upgrade. There are no credentials, TLS, saved tokens or structured commands
   in this bounded trial. This is an explicit local control opt-in, not a claim
   of protection from other trusted-LAN hosts or arbitrary non-browser clients.
3. Binary network messages are `T` (take), `H` (presence), or four bytes
   `K physical-id modifiers down`. Physical IDs follow the supported USB HID
   positions but are a browser/P4 encoding, not USB hardware traffic. P4 replies
   `A` only to a syntactically accepted, owned message. This acknowledgement is
   never forwarded on UART and is not proof of EMOS delivery. `R` releases.
4. The browser sends one message at a time, at most 64 queued messages, with a
   1.5-second acknowledgement deadline and 500 ms presence messages. P4 has a
   64-event queue and a two-second lease checked by its process task independently
   of HTTP progress. Overflow, malformed owner traffic, blur, hidden document,
   disconnect and expiry revoke. P4 releases consumed held keys before the next
   owner's queued events. An old owner cannot refresh an expired lease.
5. This test explicitly selects `SET KEYBOARD 1` (US). P4 maps physical letters,
   digits and punctuation, Shift/Caps and control letters. Browser repeat is the
   initial repeat authority. Tab stays browser navigation; Alt/Meta shortcuts
   release capture and stay local. Unsupported keys and composition/IME text
   are not converted. No other locale or complete international keyboard claim.
6. The SD program formats and echoes input through the existing resident text
   gateway. EMOS receives keys throughout each acknowledged text transaction.
   Enter starts a new line; Backspace erases within that line; lines wrap at
   70 characters. Escape exits; five minutes ends the session without a key.
   The program always removes its callback and requests mainboard input before
   returning. A queue/transport/clock failure reports FAIL. It writes one result
   byte and never changes video mode. The optional preview mirrors only text
   already acknowledged by the UART peer onto mainboard VDU for emulator review.
7. Hardware procedure and result meanings are defined beside the r03 design in
   `tests/browser-keyboard-probe-r01.md`. Human emulator review, physical typing,
   repeated reset and browser release/reacquisition remain unaccepted. Full CLI
   display switching and ExCom activation remain separate work.

Automated checks now cover stock virtual-key constants, host session mapping,
repeat and release ordering, late/stale input, queue overflow, actual Chromium
focus and acknowledgement loss, retained P4 key serialization, EMOS IRQ/text
interleaving and an absent text acknowledgement with MOS return. Shared network
F003/F012 containment is exercised by fault-injecting the maintained target
method bodies. P4 compiles/links; this does not substitute for paired hardware.

### Validation limitation discovered during preparation

The artifact-registry/template/VDP-identity checks pass. The repository-wide
version validator stops at an inherited r02 connectivity/profile hash mismatch.
Both files match this task's starting HEAD byte-for-byte; the r02 circuit remains
on hold. No r02 hash, frozen wiring or old evidence was silently rewritten to
make that unrelated check pass. This does not change the r03 typing test scope.

## Graphical typing review accepted — 2026-09-09

The Author supplied the review screenshot showing `aB3?`, newline `z`,
BROWSER TYPING PASS (8 edited characters), mainboard input and the MOS prompt.
This accepts the bounded graphical result, not physical browser typing.
Standing version preapproval advances registry r41 and the unchanged EMOS
v0.1.9/browser-keyboard-probe-r01 implementation to candidate for clean builds.
The reviewed draft builds and their results retain their original identities.
At that checkpoint, guarded Agon installation and paired P4/browser
qualification were next; subsequent results follow below. Browser input is
now deferred as stated in this task's current status.

## Physical typing checkpoint — 2026-09-09

The Author confirms that typed characters appear in the browser and that Enter
and Backspace work. Preserve this functional milestone while keeping latency
and apparent focus/capture loss unresolved. The Author's possible P4 connection
loss explanation is unverified. The operator record lives beside the design:
[operator feedback](../../hardware/designs/light2-harness-r03/tests/REMOTE-001-2026-09-09-04-46-41Z/operator-feedback.md).
Escape/MOS return and the on-card result byte remain unconfirmed for this run;
no full hardware PASS or qualification promotion is claimed.

### Next bounded investigation

1. [ ] **REMOTE-001-I001 — Responsiveness:** Measure browser event submission,
   P4 admission/UART delivery, EMOS text acknowledgement and frame presentation
   separately. Identify where the observed delay accumulates before changing
   timeout or buffering policy.
2. [ ] **REMOTE-001-I002 — Capture stability:** Distinguish DOM focus/visibility
   changes, browser acknowledgement timeout, P4 lease revocation and actual
   socket closure. Record the triggering reason and correlate it with I001;
   do not assume a network disconnect or simply lengthen deadlines.
3. [ ] After the bounded repair, repeat typing/editing, deliberate release and
   reacquisition, Escape/MOS return and Agon-only reset with the Author. Collect
   the result byte when the SD is next returned; do not require another hardware
   run merely to fill an unsupported claim about this first session.

The Author requested this checkpoint and a stop for the night. No investigation,
new firmware or additional hardware operation is included in this checkpoint.

## Morning connection-loss follow-up — 2026-09-09

The operator feedback now records keyboard socket closure preceding video
disconnection by 135 received frames, with reconnect/recapture restoring typing
without disturbing Agon. I002 must distinguish the socket-close initiator and
reason; ordinary DOM blur alone does not explain the first displayed message.
Escape/MOS return remains unconfirmed.

Bounded source inspection identifies a concrete scheduling hypothesis: video
frame sends and keyboard handling share the HTTP server task, while the typing
change sets socket send/receive timeouts to one second. Browser acknowledgement
and P4 owner-lease deadlines are 1.5 and 2 seconds respectively. Inspect send
duration, heartbeat/acknowledgement timing and owner-revocation reasons together
before selecting a repair. No measured root cause is claimed. Existing mocked
WebSocket UI tests do not cover this combined physical load; add representative
coverage with the eventual repair. No firmware or hardware changes accompany
this follow-up.

## Proposed measurement increment — I001/I002

**State:** Author authorized implementation and hardware preparation on
2026-09-09. Browser/P4 instrumentation and automated checks are complete;
operator measurements and findings are recorded below; repair review remains
pending. Physical recording-off comparison remains incomplete.

### Objective and scope

Locate visible typing delay and identify the initiator/reason of keyboard and
video socket closure in the current SD typing sample. Measure the existing
browser → P4 → EMOS/sample → P4 → browser path before choosing a repair.
This is not ordinary CLI/ExCom qualification, a stock-performance equivalence
claim, a timeout-policy change or a parallel-transport increment.

### Work items

1. [x] **I001-M1 — Define correlated checkpoints.** Browser records monotonic
   key-event, socket-send, acknowledgement, frame-receive and presentation
   timestamps. P4 records event admission, keyboard-packet UART submission and
   completion where observable, returned text receipt, render completion,
   frame identity, and video-send start/end. Document whether each checkpoint
   observes queue admission, driver completion or physical transmission; do
   not label a queued write as bytes already sent on the wire. Use event and
   session identifiers in diagnostic records without modifying stock VDP
   keyboard packets. Start with separated, single printable keys so the
   returned text can be associated unambiguously; discard ambiguous matches.
2. [x] **I001-M2 — Calculate intervals without synchronized clocks.**
   Browser measures event-to-acknowledgement and event-to-presentation on its
   own clock. P4 measures admission-to-acknowledgement handling, UART round
   trip, rendering and send duration on its own clock. A browser round trip
   includes server handling; it is not an exact one-way Ethernet measurement.
   Never subtract a P4 timestamp from a browser timestamp. Associate each
   rendered update with its actual video frame identifier so browser records
   refer to the frame containing the returned character, not merely the next
   received frame. Record superseded/dropped frames explicitly. Browser
   presentation instrumentation identifies a rendering submission/frame
   callback, not a measured physical monitor scanout; label that limit.
3. [x] **I002-M3 — Record connection lifecycle alongside timing.** P4 records
   heartbeat processing, owner-lease expiry/revocation reason, UART faults,
   socket send failures and durations, and socket closures. Browser records
   focus/visibility changes, acknowledgement timeout, intentional release,
   and WebSocket close code/reason/clean flag. Distinguish a locally initiated
   close from an observed peer closure; an abnormal close alone does not
   establish why the peer disappeared. Correlate these records with video
   sends to test the shared-HTTP-task scheduling hypothesis.
4. [ ] **I001-M4 — Keep instrumentation bounded and validate it.** Use bounded
   in-memory records with overflow counters and retrieve them after the
   observation; avoid per-key serial printing or synchronous diagnostic
   requests in the measured path. Record overhead and compare behavior with
   diagnostics disabled. Exercise real combined video/keyboard servicing;
   the existing fake-WebSocket tests do not establish scheduling under video
   load. Verify timestamp ordering, event/frame association, overflow handling
   and disconnect reason reporting with focused checks before deployment.
   Keep EMOS unchanged if P4 checkpoints suffice; propose any necessary
   resident instrumentation separately rather than assuming another MOS flash.
5. [x] **I001-M5 — Run one bounded operator session after preparation.** Read
   the machine-local bench instructions and active fixture constraints first.
   Record exact deployed identities and diagnostic settings under the version
   policy. Use the existing wiring, UART rate and SD typing application.
   Observe a short sequence of separated printable keys with video active,
   then normal typing and an idle interval within the sample's five-minute
   limit. Record sample exit separately from connection failure. If a
   disconnect occurs, retain the pre-close records and observe reconnect and
   recapture without resetting Agon. Coordinate the sole viewer with the
   Author. Use the analyzer only if software timestamps leave UART timing
   uncertain; analyzer acquisition is not a prerequisite for initial results.
6. [x] **I001-M6 — Report findings and stop before repair.** Report sample
   counts, typical and worst observed intervals, missing/ambiguous records,
   and closure ordering. Separate measured facts from hypotheses. Identify
   which interval dominates visible delay and whether HTTP send stalls
   coincide with lost keyboard service or video closure. If the failure does
   not recur, retain useful measurements but leave its cause unresolved.
   Propose the smallest supported repair for Author review; do not simply
   increase deadlines or claim full hardware qualification.

### Evidence and completion gate

Keep operator observations and resulting timing evidence beside the r03 design
under its existing tests directory, with exact provenance and machine-private
capture locations referenced through ignored local records. Update I001/I002
with conclusions and remaining uncertainties. This measurement increment is
complete when the Author can review correlated timing and lifecycle evidence
and a bounded repair recommendation, or a precise statement of what remains
unmeasured. Existing success with typing, Enter, Backspace and recapture remains
valid; Escape/MOS return is not inferred from it.

### Instrumentation checkpoint — 2026-09-09

1. Browser/P4 session IDs and ordered message records now correlate browser
   acknowledgement, P4 queue/UART/drawing activity and EVF sequence numbers.
   There is no stock UART format, EMOS binary, SD sample, timeout or cadence
   change. First guaranteed frame association is conservative and rejects
   ambiguous edits; it does not claim earliest physical visibility.
2. Source inspection found the existing 200000-us minimum browser snapshot
   interval. It differs from EVF's logical frame period and is a concrete
   possible component of visible delay. Measurement preserves it.
3. The new bounded recorder, renderer/snapshot/send checkpoints and after-run
   download live under the r02 procedure beside the r03 design. Same-clock
   analysis is in `scripts/analyze_browser_timing.py`. BTYPE/EMBOOT hashes on
   returned SD match prior deployment. Its result byte is 02 (timed exit),
   without a timestamp identifying which observation produced it.
4. Validation: P4 draft compiles/links. Actual Chromium WebSockets carry full
   640x480 frames and keys against a controlled host peer; injected serialized
   send delay is observed as acknowledgement timeout, closure and successful
   recapture/export. This tests measurement sensitivity, not physical P4
   scheduling. Existing keyboard mapping/retained serializer and focus/editing
   checks pass. Recorder concurrency/overflow/disable/lease-reason checks and
   synthetic deliberately different-clock analysis pass. Network send/failed
   registration containment covers all eight routes. Registry/template/VDP
   identity checks pass; inherited r02 hardware-profile limitation remains.
5. I001-M4 is complete for local automated checks; actual P4 overhead comparison
   remains part of operator observation. I001-M5 and findings/repair review
   remain open. Freeze the P4 measurement candidate before deployment; do not
   present an attention cue until it and the unchanged SD are ready.

### Instrumentation preparation defect and correction

The r02 candidate flashed and independently verified, but pre-handoff browser
validation did not receive frames. Passive serial capture showed a P4 HTTP
stack-protection fault in newlib snprintf formatting. The new trace handler
reserved a 2048-byte automatic export buffer inside the default 4096-byte
HTTP task stack, including control requests. This is an instrumentation defect,
not evidence of the Author's pre-existing failure. r03 moves the export buffer
to checked heap storage after observation; no task stack, transport timeout or
snapshot policy change is included. Retain the informative failed check and
exact candidate provenance. Repeat physical diagnostics/video validation before
operator handoff. Standing version preapproval covers r03 and registry r43.

### Measurement candidate handoff

r03 from commit 47e7bff was flashed and independently verified. A separate
short headless browser check received six actual P4 frames and successfully
exported matching snapshot/send records; the browser connection was closed
before handoff. The check did not take keyboard ownership or exercise Agon.
Evidence: `hardware/designs/light2-harness-r03/tests/REMOTE-001-2026-09-09-17-36-48Z/`.
I001-M5 now awaits operator input. The existing SD was verified and unmounted
without edits. No EMOS flash or Agon reset was performed.

Initial video-only medians were 118.217 ms per snapshot composition and
91.201 ms per send, with six submitted frames. They do not establish total
keypress latency. The 200000-us snapshot cadence check uses accumulated
logical boundary time, not a wall-clock five-fps guarantee. Runtime recording
off still retains hook clock/locking costs. Preserve these interpretation
limits when comparing the upcoming operator measurements.

### Immediate keyboard capture regression — 2026-09-09

The Author reports immediate capture failure with r03. Retrieved P4 records
show repeated socket opens/closes separated by only a few milliseconds, with
no keyboard_open/key_message records. Pinned IDF 5.5.5 httpd_uri.c explicitly
returns after WebSocket handshake callbacks without invoking the URI handler.
The r02/r03 diagnostic session allocation was in that skipped initial-GET
branch; the first message then had null context and failed immediately. This
is an instrumentation regression, distinct from the earlier r01 failure.

r04 moves allocation into the registered post-handshake callback. Add regression
coverage using the actual IDF dispatch branch and target handler, including
session cleanup, before rebuilding and verifying the physical endpoint. Keep
EMOS, SD application, UART bytes, deadlines and snapshot policy unchanged.
Standing version preapproval covers r04/registry r44. Original latency/closure
measurement remains pending after this preparation repair.

### Corrected keyboard callback physically verified

r04 from clean commit 1ce96dc was deployed and independently verified under
REMOTE-001-2026-09-09-17-58-10Z. A real browser/P4 check received six frames,
exported records, and confirmed keyboard_open plus first-message handling for
a non-owner heartbeat. The expected non-owner rejection followed; the former
missing-context path did not occur. No keyboard ownership or keys were injected
by the agent. Actual operator capture/typing still requires restarting the Agon
sample and reloading the page. EMOS, SD, wiring, UART and timing policy remain
unchanged. Original r01 latency/disconnection measurement remains open.

### Operator measurement and findings — 2026-09-09

Evidence and full interval/count/closure analysis:
[REMOTE-001-2026-09-09-18-00-44Z](../../hardware/designs/light2-harness-r03/tests/REMOTE-001-2026-09-09-18-00-44Z/README.md).
The unchanged raw download contains 2896 browser and 7541 P4 records, with no
overwrite. The Author typed at slow and normal cadence, recaptured after
releases, and reported video closure within Agon's five-minute session.

1. **I002: false keyboard expiry is reproduced.** Five reason-3 revocations
   occurred only 6.493–84.210 ms after accepted messages. The P4 loop caches
   its clock before potentially blocking VDU work; the HTTP task can publish
   a newer heartbeat before `pop` uses that old timestamp. Unsigned subtraction
   then falsely exceeds the two-second lease. A host reproducer using the
   actual class demonstrates this task ordering. This code exists in original
   r01, before instrumentation. The physical trace supports this cause but
   does not expose the cached argument itself.
2. **I002: P4 initiates video closure on send-budget failure.** Two partial
   frame sends exceeded the one-second budget, observed after about 1.66/1.63
   seconds because checks occur between blocking sends. Both correlate with
   browser video closure. Why those sends stalled remains unresolved. No
   browser ACK timeout or P4 UART failure is recorded. Missed heartbeats
   during those stalls do not explain the five premature lease revocations.
3. **I001: UART/EMOS echo is small; queue/display intervals are substantial.**
   Medians: P4 admission to UART submission 59.086 ms (109 matches), UART
   submission to echoed text 1.114 ms (109), snapshot composition 116.376 ms
   (1232), successful video send 89.726 ms (916). Ninety conservative
   guaranteed-containing frame matches give event-to-submission median
   422 ms, maximum 743 ms. These are different sample sets, not additive
   budgets or exact physical-display latency. Full counts/exclusions are
   recorded with the evidence.
4. **Review recommendation:** first correct lease timing across task
   interleaving while preserving true expiry, wrap behavior and held-key
   cleanup, then repeat paired typing. No EMOS or SD change is indicated.
   Keep video send scheduling and snapshot cost for the next bounded
   investigation. No original-behavior repair is implemented here.
5. I001-M5/M6 now have their measurement/report deliverable. I001-M4's physical
   recording-off comparison remains incomplete; cost counters cannot establish
   negligible total overhead. I001/I002 remain open until repairs and review.
   Escape/MOS return is not inferred. Stop for Author review before repair.

### Priority diversion accepted — 2026-09-09

The Author reviewed the measurement findings, then selected PORT-015's direct
USB keyboard input before browser repair work. Preserve this evidence and all
unresolved I001/I002 findings. No original browser-behavior repair has been
implemented; direct USB acquisition must use its own device lifetime rather
than inherit the defective browser lease. After USB CLI and gameplay passed,
the Author deferred browser input as an immediate goal. Resume only on explicit
Author reprioritization; completion of PORT-015 is not an automatic trigger.

### Current review hold — fullscreen diagnosis

Author reported capture loss when entering fullscreen and Escape leaving fullscreen
while captured. [C01-F01–F03 diagnosis](REMOTE-001/C01-ui-cleanup.md#fullscreen-feedback-diagnosis--2026-09-19)
records the reproduced explicit-blur/session-close path, native Escape limitation
and gaps in the original tests. The Author subsequently authorized the fullscreen-entry repair and accepted native
Escape exit for now. The explicit canvas focus transfer and capture-first entry/exit
regression pass locally. P4 deployment and human validation of this fix remain pending.


### Additional UI requests — documentation only

The C01 pending list now includes a green connected-state Connect button and a
header showing mode number, resolution, colors, nominal Hz and buffering mode,
followed by the existing Presented fps. Author explicitly requested no coding
yet; metadata availability must be checked before implementation.


### C02 authorized and deployed

Author authorized freeze, coding and P4 flashing. C02 now implements the green
Connect state, authoritative P4 display metadata and fullscreen-entry capture fix.
Local browser/concurrency checks and physical flash/assets/header verification
pass. Human review remains pending; Agon needs an operator reset to re-establish
keyboard admission after the P4 restart. No mainboard firmware or SD changes.


### Current disposition — browser/game input follow-up deferred

Author reports greater apparent input hangs in Rally than Nurples, with no earlier
Rally/browser baseline to establish a regression. Nurples Escape leaves fullscreen
first, then exits the game when pressed outside fullscreen. These observations
and the deferred investigation are retained in C01/C02-F01. Author directs moving
on to other priorities; no further browser/game diagnosis or repair is active.
This is deferral, not full browser-input qualification or blanket C02 acceptance.

## September21 comparison

Author reports newer firmware/browser regressed relative to the restored
September19 r01 checkpoint. [Mac observations](REMOTE-001/2026-09-21-mac-comparison.md)
record older-build figures and distinguish persistent game-input trouble. Author
requests restoration of latest pre-rollback image before their Linux comparison.

## September 21 cross-host comparison and Jukebox finding

[Mac/Linux observations](REMOTE-001/2026-09-21-mac-comparison.md) distinguish
presented frame rates, gameplay and keyboard response on the September 19
checkpoint. Latest pre-rollback P4 image was restored afterward.
[Tagged Jukebox review](REMOTE-001/JUKEBOX-INPUT-REVIEW.md) records the ExCom
input failure and successful Legacy controls for classic v0.9.6-beta and
v0.11.0-beta. No direct timer/UART vector collision found; cause unresolved.

## Consolidated human comparison — 2026-09-21

[Tabular observation summary](REMOTE-001/2026-09-21-observation-summary.md)
compares the Author's Mac/Chrome and Linux/Firefox observations, preserves the
mode 20 sequence, separates older/newer firmware, and includes both Jukebox
versions' Legacy/ExCom controls. Agent measurements are separately labeled.
