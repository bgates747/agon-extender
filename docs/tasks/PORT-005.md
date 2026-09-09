# PORT-005 — Implement the processed-keyboard input adapter

## State

- Status: Bounded controlled-sender hardware proof passes, including two additional Agon-only resets; focused browser/session integration is implemented for review; physical typing remains pending.
- Started: 2026-09-08 (P4 controlled-key sender).
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


## Current bounded implementation — controlled P4 keys

The Author authorized the P4 sender after freezing the resident EMOS receiver,
API and recovery emulator checkpoints (EMOS 55466d7; Extender a29ae36).
Keep EMOS v0.1.8 unchanged. Implement an explicitly selected P4 processed-input
binding, with a small controlled event source for first sender qualification.
The ordinary disconnected/browser display composition still has no input source.
Browser focus, network admission, layout translation and repeat generation are
later integration work, not prerequisites for this controlled sequence.

Official Keyboard/API and VDP System-Commands documentation was reviewed first.
At the pinned VDP v2.16.0 source, `handleKeyboardAndMouse` publishes event
variables, invokes CALLBACK_KEYBOARD, applies control/paged semantics and drains
`processEventQueue` after EACH input item. That queue coalesces event types and
reads current variables. Preserve that per-input drain; queue complete processed
input snapshots outside it, never several mutable states before one drain.
`send_packet` remains the sole wire serializer. The existing P4 hook currently
returns without acquiring keys; its no-device helpers retain no locale.

1. Add a bounded FIFO of processed key snapshots. Its process-task consumer
   presents one VirtualKeyItem at a time through the existing stock helper.
   Preserve callbacks, per-event serialization, modifiers and down/up/repeats.
   Reject full/invalid input rather than silently replacing queued keys.
2. Bind the retained parser to a bounded UART test Stream. EMOS sends its
   ordinary locale and matched General Poll admission; P4 serializes replies
   and key frames from the same process task. Do not introduce per-key ACKs,
   application UART access or a proprietary keyboard packet.
3. After admission, emit twelve paced events: a down/up, held Shift with three
   B downs, B/Shift releases, 7 down/up and Enter down/up. The autoexec-loaded
   eZ80 test observes callback payloads, counts, sysvars and map through public
   APIs, with a finite clock deadline and mainboard cleanup on every exit.
4. Verify event ordering/callback effects with maintained host code, compile
   the P4 composition, and review the SD fixture in the emulator before source
   freeze. Later clean candidate/deployment and real UART capture gates apply.

The first P4 helper retains accepted locale/settings bytes but does not claim
browser layout translation, physical LEDs or a typematic generator. Explicit
processed repetitions come from the controlled source. Full source-aware raw
VDU keyboard-control routing remains EMOS W3-K001. Real focus/disconnect/
takeover and abrupt resets remain unqualified. No physical action is authorized
by starting this implementation. The Author approved `uart-keyboard-probe-r01`
and registry r38; both P4 sender and SD observer remain draft.

### Implementation and bounded checks

`extender/input/processed_keyboard.hpp` holds sixteen complete snapshots with
one process-task owner. `getKeyboardKey` supplies the retained handler; its
callback/event drain and serializer are unchanged. The explicit `p4-keyboard`
composition enables this binding; ordinary `p4-browser-vdp` still has no input.
Network producers must marshal to the process task before using this FIFO.
No concurrent producer, browser session or full mode activation is claimed.

`tests/processed_keyboard_test.py` passes burst down/up and repeated-down
ordering through the actual coalescing event queue, callback order, packet
editing/suppression, control/paged effects and retained settings. Its variable
and context boundary is faked; it is not full VDP execution. The maintained
`setVDPVariable` schedules VK/DOWN events even for repeated values. The helper's
`isVKDown`/injection placeholders are still unavailable: raw `&99` queries
remain unimplemented for processed input and must not be represented as parity.

`tests/keyboard_hardware_test.py` exercises the real orchestration/Stream with
faked UART/GPIO: two successful cycles after long idle, a midstream CTS pause,
invalid input, blocked-TX timeout, absent/partial admission, UART error,
short enqueue and unexpected post-admission traffic. Every failure releases
P4 outputs and remains latched; successful completion rearms after EMOS source
release. This is host sequencing evidence, not electrical qualification.

The paired EMOS CLI test passes twelve serializer-produced stock packets and
the real resident ISR/parser, callback/count, held-key map and mainboard prompt.
A second run admits the source but withholds all keys; the SD observer reaches
its deadline, removes its callback and returns to mainboard input and MOS.
EMOS v0.1.8 and the reviewed UART1 emulator runtime remain byte-identical.
The isolated runtime exchanges bytes and cannot prove physical baud or CTS/RTS.
The supplied screenshot confirms graphical PASS; the Author subsequently froze the checkpoint and approved candidate preparation.

The [paired hardware sheet](../../hardware/designs/light2-harness-r03/tests/keyboard-sender.md)
owns the first physical sequence and future results. Candidate production,
guarded EMOS installation, P4 deployment and capture preparation follow source
review; no device, SD card or installed firmware has changed in this increment.

