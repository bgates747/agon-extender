# Native USB keyboard to ordinary EMOS CLI

Procedure identity: **usb-cli-probe-r01** (candidate; registry r47).
Owner: [PORT-015 W3](../../../../docs/tasks/PORT-015.md).
State: software and Author-supplied emulator review pass; physical result pending.

## Article and scope

One Perixx PERIBOARD-409 boot keyboard connects to the dedicated P4 USB host
through the already exercised cable/adapter. The connection and W1 remaining
power/current particulars are recorded in
[usb-keyboard-probe-r01](usb-keyboard-probe-r01.md). Agon/P4 use the existing
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

Physical result: **not run**. Record the actual checks completed, limitations,
screen observations, serial evidence, exact paired identities and source
return/repeat outcome in a run directory beside this sheet. Software tests,
successful compilation and emulator screen review do not substitute for the
USB/UART physical test. Keep ordinary setup mistakes only as brief corrections.
