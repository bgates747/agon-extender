# S06-R01 — Copy-based partial-scroll remedy

Stock's existing copy/fill scroll algorithm substantially improves the direct
renderer: the short Nurples smoke returns to 60 updates/s, while scrolling with
32 software sprites rises from about 26 to 54–55 updates/s. All 13 bounded case
executions pass, including the previously failing no-PRT finalization control.
The heavy scroller still misses 60, and ordinary busy-game flicker/input acceptance
remains with the Author. This is a measured improvement, not production acceptance.
The executable work contract remains in [SCAN-001](../SCAN-001.md).

## Implementation and source boundary

Only `P4Rgb888Controller::rawCopyRow` and `VScroll` change in the firmware source
closure. Panel-backed RGB888 uses the existing two-callback `genericVScroll`;
owned storage retains pointer rotation. The row adapter uses `memcpy` for disjoint
row spans, with the physical row pointers supplying HDMI stride and centering.
The stock helper supplies direction-safe row order, sprite hiding and brush fill.

The helper is byte-identical to the selected stock vdp-gl version recorded in
S02 (SHA-256 `4b604853476b0663b6043d7c65f0e0e6d8953f1ba5df28ef81a977715bbca2ed`).
The frozen source closure differs from the failed direct build in exactly one
file: [the direct controller](../../../vdp/video/extender/display/p4_rgb888_controller.cpp).
The native backend, shared helper, scheduler, locks, panel publisher, DMA/cache
policy, input and EMOS are unchanged. This does not make single-buffer drawing
atomic with scanout or fix the stock oversized-movement limitation.

## Host validation and build

The expanded [RGB888 golden test](../../../tests/display/rgb888_renderer_test.cpp)
passes against the retained native rasterizer: partial/full-width up/down moves,
odd X edges, region-height moves, single-pixel-width/height regions, repeated
one-row clipped tile insertion, live software sprite restoration, physical panel
margins, both panel-front choices and single/double buffering. Existing colour,
paint, overlay and DMA-release swap tests also pass. The separate HDMI scheduling
test passes buffer publication, independent clock progression and shutdown.
These host checks are not hardware timing or flicker acceptance.

Registry r142 advances the experimental renderer to `rgb-001-r02`; the fixture
remains the already deployed `scan-scroll-suite-r02`. Registry-only validation
passes. Full version validation hits the pre-existing `light2-harness-r02`
`connectivity.yaml` integrity mismatch; that file matches its committed HEAD,
and no frozen wiring record is changed by this remedy.

Build selection is `panel-copy-normal`, with the same diagnostic normal-output,
P4-PC, HDMI and USB FS/LS configuration as the failing direct comparison.
Exact source snapshots, patch, build manifest, host logs and later installation
receipts live under the ignored `agents/scan001/s06/copy-remedy` evidence directory.
The original direct and ordinary native rollback images remain retained.

## Physical deployment boundary

The candidate is `rgb-001-r02-b2026-10-07-00-49-06Z`, factory SHA-256
`7203465ac7022065ac574514c2e0c4e65d9e0a083c98ee14b7352fc156360d11`.
All 19 artifact hashes and silicon 1.3 compatibility verify. The Author's new
instruction to try the remedy with the bench "all yours" delegates this bounded
deployment/testing to the agent. The agent flashed this candidate and independently
verified all four installed segments. The card stayed in Agon; the same short
cases/controls below ran with original startup/configurations preserved for
restoration. Hold the candidate for ordinary Nurples playtesting after restoration.
The previous baseline's missing hook-free/visibility/input observations remain
open. No S07 experiment, extended direct run, commit/push or promotion is implied.

## Physical results — bounded candidate trial

All 13 case executions complete: 1,560 recorded updates, zero recorded faults
or aborts, and matching retained trajectories. These are single short runs,
not a repeatability campaign. Mainboard/native/direct-r01 columns reuse the
immediately preceding retained comparison; only the copy candidate is newly run.

### Application rates, worst achieved candidate rate first

Nominal game/application updates per second, from the raw MOS clock. T01/T03/
T07/T08 include per-update completion queries; T09 is naturally pipelined.
These are not visible HDMI frame rates. Relative change = 100 × (copy/direct-r01 − 1).

| Case | Mainboard | Native P4 | Direct r01 | Copy r02 | Change vs direct r01 |
|---|---:|---:|---:|---:|---:|
| T07 scroll + tiles + 32 software sprites | 39.78 | 56.25 | 26.18 | 54.14 | +106.8% |
| T03 scroll + clipped tiles | 60.00 | 60.00 | 34.62 | 60.00 | +73.3% |
| T09 short repaired Nurples | 60.00 | 60.00 | 39.56 | 60.00 | +51.7% |
| T08 static field + 32 software sprites | 60.00 | 60.00 | 60.00 | 60.00 | +0.0% |
| T01 static/poll | 60.00 | 60.00 | 60.00 | 60.00 | +0.0% |

### Budget and completion costs

One frame budget is nominal 16.667 ms (1,200 PRT counts). Values below are
median / p95 percentages of that budget. Synthetic completion spans submission
through the pixel-query reply; Nurples active work spans its eZ80 loop/output,
including blocking, before pacing. Keep those scopes separate. Lower is better.

| Workload and measured scope | Mainboard | Native P4 | Direct r01 | Copy r02 |
|---|---:|---:|---:|---:|
| T07 scroll + tiles + 32 software sprites — complete | 150.4% / 178.1% | 105.1% / 114.2% | 226.6% / 249.2% | 108.0% / 120.4% |
| T03 scroll + clipped tiles — complete | 54.1% / 54.8% | 61.2% / 62.3% | 172.8% / 174.2% | 65.3% / 65.8% |
| T08 static field + 32 software sprites — complete | 74.3% / 74.5% | 53.6% / 55.0% | 40.8% / 42.3% | 40.8% / 41.0% |
| T09 short repaired Nurples — active | 21.2% / 42.4% | 33.5% / 35.2% | 32.2% / 305.8% | 32.7% / 34.6% |

