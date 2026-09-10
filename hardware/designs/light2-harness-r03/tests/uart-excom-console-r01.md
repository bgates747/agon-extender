# Ordinary ExCom console — uart-excom-console-r01

Candidate procedure owned by [PORT-008](../../../../docs/tasks/PORT-008.md), using
r03's existing UART and native USB keyboard wiring. The [control contract](../../../../docs/protocols/excom-console.md)
and EMOS INTEG-010 define the bounded implementation. No physical run has yet
been performed with this composition.

## Preparation gate

Author emulator acceptance and a frozen candidate pair precede deployment.
Use the established guarded EMOS installer/rollback and P4 deployment workflow;
record exact image identities, hashes and installed results in this directory's
run record. Preserve the accepted v0.1.10/USB CLI rollback pair. Consult the
ignored machine-local bench description and active bench constraints first.
Leave the powered Agon/P4 ribbons seated. Use the native USB keyboard and P4
browser video; browser keyboard capture is not part of this procedure.

The ordinary post-install autoexec selects video mode before boot smoke, then
keyboard layout and source:

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
SET KEYBOARD 1
EMOS KEYINPUT extender
```

Keep flashing separate from this repeatable startup. No SD-loaded test program
changes video modes or bypasses EMOS transport ownership.

## Operator observations

1. Reset Agon when deployment is complete. Confirm boot smoke SD/CLOCK PASS,
   selected Extender keyboard, and the mainboard MOS prompt. Connect the
   browser to P4 video. Type `echo Legacy input` on the USB keyboard and confirm
   ordinary output on the mainboard.
2. Type `EMOS EXCOM`. Confirm the mainboard shows its mode notice with cursor
   off, and the browser shows a fresh ordinary MOS prompt. The native USB
   keyboard should continue working without reconnecting it.
3. Type `echo ExCom input`, correcting a typo with Backspace and editing with
   the arrows before Enter. Confirm the entered line and command output in
   the browser. Type `EMOS KEYINPUT` and confirm `extender` remains selected.
4. Type `EMOS LEGACY`. Confirm a fresh mainboard prompt with cursor restored.
   Type `echo Legacy return`; confirm USB input and normal command output.
5. Repeat the ExCom/Legacy cycle once using mixed-case command names. Record
   both displays, editing behavior and any noticeable input delay. Keep both
   boards powered throughout.

## Results and limits

Hardware result: pending. Record Author observations and relevant P4 logs with
the exact candidate pair; a browser image alone does not prove the return path.
The paired emulator separately tests withheld activation followed by usable
Legacy input. This sheet does not ask the operator to power down a connected
P4 to simulate absence; shared-wire power sequencing is outside this test.

This is an ordinary idle-console proof. Complete VDU/graphics/audio/RTC parity,
application display-state preservation, peer-reset/fault recovery, parallel
transport and browser input remain outside its scope. The new P4 composition's
hardware RTS and shared parser/reply scheduling require this physical check;
previous keyboard-only hardware acceptance is not sufficient evidence.
