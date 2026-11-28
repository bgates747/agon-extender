# MOS recovery on Olimex

Use the commissioned [Olimex bench procedure](operations/olimex-bench/README.md)
and its standard `FLASH mos` phase while the MOS prompt is usable. The
runner verifies FLASH's CRC for the staged 128 KiB ROM before confirmation.
FLASH reads the programmed ROM on the eZ80 and checks the CRC locally. The
runner requires that result, the automatic reboot and fresh MOS evidence.
A missing write check or boot witness calls for the bench stop procedure.

**If MOS cannot boot, the Author selects an external ESP32-WROOM programmer
connected to the eZ80 ZDI header.** The Author recalls WROOM succeeding
more than once and identifies it as the only repeatably successful route.
Commission the exact WROOM, recovery image and verification
commands for the incident before wiring or writing. Keep the production
Extender P4 and onboard VDPlet installed. The current P4-PC is unqualified as
an eZ80 ZDI programmer and must not be used as the recovery fallback or as a
routine preflight for `FLASH mos`.

## Commission WROOM recovery

1. Keep the reservation, stop the original operation, retain its logs and
   obtain the Author's recovery disposition. Establish the last verified
   ROM and whether MOS actually reached a prompt. A missing prompt alone
   cannot distinguish ROM damage from an interrupted startup handshake.
2. Pin the exact recovery ROM from the current Extender production selection,
   including its full 131,072-byte extent and SHA-256. For the complete
   installed baseline, use the production ROM linked from the bench
   procedure. Keep the SD startup and user files intact.
3. Bind the confirmed external ESP32-WROOM-32D DevKitC and its USB identity.
   Use the job's reviewed build of
   [Agon recovery](https://github.com/AgonPlatform/agon-recovery/tree/95d68464afd049945e1dfd780c1c07621d565450).
   The pinned reference uses the `esp32dev` target and a USB serial menu.
   Bind the WROOM firmware and filesystem contents to the exact MOS payload
   and flash agent before deployment. The 90-byte upstream flash-agent
   reference SHA-256 is
   `ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06`.
   Select MOS-only recovery. Verify the actual firmware, serial commands and
   firmware readout capabilities when commissioning the job.
4. With the boards powered off, confirm the header markings and attach only
   the documented WROOM ZDI signals and ground. Keep `ESP_PROG1` and
   `UART_D` open for normal onboard VDP operation. Leave the normal
   UART/PARLIO harness in its approved configuration. The Pi reset circuit
   drives reset and supplies neither ZDI programming signal.
5. Establish the expected eZ80 product and revision before any write. The
   retained Olimex identity is product `0007`, revision `AA`. Preserve the
   existing ROM and programming transcript. Verify the commissioned route can
   independently retrieve the entire ROM. A built-in programmer checksum or
   a successful serial-menu response alone is insufficient for handback.
6. Under the recovery disposition, write the pinned production EMOS ROM and
   independently compare all 131,072 bytes. Stop at the first unexpected
   result and preserve the evidence. After a successful readback, arrange
   safe removal of the programmer with the affected boards powered off. On
   restart, require the production MOS banner, a working CLI, fresh keyboard
   admission and working SD service. Follow the normal handback procedure
   before check-in.

## WROOM to Olimex ZDI1 wiring

Use the [original ZDI connector diagram](mos-recovery/zdi.png) and confirm
pin 1 on the actual board. Viewed with the notch at the top, the upper row
is 5/3/1 and the lower row is 6/4/2.

| Signal | Reference wire | WROOM GPIO | Olimex ZDI1 |
| --- | --- | --- | --- |
| Clock / TCK | Blue | GPIO26 | Pin 4 |
| Bidirectional data / TDI | Green | GPIO27 | Pin 6 |
| Common ground | Ground | GND | Pin 3, or the diagram's pin 5 |

Use a separate USB connection for the WROOM. Keep ZDI1 pin 1 (+3.3 V) and
pin 2 (reset) out of the programmer wiring. The
[WROOM-to-ZDI diagram](mos-recovery/console8_zdi.png) shows the same signal
assignment. Consult the [diagram provenance](mos-recovery/PROVENANCE.md)
for the retained source drawings.

## Why P4 is excluded on the current bench

The historical P4 ZDI record used the original **Olimex P4 DevKit**. The
retained USB-identified programmer transcript reports one successful flash
and contains a complete post-write dump matching its selected ROM. The Author
reports that the most recent attempt with that DevKit failed. The current
**P4-PC** is a different device and has no verified eZ80 ZDI write.

The November 22 INTEG-019 attempt on the current P4-PC independently verified
and booted its temporary recovery app, then failed its first ZDI identity
read with `0000/00`. The optional ZDI leads were disconnected. That result
establishes the observed stop, with no eZ80 dump, erase or write. Production
P4 was restored and independently verified. Both the candidate install and
the later production EMOS restore succeeded through standard `FLASH mos`.

The old P4 implementation and historical evidence remain available for source
inspection. Neither the old DevKit wiring record nor the standard UART/PARLIO
harness establishes the presence of ZDI leads on today's bench. The Author's
current recovery selection is the external WROOM route above.
