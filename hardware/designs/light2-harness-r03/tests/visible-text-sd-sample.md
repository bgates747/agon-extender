# UART visible text — SD-loaded counting sample

Identity: uart-visible-text-probe-r03. Status: candidate.
Owning task: [PORT-014](../../../../docs/tasks/PORT-014.md).

The SD-loaded C sample clears the EDP text area, positions the banner at (2,2),
prints `EMOS TO EDP: UART TEXT`, then decimal 1..10, each followed by CR/LF.
The sample submits the banner and each number separately. After each completed
exchange it waits approximately 250 ms before submitting the next line; UART
acknowledgement/quiet time adds to the visible interval. Preview uses the same
250 ms clock-based pause.
The application calls EMOS's resident `edu.text-probe` gateway. EMOS sends
the text over r03 UART1 at 1152000/8N1 with RTS/CTS and adds flush/General Poll.
P4 admits the complete bounded stream, runs the retained parser and transmits
its actual `80 01 A7` reply. No banner/count is synthesized on P4 or browser.
Ordinary MOS console/clock remain onboard; this is not mode activation.

## Preparation and run

1. Review the draft EMOS build and independently built sample in the emulator.
   Require ordinary boot/SD/clock, correct preview count, invalid-request
   rejection and bounded no-peer return. Preview is onboard-only evidence.
   Freeze clean candidate inputs after Author approval before installation.
2. Preserve installed v0.7.0 EMOS and r02 P4 rollback bundles under their
   original identities. Use guarded EMOS installation for v0.1.7, then separate
   same-build smoke and independently identified VTEXT.BIN media:

   ```text
   VDU 22 3
   LOAD /bin/EMBOOT.BIN
   RUN
   LOAD /bin/VTEXT.BIN
   RUN
   ```

3. Keep both boards powered and ribbons seated. Analyzer: yellow D1 PC0→RX22;
   gray D6 PC1←TX12; orange D3 PC2→CTS23; purple D4 PC3←RTS11; common ground.
   Record resistor-side probe positions. Existing r03 circuit is unchanged.
4. Start the capture, Enter to arm, then powered Agon reset only at RESET AGON
   NOW. Allow 2–3 seconds boot. Capture 24MHz, 288M samples (12 seconds) on D1/D3/D4/D6,
   D3 falling trigger, 1% pretrigger. End after acquisition and five clean
   seconds after P4 PASS; retain a bounded overall failure timeout.
5. Require Agon SD/CLOCK PASS, VDP TEXT SAMPLE PASS and final MOS prompt.
   Require 11 ordered P4 transactions, exactly 136 request bytes and 33 reply
   bytes in total, valid
   framing and CTS permission, with no late traffic/errors/restarts. Short
   analyzer acquisition or quiet tail remains a separate failed check.
6. Confirm fresh browser frames show the banner and numbers 1..10 on separate
   lines. Retain screenshot/frame receipt. After capture finishes, reset Agon
   twice more with P4/browser running; require the same display, PASS and MOS
   prompt each time. P4 errors remain latched; this tests repeated success.

## Expected bytes

Text payload totals 59 bytes across 11 transactions. EMOS appends
`17 00 CA 17 00 80 A7` to **each** submitted buffer and requires a separate
`80 01 A7` reply before returning to the sample.

1. Banner transaction: 35 bytes including suffix:

   ```text
   0C1F0202454D4F5320544F204544503A205541525420544558540D0A1700CA170080A7
   ```

2. Nine transactions for 1..9: ASCII numeral, `0D 0A`, then the suffix;
   each request is 10 bytes.
3. Final transaction for 10: `31 30 0D 0A 17 00 CA 17 00 80 A7`, 11 bytes.

The capture checker requires all 11 completions before starting its five-second
clean tail. The 12-second analyzer extent gives the paced exchanges and final
five-second quiet interval room to complete. Parser ACK and browser appearance
are independent checks.
No physical r03 run is recorded yet. Previous r01/r02 evidence retains its
original definition and identity. The old EMOS VDPTEXT/A6 command remains
available but is not the counting sample.
