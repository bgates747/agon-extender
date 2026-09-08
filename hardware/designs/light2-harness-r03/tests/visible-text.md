# UART visible text — candidate test sheet

Identity: uart-visible-text-probe-r01. Status: candidate.
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

## Results

Draft preparation: both firmware builds pass; EMOS configured/linked/runtime
and 74 host checks, P4 transaction checks with ASan/UBSan, and 24 capture
checker tests pass. Same-build ordinary/bad-SD and no-peer CLI reviews pass.
The Author's graphical screenshot confirms the same draft build, SD/CLOCK
PASS, expected transmit timeout and final MOS prompt. The Author accepted
review and approved source freeze and clean candidate preparation on 2026-09-08.
Physical installation and paired text/browser evidence remain pending.

Pending. Acquisition and minimum quiet-tail failures remain separate checks;
any acceptance exception requires explicit Author disposition. No sustained-load,
complete startup, input or Exclusive Compatible activation claim.
