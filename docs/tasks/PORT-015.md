# PORT-015 — Bring up a directly connected USB keyboard

## State and scope

- Status: W2 firmware implementation authorized and prepared while the Author
  wires W1. Host checks and source-stable draft build pass; source checkpoint
  prepares the candidate. Physical wiring confirmation/deployment remain pending.
- Started: 2026-09-09.
- Finished: --

The Author brought forward direct P4 USB keyboard input because the Agon
mainboard keyboard interface remains inoperative. First useful milestone:
USB keyboard → P4 processed keyboard → existing r03 UART1 → resident EMOS
keyboard handling → ordinary CLI on mainboard VGA. Browser input repairs
remain tracked in REMOTE-001 and follow this increment. Browser video is not
the display dependency for this proof.

Use one ordinary wired USB HID boot-protocol keyboard initially. P4 owns USB
enumeration, reports, key transitions, repeat and device removal; EMOS owns
source selection, UART1 and canonical key/sysvar/API effects. Reuse PORT-005's
processed input/stock serializer and PORT-008's 1152000/8N1 RTS/CTS transport.
Implement the existing `EMOS KEYINPUT extender` name. Preserve layout/source
separation and autoexec-only startup persistence. Do not add an application
UART bypass, proprietary keymap packet or implicit browser/USB input mixing.

## Decision register

| ID | Decision | State |
|---|---|---|
| PORT-015-D001 | Bring forward native P4 USB keyboard acquisition; first prove ordinary EMOS CLI on mainboard VGA using the existing UART contract. | Accepted by Author, 2026-09-09; SETUP-005 K009 and ADR-0014. |
| PORT-015-D002 | Use one wired boot-protocol keyboard and the existing reserved `extender` input selector for the first increment. | Accepted direction; firmware not implemented or qualified. |
| PORT-015-D003 | Author's USB-A male cable terminates in a reversed four-pin male header; a female-to-female USB-A adapter accepts the keyboard plug. | Author corrected the initial socket description; conductor order is reported, assembled continuity unverified. |

## Bounded reference

1. Olimex ESP32-P4-DevKit Rev D1 schematic and PCB at vendor commit
   `4b453612bd72e2b83b49cb1156de93f655b8aec4`, in
   `HARDWARE/ESP32-P4-DevKit-Rev.D1/` of
   <https://github.com/OLIMEX/ESP32-P4-DevKit>. The unmodified local vendor
   copies and board identity are indexed through HARDWARE.local.md.
2. ESP-IDF 5.5.5 USB host documentation and the matching
   `examples/peripherals/usb/host/hid` example. Use managed
   `espressif/usb_host_hid` **1.2.1**, vendor source
   `e3c35b840b9fc9969b981011c9ff782c01168433`. Its 1.1.0/1.2.1 releases fix
   concurrent-close and disconnect-cleanup defects present in older examples'
   driver range. This IDF version supplies the USB library itself.
   <https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/usb_host.html>
   <https://components.espressif.com/components/espressif/usb_host_hid/versions/1.2.1>
3. Before changing MOS/VDP behavior, refresh the relevant official
   Keyboard/API/System-Commands documentation and AUDIT-004's bounded packet
   and MOS traces. Official MOS v3.0.2 and VDP v2.16.0 remain read-only.
   Current complete processed events and serializer live under PORT-005;
   browser socket ownership/heartbeat policy is not a USB device lifetime.

## W2 implementation and checks

The standalone `p4-usb-keyboard` target selects one native acquisition
translation unit and uses `usb-keyboard-probe-r01` (candidate, registry r45,
standing Author preapproval). `scripts/prepare_usb_keyboard.py` produces an
identified local bundle without flashing or writing SD media. Its target lock
is `vdp/pio/p4-usb-keyboard-dependencies.lock`; ordinary EDP's
`vdp/dependencies.lock` remains unchanged. The resolver initially selected
unrelated updates for three Arduino dependencies, so the target explicitly
retains their existing versions. The builder rejects any changed existing
dependency version/hash. No vendored implementation is patched.

P4's HID task claims one boot-keyboard interface and copies eight-byte input
reports into a bounded queue. The application owner configures boot protocol,
decodes transitions and prints them on USB Serial/JTAG. Reports reserve queue
space for connection/removal notices. Lost/invalid reports clear held state;
older queued reports cannot rearm input, which requires a fresh neutral report.
P4 reports unmapped physical usage IDs rather than inventing stock key values.
The shared US subset preserves the existing browser mapping and held-key
release identity. No browser lease behavior changes here.

