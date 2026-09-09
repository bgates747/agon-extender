# Focused browser typing — browser-keyboard-probe-r01

Status: candidate after accepted graphical review. Identity preapproved 2026-09-09.
Owners: REMOTE-001/PORT-005/PORT-006; resident EMOS INTEG-009.
Exact build hashes belong in the generated EMOS, P4 and SD manifests.

## Purpose and wiring

Browser focus → P4 mapped keys → stock UART key packets → resident EMOS
callback → SD typing program → EMOS text gateway → retained P4 parser/rendering
→ browser pixels. Browser code never locally echoes text. This is a bounded
application, not ordinary CLI/ExCom display routing.

Use the accepted r03 PC0..PC3 UART wiring, shared ground and both boards powered.
Keep ribbons seated. The other Port C lanes retain the existing passive state;
parallel transport and the disconnected handshake lines are unused. UART is
1152000/8N1 with RTS/CTS. Current endpoint and deployment details remain in
ignored HARDWARE.local.md and agents/browser-typing. No analyzer acquisition
is required to judge this interactive browser step; wire qualification is
already recorded separately. Optional traces must name their own procedure.

## Prepared SD

The installer phase uses the established guarded rename plus `FLASH mos ... -f`
procedure and preserves the installed v0.1.8 rollback. It must be removed after
successful MOS installation before staging this test autoexec:

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
LOAD /bin/BTYPE.BIN
RUN
EMOS KEYINPUT
```

EMBOOT and EMOS identities must match. BTYPE is the identified r01 application.
Autoexec starts the test without a physical keyboard. Video mode appears only
in autoexec. Runtime recovery requires no browser input: after five minutes
the application restores mainboard keyboard and returns to MOS; a powered
Agon reset also restarts the prepared test. Repeated runs remain enabled.

## Operator checks

1. With the paired candidates installed, insert the prepared SD and press/release
   Agon reset. Allow boot/SD/CLOCK checks and the browser typing READY message.
2. Open the P4 page, click Connect, then Capture keyboard (or click its display).
   Check that the EMOS-to-EDP banner and instructions appear and the focus border
   indicates capture. The page states the selected US test layout.
3. Type `aB3!`, Backspace, `?`, Enter and `z`. Browser pixels should show
   `aB3?` on one line and `z` on the next. Try a held letter and shifted letters.
4. While holding Shift or a letter, click outside the display, switch window or
   tab, and release the key. Return and explicitly capture again. New typing
   must have no stuck modifier or continued old repeat. Typing in another page
   control must not reach EMOS. Tab leaves capture.
5. Disconnect/reconnect the browser, explicitly capture again and repeat typing.
   Reset only Agon and repeat once more; no P4 reflash/restart or capture script
   should be necessary. A second controller needs explicit takeover; the current
   video service still supports one viewer, so broader multi-viewer behavior is
   not part of this physical check.
6. Press Escape. Agon should show BROWSER TYPING PASS and mainboard input, then
   return to MOS. The browser retains the final P4 pixels. Resetting Agon starts
   another session. Separately allow the five-minute deadline to end one session
   if qualifying the timed exit on hardware.

## Results and limits

`/typing-state.bin` is overwritten on each exit: `01` is Escape-completed,
`02` is the timed exit, `FF` is a transport/queue/clock/cleanup failure. Its mere
existence does not prove correct rendering, key mapping or three separate runs.
Record the operator's checks alongside its independently collected byte and
identified P4 logs. The application can leave characters from a prior session
visible until the next successful clear/banner. No physical results are yet
claimed by this draft sheet.

The test chooses `SET KEYBOARD 1` and browser-supplied repeat. International
layouts, IME, complete keyboard-settings/query routing, mouse, arbitrary
application compatibility and ExCom CLI output remain separate work. This
endpoint is for the trusted bench LAN, with same-origin admission and explicit
control; it has no general remote authentication or structured agent authority.
