# Focused multi-mode rendering qualification

The Author selects stock modes 0, 3, 8, 20 and 136 for the next qualification
round. One host master runner owns sequential execution, durable collection
and the final persistent Extender display cue. Existing mode-20 evidence is
retained; the current frozen fixtures are not qualified for other geometries.
The runner and 40 per-mode fixture derivatives compile and pass offline checks.
Physical staging and short per-fixture smoke qualification are underway; the
full campaign is not yet ready to invoke.

## Bounded work contract

### MQ01 [x] Master sequencing and completion contract

1. `scripts/run_render_qualification.py` executes reviewed argument-vector
   adapters serially, without a shell or automatic reset, retry or resume.
2. The frozen local plan must cover eight workloads, three repeats, two
   renderers and five modes: 240 distinct runs. Preserve original RGB888
   comparisons separately; this campaign's RGB888 control is the most modern
   qualified optimized RGB888 build, identified by exact source and bytes.
3. Each adapter returns a durable receipt binding its job ID, renderer, mode,
   workload and repeat. It confirms validation and positive bench handback.
   Exit code alone cannot pass a case. Unknown bench state stops further
   input. A recovered failure may continue only with explicit safe-to-continue
   evidence from the adapter; it contributes to the final error result.
4. The master saves the plan, per-job adapter logs, receipts and an atomically
   updated summary with UTC timestamps and monotonic elapsed seconds. Output
   directories are exclusive; retained evidence cannot be overwritten.
5. After all jobs return, the admitted display adapter leaves repeated white
   `ALL TESTS COMPLETE SUCCESS` text on green, or
   `TESTS COMPLETE WITH ERRORS` on red. Generated MOS VDU command files select
   no mode and launch no program. Notification failure is recorded separately.
   Interrupted/unsafe campaigns remain incomplete; the host must not inject
   a speculative error screen into a possibly running application.

### MQ02 [ ] Qualify reusable fixtures for the five geometries

1. Keep the eight agreed workloads: light/heavy bitmap plotting, isolated
   partial vertical scrolling, static-background software sprites,
   scrolling-background software sprites, deterministic software Nurples,
   isolated hardware sprites, deterministic hardware Nurples.
2. Inspect existing generators before adapting. Current SCAN and Nurples
   fixtures assume mode-20 playfield dimensions and positions; do not merely
   relabel results. Preserve frozen binaries and use fresh identified builds.
3. Nurples-derived geometry adaptations must preserve deterministic updates,
   actor counts and asset provenance; document changed viewport area and
   clipping. Compare renderers within each mode, not unlike workloads across
   modes. Mode 0 uses 16 colors; palette behavior is part of qualification.
4. In mode 136 establish explicit page-flip/pacing behavior and confirm both
   pages. Single-buffer workloads must not silently measure a hidden page.
5. Reuse finite completion fences and aggregate Nurples windows. Record eZ80
   work/pacing, queued rendering and asynchronous HDMI costs separately.

Implementation: `tests/performance/scan/multimode.py` builds six bounded
synthetic workloads and two repaired-Nurples derivatives for each mode. All
40 binaries compile. The original repaired Nurples fixture reproduces byte for
byte with the selected native assembler before relying on its retained source.
The synthetic streams repeat a declared 128-update sequence; every bitmap and
sprite position passes exhaustive bounds checks over all 256 table indices.
Partial scrolling remains 256 pixels wide, with a one-scanline tile viewport;
its height follows the selected mode. Double-buffer synthetic scrolling updates
both rows elapsed since the current bank's previous visit.

Nurples remains a production gameplay target in mode 20. Other modes use
explicit test derivatives with centered 256-pixel playfields and mode-dependent
vertical bounds; original bezel/UI artwork can be clipped. Mode136 initializes
both banks and alternates the retained incremental scene algorithm. It is a
bank-stress derivative, not a claim that production Nurples is a correct
double-buffered game. Compare deterministic state within each mode/variant;
do not equate those derivatives with unchanged gameplay or cross-mode work.

The current P4 queued-render counters exclude immediate double-buffer drawing.
Mode136 therefore retains eZ80 active/pacing/completion measurements and output
phase evidence, but its queued-render reduction must be reported as unmeasured,
never inferred from zero counters. Hardware smoke admission and valid timing
records do not substitute for Author visual/gameplay acceptance.

