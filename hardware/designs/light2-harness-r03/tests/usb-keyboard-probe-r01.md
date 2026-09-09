# Native USB keyboard acquisition — usb-keyboard-probe-r01

Status: candidate procedure/firmware definition; physical result pending. Owning work:
PORT-015 W1/W2. This supplements the existing r03 assembly with a USB connection;
previous r03 UART/pinwalk results do not qualify the new conductors.

## Connection record

The Author is assembling a USB-A male cable plus female-to-female USB-A adapter
accepting the keyboard plug. These are the Author's four-pin header numbers:

| Header | Conductor | P4 DevKit Rev D1 |
|---:|---|---|
| 1 | GND | EXT2.18 GND |
| 2 | USB D+ (old KCLK position) | EXT2.19 USB-P / USB_DP |
| 3 | USB D− (old KDAT position) | EXT2.20 USB-N / USB_DN |
| 4 | +5 V VBUS | EXT2.1 board +5V |

The Author confirmed the reference socket's orientation by continuity: looking
into female USB-A with its plastic tongue on top, left-to-right is +5 V, D−,
D+, GND. This was checked on the Agon socket; it is not evidence of continuity
through the new cable/adapter or of the completed P4 wiring. `USB-P` is data.

Before deployment, record in the run: completed cable/adapter continuity and
short checks; socket supply polarity/voltage; keyboard identity and current
rating; available power budget and bench VBUS protection. EXT2.1 is the board
rail, not a separately switched/current-limited USB host power output. Keep
signal leads short/together and leave the existing Agon ribbons seated.
Current machine-specific details belong in HARDWARE.local.md.

## Preparation and execution

1. Freeze the reviewed firmware candidate and build its identified bundle with
   `scripts/prepare_usb_keyboard.py`. Retain the build manifest, binary/ELF,
   exact managed dependency lock and hashes. Check that all existing dependency
   versions/hashes match the ordinary EDP lock; only the HID driver is added.
2. After the operator completes the wiring checks, deploy through the existing
   bench procedure using P4's separate USB-C Serial/JTAG connection. Record
   write verification and the exact USB KEYBOARD build/status banner. No
   Agon reset, EMOS flash, SD edits or logic-sniffer acquisition is required.
3. Start a bounded serial recording on the bench host without resetting P4.
   Wait for `USB HOST READY`, then attach the keyboard. A keyboard present at
   P4 startup is also supported. Confirm `USB CONNECTED` and
   `USB KEYBOARD READY`, with matching device/interface details.
4. Press and release `a`, Shift+`a`, `1`, Enter and Backspace. Confirm one DOWN
   and one UP per physical transition. Expected ASCII values are 97, 65, 49,
   13 and 8; Shift produces its own modifier events. Release Shift before `a`
   once: the final release must retain uppercase `A`'s pressed identity.
5. Hold `a`: repeated unchanged USB reports must not create repeated DOWNs.
   This acquisition fixture has no software typematic. Release the key, then
   hold Shift+`a` and unplug the keyboard. Confirm both held keys receive UP
   and `USB DISCONNECTED` appears. Reconnect, type/release `a` again and
   confirm normal acquisition. Repeat removal/reconnection once more.
6. Confirm no USB transfer/report/host faults or unexpected P4 reboot. Record
   observed caps/control behavior if exercised; the fixture's US subset is
   not a claim of locale, LED, rollover, hub or complete key compatibility.

The candidate periodically reports connection, report and key-event counters
over its debug console. It sends no keys to EMOS and does not run browser video.
Entering text at the normal Agon prompt is the subsequent PORT-015 W3 proof.
On an input fault, P4 releases held state and requires all physical keys to be
released before rearming. A transfer failure may require keyboard replug; a
host fault explicitly requires P4 reset. Record failures before retrying.

## Result

Pending wiring confirmation, candidate deployment and physical acquisition.
Preserve passing serial evidence and meaningful failures under a timestamped
PORT-015 run beside this sheet; private specimen/network details remain local.
