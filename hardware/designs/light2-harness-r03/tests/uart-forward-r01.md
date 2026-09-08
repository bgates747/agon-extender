# First UART1 forward message — uart-forward-probe-r01

Owner: [PORT-009](../../../../docs/tasks/PORT-009.md). Approved paired fixture
identity: `uart-forward-probe-r01`, candidate. This sheet and the
sender/receiver are one diagnostic fixture; there is no new product protocol.
Unversioned review builds must not be deployed or recorded as qualification.

## Selected behavior and wiring

Installed EMOS remains `agon-emos-v0.2.0-b2026-09-08-01-20-50Z`, candidate.
The ordinary SD program invokes its UART1 open/write/close APIs. The eZ80
sends **18 bytes**: `EMOS UART1 -> P4` followed by CRLF, with no NUL terminator.
Expected hex: `454D4F53205541525431202D3E2050340D0A`.

| Endpoint | Role for this test |
| --- | --- |
| Agon PC0 / J1.17 → 220 Ω → P4 GPIO22 / EXT2.11 | UART1 TX → receiver RX, 115200 baud, 8N1 |
| Agon PC1 → P4 GPIO12 | Both receive/input roles; no P4 TX attachment |
| Agon PC2/PC3 → P4 GPIO23/GPIO11 | Flow control disabled; P4 pads remain inputs |
| Agon PC4–PC7 → P4 GPIO32/10/33/9 | Unused inputs |
| Agon ground ↔ P4 ground | Author confirmed connected on 2026-09-07 |

The r03 15 kΩ pull-ups remain on Agon 3.3 V; no circuit change is requested.
The Author reports both boards powered and both ribbons attached to the
breadboard. Keep the ribbons seated: the Author reports that removing them
strains the connectors and breadboard contacts, and reports successful prior
flashes with both boards powered and connected. That history is supporting
bench experience, not a measurement of every reset transient.
P4's application explicitly resets every r02/r03 harness pad to input with
internal pulls disabled, then attaches GPIO22 to RX only. It configures no
harness TX/RTS outputs. This does not establish ROM or framework startup pad
states. EMOS close_UART1 leaves PC0/PC1 muxed to UART; it is not GPIO isolation.
USB Serial/JTAG flashing uses separate GPIO24/25 (or 26/27), outside the eight
harness lanes; see Espressif's
[USB flashing documentation](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32p4/api-guides/usb-serial-jtag-console.html).
For this bounded update keep both boards powered and the Agon idle in Legacy,
with no pinwalk or UART sender running. Powering off the Agon alone is not
electrical isolation and is not required as a substitute for ribbon removal.

## Preparation and execution

1. Build the paired fixture with the workstation project interpreter:
   `.venv/bin/python scripts/prepare_uart_forward.py --output build/<new-directory>`.
   Approve its identity and commit controlled source before a candidate build.
   Require passing matcher tests, linked sender wrapper checks, RX-only P4
   source closure, effective SDK configuration, factory-image comparisons and
   output hashes. Retain the generated build manifest. Do not rebuild EMOS.
2. Leave the GPIO ribbons connected and both boards powered. The operator
   confirms the Agon is idle in Legacy with no GPIO/UART fixture running.
   The workstation verifies the current stable P4 USB identity using
   HARDWARE.local.md. Keep the Agon idle throughout P4 flashing and verification.
   Deploy only the selected frozen P4 receiver factory image, verify programmed
   bytes with esptool's verification operation, and retain logs. Use the built
   factory image at offset 0 with header settings preserved; do not substitute
   the held parallel image, generic upload target or an EMOS flash operation.
3. With the Agon SD mounted on the workstation, preserve its existing autoexec
   and any `/bin/U1SEND.BIN` destination outside the card. Reject overriding
   `!boot.obey`/`autoexec.obey` files rather than silently invoking another test.
   Stage the manifest's sender as `/bin/U1SEND.BIN` and this exact CRLF script:

   ```text
   VDU 22 3
   EMOS STATUS
   LOAD /bin/U1SEND.BIN
   RUN
   EMOS STATUS
   ```

   Verify, sync and unmount. There is no FLASH command. The first EMOS STATUS
   prevents automatic execution under stock MOS. All visible output must stay
   on the onboard VDP in Legacy with EDU inactive.
4. Once the receiver image and its input-only application are verified, keep
   the harness connected. Capture P4's USB diagnostics through the bench's
   existing pyserial environment. Confirm READY at GPIO22, 115200/8N1/no flow control, or the
   selected build's repeating WAIT report if startup output was missed.
   P4 has a 180-second first-byte deadline; if media preparation exceeded it,
   restart the verified P4 receiver for a fresh run before starting capture.
   This is a planned test start, not recovery of a failed UART transfer.
   The operator then
   cold-boots the Agon once; allow 30 seconds for MOS startup and a further
   10 seconds for the sender and final status/prompt. No keyboard input or
   P4-to-Agon response is required.
5. Run the tracked `docs/tasks/PORT-009/capture_on_pi.py` with the verified
   `--port`, `--expected-serial`, frozen `--build-id` and `--output-parent`
   from the local bench record. It reads USB diagnostics without transmitting
   or deliberately toggling reset; it creates a timestamped private capture
   folder and checks the received bytes/build. Start capture before the Agon
   boot and keep it running for its full interval, including at least five
   seconds after receipt. No additional Agon boot belongs to this one-shot run.
6. Record the Agon's `UART FORWARD SENT 18 bytes` and final Legacy/inactive-EDU
   status/prompt, plus P4's receiver PASS with the exact hex above. SENT alone
   proves no remote receipt. P4 waits 200 ms of quiet before PASS, fails a
   partial frame after 3 seconds, and permanently fails on wrong/extra bytes,
   overflow, framing/parity/break events or subsequent data after PASS. Any
   receiver restart or later FAIL invalidates an earlier PASS in the capture.
   Stop on failure; do not retry automatically or resume a held transport task.

Receiver reports repeat every five seconds so the terminal result remains
observable after startup. The capture must be tied to the exact deployment
build and checked alongside the Agon observation; an isolated log string is
not proof of the whole run.

## Evidence and limits

Keep the run manifest, source/build IDs, deployed hashes, flash verification,
USB capture, exact received bytes and Agon photograph/report beside this sheet.
Private machine/device paths and raw bench metadata stay in ignored evidence;
publish only sanitized records with integrity hashes. No hardware pass is
claimed by compilation or host tests.

This proves one short forward UART transfer through the installed EMOS driver.
It does not prove RTS/CTS, P4 TX/return traffic, sustained throughput, lossless
VDU parsing, video, keyboard input, activation or Exclusive Compatible mode.
The AgonDev UART-write wrapper's inverted return convention is documented and
checked in INTEG-003; the implementation remains local to the diagnostic caller.
