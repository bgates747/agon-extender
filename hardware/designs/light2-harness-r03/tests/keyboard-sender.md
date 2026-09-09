# Controlled P4 keyboard sender

Identity: `uart-keyboard-probe-r01`. Status: draft, not deployed.
Owner: [PORT-005](../../../../docs/tasks/PORT-005.md), coordinated with
[PORT-008](../../../../docs/tasks/PORT-008.md) and EMOS INTEG-009.

P4 presents processed events to the retained VDP keyboard helper, callbacks and
stock serializer. EMOS's resident UART1 interrupt/parser publishes the ordinary
MOS keyboard effects. This test observes those effects from an SD-loaded C
program; no browser input or full ExCom activation is included.

## Preparation and run

1. Complete host ordering/callback and orchestration checks, P4 compilation,
   paired EMOS emulator checks and Author graphical review. Freeze identified
   clean candidates before deployment. Preserve the installed EMOS v0.1.7 and
   P4 counting receiver as rollback. Review existing EMOS v0.1.8 evidence and
   use the guarded MOS installer; keep installation separate from test autoexec.
2. After installation confirmation, prepare same-build EMBOOT, `check.txt`
   and the independently built `KBWIRE.BIN`. Test autoexec contains:

   ```text
   VDU 22 3
   LOAD /bin/EMBOOT.BIN
   RUN
   LOAD /bin/KBWIRE.BIN
   RUN
   EMOS KEYINPUT
   ```

3. Keep the r03 ribbons seated and both boards powered. Record probe positions
   relative to the 220 Ω resistors. Analyzer leads: yellow D1 PC0→P4 RX22,
   gray D6 PC1←P4 TX12, orange D3 PC2→P4 CTS23, purple D4 PC3←P4 RTS11;
   common ground. The physical wiring is unchanged.
4. After separately authorized P4 deployment, use the prepared capture launcher.
   Enter arms P4/analyzer; reset the powered Agon only at RESET AGON NOW.
   Allow 2–3 seconds boot. Use 24 MHz, 288M samples on D1/D3/D4/D6 with D3
   falling trigger and 1% pretrigger. End after acquisition and five clean
   seconds after final P4 PASS, with a bounded overall failure timeout.
5. Require Agon SD/CLOCK PASS, both detailed P4 KEYBOARD PASS lines, final
   `P4 KEYBOARD PASS - returning to MOS`, mainboard input and MOS prompt.
   P4 must log locale, poll, twelve SENT events and final SENDER PASS without
   errors/restarts. Its SENT/PASS proves transmission, not eZ80 publication;
   retain the separate Agon screen and `/keyboard-state.bin` result (1).
6. Decode exact bytes, valid 8N1 at 1152000 baud, and CTS permission in each
   direction. Require complete acquisition and a five-second quiet tail as
   separate checks. After capture ends, reset only Agon twice; require the same
   successful results with P4 still running. A sender fault remains latched
   until P4 reset; successful cycles rearm after EMOS releases its input source.

## Expected traffic and effects

EMOS sends `17 00 81 01`, then `17 00 80 token`. P4 applies locale 1 and
returns the retained serializer's `80 01 token`. It waits 500 ms after TX
completion, then sends the following twelve stock packets with 250 ms between
completed transmissions. EMOS sends no per-key request or acknowledgement.

| Event | P4 → EMOS packet, hexadecimal |
|---|---|
| a down | `81 04 61 00 16 01` |
| a up | `81 04 61 00 16 00` |
| Shift down | `81 04 00 02 75 01` |
| B down, three events | `81 04 42 02 31 01` repeated three times |
| B up | `81 04 42 02 31 00` |
| Shift up | `81 04 00 00 75 00` |
| 7 down | `81 04 37 00 09 01` |
| 7 up | `81 04 37 00 09 00` |
| Enter down | `81 04 0D 00 8F 01` |
| Enter up | `81 04 0D 00 8F 00` |

Totals: 8 forward bytes, 3 poll reply bytes and 72 unsolicited key bytes.
The application verifies callback payload/order relative to publication,
counter increments, separately held Shift/B map bits, repeated-down effects,
final released state and clock progress. It has a ten-second input deadline,
clears its callback and restores mainboard input on every exit. A missing
sender must not leave an application waiting indefinitely.

## Scope and results

Pre-hardware graphical result: the Author supplied the matching
`uart-keyboard-probe-r01-b2026-09-09-02-36-43Z` screenshot showing SD/CLOCK
PASS, both detailed keyboard PASS checks, mainboard input restored and final
MOS prompt. The controlled peer reports twelve keys and PASS. EMOS remains
`agon-emos-v0.1.8-b2026-09-09-00-09-53Z`. Source-freeze approval is pending;
this is emulator evidence, not a physical P4 sender result.

Physical results pending. The local host tests exercise retained method bodies
with variable/context fakes and hardware orchestration with UART/GPIO fakes.
The emulator receives those serializer-produced bytes and executes real EMOS;
it does not execute the P4 binary or validate baud/CTS/RTS electrical timing.

Layout translation, a repeat generator, browser focus/takeover/disconnect,
keyboard settings/query routing, physical LEDs, raw `&99` key-state queries,
abrupt reset and sustained load remain separate work. The selected P4 test
Stream deliberately admits only locale and General Poll commands. The optional
processed FIFO has one process-task owner; a future network producer must
marshal events to that owner before using it.
