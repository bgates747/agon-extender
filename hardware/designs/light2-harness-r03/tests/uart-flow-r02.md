# UART RTS/CTS pause and timeout — candidate test sheet

Approved identity: **uart-flow-probe-r02**; lifecycle: **candidate**.
Owning task: [PORT-012](../../../../docs/tasks/PORT-012.md).
The Author accepted graphical review and approved source freeze/candidate preparation.
Build clean candidates before the physical procedure; draft images are retained
only as review evidence.

## Purpose and wiring

At 1152000 baud, 8N1, EMOS and the P4 diagnostic exercise both active-low
ready/wait lines in the existing seated r03 harness. EMOS owns UART1 and its
RTS output; P4 uses hardware CTS gating and deliberately controls its RTS as
a GPIO. Ordinary EMOS output and the MOS clock still use the onboard VDP.

| Analyzer lead | Agon endpoint | P4 endpoint | Meaning |
| --- | --- | --- | --- |
| Yellow / D1 | PC0 / TXD1 | GPIO22 / RX | EMOS → P4 data |
| Gray / D6 | PC1 / RXD1 | GPIO12 / TX | P4 → EMOS data |
| Orange / D3 | PC2 / RTS | GPIO23 / CTS | EMOS permits P4 transmission when LOW |
| Purple / D4 | PC3 / CTS | GPIO11 / RTS | P4 permits EMOS transmission when LOW |

These are the established ribbon/probe colors, without the obsolete diagram
circles. Record probe locations relative to the 220 Ω resistors and confirm
analyzer ground joins the boards' common ground. Keep both boards powered
and ribbons seated. PC4–PC7 remain connected but unused; PD4/PD5/PD7 remain
isolated. This test adds no parts or wires to the harness.

## Preparation

1. Review EMOS v0.5.0 using its same-build SD/clock smoke and no-peer test in
   the emulator. An absent peer must produce a bounded CTS failure and the
   final MOS prompt. That is an expected negative result, not a flow-control
   hardware PASS. Retain the working v0.4.0 rollback image.
2. After Author review and freeze, build clean EMOS and P4 candidates. Record
   their separate build identities and hashes. Install EMOS with the established
   guarded installer, then replace that installer with this test's autoexec.
   Deploy and verify the approved P4 image while Agon is idle at its prompt.
3. The combined test autoexec is exactly (CRLF):

   ```text
   VDU 22 3
   LOAD /bin/EMBOOT.BIN
   RUN
   EMOS UARTFLOW
   ```

   EMBOOT and `/emos-boot/check.txt` belong to the reviewed EMOS bundle.
   No flash command or mode switch is hidden inside a fixture. Safely unmount
   the SD card before returning it to Agon.
4. Prepare simultaneous P4 serial and logic-analyzer capture. Retain the
   original `.sr` file and acquisition metadata. Request 24 MHz and 240,000,000 samples (10 seconds),
   channels D1/D3/D4/D6, falling-edge trigger D3=f and captureratio=1
   (1% pretrigger, nominally 0.1 seconds). The PC2 start edge triggers recording;
   boot delay does not consume the saved window. Verify positive USB sample
   transfers before the reset cue, without waiting for post-trigger logic data; verify actual rate, channel mapping and sample extent
   before interpreting the trace. Decode both data lanes as 1152000/8N1,
   idle HIGH, least-significant bit first. Missing acquisition evidence leaves
   the waveform part incomplete even if endpoint logs pass.

## One powered-reset run

1. Start the prepared workstation launcher. It waits for **Enter** before
   restarting/arming P4 and saves low-level output to files. It must issue
   **RESET AGON NOW** only after the analyzer capture has started and the
   verified P4 serial port reports the selected build's empty WAIT with
   `cts=1`. A low CTS before Agon's command starts is a readiness failure.
2. Press and release Agon's reset button once at that cue, within ten seconds.
   Allow the usual 2–3 seconds for boot. Keep both boards powered. The host
   retains P4 serial capture for 90 seconds after the cue, including at least
   five seconds after P4 PASS. Do not reset again during capture.
3. EMOS should print SD/CLOCK PASS, followed by these four stage results and
   its final result:

   ```text
   UART FLOW FORWARD PAUSE PASS
   UART FLOW RETURN PAUSE PASS
   UART FLOW BLOCKED TX PASS
   UART FLOW BLOCKED RETURN QUIET PASS
   UART FLOW PASS - returning to MOS
   ```

   Confirm the normal MOS prompt and capture the screen. A hang, missing
   stage, UART error or failure is not a passing physical test.
4. The P4 capture checker requires its ordered release, exact request, queued
   ACK, sent ACK, queued blocked byte, cancelled timeout and final PASS records.
   Wrong bytes/builds, duplicate stages, restart or later error/extra bytes
   fail its verdict. P4 success alone does not establish EMOS receipt or
   prompt return.

## Waveform checks

| Phase | Required observation |
| --- | --- |
| Forward pause | PC2 falls to start. PC3 remains HIGH for about one second while EMOS attempts to send. PC0 carries no request until PC3 falls. |
| Forward resume | PC0 decodes exactly `FLOW\r\n` (hex `464C4F570D0A`). P4 raises PC3 after receiving the request. |
| Return pause | EMOS raises PC2 for about one second. P4's log proves the nine-byte ACK was queued during that stop; PC1 remains idle. |
| Return resume | After PC2 falls, PC1 decodes exactly `FLOWACK\r\n` (hex `464C4F5741434B0D0A`), with no extra bytes. |
| Blocked EMOS sender | PC3 stays HIGH after the request. EMOS reports its one-second blocked attempt; no `A5` byte appears on PC0. |
| Blocked P4 sender | The final PC2 rising edge requests a blocked `21` byte (`!`). P4 reports one second blocked and cancellation. No such byte appears on PC1, including the quiet tail. |

Measure both deliberate pause intervals; the endpoint checks require at least
0.5 seconds and enforce finite stage deadlines. Review the complete exchange
and at least five seconds after its final stop edge. Pair the trace with both
endpoint reports: a quiet data line alone does not prove a sender attempted
transmission. Record actual acquisition duration; a shortened trace cannot
silently inherit the requested duration.

On exit EMOS closes UART1 and returns its added PC2 output to GPIO input.
P4 disconnects TX before clearing its blocked FIFO, releases RTS, and keeps RX
monitoring for late errors/bytes. The existing 15 kΩ pull-ups provide the stop
level after release. A HIGH waveform alone does not prove high impedance.

## Results and limits

Pending. Record actual sample rate/count and trigger position, then decode both
lanes at 1,152,000 baud. Measure bit spacing against the nominal 0.868056 µs
(about 20.83 samples at 24 MHz); report measured timing and decode errors rather
than inferring baud from endpoint success. Require the complete exchange and
at least five seconds after the final stop. A premature trigger, missing start
edge or shortened acquisition must be reported explicitly.

The previous r01 acquisition stopped early after USB timeouts; this revised
window is not a claim that the underlying issue is repaired. Keep endpoint,
acquisition and waveform verdicts separate. No idle acquisition preflight is
required: the Author chose a paired run. Store passing or informative evidence
beside this sheet. This short exchange does not qualify sustained traffic,
buffer capacity, reset/unequal-power behavior or production EDP activation.
