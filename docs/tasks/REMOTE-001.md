# REMOTE-001 — Develop browser keyboard and remote EMOS control

## State

- Status: Physical findings reviewed by Author, 2026-09-09. Browser repairs are deferred behind PORT-015 direct USB keyboard input. Stale-time lease defect, video stalls, latency and wider qualification remain open.
- Started: 2026-09-08 (scope reconciliation); implementation 2026-09-09.
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
Guarded Agon installation and paired P4/browser qualification are next.

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
than inherit the defective browser lease. Resume browser work after the first
USB/normal-CLI proof or subsequent Author steering.
