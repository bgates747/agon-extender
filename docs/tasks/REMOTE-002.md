# REMOTE-002 — Host-controlled typing through the native keyboard path

Status: Active goal; contract frozen before implementation. Started 2026-09-13 UTC.

## Author instruction and scope

The Author accepted PC-to-Ethernet keyboard injection joining the P4's existing
USB-to-processed-key path. Update the Extender notes and commit current progress
and this contract first, then implement autonomously. Firmware flashing on the
P4 and onboard VDP, EMOS/program deployment via SD/autoexec, and Pi-controlled
Agon reset are authorized when required. Preserve rollback and identify every
deployed build. Use headless emulator work for machine checks.

At review readiness, play a new British-accented spoken alert on the Agon and
wait for the Author to reply in this chat. Only after that reply send the live
demonstration keystrokes. Autonomous bounded qualification before the alert is
authorized; do not start the attended demonstration early. A normal emulator
beep remains the fallback if hardware attention cannot work. No push requested.

The P4 only forwards host-requested input under EMOS keyboard admission. It
does not independently reset or command the mainboard. The Pi controls the
existing transistor reset actuator. No new reset wire, direct ZDI bit banging,
P4 reset of Agon, MOS memory injection, or UART ownership bypass is selected.
Browser focus/input remains deferred under REMOTE-001. Graphics/Golem work is
outside this goal. New EMOS source is needed only if an actual interface blocker
is demonstrated; add an owner-local task before such a change.

## Frozen decisions

1. Host HTTP requests enter a bounded separate automation queue; the retained
   console owner alone serializes keys over the established UART1 transport.
2. Press/release pairs and modifiers use the existing USB CLI mapping. Support
   text, Enter/Escape, arrows and explicit key transitions for held-key tests.
   Reject unsupported text before typing any portion of a batch.
3. Maintain separate physical and remote held-key state. Admit a remote session
   only while physical keys are neutral. A physical press cancels automation;
   remote releases precede the physical event, and never release physical keys.
4. One remote owner, bounded batches, paced output, explicit cancellation and
   finite timeout. Do not depend on repeated browser/network events for releases.
5. Session/boot identity and numbered requests make retries idempotent. A
   conflicting duplicate is rejected. Reboot or admission loss invalidates the
   old session; the client must not silently start over and retype a command.
6. Report accepted, emitted and cancelled progress separately. UART emission
   alone is not proof of receipt or execution by EMOS. Qualification needs an
   eZ80-side receipt or an Author observation for actual command success.
7. Firmware/network callbacks may enqueue only; no GPIO/UART/file work in HTTP
   handlers. Add routes without reviving the retired browser keyboard code.
8. Use the existing native keyboard source (`EMOS KEYINPUT extender`). Preserve
   mainboard selection, layout changes, repeat behavior and transport recovery.
9. Keep the previous installed P4 image, EMOS, service, startup, hello binaries
   and voice clips recoverable. Never replace a batch file held open by MOS.
   A verified helper batch at an unused pathname may be invoked after closing
   the original batch; finite preinstalled continuation is also available.

## Work checklist and completion gates

1. [x] R02-01: Inspect current owners; record accepted greeting/reset outcome,
   control boundary and this plan. Freeze existing changes and contract in
   separate commits before remote-keyboard implementation. Pynvaders, Rally
   and EMOS are clean at intake; no artificial changes are needed there.
2. [x] R02-02: Implement portable remote session/event engine, bounded HTTP
   adapter, console-owner integration and host typing client. Add a reusable
   host reset wrapper with machine details external to tracked code.
3. [x] R02-03: Test text/key mapping, overflow, cancellation, physical takeover,
   duplicate/lost replies, expired sessions, timer wrap, admission/layout loss
   and transport failure. Compile P4; run retained native-keyboard, network,
   console and SD checks. Exercise actual eZ80 keyboard/CLI effects headlessly.
4. [x] R02-04: Identify/stage/flash only necessary candidate firmware with
   verified rollback; perform bounded physical input qualification and SD
   regression. Preserve receipts and failures without inferring human review.
5. [x] R02-05: Prepare a new spoken review cue and known idle CLI/service handover
   using verified SD files and normal MOS/VDP APIs. Play the cue, then stop
   all demo-key submission pending the Author's reply here.
6. [ ] R02-06: After reply, demonstrate live typing, editing, command execution
   and program launch while the Author observes. Record feedback; fix any
   regressions; promote operating instructions and close the goal only after
   the required review. New emulator-coupled changes remain uncommitted until
   the applicable explicit review/commit approval; the intake freeze is approved.