Identified P4 draft `uart-keyboard-probe-r01-b2026-09-09-02-38-20Z` compiles and its BIN/ELF/factory outputs contain the exact requested identity and draft status. The reviewed SD draft is `uart-keyboard-probe-r01-b2026-09-09-02-36-43Z`.

The Author supplied the matching graphical screenshot: unchanged EMOS v0.1.8,
SD/CLOCK PASS, twelve-packet/callback/counter PASS, held-key/map/modifier/repeat
PASS, mainboard input restored and final MOS prompt. The controlled peer also
records twelve keys and PASS. This confirms the bounded emulator result;
the source checkpoint is frozen and physical P4/Agon qualification remains pending.

The Author accepted the graphical result and explicitly authorized freezing this bounded sender/observer checkpoint, then preparing the paired hardware test. Reviewed builds retain their original draft status; candidate packaging and physical qualification follow separately.

Candidate preparation and SD handover are recorded beside r03 in `PORT-005-2026-09-09-03-10-57Z`. Both exact candidate endpoint builds and the SD observer pass their applicable automatic checks. The P4 is staged only; physical MOS installation, P4 deployment and paired qualification remain pending. The generic builder portability correction preserves the reviewed runtime executable hashes exactly.

The Author subsequently reported a successful EMOS flash. The returned card's
consumed payload matches the candidate; rollback files remain intact. The
verified, safely unmounted smoke/keyboard-test SD and installation report are
recorded in [PORT-005-2026-09-09-03-19-20Z](../../hardware/designs/light2-harness-r03/tests/PORT-005-2026-09-09-03-19-20Z/README.md).
P4 candidate hashes and stable USB identity pass read-only reinspection. P4
flashing awaits explicit authorization; paired keyboard results remain pending.

The Author then authorized P4 flashing. [PORT-005-2026-09-09-03-22-37Z](../../hardware/designs/light2-harness-r03/tests/PORT-005-2026-09-09-03-22-37Z/README.md)
records the exact candidate written, independently verified and observed in
clean WAIT at 1152000 baud on the selected UART pins. Both endpoint candidates
are installed and the prepared capture launcher is active. The Author performs
the Enter/reset-cued test, then two Agon-only resets after capture completes.
Physical packet/API, waveform and repeatability results remain pending.

### Controlled-sender hardware result — PASS

[PORT-005-2026-09-09-03-26-09Z](../../hardware/designs/light2-harness-r03/tests/PORT-005-2026-09-09-03-26-09Z/README.md)
contains exact locale/poll admission and twelve unsolicited stock keyboard
packets: eight forward and 75 return bytes at 1152000 baud. Independent sigrok
and raw-sample decoders agree; framing and CTS permission at every character
start pass. All 288M samples at 24 MHz are present, with 7.590125 seconds quiet
on all four signals and 8.005626 seconds clean P4 serial after PASS. The Author
confirmed SD/CLOCK and keyboard PASS, mainboard source and MOS return on the
captured run and two further Agon-only resets. The bounded hardware proof is
complete; the broader browser/session and settings/query obligations above
remain open.

**Analysis gotcha:** EMOS raises RTS while its UART interrupt drains the FIFO.
Thirty-seven already-started P4 characters finish during the resulting CTS
pause. All characters start with permission; no new character starts while CTS
is HIGH. The earlier counting helper's whole-character LOW assertion was
inapplicable here and was corrected only in offline analysis. The recorded
data and candidate firmware are unchanged; this is not a waived framing or
flow-control failure.

The returned SD was read on 2026-09-09 at 03:44:25 UTC. Its exact `01` PASS byte
and timestamped readback receipt are retained with the result; candidate media
hashes still match. This completes supplemental collection for the last run,
while the three-run confirmation remains the Author's observation. This
checkpoint freezes the installation, deployment, passing capture and readback
evidence before the next agreed browser-input increment.

## Focused browser typing increment — 2026-09-09

The Author authorized implementation and preapproved versioning. REMOTE-001's
bounded r01 record now owns the browser-session/test scope. P4 maps US physical
key events into the retained serializer; EMOS v0.1.9 receives keyboard packets
while its resident text gateway sends the SD program's echo. UART1 remains
1152000/8N1 on r03; ordinary VDU/ExCom routing and parallel work are unchanged.
Registry r40 and browser-keyboard-probe-r01 are draft, with human review and
physical typing pending. Earlier documentation-only freeze statements describe
the previous gate and no longer prohibit this authorized increment.

## Graphical typing review accepted — 2026-09-09

The Author supplied the review screenshot showing `aB3?`, newline `z`,
BROWSER TYPING PASS (8 edited characters), mainboard input and the MOS prompt.
This accepts the bounded graphical result, not physical browser typing.
Standing version preapproval advances registry r41 and the unchanged EMOS
v0.1.9/browser-keyboard-probe-r01 implementation to candidate for clean builds.
The reviewed draft builds and their results retain their original identities.
Guarded Agon installation and paired P4/browser qualification are next.