### MQ03 [ ] Prepare admitted mode and firmware transition adapters

1. Pin actual candidate/control manifests, all adapter and fixture hashes,
   per-mode expected status and fresh result paths in an ignored local plan.
2. EMOS owns routing; the host uses the admitted CLI/listener. Select each
   fixture mode only through setup-only `/autoexec.txt` and the controlled
   reset protocol. No test launch belongs in autoexec. Explicit CLI commands
   launch each staged suite after verified readiness.
3. Preserve ordinary startup and configurations, verify every restoration,
   and retain exact firmware install receipts. No EMOS/mainboard VDP, wiring,
   parallel transport, production promotion or video timing development is
   part of this runner task.
4. Qualify the completion adapter on Extender. Keep the final banner visible;
   no subsequent automated clear/reset/game launch may erase it. Save final
   data before the banner. Distinguish host summary success from unperformed
   Author visual/input acceptance.

Implementation: `qualification/prepare_render_modes.py` prepares the immutable
local package; `qualification/render_modes.py` owns admitted installation,
setup-only mode changes, explicit invocation, collection and restoration.
The local plan selects the same-source optimized RGB888 control and winning
indexed candidate with unsuccessful optional experiments disabled. Actual
identities, host/board details, source and archive hashes remain in the ignored
bench records. The 240 full jobs and 80 separate short smoke jobs have fresh
paths; a smoke can never satisfy or overwrite a full measurement.

### MQ04 [ ] Stage, execute and report

1. Finish all independent preparation and offline fault-path tests before
   declaring physical readiness. The master is not ready merely because its
   Python coordinator compiles.
2. Stage/read back fixtures, verify the selected firmware and initial input
   readiness, then launch the master explicitly. Do not overlap another bench
   client or disturb an already running campaign.
3. Record setup, execution, collection and notification durations separately.
   Use comparable retained runtimes for estimates, never as reset deadlines.
4. Restore ordinary files before the persistent final cue. Tabulate matched
   per-mode results with units, baseline and percentage reduction; keep
   non-comparable geometry/output results explicitly separate.

The completion screen reports execution and assertion/data-validation status.
It does not promise a speedup in every mode, qualify production release, or
replace Author visual/gameplay review. No framebuffer-capture diagnostics are
inserted into the timed workloads. The final text reader only verifies the
completion cue after all measurement records have been saved.

## Framework use

Run with the project virtual environment:

```bash
.venv/bin/python scripts/run_render_qualification.py --write-banners OUTPUT_DIR
.venv/bin/python scripts/run_render_qualification.py --plan LOCAL_PLAN --check
.venv/bin/python scripts/run_render_qualification.py --plan LOCAL_PLAN --output FRESH_RUN_DIR
.venv/bin/python -m unittest discover -s tests/performance/host -p test_master_runner.py -v
.venv/bin/python -m unittest discover -s tests/performance/scan -p test_multimode.py -v
.venv/bin/python -m unittest discover -s tests/performance/host -p test_render_mode_adapters.py -v
.venv/bin/python scripts/analyze_render_qualification.py RUN_DIR --output FRESH_ANALYSIS_DIR
```

The local plan schema has `schema: 1`, explicit `ready: true`, `cwd`,
`renderers: [rgb888, indexed]`, a path-to-SHA256 `inputs` map, 240 `jobs`, and
`notification.success`/`notification.errors` argument vectors. Each job supplies
`id`, `renderer`, `mode`, `case`, `repeat`, `qualified_geometry: true` and
`command`. Workload IDs are the script's `CASES` constant. `{receipt}` and
`{evidence}` expand to fresh absolute output paths. Adapter receipts repeat
those five identity fields and supply `validated`, `bench_idle`, and, for a
recovered failure, `safe_to_continue`. The plan is trusted local configuration,
not a sandbox or permission mechanism.

## References

1. [Current optimization contract](NURPLES-PERFORMANCE-R01.md).
2. [Renewed results](NURPLES-PERFORMANCE-R02-RESULTS.md).
3. [Test execution](../../procedures/test-execution.md).
4. [Bench constraints](../../qualification/bench-constraints.md).
5. Official `agon-docs/docs/vdp/Screen-Modes.md`: mode geometry, colors and
   supported double buffering. Reference checkout remains read-only.
