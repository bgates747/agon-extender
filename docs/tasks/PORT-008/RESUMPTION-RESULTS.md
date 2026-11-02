# Parallel resumption results

## Executive summary

The bounded format4 comparison is complete on the current indexed-display,
dual-USB composition. All 48 selected records have exact 8 KiB buffer proof;
five capture-absence controls complete without panic or test flags. The Pi
restores the complete incoming P4 flash and EMOS ROM byte for byte and verifies
normal startup, both used mode0 settings and actual CLI handback.

Parallel sender wire drain improves from UART's 36.97 ms to 18.21 ms at exactly
4,096 wire bytes. One additional byte exposes a remaining delay: 65.19 ms versus
UART's 36.92 ms. This is not general parallel-pipe acceptance. Warm-reset input
readmission and the remaining control/scheduling departures are still open;
production selection is unchanged. Stop before another architectural cut.

The [portable evidence](RESUMPTION-EVIDENCE.json) retains all selected CSV rows,
actual decoded buffer bytes, source/capture hashes, build identities, controls,
reset outcomes and restoration proof. Original incomplete acquisitions remain
retained; this is not a clean first-acquisition capture-suite pass.

## Composed inputs and artifacts

| Component | Exact input/build | Result |
|---|---|---|
| P4 source | `03e428f3bb87951bd4f296ccb36ef677ef1db617`, based on installed R25 source `9c393360f8db0583e56f62c3266a6dad0090dda8` | Clean; only build wrapper changes in firmware source inventory |
| P4 image | `port-008-stream-r17-b2026-11-02-01-06-24Z` | 1,828,032 bytes; SHA256 `4e2e5348cc798336d94fa1655b32de61b52a0ce55a86dc3024e01eed49f5a1aa` |
| EMOS source / builder | `0db7276f2a61031fce9b4bc9705b41e48ce0df47` / `49dc33fee817cb184572351ee71dae7da9a139c4` | Clean canonical source and existing AgonDev builder |
| EMOS image | `agon-emos-v0.1.27-b2026-11-02-01-06-34Z` | 128,871 bytes; 2,201 free of 131,072; raw SHA256 `2f508d8e34b23ab09f7bc207cfbab6eca6ba0072f0a4ace2cff274c5e5482de3` |
| Padded EMOS ROM | Same build, erased padding | SHA256 `0a42af05e77ab335009f76e6e797a6279c9395c6323fae398dd6742f100acbf7` |
| Timing appliance | `port-008-stream-timing-r01-b2026-11-02-01-09-43Z` | 13,386 bytes; SHA256 `b71f5ee5e7bf0de372cabc8fc7e63bc9f0f0e8b17be7befbbb4d834192745c40` |

The P4 image keeps the exact installed display sources/configuration, board,
compiler, cache component, USB options, reset-endpoint hash and dependency lock.
Only unrelated graphics timing is omitted and the native format4 transport is
selected. Partition-table bytes are identical. SDK configuration differs only
in absolute generated partition-file paths. Validation covers 44 selected
sources and 1,856 compile actions. This does not repair R25's known wide-mode
deadline failure; the comparison is limited to mode0.

EMOS's `exext-controller-timing.mk` composes the existing native/timing owner
with factored, unchanged controller selection/identity checks. Its reduced
controller gateway is the existing development operations4–7, not acceptance
of old on-card controller clients. No controller application belongs to this
transport workload. Both physical USB hosts remain selected in P4.

## Offline checks

1. Native P4 build selection: 19 root tests and 18 controlled-source tests pass,
   including dirty/wrong-owner/private-endpoint/wrong-identity refusals and
   preservation of display/controller sources in the composed profile.
2. Eight sanitizer-enabled host invocations pass: control, session, block
   control, ordinary stream, native paired coordinator, P4 coordinator,
   EMOS controller and EMOS ExExt stream. LeakSanitizer requires execution
   outside the ptrace sandbox; address/undefined-behavior checking remains on.
3. Exact newly linked EMOS instructions pass controller, UART observation,
   ordinary ExExt output and IRQ checks. The exact MOSlet/ROM ABI check passes
   empty drain, refusal, timer values and register/interrupt preservation.
4. Eight fixture evidence-interpretation checks pass. Full EMOS wrapper checks
   retain physical ROM bounds, UART divisor, ABI, keyboard/callback, ordinary
   console and RST10/RST18 dispatch guards. Full P4 graph validation passes.
