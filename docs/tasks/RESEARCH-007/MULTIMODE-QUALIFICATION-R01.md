# Focused multi-mode rendering qualification

The Author selects stock modes 0, 3, 8, 20 and 136 for the next qualification
round. One host master runner owns sequential execution, durable collection
and the final persistent Extender display cue. Existing mode-20 evidence is
retained; the current frozen fixtures are not qualified for other geometries.
The runner and 40 per-mode fixture derivatives compile and pass offline checks.
Staging is complete for the current package; sixteen short RGB888 receipts are
data-valid. The Author reported vertical squashing and execution is stopped
for [HDMI-003](../HDMI-003.md). The full campaign is not ready to invoke.

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
   reset protocol. Mode setup must finish in Legacy: after EMOS temporarily
   routes mode selection to P4, explicitly return to Legacy before boot ends. No test launch belongs in autoexec. Explicit CLI commands
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

## Preparation findings — 2026-10-13

1. The first short mode-0 bitmap smoke returned safely and saved valid raw
   records, but failed the required fence-sidecar check. The selected P4 source
   at `e26c24f743b9b94efa05eac46f2f237689ac3b5b`, in
   `vdp/video/extender/diagnostics/render_benchmark.hpp`, admits fence samples
   only for diagnostic IDs 3, 7, 8, 39, 41 and 54. New workload IDs 1–8 must
   not be assumed to share that diagnostic contract. Preserve this informative
   failure; no full campaign was launched.
2. Revised fixtures keep result workload IDs 1–8 and explicitly map the B009
   carrier to the retained finite diagnostic IDs; games retain aggregate-only
   ID 9. Mode 136 also uses aggregate-only ID 9 because immediate double-buffer
   drawing remains outside the queued sampler. The host validates the mapped
   diagnostic ID and original result identity independently, with the same tag.
3. The official buffered-command documentation at reference commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   `docs/vdp/Buffered-Commands-API.md`, confirms that writes to buffer 65535
   discard their payload; CLEAR 65535 instead clears all buffers and is not
   permitted as a substitute. The diagnostic admission detail comes from the
   selected project-owned P4 source, not the stock API documentation.
4. Revised binaries and shared launchers use fresh SD filenames. Each final job launcher selects its directory inside one explicit MOS batch;
   separate host CD/EXEC commands were superseded after uncertain handback. Existing fixture assets/configurations, renderer firmware and
   frozen package identities remain retained. The first failed SD result is
   archived under a distinct filename before a fresh smoke attempt.
5. Partial staging continuation used retained whole-file-readback receipts
   plus current on-card sizes under exclusive bench ownership. The activation
   interrupted during the previous session received an independent full
   readback. Every new upload still receives a complete readback; neither
   outstanding requests nor the directory-creation batch are replayed blindly.

## Current preparation boundary — 2026-10-13

The original 743-file deployment and subsequent 80-file repaired binary/launcher
additions are fully verified. The optimized RGB888 control remains installed.
The first repaired smoke was explicitly invoked but produced neither a new P4
window nor foreground listener handback within its observation window. The
host stopped without reset, replay or further keyboard commands. Read-only
inspection cannot establish the actual foreground application or CLI state;
idle metadata access also returned unavailable. The Author subsequently restored the bench and manually selected Legacy.
The agent restored the original keyboard-only startup with full readback and
actual listener EXIT, without resetting or launching a fixture. Temporary
mode setup is being corrected to finish in Legacy. Sixteen short RGB888 receipts and its mode-0 green/red SELF-TEST readbacks
subsequently passed. The Author then reported vertical squashing; execution
is stopped pending HDMI-003. The 80-smoke admission and completion
banner checks are unfinished; no ready plan or full campaign is claimed.

## Decision register

### MQD01 — Mode-3 HDMI output aspect — transferred

The Author authorized a separate diagnosis and correction task on 2026-10-13.
[HDMI-003](../HDMI-003.md) owns the evidence, presentation decision and repair;
its H03-D01 register replaces this open decision. The unscaled source mapping
and 640×240-in-684×384 metadata are confirmed findings, but matching them to
the Author's visible report remains part of diagnosis. Benchmark preparation
stays stopped until the corrective task provides an appropriately verified
comparison pair. No specific output-scaling algorithm is accepted by this
transfer.

## References

1. [Current optimization contract](NURPLES-PERFORMANCE-R01.md).
2. [Renewed results](NURPLES-PERFORMANCE-R02-RESULTS.md).
3. [Test execution](../../procedures/test-execution.md).
4. [Bench constraints](../../qualification/bench-constraints.md).
5. Official `agon-docs/docs/vdp/Screen-Modes.md`: mode geometry, colors and
   supported double buffering. Reference checkout remains read-only.
