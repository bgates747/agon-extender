# PORT-005 — Implement the processed-keyboard input adapter

## State

- Status: Browser-keyboard plan accepted for freeze, 2026-09-08; implementation not started.
- Started: -- (implementation has not started).
- Finished: --

## Intent and ownership

P4 accepts processed browser keyboard events from REMOTE-001 through the
PORT-006 network boundary. The adapter maps them to the retained VDP event,
virtual-key and modifier vocabulary, updates EDP-local keyboard state and
callbacks, and emits ordinary stock keyboard packets through PORT-008's UART
sender. EMOS alone processes those packets into canonical eZ80 keyboard state.

This supersedes the earlier immediate proof-of-concept assumption that an
EDU-aware Agon application must first read onboard input and forward it to P4.
That aware-application adapter and mouse injection remain later scope. A
forwarded copy must not echo back as a duplicate event; this non-echo rule does
not suppress browser-originated key packets.

## Authority and bounded reference

1. SETUP-005 D003/D007 and ADR-0014 select browser → P4 → EMOS over r03 UART1.
2. ADR-0013 decisions 26–28 preserve processed-input integration and omit
   physical PS/2 drivers. Existing vendored source remains intact; pure stock
   key/event definitions may inform the browser adapter without enabling a
   physical keyboard engine.
3. AUDIT-004 P013/P014, A003–A005 and its primary/MOS traces establish the stock
   packet and host effects. Use the source-qualified notes where official
   documentation differs from the selected source; do not repair upstream
   behavior incidentally in this increment.
4. Official `agon-docs/docs/mos/Keyboard.md`, `mos/API.md` and
   `vdp/System-Commands.md`, stock MOS `src/vdp_protocol.asm` and
   `src/keyboard.asm`, and VDP `video/vdu_stream_processor.h`/`video/vdu_sys.h`
   bound the implementation. AUDIT-004 retains exact commit links.

The accepted CLI contract in ADR-0014 uses `EMOS KEYINPUT browser` or
`mainboard` to select the source and reserves `extender` for future hardware.
The runtime `SET KEYBOARD n` layout must apply consistently to the selected
path and survive mode changes. Autoexec alone restores settings across boots;
do not add a separate saved configuration. Do not conflate layout with source,
or add numeric source codes.

## Required keyboard outcomes

SETUP-005 K002 now selects autoexec enablement and P4-only keyboard input for
the first increment. On focus loss/disconnect, P4 sends stock key-up packets
for held keys, then stops keyboard delivery to EMOS. The Author accepted this
cleanup for trial; items 4 and 6 must verify it even after abrupt browser loss.

1. [ ] Preserve keycode, modifier bits, FabGL/vdp-gl virtual-key identity and
   down/up state. Stock event wire form is `81 04 keycode modifiers vkey down`.
   It is not an ASCII-only terminal stream.
2. [ ] Preserve relevant retained VDP event variables, callback ordering,
   control-key and paged-mode semantics. Use the real stock packet serializer
   and UART adapter rather than a fixture-generated substitute reply.
3. [ ] Specify and test locale, repeat/LED state, control-key setting and
   current-key-state query behavior for the selected first keyboard scope.
   Applicable stock commands include `23,0,&81`, `&88`, `&98` and `&99`.
   The settings reply is `88 05 delay_lo delay_hi rate_lo rate_hi led`;
   EMOS owns resulting settings sysvars. No physical LED claim is implied.
4. [ ] Maintain ordered key transitions under backpressure. Release held keys
   and modifiers under the accepted blur/disconnect/session-reset policy;
   choose one repeat authority to avoid browser/P4 double repeats. On explicit
   browser takeover, emit the previous owner's held-key releases before any
   new owner's input; do not let queued old-session events restore those keys.
5. [ ] Feed the UART stock event stream to EMOS; never transmit a proprietary
   sysvar/keymap image or write MOS memory from P4. EMOS's existing parser,
   keymap handler and application APIs remain the compatibility destination.
6. [ ] Test key-down/up, multiple held keys, modifiers/locks, repeat, rapid
   transitions, callbacks, query/settings effects and focus/disconnect cleanup.
   Report exactly which cases are covered before claiming keyboard parity.

## Resident EMOS integration

INTEG-009 extends resident EMOS with normal compile-time linking and explicit
ownership boundaries. The Author rejected the proposed module loader and
runtime relocation; MOS-001 is cancelled in favor of resident EMOS extensions.
P4/browser work retains its existing ownership and stock UART contract.

## Dependencies and gates

REMOTE-001 owns browser/session semantics; PORT-006 owns network delivery;
PORT-008 and agon-emos INTEG-009 own UART/EMOS integration. SETUP-005 resolves
input-source selection, so UART0 and UART1 cannot race to publish conflicting
keyboard state. QUAL-001 records the bounded keyboard obligations; finishing
its entire matrix is not a prerequisite for this increment.

SETUP-004 and PORT-002's accepted source inventory are references, not new
surveys to restart. No parallel transport, physical keyboard repair, direct
onboard-VDP link, complete MOS Modules framework, mouse implementation or completion of
all display/audio work is required. Keep autoexec invocation and video-mode
selection under BC-001. Documentation review/freeze precedes coding and new
artifact identities retain the normal Author-approval policy.

## Retained REMED-002 risk

1. [ ] **R002:** The inherited `thread_safe_variant_deque` coalesces events by
   type and packet generation can read mutable current state. Before selecting
   an injection queue, prove that key-down/up, modifiers and repeat cannot be
   collapsed, reordered or replaced by a later event's state.
2. [ ] Reuse retained mechanisms only where ordered-event fixtures establish
   correctness; otherwise use an explicit ordered input representation while
   preserving stock callbacks and emitted packet semantics. Later mouse cases
   remain separate scope.

Later aware-application EDU injection retains versioned command definitions,
EDP-local updates and non-echo behavior. It is not the browser keyboard's
critical path. Exact evidence/provenance for R002 remains in REMED-002 and its
accepted integrity audit.
