# NET-009 — Update the ESP8266 through the Pi5 UART

Use the existing Pi5 header UART to test whether newer ESP8266 AT firmware
improves upload reliability. Smith puts the module into its serial loader.
Extender first identifies the flash and saves a verified rollback image.
The first comparison uses the Pi5 at both ends so it can run independently
of the Olimex P4 bench.

## Scope and starting point

1. The Olimex MOD-WIFI-ESP8266 reported AT 1.3.0.0 and SDK 2.0.0. The
   [Pi TCP control](PI-PEER-R01-RESULT.md) passed a 60-second upload at
   576,000 baud and lost bytes at 1,152,000. Retain those raw results.
2. The Pi5 owns RP1 header UART0 on GPIO14/15, previously verified at
   `/dev/ttyAMA0`. The module remains powered by the Pi5 3.3 V supply,
   using the [existing wiring sheet](PI5-ESP8266-WIRING.png). Preserve the
   Pi's debug UART, GPIO17 reset circuit and shared ground. This task
   changes only the ESP8266 firmware.
3. Espressif's [ESP8266 AT 2.2.2.0 release notes](https://github.com/espressif/esp-at/releases/tag/v2.2.2.0_esp8266)
   identify a UART RX ring-buffer fix. Start candidate preparation from
   [ESP8266 AT 2.3.0.0](https://github.com/espressif/esp-at/releases/tag/v2.3.0.0_esp8266),
   a later release in the same line. The measured deletion phenotype
   still needs an on-device comparison.

## Smith's first step

1. Leave the Pi5 running. At the **module end** of the harness, disconnect
   both UART signal leads (green and orange), then disconnect the red 3.3 V
   lead. Leave the module ground attached. Disconnecting the signal leads
   first prevents the Pi's UART from feeding the unpowered module.
2. Hold the module's **BOOT** button while reconnecting red 3.3 V.
   Release the button once the module powers up, then reconnect green and
   orange to their original positions using the wiring sheet.
3. Tell Extender the module is powered in bootloader mode. Leave it in
   that state for the Pi5's first read. After programming or recovery,
   Smith repeats the module-only power cycle with BOOT **released** to
   start the firmware. [Olimex module instructions](https://www.olimex.com/Products/IoT/ESP8266/MOD-WIFI-ESP8266/open-source-hardware) and
   [Espressif boot-mode guide](https://docs.espressif.com/projects/esptool/en/latest/esp8266/advanced-topics/boot-mode-selection.html).

## Extender execution and acceptance

1. **Identify.** Confirm the selected tty still points to RP1
   `serial@30000`, is outside the Linux console list and has no other
   owner. Use the project environment's `esptool` at 115,200 baud for a
   bounded read-only `flash-id` with `--before no-reset --after no-reset
   --no-stub`. Record ROM sync and detected flash capacity. If sync fails,
   retain the diagnostic and reconcile boot mode, wiring and host tty before
   attempting a write. The fallback programmer order is WROOM devkit,
   P4 devkit, then a 3.3 V TTL serial adapter.
2. **Preserve.** Read the detected full flash extent and verify the saved
   bytes against the device. Record the extent and SHA-256. Keep the image
   and device identifiers in access-restricted, ignored local evidence.
   The original flash may contain device-specific settings.
3. **Prepare.** Freeze the exact upstream archive or source revision, actual
   flash geometry and supported flash mode, image offsets, and hashes of
   the chosen write segments. Configure the candidate's AT UART for
   **GPIO1 TX / GPIO3 RX** at 115,200 baud with flow control disabled.
   Keep firmware logs off the command UART. Verify the board profile and
   factory-parameter bytes against the
   [Espressif ESP8266 port options](https://docs.espressif.com/projects/esp-at/en/release-v2.3.0.0_esp8266/Compile_and_Develop/How_to_set_AT_port_pin.html#esp8266-series).
   Document which original flash ranges the write replaces and how Extender
   would restore the verified original through the same Pi UART.
4. **Install and bring up.** Extender writes the frozen ESP8266 image and
   verifies the written ranges while the module remains in the loader.
   After Smith's normal power cycle, require `AT` and the expected
   `AT+GMR` on the same UART. Adapt the host association commands to the
   selected firmware if needed. Confirm runtime-only configuration with
   `AT+SYSSTORE=0` before using `AT+CWMODE` or `AT+CWJAP`. Use the Pi5's
   existing private credential provider for the Wi-Fi join. Keep credential
   bytes out of captures, process arguments and Git. [ESP-AT store mode](https://docs.espressif.com/projects/esp-at/en/release-v2.3.0.0_esp8266/AT_Command_Set/Basic_AT_Commands.html#cmd-sysstore).
5. **Compare.** Reuse the Pi TCP peer, wiring and deterministic CRC/sequence
   oracle from [PI-PEER-R01](PI-PEER-R01.md). Run the same finite directional
   baud ladder and 10/30/60-second backoff. Report the fastest error-free
   60-second upload, first fault and counts, and the reverse control. A
   passing host process alone does not qualify the rate. The Pi-to-P4
   Ethernet case stays a separate comparison under normal bench custody.
6. **Hand back.** Record installed firmware and final UART baud, return the
   modem to command mode, and close the tty. If the candidate fails basic
   bring-up, preserve the first failure and use the verified rollback image
   through the Pi UART. Keep the backup available for any later A/B repeat.

## Status

Bootloader sync, backup, candidate preparation, firmware installation and
comparison are pending.