5. AgonDev clang15 cannot lower SJLJ exception contexts. The appliance builder
   now explicitly disables exceptions; ordinary return-path cursor cleanup
   then compiles and links. The compiler failure remains retained as a bounded
   toolchain gotcha, not a firmware or bench failure.

## Physical transport comparison

The same frozen appliance executes all eight mode0 cases, one warm-up and five
measured samples per route/length. The Pi selects each route through EMOS,
confirms mode0, waits at least one second and issues an explicit RUN. Passive
P4 USB collection occurs during the workload; no HTTP polling occurs during
measurement. Buffer dumps and CSV retrieval occur outside the timed regions.
Each wire-byte count includes the 11-byte buffered-update command header.

Worst parallel sender wire-drain increase first; values are median elapsed
milliseconds, five measured rows per cell. Positive change means parallel takes
longer: `100 × (parallel / UART − 1)`.

| Wire bytes | UART wire drain (ms) | Parallel wire drain (ms) | Change |
|---:|---:|---:|---:|
| 4,097 | 36.9167 | 65.1944 | +76.6% |
| 256 | 2.3333 | 2.8472 | +22.0% |
| 8,192 | 82.0139 | 82.2361 | +0.3% |
| 4,096 | 36.9722 | 18.2083 | −50.8% |

The 8 KiB medians are effectively tied within observed variation. The parallel
4,097-byte wire-drain samples range from 20.8194 to 66.6806 ms, so the median
alone must not be treated as a fixed per-transfer penalty. Existing single
receive-buffer/consumer backpressure and partial-output/VBlank scheduling are
candidates for the boundary delay; this run does not isolate their contributions.
Do not declare either one the proven cause.

Ordered buffer-processing/reply latency has a different scope. Worst parallel
reply increase first, with the same baseline and percentage definition:

| Wire bytes | UART ordered reply (ms) | Parallel ordered reply (ms) | Change |
|---:|---:|---:|---:|
| 256 | 6.5417 | 16.6944 | +155.2% |
| 4,097 | 82.3750 | 83.4028 | +1.2% |
| 4,096 | 82.3472 | 83.3333 | +1.2% |
| 8,192 | 165.2778 | 149.9444 | −9.3% |

The portable record retains submission timing, ranges, raw timer counts,
equivalent cycles and local block completion. Its legacy `receipt_prt` column
means physical cleanup and reciprocal UART return for format4; no software
COMPLETE/ACK exchange remains. The last block's completion-minus-drain interval
does not measure all earlier handovers. The ordered seven-byte reply includes
reverse traffic and synchronous buffer processing; it does not fence all
rendering or scanout.

The eZ80 PRT1 uses the nominal 18.432 MHz clock divided by 256: 72,000 counts/s,
13.8889 µs resolution, with interrupts and their elapsed waiting included.
No independent oscillator calibration was performed. Zero read-overhead controls
are quantized observations, not proof of zero physical cost. PRT counts converted
to equivalent cycles are not counts of retired instructions. No file-transfer
speed, GPU completion, HDMI FPS or game-performance result follows. Comparing
these figures to October's different display/component composition would not
isolate the effect of CRC/COMPLETE removal.

## Acquisition and capture-absence controls

All eight original invocations complete six CSV rows with zero flags. Five
logical cases have incomplete USB byte dumps. Retain those captures and their
positive completion records; missing USB lines do not establish bad parallel
data. Five explicit, separately labeled repeats of already-completed cases
supply additional complete samples, while also retaining any short repeat dumps.

Across 13 captured acquisitions, all 78 CSV rows remain retained. Integrity-only
selection takes 43 original records and five repeat records, never selecting by
elapsed time. All 48 selected records match their actual decoded 8,192-byte
buffers: 393,216 verified bytes, 24 records and 196,608 bytes per route. Eight
warm-ups remain in evidence but are excluded from the 40 comparison rows. Each
selected source row/chunk, raw-log/CSV digest and decoded-byte digest is recorded.
Missing bytes are never padded or reconstructed from the expected pattern.

The isolated control source `909409506a357f482feea30e18c07cddad18f659`, based on
exact captured source `03e428f3`, removes only the buffered-command128 debug-body
implementation and consumes that opcode as a no-op. Renderer, transport, USB,
compiler, options and dependency lock remain unchanged. The debug literal is
absent in the actual control ELF/application and present in the captured build.
This deliberate debug-API deviation is not merged into product or production.
Control build `port-008-stream-r17-b2026-11-02-02-15-00Z` is 1,826,976 bytes,
SHA256 `4ea314bd679fa90f73d2eaf5542f35710cd0b6248ae1e8d59764221dfe6c0956`.

