# UART pathway benchmark — use and evidence

The Author authorized implementation and SD deployment on 2026-09-10.
This is an exploratory diagnostic, not a qualified performance baseline.
The [plan](paired-benchmark-plan.md) defines the measurements and their limits.
Both installed firmware images remain unchanged.

## Completed full-suite baseline

The Author's returned r03 hardware run completes all 48 rows. The CSV passes
status, mode, pixel, clock arithmetic and final Legacy-return validation.
The [measured comparison](hardware-baseline.md) retains the original data,
hashes and per-case ranges. Direct ExCom output takes 2.61–4.52× the Legacy
send-time medians. Ordinary wait expirations remain visible: 24 ExCom setup
queries and 18 completion queries, none in Legacy.

The authorized `trace count points` [UART/CTS capture](uart-cts-capture.md)
now passes waveform checks. Its [findings](uart-cts-findings.md) show 3.407
of 4.456 payload-wire seconds idle while P4 withholds permission. The returned
one-row CSV agrees within clock resolution and confirms Legacy return. W6
measurement is complete and accepted. The [browser-disconnected control](browser-disconnected-control.md)
is now authorized as W7. No screenshot or repeat is needed to validate this run.

## r03 measurement deadline and prior diagnosis

The [physical pixel diagnostic](evidence/pixel-probe-hardware/00000002.CSV)
answered the first ExCom pixel query within clock resolution. After screen
setup and the banner, MOS's first wait expired at 30 ticks (about 250 ms),
and the correct black-pixel reply arrived at 66 ticks (about 550 ms).
Legacy recovery succeeded. The reply was late, not absent in this window.
The delay's contribution from parsing, drawing and presentation contention
has not been isolated.

`uart-path-benchmark-r03-b2026-09-10-18-21-38Z` resumes the full 48-row
comparison. On both routes it observes a single reply for up to 600 clock
ticks (nominally five seconds), retaining the first stock wait status.
It checks the bound between stock API calls; a call may finish after the
bound, but such a response fails the row. A maximum of 24 calls supplies a
CPU-loop backstop if the clock stops. No request is retransmitted. Probe mode
retains its previous first-timeout-fails behavior.

Each measured row now includes `setup_first_status`, `setup_reply_ticks`,
`first_reply_status` and `reply_wait_ticks`. A complete measurement can have
first status 15 and final status 0: this means a delayed response was measured,
not that the ordinary MOS timeout contract passed. The analyzer reports those
misses explicitly and rejects replies beyond the measurement bound. Actual
waiting remains in the timing; no delay is subtracted or replaced by a fixed
sleep. Neither firmware image changes.

The filesystem test has passed on the physical Agon. Its hardware evidence and
finished, unsubmitted report are in [REMED-003](../REMED-003.md). The new startup
runs the benchmark directly after ordinary setup, without repeating FSCHECK.

## Previous short diagnostic

The first hardware suite stopped before its first ExCom measurement. All eight
Legacy rows were saved, followed by status 15 (reply timeout), and Legacy
recovery succeeded. The [original CSV](evidence/first-hardware-attempt/00000001.CSV)
is preserved. This is an incomplete comparison, not an ExCom speed result.

The diagnostic application was `uart-path-benchmark-r02-b2026-09-10-18-10-09Z`.
Its startup ran the independent filesystem probe first, then
`RUN . probe`. Insert the card, connect one browser video client and reset
Agon once. Leave keys released until the final diagnostic result and Legacy
prompt, then return the SD. No capture script or firmware flash is required.
If the filesystem check fails, autoexec stops there and its saved result
should be returned before trying the pixel diagnostic manually.

The diagnostic checks mode information, an initial pixel, a cleared black
pixel and a plotted white pixel on each endpoint. It records the exact phase,
send status, first reply-wait status, raw clock intervals and observed values.
On timeout it watches the same outstanding reply for up to nine additional
stock API waits, without retransmission or clearing its flag. A late reply
still fails the original deadline. The record distinguishes late arrival from
no observed arrival within that bounded window; it does not declare a reply
permanently absent. MOS implements this API's nominal one-second wait using
a CPU loop, so the measured intervals, not the nominal description, govern
interpretation. No throughput workload is run in probe mode.

The CSV contains `# query;...` records and zero benchmark rows. The full-suite
analyzer deliberately rejects it as performance evidence. Normal, withheld
and 1.5-second-delayed native replies were checked in isolated emulator
profiles; the late case retains timeout status while recording its eventual
reply. The exact combined filesystem/probe startup also passes in raw-image
emulation. The physical result above establishes a late post-clear reply.

