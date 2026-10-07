# Deterministic rendering load suite

## Executive summary

One eZ80 fixture renders the same preloaded VDU workload through EMOS to the
mainboard VDP or P4. Each case repeats indefinitely: **Space advances one case;
Escape closes the active measurement and exits**. The Pi can automate those
same keys at wall-clock intervals. Application completion, P4 conversion and
HDMI scanout are reported separately; none establishes physical displayed FPS.

The current [r04 contract](render-load-contract-r04.md) and
[machine-readable definition](../../tests/performance/render_load/contract-r04.json)
freeze the workload and execution rules. [BENCH-009](../tasks/BENCH-009.md)
owns implementation/qualification and retained evidence. Partial paired results
are retained; the Author paused the long campaign for discussion. The continuous
clock/control pilots, r04 sprite pilots on both endpoints and a P4 double-buffer
pilot pass. Offline result plotting does not resume the bench campaign.

The [resident selection](resident-render-suite.md) keeps the tested executable,
drawing data, colour charts and familiar-art visual checks permanently on Agon
SD. Routine runs reuse those exact files. Local-card collection can replace
bulk UART result retrieval without changing the frozen workload.

## Offline completion plots

`qualification/render_load_plots.py` creates a self-contained local HTML page
from a retained analysis directory. Set `RENDER_ANALYSIS` to that directory and
`RENDER_PAGE` to a new HTML filename outside it:

```sh
.venv/bin/python -m pip install -r tests/performance/render_load/requirements-plots.txt
.venv/bin/python qualification/render_load_plots.py --analysis "$RENDER_ANALYSIS" --output "$RENDER_PAGE"
```

Open the generated HTML directly in a browser. It embeds Plotly and its data;
no server or network connection is required. An adjacent provenance JSON records
input, generator, template, runtime and output hashes. Existing output files are
preserved. The tool requires the raw-provenance audit and verifies a retained
pause manifest's hashes when present. It reads local files only and cannot
deploy a fixture or contact the bench.

1. Device scatter: mainboard completion on X, P4 completion on Y, equal-time
   diagonal and nominal16.67ms budget lines. Colour identifies workload family;
   point size indicates load. Optional lines follow each variant's increasing
   levels, leaving gaps where paired measurements are missing.
2. Load curve: select one workload variant and compare endpoint completion as
   load rises1/4/16/64. The load axis is logarithmically spaced; its exact units
   depend on the family and appear above the plot.
3. Filter by mode, pacing, family, linear/log time axes and median/p95. All
   measurements use matching pass numbers. Medians and p95 values are medians
   of per-pass statistics; optional whiskers show the range of pass medians.
   Whiskers are unavailable for the p95 view and are not confidence intervals.
4. Click a point or table row for application rates, P4 accepted framebuffer
   submissions, DMA proxy and original run references. Completion and HDMI
   presentation remain separate. Hardware-sprite recurring composition is
   outside the command fence; double-buffer swaps include vblank waiting.
5. Export each plot as SVG from its toolbar, or download filtered rows as CSV.
   The table ranks worst P4 slowdown first, using mainboard completion as its
   baseline. Missing/failing measurements are never plotted as zero time.