## Focused research and pitfalls

Current source: input/usb_boot_keyboard.hpp, usb_cli_keyboard.hpp,
usb_key_queue.hpp; transport/console_hardware.inc; network/wired_network_service.*
and storage/sd_target.hpp, all beneath vdp/video/extender. USB callbacks queue
reports; the retained owner pumps reports, processes one stock key and shares
the UART serializer with replies/SD. No remote-key HTTP endpoint existed at intake.

Official references are read-only Agon MOS v3.0.2 API keyboard/sysvar contracts
and VDP v2.16.0 keyboard packet/control behavior. Existing PORT-015 tests pin
the mapping. REMOTE-001 retains a stale-time lease bug and video stalls; reuse
its lessons, not its retired networking implementation. SD qualification uses
raw FAT images because Fab's directory backend has known create/sync defects.
The UART-peer emulator models ordered bytes and backpressure, not physical baud.

EMOS and the current service are independently accepted candidates. Autoexec
currently runs hello/service/hello/service and can remain open while the
service runs. Network EXIT is a batch continuation, not an arbitrary launch.
The working Pi reset is ordinary reset-pin actuation through the existing
GPIO17 transistor; the six-pin connector's ZDI label does not imply a debug
protocol. The Author corrected a ground connection and confirmed success.

Machine state, host commands, backups and staging live in ignored
agents/remote-keyboard and HARDWARE.local.md. Maintained contract is
docs/remote-keyboard.md; accepted ownership decision is ADR-0019.

## Implementation and qualification progress

R02-02 is implemented provisionally. The portable engine, bounded HTTP adapter,
console-owner integration, journaled host client and configurable Pi reset
wrapper are present. Post-freeze changes remain uncommitted for the applicable
attended review gate; current firmware tests are explicitly authorized by the
Author. Standing identity preapproval selects console r13 as draft while r12
remains recoverable. No EMOS or mainboard VDP source change is needed so far.

Host tests pass all printable ASCII through both retained layouts, lost accepted
HTTP reply without duplicate typing, physical takeover, timeout, bounds, CRC,
admission and timer wrap. Existing USB, processed serializer, network route
rollback and SD tests pass. One inherited mode-test harness lacked the current
activeDisplayController seam; the local fake now models that existing accessor.

The first actual eZ80/raw-FAT run passes all 28 expected receiver events, MOS
keymap cleanup after cancellation/timeout, ordinary CLI Backspace editing/COPY,
typed LOAD/RUN of sdserve and a 536-byte SD write/read including a deliberately
lost WRITE response. This models UART bytes, not physical baud or USB hardware.
Final identified build and physical qualification remain open. The receiver
fixture uses MOS sysvars and the 128-bit BBC physical-key map; FabGL virtual-key
numbers are not direct indexes into that map. No mode switch belongs in it.


Hardware continuation: identified r13 draft built successfully and was flashed
with independent full-image verification and observed native USB startup. The
physical receiver matched all 28 events and held-key cleanup. A first CLI test
correctly failed: Escape returned from sdserve into the next autoexec command,
which was another receiver. The receiver recorded the would-be CLI text, proving
the handover error. EMOS mos_EXEC simply continues successful batch commands;
Escape in an application does not universally abort its caller. Preserve this
informative failure and never infer that a batch is closed merely from Escape.

Exiting the known FINAL service then typing COPY with Backspace editing, LOAD
and RUN succeeded on the physical board; the new file matched its source and a
536-byte SD roundtrip passed. Startup was normalized to one receiver/one final
service; the complete physical check then passed with a fresh, absent target.
The reviewed earlier greeting and prior startup backups remain on the card.
The new spoken cue has passed headless execution/audio acknowledgement and has
not yet been played on hardware. Physical keyboard takeover remains an attended
review item; host source-separation tests do not substitute for that observation.

The repeat exposed a second handover requirement: P4 survives mainboard reset,
so old `ready=true` is not proof of a fresh EMOS admission. Sending a batch too
early exercised the five-second transport timeout: it discarded 13 pending
events and invalidated the session. Waiting for a changed admission epoch and
ready state fixes the test controller. The subsequent complete physical run
passes all 28 receiver events, timeout/cancel releases, edited COPY to an
explicitly absent target, typed LOAD/RUN and the SD write/read. No firmware
change was required for either handover correction. Preserve both useful
failures alongside the passing evidence.

R02-03 and R02-04 are complete within their machine-test scope. See
`evidence/qualification.json` and the dated development record for identities
and limits. R02-05 completed the new review voice/startup; R02-06 remains gated
by the Author's chat reply after the spoken cue. Do not send live demo input
before that reply. All post-contract maintained changes remain uncommitted.


