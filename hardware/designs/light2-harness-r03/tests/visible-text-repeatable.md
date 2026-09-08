# UART visible text — repeatable candidate test sheet

Identity: uart-visible-text-probe-r02. Status: candidate.
Owning task: [PORT-014](../../../../docs/tasks/PORT-014.md).

EMOS VDPTEXT sends one 35-byte clear/position/text/flush/poll sequence over
r03 UART1, 1152000/8N1 with RTS/CTS. EDP's retained parser draws
`EMOS TO EDP: UART TEXT` at character position (2,2), flushes drawing and
produces General Poll return `80 01 A6`. The browser must show the message
from the existing P4 framebuffer service. Parser ACK alone is not display proof.
No video-mode switch is sent; EMOS stays in Legacy with onboard console/clock.

## Preparation and run

1. Pass draft host/build/linked/runtime checks and Author graphical no-peer
   review. Freeze clean identified candidates before physical installation.
   Preserve passing EMOS v0.6.0 and General Poll P4 rollback.
2. Use guarded EMOS installation, then separate same-build smoke/test media:

   ```text
   VDU 22 3
   LOAD /bin/EMBOOT.BIN
   RUN
   EMOS VDPTEXT
   ```

3. Keep both boards powered and the r03 harness seated. Analyzer leads:
   yellow D1 PC0→P4 RX22; gray D6 PC1←P4 TX12; orange D3 PC2→P4 CTS23;
   purple D4 PC3←P4 RTS11, common ground. Record probe resistor-side positions.
4. Start the prepared workstation capture, Enter to arm, then powered Agon
   reset only at RESET AGON NOW. Allow 2–3 seconds for boot. Capture 24MHz,
   240M samples on D1/D3/D4/D6, D3 falling trigger, 1% pretrigger. End after
   acquisition completion and five clean seconds after P4 final PASS.
5. Confirm Agon SD/CLOCK PASS, VDP TEXT PASS and final MOS prompt. Require
   exact complete request/reply with valid framing and CTS permission, and
   ordered P4 receiver/parser/send/PASS records without errors/restarts.
6. Open the existing P4 browser display, confirm the exact message and retain
   a screenshot/frame receipt. Record browser connection and successful fresh
   frame delivery. No test text may be synthesized by browser or P4 fixture.

## Repeat without restarting P4

After the captured exchange, reset Agon again while leaving P4 and the browser
running. Require another Agon TEXT PASS and prompt return, an incremented P4
CYCLE record and the same browser text. Repeat once more. The browser may
connect after any exchange; P4 retains the framebuffer. Idle waiting does not
expire. Active-transfer deadlines and malformed/extra-byte checks remain.

P4 releases its driven UART pins after the ACK and waits for EMOS RTS to stop
before clearing the completed transaction. A new EMOS RTS assertion reconnects
P4's TX/RTS pins and admits the next exact request. Failures stay latched for
inspection; this revision adds repeatability after success, not fault recovery.
The capture launcher still measures one transaction per invocation; its P4
restart provides a known acquisition baseline. Extra resets belong after that
capture has finished and are separately observed repeatability checks.

## Results

The original r01 definition remains frozen in commit a3ab788. The first r01
run has P4/Agon success, complete acquisition and browser-visible text; exact
waveform review and final Agon smoke/prompt confirmation are tracked separately.
The Author requested repeatability after an Agon-only second reset timed out.
R02 host checks pass for repeated success, idle beyond 180 seconds, malformed
input and active transmit timeout. Physical r02 repeatability remains pending.
