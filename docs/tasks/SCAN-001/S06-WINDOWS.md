# SCAN01-S06 — Correlated diagnostic windows

**S06 in progress.** This document retains the native/mainboard and original
direct-renderer comparisons, including the failed finalization control. The
subsequent authorized [copy-scroll remedy](S06-COPY-REMEDY.md) is recorded
separately; its measurements are also included in the machine-readable results.
Do not treat the original direct results below as measurements of that candidate.
No S07 descriptor experiment has started.

## Fixture change and scope

W01 [x] Build an explicitly new `scan-scroll-suite-r02` fixture. S05's r01
binaries/evidence remain immutable. r02 adds optional BEGIN/END carriers and a
fresh synthetic pacing epoch after warm-up for all variants. The old epoch could
retain accumulated warm-up deadline debt; keep r01 timings separately labelled.
No drawing command, asset, simulation input or game logic changes. All nine
compiled binaries carry the new build identity; this tranche deploys only
T01/T03/T07/T08/T09 as `window-r02.bin` alongside their existing r01 assets.

W02 [x] Reuse official buffer-write command0 to reserved ID65535, which stock
consumes/discards. Never CLEAR that ID. The diagnostic firmware recognizes the
existing B00912-byte payload, case ID and nonzero24-bit run tag. New config bit2
selects carriers; config11/header10 store the tag. Official documentation at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`: [buffer command0](../../../../../agon-docs/docs/vdp/Buffered-Commands-API.md).
Stock VDP v2.16.0 and the existing `vdu_buffered.h`/`render_benchmark.hpp`
implementation establish consumption and diagnostics. No mainboard flash is
needed. Mainboard receives the same marked fixture command bytes for comparison.

W03 [x] Bracket actual work. Drain warm-up before BEGIN; acknowledge BEGIN with
an ordinary pixel query; start the eZ80 measured epoch; execute the finite
workload; record end; perform separately recorded final drain; send END; clean
up and save SD records. No per-update carriers/callbacks, logging, HTTP polling
or captures. P4 wall time includes opening acknowledgement, record/checkpoint
tails, final drain and closing-carrier transit. It excludes assets and warm-up.
It is not identical to the sum of eZ80 per-update timings.

W04 [x] Validate physically: exactly one closed window per case/tag, no overflow,
expected row count, no abort/fence/saturation/game fault, matching Nurples
trajectory. Compare aggregate wall time to the eZ80 window as a boundary sanity
check, not cross-processor timestamp subtraction. Retain boundary-dropped scopes.

W05 [x] Run the same five short identities on native diagnostic P4 and mainboard.
Run bounded T07/T08/T09 unmarked/no-PRT controls and T07/T08 natural pacing (T09
already unfenced). Distinguish compiled-in inactive hooks from hook-free images.
The r02 ordinary-image control remains due at rollback; earlier r01 cannot
silently substitute for it. No broad full-suite campaign or OFF output replay. Native/mainboard short controls
are complete; the separately stated r02 hook-free firmware control still awaits
rollback and is not covered by this checkmark.

W05A [x] **Author-approved addition:** after the short smoke showed zero enemy
actors, run one3600-update T09 on mainboard and one on the currently installed
native P4. Existing binary/map/script,120warm-up updates, no new workload.
Compare identical state trajectories and separately report busier intervals;
approximately60s of measured execution if it maintains60updates/s, excluding
loading/warm-up/retrieval. No automatic direct/full or repeated long campaign
is authorized by this bounded addition.

W06 [x] Preserve native evidence, restore original startup/configurations, and
prepare the retained direct-image flash command for the Author. This staging is
complete; the actual direct comparison remains for the next Author-controlled
flash. Compare direct under matched scopes before ranking a mechanism as demonstrated. S06 stays open
at this Author-controlled flash boundary; do not move to S07.

W07 [x] Execute the already planned direct-image comparison: the same five
120-update marked cases, then the matched short unmarked, natural-pacing and
no-PRT controls. No longer direct Nurples run is implied by W05A. Retain failures,
compare matched trajectories and timing scopes, restore startup/configurations,
and report the remaining hook-free firmware/visibility/input boundary.

### Author observation before the direct comparison

After flashing the retained direct diagnostic build, the Author ran ordinary
Nurples and reported the same sprite flicker and poor keyboard responsiveness.
After the game ended, Escape returned control; the Author ran the same game on
mainboard without resetting and reported normal operation. This is a manual
gameplay observation, not a timed fixture or precise localization of input delay.
It confirms that the direct build is not an accepted remedy. The earlier
promising short run used the native renderer; neither observation establishes
native busy-scene visual/input acceptance.

## Counter interpretation

The existing P4 counters observe Drain, RowWait, RowCompose, Expand, Cache and
Conversion. These are wall-time scopes, sometimes nested and concurrent, not
additive CPU percentages. Conversion includes output-buffer waiting. Drain spans
an entire admitted worker drain and can include waits; it is not an individual
scroll timer. RowWait measures output-row acquisition of native exclusion.

The Drain hook is specifically around the background worker's `controller_->drain()`
in `stock_p4_service.cpp`. Pixel-query completion can instead execute queued
primitives synchronously through `Canvas::waitCompletion(false)` and
`BitmappedDisplayController::processPrimitives()`. That work is outside this hook;
low Drain totals in a fenced case do not establish cheap drawing. In the direct
publisher, Conversion includes acquiring native exclusion and preparing overlays;
it does not mean RGB expansion, which the direct path skips.

No per-frame pixel marker is added to these scenes. Consequently firmware
`marker_invalid`, last-frame and transition counts are inapplicable. `updates`
counts publication submissions and scanouts count DMA cadence; neither proves
fresh coherent pictures or absence of flicker. Existing hooks do not directly
measure queue occupancy, isolated scroll duration or the interval with software
sprites hidden. Preserve those limits rather than claim the missing observations.

## Validation and evidence

r02 builds on the native assembler, retaining source/build hashes and address
maps. Four host tests pass, including unchanged tile/scroll/software-sprite
semantics and tag/control validation. Generated assets/streams match r01 exactly;
all nine binaries contain the expected single20-byte carrier. Nurples table end
remains below the0x50000 scratch region; records stay at0x80000. The five marked native/mainboard short cases now physically pass:120 records
each, matching Nurples checkpoints, five correctly correlated P4 windows, no
open window/overflow or fixture faults. Window durations agree with the coarse
eZ80 clock within3.3ms for these short runs. Emulator profiles and production
firmware/game files are unchanged.

Machine-specific runner, configurations, receipts and raw records are retained
under `agents/scan001/s06`; card results under
`/agents/extender/results/scan-r01/s06b`. The existing original startup is preserved
and must be restored/read back before closeout. No commit or push authorized.

## Results — native diagnostic image, before direct comparison

**The longer deterministic Nurples run sustains nominal60 game updates/s on both
endpoints, including the busier section.** Native P4 has similar or better active
headroom in that busier section, but its diagnostic image submits only21.03 HDMI
pictures/s while DMA scans at59.99Hz. No render optimization was made in this
tranche. Direct-renderer comparison, hook-free r02 control and visual/input
acceptance remain open; this is not completion of S06 or approval to begin S07.

Both3600-update records match on every retained simulation checkpoint, phase,
actor/projectile count, map progression and RNG. They reach five live enemy-table
actors and four live player projectiles. This covers the approved deterministic
map/script; it is not a claim about every possible game state or maximum sprite
population. The Author's promising visual observation concerned the earlier short
smoke, whose measured interval had zero enemies, and is not upgraded to a pass
for crowded gameplay without their observation.

### Game-loop budget, busy intervals first

Budget = nominal16.667ms. Active work includes eZ80 execution, MOS output and any
transport blocking. Values are percentages, not processor utilization. Remaining
active headroom =100% minus the table value. Groups are identical on both boards,
ranked by P4 p95 active cost; enemy-table actors may include hostile projectiles.

| Live enemy-table actors | Updates | Mainboard median / p95 budget used | Native P4 median / p95 budget used | P4 p95 change vs mainboard |
|---|---:|---:|---:|---:|
| 3–5 | 995 | 49.6% / 70.4% | 47.6% / 55.2% | -21.5% |
| 1–2 | 1921 | 34.2% / 64.4% | 42.2% / 52.3% | -18.8% |
| 0 | 684 | 19.7% / 43.0% | 29.6% / 39.0% | -9.3% |

Relative change =100×(P4 active time/mainboard active time−1). These are one run
per endpoint, not a repeatability study. Across the complete long run, neither
endpoint has an active-work sample beyond16.667ms or a recorded fault; maximum
active work is14.39ms on mainboard and11.67ms on P4. That does not prove live key
latency, coherent presentation or flicker-free software sprites.

### Short controls, same workload identities

These are120-update windows. T07 combines partial scrolling/tile insertion and32
software sprites; T08 keeps the same32 sprites without scrolling. T09 is Nurples.
Per-update queries force completion/reply and alter pipelining. No-query rates
are submission/pacing rates; a final drain is reported separately.

| Variant | Mainboard T07 updates/s | Native P4 T07 updates/s | Scope |
|---|---:|---:|---|
| marked | 39.78 | 56.25 | Per-update query; carrier/PRT enabled |
| natural | 42.35 | 60.00 | No per-update query; PRT enabled |
| no-timing | 40.22 | 57.60 | Per-update query; markers/PRT disabled |

T08 and the short T09 controls maintain60 wherever run. Native T07 with PRT on
but windows off reaches58.06updates/s versus56.25 with windows on:3.1% lower
with active windows in these two samples. No universal correction factor follows.
The natural T07 final drain is8.17ms on mainboard and52.11ms on native P4; T08
is4.53ms and0.75ms respectively. Native's60/s short submission rate plus its
52ms tail does not establish sustained60/s completed rendering, nor by itself
prove that backlog is growing rather than a bounded pipeline delay. Mainboard's
natural T07 remains below target at42.35/s, with active-output stalls up to42.69ms.

The native no-window/no-PRT controls keep the diagnostic firmware compiled in;
they are not a hook-free firmware comparison. A matched r02 ordinary-image
control remains due at rollback. Historical r01 results use a different initial
pacing epoch and stay separate.

### P4 output observations and ranking

Window time is measured on P4; scopes are nested/concurrent and cannot be added
as CPU percentages. They are not mainboard-comparable render-time columns.
No pixel frame-marker was drawn, so old marker-valid/invalid fields are ignored.

| Native workload | eZ80 updates/s | HDMI submissions/s | DMA scanouts/s | Mean conversion/publication preparation ms |
|---|---:|---:|---:|---:|
| T07 | 56.25 | 18.78 | 60.09 | 51.31 |
| T09 long | 60.00 | 21.03 | 59.99 | 46.02 |
| T03 | 60.00 | 21.48 | 59.94 | 44.32 |
| T08 | 60.00 | 23.97 | 59.93 | 39.68 |
| T01 | 60.00 | 26.97 | 59.94 | 34.82 |

F01 — Full-picture expansion is a measured native-output cost even in the static
control. In the long game, the expand scope totals36.45s over a60.06s aggregate
window; mean conversion is46.02ms per completed scope. Its mean row expansion
is75.14µs, or28.85ms for384 rows as an operation-cost illustration. This is a
stronger target than game-loop work for this particular long native run, but
instrumentation overhead and memory/scheduler effects remain included.

F02 — Drawing/output exclusion adds measurable waiting: long-game row acquisition
wait totals12.62s, with a3.33ms largest individual wait. Row composition totals
4.75s; the cache/submission call totals0.67s. These overlap/nest with other scopes;
no CPU-load sum or claim that cache is universally cheap is made. Existing hooks
do not separate queue occupancy, scheduler delay, or each scrolling primitive.
These data also do not isolate PSRAM contention from CPU/cache/scheduling cost.

F03 — The current direct renderer remains an unmeasured alternative in S06.
S02's ninefold pixel-exchange operation count and direct-DMA sprite-exposure
hypotheses are not converted into measured slowdown/flicker claims. The next
Author flash uses the retained matched direct diagnostic image, with the same
r02 fixtures. It must be measured before selecting a remedy.

F04 — No scope directly measures sprite-hidden time or delivered key-to-consumption
latency, and no image is captured during timing. Crossing-window phase samples
can be dropped; those counts are retained. Continuous output passes may straddle
the edges, so the window does not promise perfectly aligned first/last HDMI
pictures. Neither stable DMA cadence nor no fixture faults closes those gates.

### Evidence and current boundary

[Fixture manifest](S06-FIXTURES.json), [explicit on-card mapping](S06-DEPLOYMENT.json)
and [results with phase/raw-record hashes](S06-WINDOW-RESULTS.json) are retained.
Raw records, per-run tags/configurations, exact startup, P4 windows and host logs
remain under `agents/scan001/s06/windows`; SD results are in its named s06b
result directory. The decoder/analysis tool is maintained beside the fixture.
P4 identity follows the Author's fresh four-segment verification receipt;
mainboard/EMOS identities still follow retained installation records, not a fresh
ROM attestation. Clock units/calibration limits from the baseline remain.

The next direct image's19 artifact hashes and silicon1.3 compatibility were
reverified without flashing. Author-controlled flashing remains required.
Closeout is verified: original38-byte startup and all five original smoke
configurations restored by whole-file readback, followed by Agon reset. Input
is ready with no held/pending keys; listener is offline, and no diagnostic
window remains open or overflowed. The native diagnostic firmware remains
installed; no ordinary or direct image was flashed by the agent.
S06 remains open; no S07 work, commit, push or production promotion occurred.

## Results — direct comparison, 2026-10-06 local date

**The direct implementation fails the scrolling workload even without busy enemy scenes.** It sustains 60 updates/s with 32 software sprites on a static background, but only about 26 with the same sprites plus scrolling/tiles. The short Nurples run falls to 36–40 updates/s and leaves about 0.43 seconds of drawing/reply work at the final drain. The native and mainboard short Nurples controls both sustain 60. This is a measured regression, not a successful fix.

Four direct batches retain 13 case executions and 1,560 rows. Twelve finish without recorded faults or abort. The timing-disabled Nurples control contains all 120 rows but reports an abort at finalization; it is explicitly failed, not counted as a clean pass. The same five workload identities and previously deployed r02 binaries are used. No direct 3,600-update run, renderer change, image capture, or production game modification occurred.

### Matched short workload rates

All values are nominal eZ80 updates/s; 120 measured updates after fixed warm-up. T01/T03/T07/T08 include one completion query per update. T09 is unfenced gameplay submission/pacing. Rank: lowest direct update rate first. Percentage change = 100 × (direct/native − 1); native diagnostic P4 is the baseline. These are not HDMI picture rates.

| Workload | Mainboard updates/s | Native P4 updates/s | Direct P4 updates/s | Direct rate change vs native |
|---|---:|---:|---:|---:|
| Scrolling/tiles + 32 software sprites (T07) | 39.78 | 56.25 | 26.18 | -53.5% |
| Partial scrolling + clipped tiles (T03) | 60.00 | 60.00 | 34.62 | -42.3% |
| Nurples, short scripted run (T09) | 60.00 | 60.00 | 39.56 | -34.1% |
| 32 software sprites, static background (T08) | 60.00 | 60.00 | 60.00 | +0.0% |
| Static/polling (T01) | 60.00 | 60.00 | 60.00 | +0.0% |

For fenced work, completion includes eZ80 submission, rendering and the reply. The median T03 completion is 9.01 ms on mainboard, 10.21 ms on native P4, and 28.81 ms on direct P4: direct uses **173% of one 60 Hz update budget**, versus 61% for native. T07 direct completion consumes 227% at the median and 249% at p95. Static-sprite T08 completes in 6.81 ms on direct versus 8.93 ms on native: the direct implementation is not uniformly slower.

### Instrumentation and natural-pacing controls

T07 controls below retain the same command stream except for the stated completion query/carriers. All T08 controls remain at 60 updates/s. Compiled-in inactive diagnostic hooks remain present; a hook-free firmware comparison is still outstanding. Rank: lowest direct rate first.

| T07 variant | Mainboard updates/s | Native P4 updates/s | Direct P4 updates/s |
|---|---:|---:|---:|
| no-timing | 40.22 | 57.60 | 25.71 |
| unmarked | Not run | 58.06 | 25.81 |
| marked | 39.78 | 56.25 | 26.18 |
| natural | 42.35 | 60.00 | 26.77 |

`natural` omits per-update queries; `unmarked` keeps PRT but disables P4 windows; `no-timing` disables both. The slowdown persists across all four controls. Natural direct T07 finishes its submitted workload at 26.77 updates/s, then needs a separately timed 283.97 ms final drain (native 52.11 ms; mainboard 8.17 ms). The direct natural T07 active p95 consumes 381% of a nominal update budget. These data do not establish actual queue occupancy or isolate scroll duration from tiles/sprites.

### Nurples headroom and finalization

All short Nurples trajectories match, including the retained failed-finalization control. Their measured intervals have zero enemy-table actors and up to four player projectiles. They already distinguish the failing direct path; they do not replace the earlier native/mainboard long busy-scene pair. Rank: highest active p95 first.

| Short Nurples variant | Updates/s | Active p95 budget used | Largest active interval ms | Final drain ms |
|---|---:|---:|---:|---:|
| Direct, windows off | 35.64 | 327.6% | 68.99 | 432.99 |
| Direct, marked | 39.56 | 305.8% | 62.62 | 426.36 |
| Mainboard, marked carrier | 60.00 | 42.4% | 8.60 | 2.53 |
| Native, marked | 60.00 | 35.2% | 6.17 | 0.79 |

The no-timing direct Nurples record has 120/120 rows, no row fault flags, but `abort=true`; its coarse pre-finalization window suggests 35.29 updates/s and is retained only as incomplete-control evidence. The listener was online afterward, so the batch returned safely. Source review finds a finite 65,536-poll completion wait when PRT is disabled; a final-query timeout sets the header abort after the final row has been stored. That is consistent with these bytes and the long tails in the successful PRT runs, but no retained finalization-reason field proves it. No exact watchdog duration is inferred, no fixture was silently repaired, and no failed evidence was discarded.

### Output counters and mechanism ranking

Direct T03/T07 submit approximately 60 panel selections/s even though the application achieves only 35/26 updates/s. These submissions can repeat or expose partially drawn contents; 60 Hz DMA and submission counts are not evidence of 60 coherent game pictures. In short direct Nurples, the measured worker drain reaches 114.83 ms (about 6.9 frame periods); native short Nurples reaches 4.16 ms. The direct counters do not cover every foreground drawing operation, and a long worker drain does not prove that a sprite is absent for its whole duration.

F05 — **First optimization target: partial vertical scrolling.** The no-scroll 32-sprite control holds 60; scrolling/tile cases fail with and without measurement/query overhead. The source-audited whole-row-plus-sidebar exchanges remain the leading mechanism. This establishes a workload-specific regression, not a measured ninefold slowdown, PSRAM bandwidth attribution, or isolated `VScroll` time.

F06 — **Sprite exposure remains a separate correctness risk.** The Author reproduces flicker in the direct build; CPU sprite hide/redraw shares DMA-scanned storage. Long drawing intervals make exposure plausible, but no hidden-sprite interval or coherent-picture trace was captured. Reducing scroll cost alone would need a fresh visual check; it cannot be declared a flicker fix.

F07 — **Input delay remains incompletely localized.** Long eZ80 active/output stalls and worker drains provide concrete delay opportunities. Parser/drawing sharing and native exclusion were established in S02. This fixture substitutes a private scripted key map, so it does not prove where real keyboard packets wait or establish a keyboard-latency pass.

F08 — **Bounded remedy candidate for the next decision:** reuse stock FabGL’s existing two-callback `genericVScroll` helper, copying only the selected field in overlap-safe row order instead of exchanging sidebars and complete rows. The direct class currently leaves `rawCopyRow` empty, so the processor/output-specific copy adapter would be required. S02 calculates one-sixth of current algorithmic read/write volume for this field; that is not a speedup promise. This is an alternative already contemplated by S08, not approval to skip the Author’s architecture/implementation gate or abandon the segmented-DMA study. No implementation begins here.

### Evidence and next boundary

The [machine-readable results](S06-WINDOW-RESULTS.json) include all prior native/mainboard runs and four direct batches, raw hashes, tagged windows, trajectory hashes, the failed-control disposition, and exact build identities. Direct installation follows the Author’s new four-segment verification receipt for `rgb-001-r01-b2026-10-05-23-30-11Z`. All measured loops ran without host HTTP/SD/serial activity. Primary PRT calibration totals are 34,881–35,929 counts over 60 raw MOS units; nominal 72 kHz / 120-unit clocks and tick-phase uncertainty remain, not independent frequency calibration.

Original 38-byte startup and all five original smoke configurations are restored and whole-file-readback verified. After reset, input is ready/neutral, the listener is offline with no pending job, and all five diagnostic windows are closed without overflow. The direct image remains installed. The ordinary r03 rollback image’s 19 artifact hashes and silicon compatibility have been verified without flashing. The host runner/report reader is prepared to accept an absent diagnostic endpoint only for the specifically verified ordinary rollback, with missing telemetry explicitly recorded. No hook-free run is claimed yet. The next Author-controlled boundary is restoring that image for the remaining matched r02 hook-free controls; visibility/input and isolated mechanism measurements remain open. S06 is incomplete and S07 has not started. No commit, push, or production promotion.
