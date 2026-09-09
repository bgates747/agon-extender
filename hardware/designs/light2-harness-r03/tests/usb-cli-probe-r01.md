# Native USB keyboard to ordinary EMOS CLI

Procedure identity: **usb-cli-probe-r01** (candidate; registry r47).
Owner: [PORT-015 W3](../../../../docs/tasks/PORT-015.md).
State: software/graphical review and bounded physical CLI, editing/repeat/reconnect/source-return checks pass; wider keyboard parity remains open.

## Article and scope

One Perixx PERIBOARD-409 boot keyboard connects to the dedicated P4 USB host
through the already exercised cable/adapter. The connection and completed
W1 power record are in the
[design specification](../README.md#usb-keyboard-addition--2026-09-09). Agon/P4 use the existing
r03 four-wire UART1 connection, 1152000 baud, 8N1 with RTS/CTS and common ground.
Keep the GPIO ribbons seated. This test adds no parallel wiring or transport.

Pair a frozen `usb-cli-probe-r01` P4 build with EMOS v0.1.10. Record both exact
build IDs, source commits, image hashes, deployment verification and run ID
before the physical result. Draft host builds are not physical candidates.
Use the machine-local bench record for device access and existing guarded
EMOS installation/rollback preparation. Installation cannot rely on the
keyboard under test; BC-001 remains active.

P4 acquires USB events and sends ordinary stock keyboard packets to resident
EMOS. EMOS updates its ordinary keyboard state and CLI line buffer, then
sends ordinary output to mainboard VDP/VGA. P4 does not echo typed characters
or serve browser video in this composition. Mainboard VDP still supplies the
clock and cursor. USB removal is independent of browser focus/lease handling.

Initial scope: UK/US ordinary printable/editing keys and modifiers, software
Caps Lock state, bounded repeat and removal/reconnect. LED updates, keypad,
other layouts, complete keyboard settings/query and VDP-local control parity
remain open. Do not use a Caps Lock LED as the pass criterion. Browser/native
input mixing and ExCom display switching are outside this procedure.

## Prepared startup

The test card's autoexec, after guarded installation is complete, contains:

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
SET KEYBOARD 1
EMOS KEYINPUT extender
```

Use the EMBOOT image paired with the exact EMOS build. Autoexec returns to the
ordinary MOS prompt; there is no typing fixture, five-minute timeout, or Escape
exit. EMOS prints `Keyboard input: extender` only after admission. Failed
admission returns a reason and retains mainboard input. Start P4 first, then
blip Agon reset once when the capture is ready. Neither board needs a power
cycle for an ordinary repeated test.

## Operator checks

1. Confirm the EMOS identity, SD/CLOCK PASS, `Keyboard input: extender` and
   the normal MOS prompt on mainboard VGA. The P4 serial record must show the
   expected image, USB keyboard readiness and native input admission.
2. Type `echo Usb 123!` and press Enter. The ordinary command line and echoed
   text must match, including case, numeral and shifted punctuation. The
   normal prompt must return. Record any lost keys or noticeable latency.
3. Type `echo usb clx`, Backspace once, then `i`. Move Left once and Right
   once before Enter. The result must be `usb cli`; neither arrow may delete
   a character. This exercises the stock CLI editor, not a sample editor.
4. At a fresh line type `echo `, hold `a` briefly, release it, then press Enter.
   Repeat should start after about 500 ms and continue around 100 ms per key;
   it must stop on release. Exact timing is not established by visual review.
5. Release all keys, unplug the keyboard and reconnect it. Type another
   `echo reconnected` command. No board reset or source re-selection should be
   needed. The accepted W2 held-key removal already covers synthetic releases;
   do not repeat the awkward held-key/unplug manoeuvre without a new reason.
6. Enter `EmOs KeYiNpUt`; expect `Keyboard input: extender`. Enter
   `emos keyinput mainboard`; expect its confirmation and the normal prompt.
   Further USB keystrokes must not enter MOS. Mainboard input hardware remains
   broken, so blip Agon reset to let autoexec restore USB input for a repeat.
   Confirm typing works again without resetting P4.

P4 logs driver/transport faults explicitly. Unplug-only HID 1.2.1 endpoint
clear diagnostics have the bounded disposition in
[usb-keyboard-unplug-review](usb-keyboard-unplug-review.md); other faults are
not covered by that disposition. Report a fault or loss of prompt before
assuming a wiring or operator mistake. A permanently blocked TX is cancelled
after five seconds; fresh EMOS locale/poll admission permits retry. A malformed
command or receive fault requires P4 reset in this bounded composition.

## Result record

Physical result: **bounded CLI checks pass**, as recorded below. Record further checks, limitations,
screen observations, serial evidence, exact paired identities and source
return/repeat outcome in a run directory beside this sheet. Software tests,
successful compilation and emulator screen review do not substitute for the
USB/UART physical test. Keep ordinary setup mistakes only as brief corrections.


### First ordinary USB CLI hardware pass

The Author reports PASS for the prepared startup and `echo Usb 123!` test:
SD/CLOCK checks, extender admission, physical USB keyboard command entry and
echoed output on mainboard VGA. Paired candidates are EMOS
agon-emos-v0.1.10-b2026-09-09-21-51-31Z and P4
usb-cli-probe-r01-b2026-09-09-21-51-31Z. This is Author-observed functional
evidence; no waveform or latency measurement was collected. Editing, held-key
repeat, reconnect and source-return/repeated-reset checks in the test sheet
are not inferred from this report. W1 power particulars and wider keyboard
compatibility remain open. No hardware or SD operation accompanied recording.

The Author additionally reports **zero noticeable latency** during native USB
CLI typing. This is a subjective responsiveness observation, not a measured
zero-latency claim.

### Gameplay observations and priority decision — 2026-09-09

The Author subsequently used the Extender USB keyboard with AgonWolf3D and
Nurples. Nurples' Up problem was traced to its legacy GPIO joystick reads:
PC3 low for P4 RTS/Agon CTS was interpreted as joystick Down. Nurples commit
`4a52199` adds a splash Y/N choice and skips direction/fire GPIO polling when
disabled. The Author accepted that build in the emulator and then on Agon
hardware with the joystick disabled. No EMOS/P4 image changed for that fix.

After gameplay, the Author reported possibly a slight increase in keyboard
latency relative to the stock interface, but not enough to materially affect
play. This qualifies the earlier CLI impression of no noticeable delay; neither
report is an instrumented latency measurement or establishes equality with
stock timing. The Author accepted the practical result and selected
mainboard/Extender keyboard choice as the immediate goal, deferring browser
input. Full source-return, repeat/reconnect, electrical and wider keyboard
qualification are not inferred from this gameplay observation.

### Editing, repeat, reconnect and source-return pass — 2026-09-09

The Author accepted all requested continuation checks in
[PORT-015-2026-09-09-23-25-54Z](PORT-015-2026-09-09-23-25-54Z/README.md).
Boot smoke, editing, held-repeat release, USB reconnect, mixed-case source
query, mainboard exclusion and Agon-only reset readmission passed. The run
retains P4 serial evidence and the bounded dispositions of unplug logging and
blocked-TX cleanup. Together with prior typing/gameplay results this completes
PORT-015 W3; it does not close W1 power particulars or PORT-005's wider parity.

### Subsequent power-record completion — 2026-09-09

The Author confirmed the keyboard's 100 mA label rating and sole USB power
to P4, with keyboard VBUS drawn from P4's +5 V rail rather than the Agon.
The [design specification](../README.md#usb-keyboard-addition--2026-09-09)
records that arrangement. This closes PORT-015 W1's bounded record without
changing any earlier run observation or claiming measured supply headroom.
