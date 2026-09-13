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
2. [ ] R02-02: Implement portable remote session/event engine, bounded HTTP
   adapter, console-owner integration and host typing client. Add a reusable
   host reset wrapper with machine details external to tracked code.
3. [ ] R02-03: Test text/key mapping, overflow, cancellation, physical takeover,
   duplicate/lost replies, expired sessions, timer wrap, admission/layout loss
   and transport failure. Compile P4; run retained native-keyboard, network,
   console and SD checks. Exercise actual eZ80 keyboard/CLI effects headlessly.
4. [ ] R02-04: Identify/stage/flash only necessary candidate firmware with
   verified rollback; perform bounded physical input qualification and SD
   regression. Preserve receipts and failures without inferring human review.
5. [ ] R02-05: Prepare a new spoken review cue and known idle CLI/service handover
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
the UART serializer with replies/SD. No remote-key HTTP endpoint exists today.

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