W2 does not initialize the Agon UART, send keyboard packets, switch display or
input source, or modify EMOS. Typematic, LEDs, selected layouts and the complete
stock key set remain W3 work. Diagnostic USB acquisition cannot establish that
`EMOS KEYINPUT extender` works. Installed EMOS and P4 images remain unchanged.

Verification commands:

```text
.venv/bin/python tests/usb_boot_keyboard_test.py
.venv/bin/python tests/browser_keyboard_test.py
.venv/bin/python tests/usb_source_selection_test.py
.venv/bin/python scripts/prepare_usb_keyboard.py --output <new-local-bundle-directory>
```

Decoder tests exercise exact report transitions, modifier-only reports,
retained releases after modifier changes, duplicate/reordered slots, rollover,
lost-report neutral recovery, unmapped keys and removal. Existing browser
mapping/ownership tests pass unchanged. Selection-hook checks cover target
manifest/lock switching and protection of hand-maintained files. A successful
compile is separate from a source-stable identified bundle and physical proof.
The identified draft `usb-keyboard-probe-r01-b2026-09-09-19-55-40Z` passed
source-stability, exact embedded identities, output hashes and dependency
closure checks. The deployable candidate is built from the source checkpoint
and gets its own timestamp. The artifact registry validates. The full version
validator still fails the pre-existing, unchanged r02 profile/connectivity
hash mismatch; repairing that held historical design is outside this increment.
The [USB acquisition test sheet](../../hardware/designs/light2-harness-r03/tests/usb-keyboard-probe-r01.md)
owns the wiring confirmation and operator observations.

## Proposed connector mapping

This table uses the Author's cable-header numbering, not USB receptacle contact
numbering. The cable has a male USB-A plug with a female-to-female USB-A adapter
accepting the keyboard's plug. Check the complete cable/adapter assembly.
Legacy `KCLK`/`KDAT` labels identify positions only: these wires carry
actual USB D+/D− here, not PS/2 clock/data.

| Cable header pin | Reported conductor | P4 DevKit connection |
|---:|---|---|
| 1 | GND | EXT2 pin 18, GND |
| 2 | KCLK / USB D+ position | EXT2 pin 19, `USB_DP`, silkscreen `USB-P` |
| 3 | KDAT / USB D− position | EXT2 pin 20, `USB_DN`, silkscreen `USB-N` |
| 4 | +5 V / VBUS | EXT2 pin 1, `+5V` |

`USB-P` is the positive USB data signal, not a power source. The dedicated
host signals reach chip DP/DM pins 50/49. The existing USB-C Serial/JTAG path
uses different pins and stays available for programming. EXT2.1 is the board's
5 V rail, not a separately switched/current-limited host VBUS output. The
keyboard's load and available bench supply budget must be checked before use;
do not infer a qualified host power circuit from a net named `+5V`.

Keep the D+/D− connection short and together. Do not reuse the Agon Port C
pull-ups or series resistors for USB. The new connection is not part of the
previously qualified r03 pinwalk/UART evidence; record its as-built state and
eventual fixture identity beside the hardware design before powered testing.

## Work

1. [ ] **W1 — Verify the physical connection.** With boards powered down and
   ribbons seated, the operator checks socket-to-header continuity and absence
   of shorts, then connects the four mapped conductors. Record cable orientation
   and keyboard identity/current rating. Verify supply polarity/voltage at the
   socket before attaching the keyboard. No firmware enumeration is possible
   in the currently installed browser-only image. Prepare the controlled
   wiring/test record and suitable VBUS protection/power scope before deployment.
2. [ ] **W2 — Prove P4 USB acquisition.** Integrate the supported HID host
   component with a bounded event source; first observe enumeration and exact
   press/release/modifier reports. Keep USB work outside HTTP handling and
   deliver events through the P4 process owner. Verify removal clears held
   state. Freeze the identified candidate before bench deployment; preserve
   existing UART pins and avoid sending unsolicited input to EMOS.
3. [ ] **W3 — Prove the ordinary EMOS CLI.** Implement and test explicit
   `extender` source admission and source-return cleanup, reusing stock packet
   handling. Handle key transitions, layout, repeat and removal; define the
   supported keyboard set before claiming parity. Autoexec performs setup and
   returns to the normal CLI on mainboard VGA. Test typing/editing, modifiers,
   held/released keys and unplug/replug without relying on browser focus or
   video. Record result and remaining compatibility limits beside the design.

BC-001 remains active for installation/recovery: the keyboard under test cannot
be assumed working to launch or repair its own test. Native USB input does not
clear the mainboard fault or qualify ExCom, hubs, mice, arbitrary report formats,
multiple keyboards, or the browser transport. Firmware/version selection uses
the existing standing Author preapproval and normal clean candidate gates.
