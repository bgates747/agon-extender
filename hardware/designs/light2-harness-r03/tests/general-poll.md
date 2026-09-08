# General Poll — candidate test sheet

Identity: **uart-general-poll-probe-r01**; status: **candidate**.
Owning task: [PORT-013](../../../../docs/tasks/PORT-013.md).

## Contract

EMOS in Legacy sends `17 00 80 A5` over UART1 at 1,152,000 baud, 8N1,
with RTS/CTS. EDP's retained VDU parser, General Poll callback/variable handler
and packet serializer produce exactly `80 01 A5`. The P4 fixture admits one
complete request and transmits the parser's buffered output. It does not
implement its own General Poll response. This does not activate a product mode
or implement the rest of startup (including automatic mode information).

| Probe | Agon | P4 | Direction |
| --- | --- | --- | --- |
| Yellow D1 | PC0 TX | GPIO22 RX | EMOS → EDP |
| Gray D6 | PC1 RX | GPIO12 TX | EDP → EMOS |
| Orange D3 | PC2 RTS | GPIO23 CTS | EMOS permits EDP when LOW |
| Purple D4 | PC3 CTS | GPIO11 RTS | EDP permits EMOS when LOW |

Keep the seated r03 harness and common ground. Record probe positions relative
to the 220 Ω resistors. No parts/wires change. Onboard VDP remains the ordinary
console and 60 Hz clock source. P4's diagnostic omits browser/network startup.

## Preparation and run

1. Pass EMOS host/full configured/linked/runtime checks, same-build ordinary
   and bad-SD smoke, and graphical no-peer review. Expected absent-peer result:
   bounded transmit timeout or no reply, then MOS prompt. Freeze reviewed
   candidate inputs and rebuild cleanly before authorized hardware deployment.
2. Preserve passing v0.5.0/r02 rollback. Use guarded EMOS installation media,
   then replace the installer with same-build EMBOOT/check.txt and autoexec:

   ```text
   VDU 22 3
   LOAD /bin/EMBOOT.BIN
   RUN
   EMOS VDPPOLL
   ```

3. After both candidates are installed, insert prepared SD and start the
   combined capture. Press Enter; wait for verified empty P4 WAIT/CTS HIGH and
   positive analyzer transfers. Press powered Agon reset only at RESET AGON NOW,
   within ten seconds; allow the normal 2–3-second boot delay.
4. Request 24 MHz, 240,000,000 samples (10 seconds), D1/D3/D4/D6, D3 falling
   trigger and 1% pretrigger. Finish after analyzer completion and five clean
   seconds after final P4 PASS. Ninety seconds is a stall deadline, not a
   mandatory wait. Retain errors/restarts/late bytes as failures.
5. Confirm Agon SD/CLOCK PASS, `VDP POLL PASS: reply 80 01 A5 - returning to MOS`
   and final prompt. Require ordered P4 START, exact REQUEST, PARSER reply,
   SENT count=3 and PASS. Verify actual acquisition extent, decode both exact
   frames at the target baud without warnings, require data only while CTS
   permits it and at least five seconds of quiet after the final RTS stop.

## Results

Hardware result pending. [Installation media](PORT-013-2026-09-08-17-55-37Z/README.md)
is prepared from the clean candidate; the card is safely unmounted and working
v0.5.0 is retained for rollback. P4 staging is verified; flashing is pending.

Preserve original trace, serial log, identities, command/extent metadata,
measured waveform and Author screen/prompt observation beside this sheet.
No sustained-load, analog-margin or complete startup qualification is implied.
