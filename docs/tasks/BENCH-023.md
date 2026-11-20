# BENCH-023 — Detect and report a mainboard ESP32 programmer sync failure

Research how the Pi5 runner can identify a failed ESP32 ROM session, tell the operator whether it reached flash, and point to the original evidence. On 2026-11-20, the ten USB flash attempts with upstream Bistromathics produced eight verified writes and two failures before writing. The standard app0 programmer reproduced the earlier ROM SYNC error. Production app0 and working MOS were verified at handback. The reporting design remains a proposal.

## Incident and sources

VDPL-057 reached a working MOS prompt on boot `619087984`. Its next worker, `restore-store`, called the classic ESP32 programmer at 115,200 baud. The connection call raised before the programmer reached its store operation. The parent recorded exit 1 and joined the worker. That attempt performed zero flash reads, erases or writes. Entering the ROM downloader can itself interrupt normal execution, so the earlier prompt is historical. The last verified application selection was the candidate in app1. [Original programmer log](../../../../agon-vdplet/build/vdpl057/olimex01/run/restore-store/programmer.log) · [Parent wait record](../../../../agon-vdplet/build/vdpl057/olimex01/run/restore-store/child-terminal.json) · [Earlier cases and passing comparisons](BENCH-022/FINDINGS.md)

| Source reviewed | Finding relevant to the trap |
| --- | --- |
| Agon Platform firmware guide and FAQ, documentation revision `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` | The Pi’s external USB programming path targets the mainboard ESP32. The ESP-PROG jumper permits entry to programming mode on reset. MOS also has an SD-based updater with a different execution path. In this case the USB connection failed during store cleanup. [Firmware guide](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Updating-Firmware.md) · [Agon FAQ](https://agonplatform.github.io/agon-docs/FAQ/) |
| Espressif esptool v4 documentation for classic ESP32 | The ROM boot announcement is evidence of traffic from ESP32 to Pi. The Pi then sends a SYNC command (opcode `0x08`) and expects a valid reply. Espressif identifies the host-to-chip TX path as a diagnostic lead for this signature. A host trace can show attempted transmissions and received bytes. Pin-level delivery and the electrical cause remain unknown. [Troubleshooting](https://docs.espressif.com/projects/esptool/en/release-v4/esp32/troubleshooting.html) · [Serial protocol](https://docs.espressif.com/projects/esptool/en/release-v4/esp32/advanced-topics/serial-protocol.html) |
| Commissioned esptool 4.12 and Extender caller | In `ESPLoader._connect_attempt`, esptool examines ROM boot text, tries SYNC up to five times per connection attempt, and can replace the last protocol error with a general download-mode diagnostic. The parent sees a nonzero programmer subprocess exit. The original log and the point of failure inside the child carry more information than that exit code. [Shared programmer](../../scripts/olimex_flash.py) · [VDPlet caller](../../../../agon-vdplet/docs/tasks/VDPL-057/restore_olimex.py) |

A future [mainboard text snapshot](BENCH-017.md) could preserve what MOS displayed before the programmer reset. Label it with its capture time. Once the ESP32 enters its ROM downloader, VDPlet cannot serve a live snapshot. Diagnose SYNC from the original programmer session independently of screen observation.

## Research plan

- BENCH-023-001 [ ] Compare the failing VDPL-057 programmer log with the first-attempt OLX-06 and Nurples sync failures, successful FLY-07 sessions, and a failure after successful sync. Record the last positive observation, connection parameters, reset history where available, and earliest flash operation for each. Count esptool’s internal SYNC attempts separately from an operator retry.
- BENCH-023-002 [ ] Trace the exception from esptool through the shared programmer, the job-specific store adapter, and the parent supervisor. Compare catching the error narrowly around connection establishment with classifying an already-finished child from its log. Determine which observations a small stable receipt can carry across both callers. Account for a changed esptool message, a truncated log, and an interrupted child.
- BENCH-023-003 [ ] Propose the operator-visible outcome and evidence fields. Include the tool version, phase, ROM download-mode evidence, last acknowledged protocol operation, whether flash access started, and worker exit/join. Define when the runner can affirm zero flash operations and when it must report an unknown outcome. Preserve the raw exception. Evaluate the cost of capturing bounded boot/SYNC trace data in the original programmer session so evidence survives the next intermittent failure.
- BENCH-023-004 [ ] Specify offline replay cases for a successful connection, this exact signature, no boot bytes, wrong boot mode, serial-open failure, and a fault after a write began. Require that only the matching case receives the specific sync diagnosis, all failed cases retain their failure status, and ambiguous cases retain uncertainty about flash. Detection must require no second serial open, reset, retry or hardware write.
- BENCH-023-005 [ ] Return the recommended detection point, example operator report, coverage limits and any remaining unanswered question to Smith. If saved logs cannot distinguish causes, describe one separately selectable measurement and the evidence it could add. A retry policy or a claim of defective wiring needs its own evidence.

## Ten upstream VDP flash trials

Use the official [Bistromathics v2.16.0 release](https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0). This was the latest release when checked on 2026-11-20. The tag resolves to `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. The published `firmware.bin` is 1,077,840 bytes with SHA-256 `b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f`. The published `partitions.bin` matches the commissioned stock table byte for byte. The published application padded with `0xff` to the commissioned `0x116000` write extent has SHA-256 `86e4e8d383e16cac7ada4e3b451c6a09a5b39c54ffc78cfba0e7780e683410ec`. Use the [current production companion](../../production/companions/olimex-mainboard-vdplet-v0.1.3-alpha.yaml) for the production restore and live table comparison. Both artifacts and programmer interpreters passed offline verification.

The Pi uses the commissioned [Olimex procedure](../operations/olimex-bench/README.md) and shared mainboard programmer for the ten trials. Write only mainboard app0 at `0x10000`. Keep the board, USB port, cable, programmer environment, automatic reset, and baud settings fixed. The standard ROM handshake runs at 115,200 baud. The stub handles flash at 460,800 baud. Start from checked-in production app0. After each completed attempt, establish the ordinary boot boundary before the next one. Record which firmware was running at entry. Production is the initial state and Bistromathics is the expected state after its first successful write.

One trial is one invocation of the programmer against the published application, including one normal connection attempt with esptool’s internal SYNC exchanges. Give each invocation a new numbered evidence directory. A connection, programming or readback error counts as that trial’s failure. A success requires the full write and independent matching readback. Record the subsequent boot and MOS result separately so a boot failure cannot be mistaken for a failed serial transfer. Preserve the failing phase, original output, timestamps and joined process receipt for every attempt. Return to a verified starting state before continuing after a failure. If entry state or a potentially partial write cannot be reconciled, stop and preserve custody. Count only programmer invocations that actually started. Restore production in a separately recorded phase outside the ten trials and verify MOS and normal check-in.

- BENCH-023-006 [x] Verify the release tag, asset identity, stock table match, current production restore pins and commissioned operator readiness. Local inputs and the accepted reservation receipt are retained under `agents/bench-023/BENCH-023-2026-11-20T18-16-32Z/`.

- BENCH-023-007 [x] Bind the app0 starting state. Smith directed an immediate transfer and the scheduler opened Extender’s slot following VDPlet’s joined handoff. Trial 1 confirmed the retained app1 selector. The established MOS OTA route then returned to production app0. Trial 2 confirmed the app0 selector before writing. The test store was left alone.

- BENCH-023-008 [x] Run ten numbered attempts and report successes and failures out of ten, with the first fault stage for each failed attempt and the separate boot/CLI outcomes. Results below.

- BENCH-023-009 [x] Verify the production restore, working MOS and stopped worker group. The scheduler accepted the normal check-in.

### Observed results, 2026-11-20

| Trial | Starting selection | Result |
| --- | --- | --- |
| 1 | Retained VDPL-057 candidate in app1 | ROM SYNC, RAM stub, stock table and selector reads succeeded. The app0-only programmer refused the selector before writing. Counted as a failed flash. |
| 2 | Production app0 after MOS OTA | Full app0 write and 1,138,688-byte readback matched Bistromathics. MOS responded. |
| 3 | Bistromathics app0 | ESP32 announced ROM download mode. The standard programmer received no valid SYNC reply at 115,200 baud. Worker exited before flash access. Paired restart and MOS check completed before trial 4. |
| 4–10 | Bistromathics app0 | All seven full writes and independent readbacks matched. MOS responded after each. |

**8 succeeded and 2 failed out of 10.** On the nine attempts from app0, eight succeeded and one failed at ROM SYNC. The SYNC failure occurred using the standard programmer while stock firmware had been running. It therefore occurs outside the VDPL-057 store cleanup sequence. The record does not establish why SYNC was lost.

An initial host adapter error occurred before opening the programmer and is archived as `setup-fault-01`. The first app0 preparation phase stopped before OTA because the job packet used an obsolete SD listener pin. The corrected phase closed the existing listener session and used the previously staged production image. Neither preparation phase was a flash trial.

The bench returned to VDPlet v0.1.3-alpha production app0 with the exact `0x116000` write extent independently verified. The handback proved working MOS, idle transfers, closed serial ports and joined workers. Local evidence follows the run-directory convention above. See `trial-results.json`, the numbered `programmer.log` files, `verified-handback.json` and `checkin-delivery.json`.

## Traced ROM-only test

On 2026-11-20 Smith asked Extender to take the bench after Wolf3dOrig checks in
and capture a failed SYNC with esptool tracing enabled. Use the same mainboard
USB bridge, classic ESP32 target, automatic reset and 115,200-baud ROM entry as
the ordinary programmer. On successful SYNC, read the MAC from the ROM's
register interface and close the programmer. End the series at the first
failed connection or after ten successful sessions. Between sessions use
the ordinary restart to start the next session from normal operation. No
stub upload, flash access or firmware change is in scope.

Capture esptool's native trace and the serial reads at the host, including the
boot bytes esptool reads before the first packet. Record bytes accepted by the
serial driver and the sequence of reads and input flushes. Host evidence can
show transmission requests and replies but cannot establish delivery to the
ESP32 pin. After the series, verify a working MOS prompt and idle bench before
check-in. Keep all attempts and the final joined receipts.

- BENCH-023-010 [x] Capture the traced ROM sessions. Session 2 reproduced the failure. Both traces and the raw host serial events are retained.

- BENCH-023-011 [x] Verify normal MOS startup and bench handback. Joined worker, idle transfer and free serial port checks passed.

### ROM trace results, 2026-11-20

In both sessions the Pi received the same 129-byte ESP32 ROM banner before
sending SYNC. It included `rst:0x1 (POWERON_RESET)`, `boot:0x0 (DOWNLOAD_BOOT(UART0/UART1/SDIO_FEI_FEO_V2))`
and `waiting for download`.

| Session | Observed exchanges |
| --- | --- |
| 1 | SYNC 1 received zero bytes in 100 ms. SYNC 2 received the first reply byte after about 7 ms, followed by the valid SYNC replies. The ROM MAC matched. |
| 2 | The serial driver accepted each of five identical 46-byte SYNC frames. Each read returned zero bytes after about 100 ms. Esptool then reported download mode detected with no SYNC reply and exited 1. |

The failed session establishes silence in the host's five receive windows.
The trace records input flushes before each SYNC. It cannot establish what
reached the ESP32 pin or what the host might have discarded between windows.
The failure reproduced with production VDPlet at entry and a ROM-only probe.
The mainboard restarted normally after the probe and MOS handback passed.

Evidence is under `agents/bench-023/BENCH-023-2026-11-20T18-38-54Z/`. In
`rom-02/`, `esptool-trace.log` records protocol decisions and
`serial-events.json` holds the raw boot bytes and timed reads and writes.
The matching files under `rom-01/` show a recovered SYNC timeout.
The parent receipts and `handback/handback.json` cover the return to MOS.

## Repeat the ten-flash suite after removing the probes

Smith removed the sniffer leads from the boards and unplugged both the
sniffer and the ESP8266 module from the Pi5. Smith then powered the bench
back up and confirmed that remote input and MOS `DIR` worked. Repeat the
same Bistromathics app0 writes with the original USB cables, programmer,
baud and full-extent verification. Treat the wiring removal, USB peripheral
removal and power cycle as one change to the test conditions.

- BENCH-023-012 [ ] Run up to ten numbered attempts. Stop on the first error, alert Smith immediately with **Agent has a question**, and leave the bench in the resulting state. If the series succeeds, restore and verify production app0, verify MOS and idle services, and check in. A cable swap is a separate test.