The first-cut page uses the paused r04 snapshot:396 paired workload points,
1,252 valid scheduled executions,18 failed/invalid and2,678 unperformed. It does
not establish physical displayed FPS or complete three-pass coverage. Its
40 mode/pacing/statistic/scale combinations, coordinate/data agreement, missing
load gaps, point/table selection, CSV/SVG exports, mobile layout and absence of
external page requests were checked in Chromium. Plotly's
[HTML export](https://plotly.com/python/interactive-html-export/) and
[JavaScript function reference](https://plotly.com/javascript/plotlyjs-function-reference/)
describe the underlying plotting/export APIs.

## Build and preparation

### Supplemental fixed-source conversion control

`tests/performance/render_load/static_conversion.py` builds the experimental
static full-palette chart fixture using the same native assembler. Supply fresh
build output and the assembler explicitly. It produces numbered charts and SVG
references for20/8/136/21/149; mode selection remains in startup. The eZ80 draws
once, fences setup, waits five nominal seconds, then opens three ten-second
P4 windows without drawing, swaps, queries or SD work. The chart remains until
Escape. Double-buffered modes expose their back buffer once before measurement.

`qualification/static_conversion.py` stages one mode through the fast listener,
verifies executable bytes once, selects startup through EMOS and resets the Agon
using its admitted configuration. It collects small HTTP phase telemetry and
stops for visual review. Its default `normal` variant requires the installed
normal diagnostic image; `--variant convert-off` requires the separately verified
no-scanout conversion image. The latter retains RGB888 allocations and matching
single/double allocation selection but uses a software60Hz clock, creates no
DSI/DMA scanout, and performs no cache/panel submission. Image installation and
restoration remain the owning controller's responsibility, not this runner's.

Report native-row read/composition, lock waiting, RGB888 expansion, preparation
attempt, cache submission, accepted HDMI buffers and DMA cadence separately.
Equivalent frames/s is1000/ms for the named phase alone; it is not physical
displayed FPS. Preparation repeats on a static source and excludes submission/
trailing buffer-reuse wait. Row wall means are normalized by native image height;
they are neither CPU-only measurements nor per-frame percentile distributions.

`qualification/static_conversion_report.py` reads completed supplemental evidence
offline, verifies raw/controller hashes, excludes explicitly invalid controls,
requires five matching fixed-pattern pairs plus restoration, and generates a
self-contained HTML table/report, CSV, JSON and provenance into a fresh output
directory. [BENCH-009](../tasks/BENCH-009.md) records its experimental results,
known limits and the initial repeated-clear diagnostic defect. This supplement
does not resume the paused r04 workload campaign.

### Progressive workload preparation

1. Read the current local bench record, [bench constraints](../qualification/bench-constraints.md)
   and [SD layout](../sd-layout.md). The bench configuration JSON is ignored;
   it supplies network endpoints, reset configuration, fixture/result roots and
   the exact executable filename. Do not infer installed firmware from Git HEAD.
2. Build the application with `tests/performance/render_load/build.py` using a
   verified native assembler. The build stamps an immutable identity and hashes
   source, labels, assembler and contract. Its code must fit below0x042000.
3. `generate.py` preserves the frozen r01 drawing templates; r02/r03 change their
   execution/recording; r04 corrects untimed per-sprite setup. Per-frame commands
   remain unchanged. `packing.py` can
   losslessly column/delta-filter and byte-run-pack each case. The host verifies
   the decoded stream against its original hash. The eZ80 restores an entire
   case before setup, warm-up or measurement.
4. Deploy with `qualification/render_load_deploy.py` through the foreground
   **fast** EMOS SD listener. Upload packet CRCs remain enabled; the Pi performs
   one whole-file readback/hash per deployed file. No repeated checked-upload
   passes or SD operations occur inside measured frames.
5. Select video mode only in `/autoexec.txt`, before invoking the fixture. The
   runner preserves the original startup byte-for-byte, moves prior startup
   files into its owned result tree, installs a fresh plan/startup and uses the
   configured reset actuator. It never switches modes inside the application.

## Visual inspection and timed runs

Supply the ignored local configuration and evidence directory as shell variables
`RENDER_CONFIG` and `RENDER_EVIDENCE`. After deployment and readiness checks:

```sh
.venv/bin/python qualification/render_load.py --config "$RENDER_CONFIG" --evidence "$RENDER_EVIDENCE" run --mode 20 --endpoint p4 --manual
```

The manual form schedules no keys. Use the admitted web keyboard while the
workload is running: Space advances; Escape exits. The current bench's physical
USB keyboard path remains unavailable. The on-screen label identifies case,
family, variant, level and paced/throughput style. Templates and marker IDs
repeat every40 frames; marker IDs are not globally unique presentation numbers.

For an automated run of the same application:

```sh
.venv/bin/python qualification/render_load.py --config "$RENDER_CONFIG" --evidence "$RENDER_EVIDENCE" run --mode 20 --endpoint p4 --wait 20 --interval 10 --deadline 1100
```

The Pi injects Space on the declared wall-clock schedule and logs actual send
and completion times. The eZ80 records actual window bounds and frame counts;
setup/checkpoint time can shorten a window. Runs with fewer than64 measured
frames, truncation, timer saturation or protocol failure are invalid for the
comparison and require an explicit longer or recovered rerun. `--last-key escape`
exercises exit cleanup on the final selected case. `--first`/`--end` select a
bounded subset from the same immutable template stream.

After successful fixture return, startup launches the fast foreground listener
in Legacy for result retrieval. This happens after measurement. A fixture error
may stop autoexec at CLI. Direct startup ExCom has not negotiated Legacy SD
capabilities and can return503 even at a prompt. The runner confirms eligible
read-only metadata or rendered benchmark error/prompt text before requesting
EMOS Legacy and restarting the listener. Missing readiness or an uncertain request is a recovery
boundary, not permission to replay a mutation.

`qualification/render_load_campaign.py` runs the frozen three-pass endpoint
ordering for an explicitly installed output variant. It retains partial results,
continues independent cases after confirmed recovery, gives short samples a
longer window and runs marked cases with timing probes suppressed. A matching
control replays the failed invocation's preceding setup order at its original
key cadence; an isolated replay changes history and remains limited evidence. It never
selects or flashes firmware; the outer bench workflow owns verified image changes
and final restoration. Probe suppression leaves the bounded fence watchdog and
compiled diagnostic carrier present; it is not a claim that all instrumentation
has been removed.

`qualification/render_load_controls.py` supplies a separately identified
ordinary-image presentation control. Its caller must first verify the preserved
ordinary HDMI image and CLI readiness; the runner checks the installation,
compilation definitions and absence of the diagnostic endpoint. An ignored
configuration/selection supplies the stable serial identity and affected setup
prefixes. It suppresses timing probes, retains ordinary serial logs and restores
startup/admission. Missing diagnostic windows are permitted only for this
control suite; they remain invalid in scheduled paired comparisons. Ordinary
logging can omit all-zero submission intervals, so silence is inconclusive.

## Clocks, records and limits

1. PRT1 uses the system clock divided by256: nominal72,000 counts/s,
   13.889µs/count, with0.9102s saturation. The fixture calibrates against raw
   MOS vblank time and leaves PRT0/source selection unchanged. Raw MOS time is
   nominal120 units/s at60Hz with16.67ms granularity. Calibration has start-phase
   quantisation; it is not a precision external oscillator measurement.
2. A screen-pixel reply fences prior drawing. Completion includes EMOS routing,
   transport backpressure, drawing and the reply; it does not measure coherent
   output delivery or every recurring hardware-sprite operation.
3. `B9R2` results contain a128-byte build/calibration header, then variable-length
   `B9C2` case headers and12-byte per-frame records. The strict host codec rejects
   incomplete checkpoints and broken template ordering. The fixture checkpoints
   only after an operator/scripted transition ends the case.
4. Module-safe Agon user RAM ends at0x0B0000. Samples use15,018 records at0x044000
   and16,384 at0x080000. The latter reuses packing memory only after decoding;
   the active VDU template remains at0x070000. Rendering continues indefinitely
   after31,402 stored records, but marks truncation. A truncated visual run is
   not a complete statistical benchmark distribution.
5. Primitive/bitmap counts name submitted operations. The frozen grid can clip
   some32-pixel bitmaps at a screen edge; paired endpoints receive identical
   coordinates. Do not interpret count as fully visible pixel area or compare
   different resolutions as equal pixel workloads.
6. P4 diagnostic builds expose closed phase windows. Full HDMI, held conversion
   and absent scanout are distinct variants. The absent-scanout variant uses a
   software60Hz clock and retains framebuffer memory; disclose that difference.
   Generic display metadata alone does not establish that scanout is active.
7. An ordinary double-buffer swap can impose vblank cadence even in throughput
   style. Include that behavior when interpreting application updates/s.
8. Hardware/software sprite labels refer to the VDP API flag. The P4 adapter
   composes hardware sprites in its native-row presentation reader; this is
   CPU work, not PPA acceleration. Hold/off suppress that composition together
   with conversion. Hardware-sprite completion therefore measures pose-command
   processing; these controls do not measure hardware-sprite rendering throughput.
9. A conversion scope also closes when publication aborts. Its calls and wall
   times describe attempts; completed submission counts advance only after the
   driver accepts a framebuffer. A zero-submission window can have successful
   application drawing and steady DMA scanout of an older frame. The report
   keeps tails/budget percentages, phases and zero-submission outcomes separate.

## Restoration and evidence

After generating the analysis, audit execution coverage against retained raw
records and failure receipts:

```sh
.venv/bin/python qualification/render_load_audit.py --evidence "$RENDER_EVIDENCE" --analysis "$RENDER_RESULTS" --output "$RENDER_RESULTS/execution-audit.json"
```

`RENDER_RESULTS` is the local derived-results directory. The audit verifies
raw hashes, identities, checkpoint order and agreement with decoded records.
It distinguishes valid measurements, failed/invalid executions and unperformed
cases. A fence failure at the next case boundary is explicitly inferred from
preceding checkpoints. Corrupt provenance cannot supply coverage. Regenerate
analysis and audit after the controller is terminal before final closeout;
execution coverage alone does not prove controls or restoration complete.

The maintained campaign accepts explicit `--first-case`, `--end-case` and
`--endpoint` selections for a separately receipted continuation. Use them only
after auditing retained checkpoints and the original unperformed range; do not
repeat valid records under the same pass. A recovered warm-up fence failure is
a case outcome, so subsequent independent cases continue. Mode/load/timer
failures and unresolved readiness still stop the affected preparation.

Recovery Escape requires both admitted input and the invocation's tagged active
window: keyboard admission alone can precede installation of RUN's callback.
Retain any post-reset recovery checkpoint separately from the interrupted
measurement. Recovery waits do not stretch the scheduled measurement keys.

After Escape/automatic completion has returned to the listener, restore startup:

```sh
.venv/bin/python qualification/render_load.py --config "$RENDER_CONFIG" --evidence "$RENDER_EVIDENCE" restore
```

The owning bench workflow also restores the exact ordinary P4 HDMI image,
verifies its deployed segments and checks EMOS admission/HTTP readiness. Preserve
source/build receipts, deployed hashes, startup history, actual key schedules,
raw records, telemetry and informative failures. Keep preparation, fixture
execution/return and retrieval durations separate. No production promotion,
commit or remote publication is part of benchmark execution.