## Full suite instructions

1. Insert the prepared SD. Keep Agon and P4 powered, the existing ribbons
   seated, and one browser video client connected and visible.
2. Press and release Agon's reset. Autoexec runs boot smoke, selects the
   Extender keyboard, prepares mode 0 on both displays and runs `UPBENCH.BIN`.
3. Leave keys released. The displays switch between Legacy and ExCom; a row
   indicator and eight points are normal. CLI rows take noticeably longer.
   Allow several minutes for all 48 rows; this is not a fixed capture timer.
4. Wait for `UART benchmark PASS: 48 rows saved` and the Legacy prompt.
   The filename appears below the result. Return the SD to the PC for
   collection and comparison. A failure or missing final record is not a pass.

No Pi script or sniffer is needed for this first baseline. The application
does not overwrite existing result files. Each invocation chooses the next
unused `/extender/uartbench/results/nnnnnnnn.CSV`.

For a manual rerun, both displays must still be in mode 0. From the current
prepared prompt:

```text
LOAD /extender/uartbench/UPBENCH.BIN
RUN
```

The optional `RUN . trace count points` runs one ExCom row with boundary
queries. Select a capture after inspecting the complete suite; the first
deployment does not arm or require an analyzer.

## Separate filesystem reproducer

The card also contains [REMED-003's test](../REMED-003.md). After the benchmark
returns to the Legacy prompt, run:

```text
LOAD /extender/fscheck/FSCHECK.BIN
RUN
```

Expect `create_existing=8`, `sync_open_written=0`, and `Filesystem probe PASS`.
The test saves `/extender/fscheck/Rnnnnn/RESULT.TXT`. Return that file with the
benchmark CSV. Its hardware result is needed before finalizing the emulator
bug report. It does not change the selected keyboard or display route.

## Host build and collection

Use the project `.venv`. `scripts/build.py --output <new-local-bundle>` builds
with the approved AgonDev toolchain and records source/compiler hashes plus
the existing firmware requirements. Generated binaries, maps and profiles
stay ignored; version identity and sources are tracked here.

The first exploratory SD deployment uses
`uart-path-benchmark-r01-b2026-09-10-17-45-53Z` and the separate
`fatfs-file-probe-r01-b2026-09-10-17-44-59Z`. Full-suite and selected-case
emulator reviews passed. All 24 full-suite ExCom payloads matched exactly;
the reviews preserved a deliberately pre-existing results file and returned
to Legacy. These observations do not establish hardware timing or P4 speed.

`scripts/deploy.py --bundle <bundle> --mount <exact-FAT-mount> --backup
<new-local-backup>` installs only the application, manifest and autoexec,
preserving existing results. It refuses an unmounted or non-FAT target and
backs up each replaced file before committing startup last. Local deployment
records retain the actual mount and backup paths.
Optional `--fs-bundle <filesystem-probe-bundle>` adds the independent
filesystem reproducer. `--fs-first` additionally composes startup to run it
before keyboard selection and the UART application. That exact composed
autoexec and its hash are retained in the deployment receipt; the original
build bundle stays immutable. Build with `--probe` to select the short
diagnostic instead of the full suite. The review preparer accepts
`--fs-bundle` to exercise the same combined startup in a raw FAT image.

After copying the hardware CSV into a run record, use:

```text
.venv/bin/python -B docs/tasks/AUDIT-005/scripts/analyze.py <saved-CSV>
```

The analyzer rejects incomplete matrices, unsuccessful replies, wrong pixels,
duplicate rows and inconsistent timestamps. It reports median/range raw clock
units and route ratios. Timings from a native-VDP emulator do not establish P4
performance or the cause of the reported game lag.

## Emulator-specific discovery

The original directory-backed review exposed Fab create-new/sync defects,
now owned by REMED-003. `prepare_review.py` instead creates a disposable FAT16
image and uses the existing raw-SD backend, so MOS executes its real filesystem
code. No storage call is stubbed to force success. The peer grammar admits RTC
queries for FatFS timestamps outside the timed windows. It uses native stock
VDP plus the maintained console-control helper as the UART1 substitute; it is
not an ESP-IDF, electrical flow-control or browser performance model.

The initial 240-second review limit expired after 47 valid rows; the complete
review now allows 600 seconds rather than truncating the CLI workload. This
host deadline is not an imposed delay or a hardware benchmark result.