Review cue completed on hardware at 2026-09-13 04:34:25 UTC. The read-back
receipt is stage4/audio_commands=pass; the final sdserve is online and native
keyboard admission is fresh, with no held or pending remote keys. The program
asks the Author to reply in chat when ready to watch typing. No keystrokes were
submitted after triggering this cue. STOP here until that reply. Human hearing,
visual demonstration, physical takeover and commit approval remain pending.


The Author returned after the cue and observed the first attended messages and
Backspace correction, calling the result "spooky impressive". The cursor demo
then stopped on a premature lease expiry; no Rally launch occurred. This is
partial positive visual feedback, not full acceptance. The Author requested
that comments shown on the Agon also appear in chat, then returned to the couch
and requested a fresh spoken hardware cue after repair, followed by another
chat reply before resuming the demonstration.

The reproducing regression identifies the clock bug: the console samples its
iteration time before acquiring the shared remote-input lock. HTTP can renew
the lease with a newer timestamp before that lock is acquired. Unsigned elapsed
subtraction interprets the slightly older console time as nearly 49 days and
expires the new request. Signed modular elapsed comparison fixes the issue and
retains the timer-wrap and real five-second-expiry checks. The new test fails
r13 and passes the correction. Standing preapproval selects r14/registry r73;
r14 remains draft pending the extended physical cursor test and renewed review.
The qualifier now exercises 80 small cursor batches before its file-producing
edit command. Keep the stopped live-demo record as evidence.


r14 passed all receiver events and 80 cursor batches physically, with the edited
COPY file later verified intact. Its subsequent service launch timed out. The
controller had treated a 300 ms sleep after typed LOAD as completion evidence;
slow explicit recovery restored the service. The final procedure types EXEC
of a freshly uploaded/read-back helper batch, so MOS orders LOAD completion
before RUN. This is stronger than relying on host wall-clock delay. The final
service holds only that new helper batch open; the root autoexec is closed.

A separate regression also found that resetting due_ on each events request
let adjacent small batches bypass the stated 20 ms event spacing. r15 preserves
the existing deadline across request boundaries and initializes it at OPEN.
The new case fails r14 and passes r15. Standing approval selects r15/registry
r74, retaining the signed modular expiry fix. No protocol-format change and no
physical-keyboard pacing change. Extended headless receiver/cursor/EXEC/SD and
new stage5 spoken-cue checks pass; r15 is flashed/verified for physical retest.

The r15 extended physical retest now passes: all 28 receiver events, cancel and
expiry releases, 80 separate cursor batches, edited COPY to a previously absent
file, typed EXEC launching the verified service batch, and 536-byte SD readback.
The passing run is retained in `evidence/qualification-r15.json` alongside the
earlier r13 record. These are dirty draft development builds, not a qualified
release. Physical USB takeover and renewed attended acceptance remain open.

The initially failed r15 launch was investigated with a bounded ordinary eZ80
program using stock VDP character readback (`23,0,&83`). Its preserved screen
capture shows `XEC` followed by `Invalid command`: MOS missed the first letter
after COPY, while the cursor edit and copied file were correct. MOS/EMOS
`mos_editor.c` waits for a new key-count change when entering its input loop;
input emission counters do not establish prompt readiness. Increasing the
fixture's post-command pause to two seconds fixes this observed handover. The
finite helper still supplies the stronger LOAD-before-RUN ordering. Do not
generalize the two-second pause to arbitrary programs or file sizes.

The diagnostic source is `examples/keyboard-screen`; its README records the
stock API, bounds, build stamp and reproduction procedure. It selects no mode
and captures before displaying its completion text. No onboard VDP or EMOS
firmware was changed to obtain this evidence.

The Author reports concurrent work on the Extender remote in different files
and task namespaces. Keep this implementation within REMOTE-002, preserve other
agents' changes, and do not pull, merge or publish unrelated remote work as part
of this review. A fresh spoken cue is being staged after the passing retest;
another Author reply is required before any further attended demo input.


Renewed stage5 hardware cue completed at 2026-09-13T05:21:54.132664+00:00. The
read-back receipt is stage=5/audio_commands=pass, a fresh final SD service is
online, and keyboard admission is ready with zero held or pending remote keys.
No keystrokes were sent after the cue. WAIT for a new Author reply before
resuming the attended demo; human hearing and full visual acceptance remain
unconfirmed. Evidence: docs/tasks/REMOTE-002/evidence/review-fixed-cue.json.
