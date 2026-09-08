# PORT-011 — Prove UART RTS/CTS pause, resume and timeout

Status: reviewed and approved for source freeze and candidate deployment;
physical flow-control qualification pending.
Started: 2026-09-08.

## Scope and decisions

The Author authorized the next bounded r03 increment after PORT-010 passed.
Keep 115200/8N1, the seated four-wire UART harness, powered Agon reset,
Enter-to-arm capture and ordinary onboard VDP output. EMOS owns UART1 in Legacy.
Test both ready/wait directions and permanently blocked senders. No production
activation, VDU routing, parallel transport, wiring change or speed increase.

Author approved agon-emos-v0.4.0, uart-flow-probe-r01 and registry r29 for draft
review. Firmware source must pass automated and Author emulator review before
commit/candidate rebuilding. Existing working images and SD contents remain
until the replacement is concrete and reviewed. Physical deployment follows
the current bench authorization boundary. No new electrical claim is implied.

## Bounded research and implementation contract

1. Official MOS [UART API documentation](../../../../agon-docs/docs/mos/API.md#0x15-mos_uopen)
   provides the settings structure and blocking API contract. The accepted
   [stock audit](AUDIT-004/trace-hardware-and-dependencies.md) explains active-low
   RTS/CTS and that stock UART1 configures CTS on PC3 only. Official
   [uart.c](../../../../agon-mos/src/uart.c) and
   [serial.asm](../../../../agon-mos/src/serial.asm) remain read-only. EMOS Core
   adds bounded polling and explicit RTS ownership without changing public
   MOS blocking API semantics or adding an application transport bypass.
2. EMOS PC0 → P4 GPIO22 carries forward data; P4 GPIO12 → PC1 returns it.
   EMOS PC2 → P4 GPIO23 is P4 CTS; P4 GPIO11 → EMOS PC3 is EMOS CTS.
   HIGH means stop and LOW means ready. EMOS's internal driver must check CTS
   before each transmit-register write and reject another UART/RTS owner.
3. P4 uses the pinned ESP-IDF UART driver with CTS gating and a GPIO-controlled
   RTS for deliberately forced pauses. The [Espressif UART API](https://docs.espressif.com/projects/esp-idf/en/v5.3/esp32p4/api-reference/peripherals/uart.html)
   defines nonblocking FIFO enqueue via uart_tx_chars and bounded completion
   waits. Verify cancellation against the installed 5.5.5 source; do not leave
   a timed-out byte pending for later CTS release.
   The implementation disconnects physical TX, disables TX interrupts and
   resets only the owned TX FIFO through the pinned low-level API. RX remains
   live to detect later bytes/errors. The code records why the public RX-only
   flush cannot provide TX cancellation and when to remove this workaround.
4. The fixture uses a short fixed FLOW request/ACK, separate from product EDP
   protocol. P4 initially withholds CTS, observes the Agon RTS start edge, holds
   forward traffic for one second, then permits the request. EMOS then pauses
   return traffic for one second while P4 queues its ACK under hardware CTS.
   After exact ACK receipt, EMOS proves a blocked-transmit timeout; its RTS
   stop edge then triggers P4's own permanently blocked transmit-timeout check.
   Both endpoints check unexpected bytes/errors and require their own PASS.
5. Logs and the logic sniffer must distinguish an attempted, held transfer
   from an idle sender. Each endpoint has finite stage deadlines; EMOS also
   retains a finite stalled-clock polling escape. Finish with UART closed,
   added RTS ownership released and a normal MOS prompt. No test switches video
   modes; autoexec selects VDU 22 3 before same-build smoke and UARTFLOW.

## Work

1. [x] Implement EMOS driver/command and P4 peer with host negative tests.
2. [x] Build through the full existing EMOS gate, verify P4 compilation, and
   prepare same-build SD/clock/absent-peer emulator review and test sheet.
3. [ ] Obtain Author graphical acceptance and source-freeze approval; build
   clean candidates, preserve rollback media and prepare deployment/capture.
4. [ ] Qualify pause/resume and blocked timeouts on hardware, including exact
   bytes, no late traffic and prompt return. Keep results beside r03 design.

Machine-local topology, SD backup and hardware access live in HARDWARE.local.md
and ignored agents records. PORT-008 and held hardware tasks stay on hold.

The [test sheet](../../hardware/designs/light2-harness-r03/tests/uart-flow.md)
defines the four probe colors, exact wire exchange, separate endpoint verdicts
and waveform checks. Candidate capture preparation must combine analyzer
startup with the existing Enter/verified-WAIT reset cue; serial capture alone
cannot complete the waveform gate.

## Draft validation checkpoint — 2026-09-08

EMOS build agon-emos-v0.4.0-b2026-09-08-05-12-13Z passed the configured
qualification gate, linked UART-divisor/ABI/VDU/parallel checks and the runtime
regression. All 68 EMOS host tests passed with that build's prepared worktree.
The new command harness covers 15 success/failure scenarios, including a
stopped clock, stuck CTS, early/corrupt/extra replies and cleanup. An initial
direct unittest invocation selected the default stock worktree; rerunning the
repository test target with the correct EMOS worktree resolved those provenance
failures without weakening tests.

Same-build ordinary and deliberately bad-SD smoke passed against both stock
MOS and EMOS. The no-peer emulator case reported `peer did not hold CTS` and
returned to the prompt. The CLI exposes an unheld CTS in this configuration; this
is the expected diagnostic rejection, not proof of physical CTS timing.
MOS also prints its generic `Volume timeout` for this command's FR_TIMEOUT;
the preceding UART FLOW reason identifies the diagnostic failure, not an SD
fault. The graphical profile combines ordinary smoke and UARTFLOW for review.

P4 target compilation passed. Sanitized tests exercise the actual peer state
machine, including deadline wrap, missing/wrong/extra data, missing stop edges,
escaped blocked bytes and late failure. All 18 current UART capture-checker
tests passed, including five flow-specific tests of stage/order/identity and
readiness validation. These checks do not establish physical flow control.

Working SD files were copied and hash-verified off-card. No SD file, installed
image, physical processor state or wiring changed. Source remains uncommitted
pending the required Author emulator gate. Private bundles, logs and the
profile launcher are indexed in agents/uart-flow-handoff.md.

Registry r29 passes artifact validation. The repository-wide version-record
validator still stops on the held r02 profile's connectivity hash: the profile
expects `560ab589c9f0bbf63ecc17e747eff15208fb672723489c3b4755d7d9fea6b79c`,
while committed connectivity.yaml hashes to
`c68e4d4ffa2211cb18d3d558b3c88393cb1583d431e9258b6e78e7a10a6eda6f`.
Both files match HEAD; this mismatch predates this task. The held design was
not edited or requalified to clear an unrelated validation failure.

## Author graphical observation — 2026-09-08

The Author supplied a screenshot of the same draft build showing SD/CLOCK
PASS, `UART FLOW FAIL: CTS did not release`, the inherited `Volume timeout`
message and the final MOS prompt. The graphical emulator therefore exercised
the other permitted no-peer outcome: CTS stayed stopped until EMOS's bounded
deadline. The earlier CLI's unheld-CTS rejection and this graphical timeout
are separate observations; both meet the absent-peer review contract. Exact
wall-clock duration was not measured from the screenshot.

The Author requested that the agent launch graphical emulators for attention
alerts, including when no emulator validation is required, and subsequently
requested SD preparation and firmware deployment. The notification convention
is recorded in canonical development instructions. Explicit source-freeze
approval has been requested; no candidate or physical outcome is inferred
from the screenshot.

## Source freeze and deployment authorization — 2026-09-08

The Author explicitly approved the pending freeze/deployment request after
providing the expected graphical result. Freeze the reviewed implementation
as candidate, then build from clean committed EMOS/builder and P4 inputs.
The approved r29 registry is first committed with these candidate selections;
prior draft build manifests retain their original status and hashes. No new
version or revision is assigned. Preserve v0.3.0 as EMPREV.BIN and the existing
v0.2.0 EMBACK.BIN, with verified off-card backups. The authorization includes
preparing Agon installation media and flashing the P4 candidate with both
boards powered and the harness seated. Physical Agon installation still needs
the Author to move the SD card and press its reset button.
