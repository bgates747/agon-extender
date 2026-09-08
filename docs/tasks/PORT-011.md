# PORT-011 — Prove UART RTS/CTS pause, resume and timeout

Status: complete. Author accepted the UART flow test as PASS, including the
explicit shortened-acquisition exception. Candidate identities are unchanged.
Started: 2026-09-08.
Finished: 2026-09-08.

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
3. [x] Prepare capture. Author graphical acceptance/source freeze, clean builds,
   both installations, rollback/test media and capture handover are done.
   The Author chose to proceed directly to the paired run; verify actual
   acquisition duration in its results, retaining the existing 60-second check.
4. [x] Qualify pause/resume and blocked timeouts on hardware, including exact
   bytes, no late traffic and prompt return. Keep results beside r03 design.
   Endpoint and retained-waveform checks pass; the Author accepted the
   shortened acquisition explicitly for this completed run.

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

## Candidate preparation and P4 deployment — 2026-09-08

EMOS `agon-emos-v0.4.0-b2026-09-08-05-51-31Z` was built from clean EMOS
`3d8e09d` and builder `cf24304`. Its full
configured gate, 68 host tests and exact-candidate ordinary/bad-SD/no-peer
checks passed. The implementation matches the reviewed draft.

P4 `uart-flow-probe-r01-b2026-09-08-05-51-31Z` was built from clean Extender
`3869264`, flashed and independently verified under the Author's
authorization. [Deployment PORT-011-2026-09-08-05-54-22Z](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-05-54-22Z/README.md)
records the matching candidate startup and empty stopped-CTS WAIT.

[Preparation PORT-011-2026-09-08-05-55-02Z](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-05-55-02Z/README.md)
records verified, safely unmounted Agon installation media and both rollback
payloads. The Author must insert SD and reset Agon once to install EMOS, then
remount SD for the separate smoke/UARTFLOW test. Physical installation, the
combined analyzer capture launcher and actual flow-control results remain
pending. No existing qualified result is extended by these preparation checks.

## EMOS installed; analyzer preflight incomplete — 2026-09-08

The Author reported a successful EMOS flash. The remounted SD's EMDONE.BIN
matches the selected v0.4.0 candidate exactly; EMNEW.BIN is absent and both
rollback images remain intact. The installation record above now includes
that report. No raw flash-screen CRC or physical UARTFLOW result is inferred.

[Preparation PORT-011-2026-09-08-06-05-59Z](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-06-05-59Z/README.md)
replaced the guarded installer with the exact same-build smoke/UARTFLOW media,
verified the copied hashes and safely unmounted the SD. Both boards remain
powered and the harness remains seated. No processor was reset this turn.

The private combined launcher is staged. It verifies the selected P4, waits
for actual analyzer data and the frozen serial checker's empty WAIT before
issuing the reset cue, and separately verifies saved sample extent. Checks
reject both real truncated traces and a synthetic wrong-channel capture;
an exact-size synthetic capture passes acquisition validation only.
The orchestrator has not yet run against the physical flow exchange.

Two measurement-only preflights requested the approved 2 MHz / 60-second /
D1,D3,D4,D6 capture but saved only
[15.84128 seconds](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-06-05-31Z/README.md)
and [20.85888 seconds](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-06-12-01Z/README.md).
Both exited zero after repeated empty USB transfer timeouts. This reproduces
the acquisition issue seen during pinwalk, without establishing its cause or
any UART result. USB autosuspend was already disabled; no corresponding USB
disconnect was present in the inspected kernel log. Do not weaken the capture
duration or infer success from the process exit code.

The Author subsequently cycled the sniffer and explicitly chose the paired
test run without another idle-wire preflight. The requested acquisition settings
and separate sample-extent verdict remain unchanged. Earlier short traces
remain informative; no endpoint firmware change is justified by them.

## Capture discovery correction and Pi restart — 2026-09-08

Attempt PORT-011-2026-09-08-16-06-12Z stopped during discovery before P4 rearm,
analyzer sampling or an Agon reset cue. The sniffer was present in the saved
scan. The private launcher incorrectly parsed the short `sigrok-cli --scan`
output as a detailed device row and omitted the detailed row's channel suffix.
Its printed P4/acquisition FAIL lines therefore describe checks that did not
run; they are not endpoint or waveform failures. Preserve this informative
launcher defect in the local attempt record.

