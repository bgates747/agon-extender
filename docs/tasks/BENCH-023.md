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

## Programmer history and earlier reproduction

- On August 31 the early Extender bench used direct USB esptool to flash a
  rebuilt Bistromathics image, including the bootloader, partition table and
  OTA data. The retained result records verified segments and a hard reset.
  [August record](PORT-008/emos-hardware-diagnostic/README.md)
- On October 12 the same ESP32-PICO-D4 passed an app0-only write and verify
  using esptool 5.1.0 at a requested 460,800 baud. The helper used automatic
  reset for identification, reopened with no reset for the write and verify,
  and hard-reset after verification. The helper and logs are retained under
  `agents/bench010/stock-vdp-r01/`.
- On November 16 the first standardized runner used esptool 4.12 in separate
  CLI processes. Its cold rehearsal failed on the write process's reopen,
  after the table and selector reads. Commit `7b2e9836` consolidated those
  operations into one esptool 4.12 session. The later paired restart change
  applies after verification. No initial selection record compares 4.12
  against the earlier successful 5.1 control.
  [Cold rehearsal record](BENCH-019/REHEARSAL-R02-RESULT.md)
- On November 19 the VDPL-057 rerun first stopped at ROM SYNC. A later
  recovery connected, switched to 460,800, read the table and selector, and
  then got a short 3,949-byte frame while reading app0. Extender's matched
  read with 115,200 throughout matched the full 1,164,592-byte app0 capture,
  table and selector. The next restoration attempt on November 20 stayed
  at 115,200 and failed before the stub at initial ROM SYNC. See the retained
  `agents/vdpl057-programmer-diagnostic/evidence-115200/` and the VDPL-057
  recovery receipts.

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

- BENCH-023-012 [x] Run up to ten numbered attempts and stop on the first error. Four passed. Trial 5 announced download mode and stopped at ROM SYNC before any flash access. The worker joined and Extender retained custody. The desktop question request was accepted, and Smith reported that it disappeared while he was away. Local evidence is under `agents/bench-023/BENCH-023-2026-11-20T19-51-41Z/`.

## Repeat with the P4 and mainboard USB cables exchanged

Smith swapped the USB cables between the two boards and directed the same
ten-flash test, stopping and alerting at the first failure. The host saw the
two existing devices trade Pi5 USB paths. Use a job-local identity record for
the swapped mainboard USB path, with the same device identity, firmware
image, programmer, baud and verification. The starting app0 is Bistromathics
from the previous series, verified in its trial 4, followed by a pre-flash
stop in trial 5. Preserve that failure and reconcile its pending inventory
entry before the first new attempt. The swap changes both the cable and Pi5
USB path assigned to each device. The test therefore cannot isolate a cable
from its host port.

- BENCH-023-013 [x] Run up to ten numbered attempts with swapped USB connections. Five passed. Trial 6 reproduced the same 115,200-baud ROM SYNC failure before any flash access. The worker joined, the desktop question was accepted, and Extender held the resulting bench state. Evidence is under `agents/bench-023/BENCH-023-2026-11-20T20-13-45Z/`.

## Compare esptool 5.1.0 and 4.12.0 at ROM SYNC

On November 20 Smith requested a ROM-only comparison at 115,200 baud with
the swapped USB wiring left in place. Return the bench from the prior
programmer stop using the normal paired restart. Use the same mainboard
endpoint, fixed ROM baud, automatic reset, single connection attempt and
both native and host serial traces. Start with 5.1.0, then alternate with
4.12.0 for up to ten sessions total. Keep esptool's built-in SYNC exchanges
inside each connection attempt. After successful SYNC, read the ESP32 MAC
without uploading a stub or accessing flash. Restart normally after a
successful session to set up the next one. Stop at the first failed session
and send **Agent has a question**. Keep that state intact for Smith. Compare
the two installed tool environments and report any unequal coverage if the
first failure truncates the series.

- BENCH-023-014 [x] Run the ROM-only comparison and record the first failed session or all ten passes. Session 4 failed at SYNC. The worker joined and the desktop question request was accepted. Extender retained custody and stopped with the board in the post-failure state.

### Version comparison results, 2026-11-20

| Session | esptool | Result | ROM SYNC exchange that received a reply |
| --- | --- | --- | --- |
| 1 | 5.1.0 | ROM MAC matched | 2 of 2 sent |
| 2 | 4.12.0 | ROM MAC matched | 4 of 4 sent |
| 3 | 5.1.0 | ROM MAC matched | 2 of 2 sent |
| 4 | 4.12.0 | ROM SYNC failed | None of 5 sent |