| Affected route | Wire bytes | Bounded control | Completed rows | Flags / panic / reboot |
|---|---:|---|---:|---|
| UART / ExCom | 4,096 | 60 seconds, positive CLI | 6 | 0 / absent / absent |
| Parallel / ExExt | 4,096 | 60 seconds, positive CLI | 6 | 0 / absent / absent |
| UART / ExCom | 4,097 | 60 seconds, positive CLI | 6 | 0 / absent / absent |
| Parallel / ExExt | 4,097 | 60 seconds, positive CLI | 6 | 0 / absent / absent |
| Parallel / ExExt | 8,192 | 60 seconds, positive CLI | 6 | 0 / absent / absent |

Each control uses the same frozen fixture, exact EMOS, mode0, setup/teardown,
pacing and ordered fences. Ordinary passive serial observation retains panic
output; all five controls yield positive completed CLI and saved CSVs. Their
546.430-second host job duration includes coordination/retrieval and is not
fixture runtime or a new automatic reset deadline. These bounded controls do
not prove capture caused missing logs and supply no missing byte or pixel proof.

Ten planned Agon-only capture-recovery resets yield nine verified admissions;
one fails input readmission. The standing P4-then-Agon recovery then proves
actual CLI, with unchanged test firmware and no automatic workload replay.
Warm-reset readiness is not qualified or fixed by this campaign.

## Installation, restoration and limits

Support files and exact rollback bytes are staged and read back under the
current SD layout. A preparation SAVE completes, but immediately injected
listener input fails handback; one Agon reset recovers. Explicit finite EXEC
batches now serialize SAVE and listener entry. Startup is never edited.
The matched installation observes the exact EMOS identity after FLASH, retains
full P4 flash and independently verifies both newly installed images before
RUN. Native P4 initialization releases its pads before Agon release; ordinary
UART/USB readiness follows the reciprocal EMOS boot fence. Correcting that
installer observation order does not require another flash or P4 reset.

After the captured study and five controls, the Pi restores the exact incoming
pair. Complete independent readbacks establish:

| Restored item | Exact result |
|---|---|
| P4 complete 16 MiB flash | Byte-for-byte incoming image; SHA256 `006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b` |
| P4 R25 application | `indexed-hdmi-r25-b2026-11-01-20-18-04Z`; SHA256 `eb1334276c0c6e5766f718b2aef7984c382931b2a6ae6cb39c0a7ea3332c0645` |
| EMOS complete 128 KiB ROM | `agon-emos-v0.1.27-b2026-10-26-01-06-54Z`; byte-for-byte incoming ROM, SHA256 `84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79` |
| Startup | Unchanged 108-byte load-only file; SHA256 `9e97ceae5489e1b6330c6a2f207d95c6566c60cac304d65e7aad54b610a5b423` |
| Foreground listener | Unchanged 22,968 bytes; SHA256 `04e7ef596a862b1a6b4f265b6c647e461ef0f65db4851873ac3dd31e4f03f10d` |
| Mainboard VDP | Never flashed in this tranche; F060 remains, no new independent full-flash readback claimed |
| Handback | Entry/exit mainboard mode0, P4 mode0/fault0, Legacy route; two actual CLI exchanges, neutral ready input and valid USB controller |

The original expanded application erase span is restored, including old slack
beyond the shorter R25 application; restoration is not merely an app-prefix
comparison. Text/visible/flashing cursor controls are sent to both used displays.
No optical confirmation is claimed. No runner, reader, reset hold or transfer
remains active. The restored R25 image retains its known wide-mode defect;
this transport study neither repairs nor expands its accepted scope.

Ignored `agents/parallel-resumption` retains exact images/ELFs, full restoration
readbacks, requests/manifests, source inventories, raw logs and all finite helper
journals. The portable tracked record preserves independent selected-data and
analysis reproduction without private host/device details. Neither evidence
location is a selected production installation or public application API.

The broader task stays open. The next control/scheduling cut requires discussion
under P08-D02; the boundary delay has not been attributed by this comparison.
Direct ExCom ↔ ExExt transitions, persistent UART shutdown, bulk reverse payload,
other video modes, games and final production qualification remain outside this
tranche. No new version, release tag or production promotion is requested.