### Measurement controls and pending work

| Control | Case | Mainboard updates/s | Native P4 updates/s | Direct r01 updates/s | Copy r02 updates/s | Copy final drain ms |
|---|---|---:|---:|---:|---:|---:|
| natural | T07 | 42.35 | 60.00 | 26.77 | 55.38 | 133.50 |
| natural | T08 | 60.00 | 60.00 | 60.00 | 60.00 | 2.28 |
| unmarked | T07 | Not run | 58.06 | 25.81 | 53.73 | 0.53 |
| unmarked | T08 | Not run | 60.00 | 60.00 | 60.00 | 0.39 |
| unmarked | T09 | Not run | 60.00 | 35.64 | 60.00 | 0.64 |
| no-timing | T07 | 40.22 | 57.60 | 25.71 | 53.73 | Not measured |
| no-timing | T08 | 60.00 | 60.00 | 60.00 | 60.00 | Not measured |
| no-timing | T09 | 60.00 | 60.00 | 35.29 (failed finalization) | 60.00 | Not measured |

Natural removes per-update queries. Unmarked disables window carriers; no-timing
also disables PRT probes. Synthetic completion queries remain in the latter two;
T09 never has per-update queries. Disabled hooks remain compiled in.

The natural T07 candidate still falls below 60 updates/s and ends with a
133.50 ms drain, versus 283.97 ms
on direct r01 and 52.11 ms on native P4.
Its short submission rate does not establish sustained completed rendering.
At 32 sprites this bounded remedy exceeds the mainboard rate in these matched
cases, but does not establish a stable 60-update heavy-scene target.

### HDMI observations, distinct from application rates

| Case | Application updates/s | P4 submissions/s | DMA scanouts/s | P4 observation window s |
|---|---:|---:|---:|---:|
| T07 | 54.14 | 60.06 | 60.06 | 2.231 |
| T03 | 60.00 | 59.94 | 59.94 | 2.002 |
| T09 | 60.00 | 59.98 | 59.98 | 2.001 |
| T08 | 60.00 | 59.94 | 59.94 | 2.002 |
| T01 | 60.00 | 59.94 | 59.94 | 2.002 |

Submissions/DMA cadence do not establish coherent fresh frames or sprite visibility.
The controller still edits the single buffer being scanned. Worker Drain omits
foreground query-driven primitive execution; concurrent/nested phase wall times
cannot be added as CPU use. No live key-latency or optical capture was collected.

The 120-update Nurples smoke reaches four player projectiles but zero enemy-table
actors. Its marked active-work p95 is 34.6% of the budget (about 65.4% headroom at that percentile).
Its final drain changes from 426.36 ms to 2.19 ms.
Neither result substitutes for the Author playing the ordinary repaired game
through busy enemies and assessing flicker and physical keyboard responsiveness.
No new 3,600-update candidate run or additional optimization is performed.

### Evidence and timing limits

[Machine-readable results](S06-WINDOW-RESULTS.json) retain every raw-result hash,
trajectory hash, per-run firmware identity, aggregate counter and clock field.
Candidate raw records/configurations/startup/receipts live in the ignored
`agents/scan001/s06/windows/copy-*` and `copy-remedy` evidence directories.
The SD evidence stays under `/agents/extender/results/scan-r01/s06b`.
Mainboard/EMOS identity follows retained installation records; P4 installation
has a fresh four-segment flash verification. No current game binary was replaced.

PRT counts use nominal 72 kHz; raw MOS time uses nominal 120 units/s observed
in steps of two. This is not an external clock calibration. Each marked P4
window durably records begin/end and includes opening acknowledgement, final
drain and close. Host reset-to-retrieval spans include boot, setup, SD writes
and operator-independent waits; they are not fixture runtime. Request ledgers
separately retain transfer/readback durations. No automatic reset deadline was
derived from an estimate, and no HTTP/SD/serial acquisition ran during timed loops.

## Closeout and Author review

All five original run configurations and the original 38-byte startup were
restored with whole-file readback. The listener exited normally, Agon was reset,
and post-reset input is ready/neutral with no held or queued keys. The SD service
is offline with no pending job; all diagnostic windows are closed without
overflow. The local `copy-restoration.json` pins those checks and restoration
hashes. The candidate remains installed; original direct and native rollback
images remain available. The Agon SD stays in Agon.

The next action is the Author's ordinary repaired Nurples playtest in ExCom,
including a busier enemy section and physical keyboard response. No further
optimization or descriptor work begins without discussion. S06 remains open.
No commit, push, production promotion or emulator change occurred.

## Author gameplay disposition — 2026-10-06

The Author calls the remedy a Nurples pass. Rally remains unresponsive to input,
as before; the Author explicitly distinguishes that unresolved issue from this
scrolling remedy. No precise residual flicker, latency or enemy-population
measurement is inferred from the qualitative pass.

Acceptance authorizes the normal closeout/promotion work under project policy;
it does not authorize another rendering experiment. Preserve the exact installed
bytes. Production promotion is not yet complete: the current production selection
is still the earlier DevKit bundle, and its canonical qualification includes
browser-video checks whereas this P4-PC build uses HDMI. Establish applicable
qualification coverage and satisfy it, then prepare the versioned bundle and tag
under existing version/publication authority. Do not silently waive video checks,
claim full firmware qualification from this bounded suite, or promote unrelated
dirty development. No further bench operation occurred while recording this reply.