All four sessions began with the same 129-byte download-mode banner. In
session 4, the host driver accepted each of the five 46-byte SYNC frames and
the Pi received zero bytes in the five receive windows. Both 5.1.0 sessions
also received zero bytes on their first SYNC exchange. Two sessions per
version establish a reproduction under 4.12.0 with the existing wiring.
The sample is too small to establish that switching to 5.1.0 fixes the
intermittent failure. Both environments used pySerial 3.5.

Evidence is under `agents/bench-023/BENCH-023-2026-11-20T20-47-29Z/`.
`series.json` gives the joined session outcomes. Each `rom-NN/` holds the
native trace and timed serial events. The series uploaded no stub and
reached no flash operation. The stop leaves post-failure MOS unverified.

## Repeat the Bistromathics flash series with esptool 5.1.0

On November 20 Smith requested up to ten app0 writes using esptool 5.1.0.
Retain the swapped USB wiring and the published Bistromathics image. Keep
the standard single programmer session, 115,200-baud automatic-reset ROM
entry, 460,800-baud stub transfer, app0 and table checks, full write extent
and independent readback. The job-local adapter calls the 5.1.0 API at those
boundaries. Reconcile the previous joined pre-flash stop and start from
normal operation with the already verified Bistromathics app0.

- BENCH-023-015 [x] Run until the first failure or ten attempts. Trials 1 and 2 verified the full Bistromathics write extent and returned to MOS. In trial 3, esptool 5.1.0 detected ESP32 download mode but received no valid SYNC reply. The worker joined before any flash access. The [Oryx spoken alert](../../../agon-dev-env/codex/urgent-alerts.md) playback command completed. Extender retained the bench in the post-failure state. Local evidence is under `agents/bench-023/BENCH-023-2026-11-20T21-10-28Z/`.

The 5.1.0 result reproduces the same first connection failure seen on
4.12.0. The earlier two successful 5.1.0 ROM-only sessions were insufficient
to establish that the newer tool fixed the problem. The version change
alone leaves the intermittent SYNC failure unresolved.

## Repeat with PlatformIO's bundled esptool

Smith requested up to ten Bistromathics app0 writes using the uploader
bundled with the upstream PlatformIO environment. The Pi uses the installed
`tool-esptoolpy` package 1.40501.0, esptool 4.5.1, from Espressif32 platform
6.6.0. The test retains the swapped USB wiring, exact Bistromathics image,
app0 extent, one programmer session, 115,200-baud ROM entry and 460,800-baud
stub transfer. Keeping both rates fixed isolates the uploader package from
the upstream project's separate 600,000-baud upload setting. The job uses
the bundled API to write only app0 and independently read it back.

- BENCH-023-016 [x] Run until the first failure or ten attempts. Stopped during trial 4 when the host runner ended without a terminal receipt. The [Oryx spoken alert](../../../agon-dev-env/codex/urgent-alerts.md) playback command completed. Trials 5–10 and production restoration were not run. Extender retained the bench with the verified Bistromathics app0. Local evidence is under `agents/bench-023/BENCH-023-2026-11-20T21-34-09Z/`.

| Trials | Mainboard outcome | Runner outcome |
| --- | --- | --- |
| 1–3 | Bistromathics app0 write, matching full readback and responsive MOS | Each exited 0 with a joined-worker receipt |
| 4 | Bistromathics app0 write, matching full readback and responsive MOS | Outer shell exited 143. The worker's final wait receipt is missing. |
| 5–10 | Pending at the initial stop | See the continuation below |

All four saved 1,138,688-byte readbacks independently hash to
`86e4e8d383e16cac7ada4e3b451c6a09a5b39c54ffc78cfba0e7780e683410ec`.
Trial 4's programmer log reached `Hash of data verified` and its
`independent-verification.json` records `boot_cli_ready: true`. The ROM
handshake succeeded on all four attempts. The runner interruption stopped the
initial invocation after four trials. The continuation below records the
remaining six.

## Diagnose the host interruption and continue trials 5–10

Smith authorized fixing the launcher and completing only the six remaining
PlatformIO attempts. Use the same bundled esptool 4.5.1, firmware bytes,
app0 extent, reset sequence, baud rates and wiring. On the first failure,
retain custody and the bench state and send the Oryx spoken alert. If the
six trials pass, restore production app0, verify handback and check in.

- BENCH-023-017 [x] Identify the interruption from the original Codex command record and Pi receipts. Codex recorded outer shell exit 143 at 16:38:42 EST during trial 4, consistent with SIGTERM. The worker survived until at least 16:39:06 EST, when it verified the write and MOS and committed the inventory. The supervisor did not leave a final wait receipt. Context compaction was in progress, but the record does not identify who sent the signal. Trial 4 counts as a verified hardware result with an interrupted host execution record.

