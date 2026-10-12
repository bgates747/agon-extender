# BENCH-010 serial-open repair — 2026-10-12

The unwanted USB-monitor reset is repaired in the maintained host reader.
Three corrected open/close trials preserved working input; a separate ordinary
100 ms reset recovered keyboard on its first attempt. No firmware, startup,
fixture, video mode or wiring was changed. Use [the serial capture guide](../../serial-monitor.md)
and its reusable opener instead of copying the old pyserial initialization.
The unusual failure after a short serial-induced reset was avoided, not repaired
inside EMOS: no independent firmware defect was established in this tranche.

## R02-01 — Mechanism and source evidence

Linux's tty nonblocking open raises both DTR/RTS together. The old collector sets
both false before calling pyserial open, but pyserial applies those settings in
two driver operations: DTR false first, RTS false second. The intermediate
DTR=false/RTS=true asserts the Olimex shared reset transistor. This accounts for
a reset despite the collector never requesting one explicitly. Reversing the
order would instead visit the ESP32 boot-selection state; the fix updates both
controls together.

Primary sources: [Linux tty_port.c](https://raw.githubusercontent.com/raspberrypi/linux/rpi-6.18.y/drivers/tty/tty_port.c)
nonblocking tty_port_block_til_ready; [CH341 driver](https://raw.githubusercontent.com/raspberrypi/linux/rpi-6.18.y/drivers/usb/serial/ch341.c)
ch341_dtr_rts and ch341_tiocmset; installed pyserial3.5 Serial.open;
Olimex Rev B schematic sheets1/2/4 retained under AUDIT-004;
[Espressif reset circuit](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html).
The inspected Linux branch matches the running kernel family; exact installed
kernel object disassembly and oscilloscope measurement were not performed.

The regression test exercises actual pyserial open under a control-line model.
Old code reaches the differential reset state; the joined clearer does not.
Unsupported joined ioctls fail rather than pyserial silently ignoring them.

## R02-02 — Exact firmware and bounded hardware results

Installed combination is the [R01 installed-source selection](CODE-REVIEW-R01.md):
P2 count/resource SHA256
`3cbc3efc01e2fad673c9433868627f3a14b2cdaeb9f8a1ca429327b2e357a2a6`,
EDP `rgb-001-r10-b2026-10-07-22-56-28Z`, and EMOS
`agon-emos-v0.1.24-b2026-10-07-23-11-33Z`. Existing verified receipts select these;
no reset-inducing flash-tool readback was repeated for this host-only repair.

| Trial | Serial reader lifecycle | Actual keyboard/CLI service evidence | Startup messages / input epoch | Result |
| --- | --- | --- | --- | --- |
| Baseline | Closed | sdserve entry, startup readback, EXIT | Original epoch | Pass |
| Corrected open/close 1 | Open, read, close | Successful entry/read/EXIT while open and again after close | 0 serial bytes; unchanged epoch | Pass |
| Corrected open/close 2 | Open, read, close | Successful entry/read/EXIT while open and again after close | 0 serial bytes; unchanged epoch | Pass |
| Corrected open/close 3 | Open, read, close | Successful entry/read/EXIT while open and again after close | 0 serial bytes; unchanged epoch | Pass |
| Ordinary reset | Corrected reader already open; one deliberate 100 ms pulse | Fresh admission, then successful entry/read/EXIT | Expected startup diagnostic; epoch increments once | Pass on first reset |

Eight actual keyboard/listener/startup-read/EXIT exchanges passed across these
checks. All startup readbacks match the original38 bytes, SHA256
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`.
No game or timing benchmark was launched, and no new SD file was written.

An overlapping USB-monitor window retained one complete corrected open/close
cycle. All five CH341 modem-control requests show equal logical DTR/RTS;
no differential reset/boot-selection request occurs. This corroborates the
joined update at the USB-command layer; it is not an analog waveform measurement.
The three corrected opens contain no startup diagnostic. The deliberate ordinary
reset does produce the familiar disableCore1WDT startup warning and still restores
input, so that warning is not by itself a fatal keyboard error.

## R02-03 — Maintained changes and limits

`passive_serial.py` owns the combined ioctl; `serial_monitor.py` provides the
bounded capture CLI. Five retained Extender capture entry points and the maintained
performance reader now use that opener. Reset-helper output distinguishes fresh
P4 admission from unverified MOS command execution. Host regression checks pass:
3 passive-open cases, 2 reset cases and 19 existing capture-verdict cases.
Python compile checks pass for all changed Python entry points.

Consumer-specific fsim collectors are outside Extender ownership and were not
edited here. The owner must adopt this maintained helper before reopening them;
its copied False/False initialization remains unsafe until replaced. No generic
claim covers third-party serial terminals, another host driver or another board.
The second-reset symptom remains recorded as behavior of the old induced reset;
normal 100 ms reset passed once, not an exhaustive boot/power-cycle campaign.
Earlier unrelated USB disconnects and broader paired-reset qualification remain
open. Production selection/version/tag unchanged; Author acceptance pending.

Local evidence: ignored `agents/bench010/serial-repair-r01`, including run config,
source hashes, per-exchange input/SD journals, unchanged startup readbacks,
three serial logs, ordinary-reset capture/receipt and USB requests. The helper
writes no serial bytes and performs no reset. All readers/listeners are closed
at handback; input is admitted and neutral at the Legacy MOS CLI.