The helper now requests `--scan --show`, validates the complete device row,
and uses its current connection identifier. After a power cycle, the first
scan can return a bare row while the FX2 firmware loads and USB re-enumerates;
in that specific case, the helper waits two seconds and rescans once. Missing,
duplicate or unexpected devices still stop setup before P4 rearm. Checks not
started are reported as NOT RUN, with null verdicts in the result record.

The Author suggested restarting the Pi, which completed and was verified by
a changed boot ID. The Author clarified that the intervening P4 USB absence
was their power-down to inspect wiring; it is not evidence of a USB defect.
Both devices are now back up and pass the corrected discovery checks. The
helper's local/remote hashes match; tests cover real scan formatting, initial
bare-row recovery, bounded retries, rejection cases and no-reset/NOT RUN
behavior on setup failure. No additional sampling or UARTFLOW run occurred.

The remounted SD's test files and consumed payload still match the frozen
candidate; no higher-priority boot script or EMNEW.BIN is present. The card
was safely unmounted without edits. Next action: Author inserts the card,
runs the existing workstation launcher, presses Enter, then resets Agon at
the cue. Preserve the 90-second serial capture and report analyzer extent
separately; the earlier shortened acquisitions remain unresolved observations.

## Physical flow result — 2026-09-08

[Run PORT-011-2026-09-08-16-16-36Z](../../hardware/designs/light2-harness-r03/tests/PORT-011-2026-09-08-16-16-36Z/README.md)
passes the P4's exact ordered flow-stage checker. The Author independently
confirmed Agon UART FLOW PASS, SD/CLOCK PASS and normal MOS prompt return.
Raw serial integrity and the frozen verdict were independently rechecked;
capture includes 70.125 seconds after first P4 success without later RX errors
or unexpected bytes. No new screen image was supplied.

The retained 2 MHz waveform decodes exactly six forward bytes `FLOW\r\n`
and nine return bytes `FLOWACK\r\n`. Measured forward/return holds are
1.0012325 and 0.985767 seconds. Both senders remain silent while stopped;
the trace contains 11.526723 seconds after the final stop, with no escaped
A5 or 21 byte. P4 queue/cancellation logs and the Author's EMOS PASS support
the attempted-transfer checks that a quiet waveform alone cannot establish.

Acquisition nevertheless saved only 55,152,640 samples (27.57632 seconds),
with the same empty USB timeouts and zero exit code as the earlier preflights.
The original acquisition FAIL remains. The run outcome is partial pending
Author disposition; the recommendation is to accept the bounded UART increment
because the complete exchange and required quiet tail are present, retaining
the analyzer defect separately. No firmware version/status, capture threshold,
task completion or qualification claim has been changed by that recommendation.

The Author suggested exhaustion of sampling memory. The installed
[libsigrok 0.5.2 driver](https://raw.githubusercontent.com/sigrokproject/libsigrok/libsigrok-0.5.2/src/hardware/fx2lafw/protocol.c)
continuously forwards incoming samples and resubmits USB buffers; its start
command sends sampling settings, with the sample-count limit enforced by the
host. The three 2 MHz attempts stopped at different sample counts. This makes
a fixed onboard capture-capacity limit less likely. A temporary FIFO/USB
buffer overrun or host streaming stall remains a hypothesis, not an observed
cause. No lower-rate diagnostic or further hardware operation was run during
this evidence review.

## Author acceptance and completion — 2026-09-08

The Author instructed: "approve this as a passed test." Run
PORT-011-2026-09-08-16-16-36Z is accepted as PASS for the declared bounded
UART flow-control scope. Its 27.57632-second trace contains the entire
exchange and 11.526723 seconds after the final stop, alongside both endpoint
reports and normal MOS prompt return. The run manifest records the dated
change from partial to accepted pass without altering original measurements
or the acquisition FAIL. The 60-second procedure remains unchanged for future
runs; the analyzer issue is unresolved and is retained as a known limitation.

All work is complete. Removed this task and sibling EMOS INTEG-005 from their
authoritative TODOs. No new firmware version, lifecycle promotion, hardware
operation or broader compatibility claim follows from this acceptance.