- BENCH-023-018 [x] Run the same bounded phase supervisor under a transient Pi user service outside the tool session. Host-only preflight reconciled trial 4's saved readback, MOS and inventory. A simulated trial 6 failure stopped the launcher, invoked the mocked alert exactly once and dispatched no later phase. In the live run the service retained its terminal status, completion log and accepted owner-chat wake-up. The original trial records were preserved.

- BENCH-023-019 [x] Trials 5–10 all passed on the original packet and phase workers. Each matched the full 1,138,688-byte app0 readback, returned to a working MOS prompt and left a successful, joined-worker receipt. The service logged no failure and did not invoke the Oryx alert. The production VDPlet v0.1.3-alpha app0 restore passed its full extent readback. Handback verified Legacy CLI, listener offline, transfers idle and serial handles free. The scheduler accepted check-in and the FIFO became empty.

The combined series is **10 verified app0 writes and zero ROM SYNC failures**
using PlatformIO's bundled esptool 4.5.1 at 115,200-baud ROM entry and
460,800-baud stub transfer. Nine attempts have normal trial-exit receipts.
Trial 4 has an independently verified write, MOS and inventory, with the
interrupted launcher receipt preserved. Ten attempts bound this observation.
The intermittent failure's underlying cause remains unresolved.

The PlatformIO evidence directory retains `original-shell-terminal.json`,
`resume-files.sha256`, `resume-launcher-offline/`, `resume-supervisor.log`
and its terminal and wake-up receipts, the individual phases, and
`checkin-delivery.json`.

## Verify one continuous ten-flash run under the Pi service

Smith requested one fresh series of ten attempts from the checked-in
production baseline. Use the same Bistromathics v2.16.0 app0 extent, PlatformIO
esptool 4.5.1, 115,200-baud ROM entry, 460,800-baud stub transfer, and swapped
USB wiring. Keep the first-failure stop and Oryx spoken alert. On ten passes,
verify the production app0 restore and handback, then check in.

- BENCH-023-020 [x] The single Pi service passed trials 1 and 2 with full 1,138,688-byte app0 readbacks, working MOS prompts and joined exit-zero workers. Trial 3 failed at 115,200-baud ROM SYNC. esptool 4.5.1 detected download mode and received no valid SYNC reply. The failed attempt reached neither the stub nor any flash access. Its worker joined with exit 1. Trials 4–10 and the production restore were not started. Extender retains the reservation. The last verified app0 is Bistromathics from trial 2. MOS after the failure is unverified.

The Pi service recorded exit 1 and woke the idle owner chat. The Oryx spoken
alert playback command completed. The launcher's failure text classifier could
not find `rg` on the service `PATH`, so the alert used its generic trial 3
failure wording. The escalation and first-failure stop both ran. This was a
reproduction of the earlier ROM SYNC symptom with the bundled uploader, at a
different point from the earlier host launcher interruption.

Evidence is under `agents/bench-023/BENCH-023-2026-11-20T22-12-08Z/`, including
the service log and terminal and wake-up receipts, `oryx-alert.log`, the two
passing readbacks and `trial-03/programmer.log` and `child-terminal.json`.

- BENCH-023-021 [x] Fix the alert text classifier in `run-series-r02.sh` in the evidence directory above. Use `/usr/bin/grep -Fq` on a readable programmer log and retain the generic alert when the log is unavailable. Preserve the original launcher and input pins. An offline Pi user service with no `rg` on its `PATH` tested both the saved ROM SYNC failure and a missing log. Each case stopped at the simulated third trial, exited 1 and issued exactly one mock alert with the expected wording. The receipt is `alert-classifier-offline-r02.json`.

## Repeat the batch with standalone esptool 5.1.0

Smith requested up to ten new Bistromathics app0 attempts with standalone
esptool 5.1.0. Use the exact prior 5.1.0 uploader from the Pi's Python
environment, the same USB wiring and firmware bytes, the 115,200-baud ROM
handshake and 460,800-baud stub transfer. Under the retained slot, reconcile
the last joined failure before flash access and use the ordinary paired
restart to recover MOS with the verified Bistromathics app0 still installed.

- BENCH-023-022 [ ] Run one Pi service with the tested Oryx alert classifier. Stop at the first failure and wake the owning chat. After ten passes, restore and verify production app0, verify handback and check in. Record the entry, trial results and resulting bench state. Evidence is under `agents/bench-023/BENCH-023-2026-11-20T22-29-21Z/`.
