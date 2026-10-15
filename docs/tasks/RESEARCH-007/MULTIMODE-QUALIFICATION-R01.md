# Focused multi-mode rendering qualification

The Author selects stock modes 0, 3, 8, 20 and 136 for the next qualification
round. One host master runner owns sequential execution, durable collection
and the final persistent Extender display cue. Existing mode-20 evidence is
retained; the current frozen fixtures are not qualified for other geometries.
The runner and 40 per-mode fixture derivatives compile and pass offline checks.
The predecessor package retains sixteen data-valid short RGB888 receipts.
The correction tracked in [HDMI-003](../HDMI-003.md) restores stock mode-3 row
aspect; the Author confirms that its indexed diagnostic box looks square.
All eighty corrected-pair short admissions now pass, with matching deterministic
trajectories within each mode/workload. Both mode132 bank controls and all
mode0/136 green/red banner controls pass. Physical collection handback and the
safer staged startup replacement pass hardware checks. The Author invoked the full master. All 240 runs have finished, and copied-card
raw validation now passes for all runs and all 120 paired trajectories. The
[full results](MULTIMODE-RESULTS-2026-10-13.md) separate queued rendering from
application pacing and record regressions. Startup restoration and safe listener
handback passed. Final hardware notification remains unissued; the missing
execution-finished/awaiting-collection cue is a host-runner omission to correct.
No release promotion or broader visual/gameplay acceptance is claimed.

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

### MQ02 [x] Qualify reusable fixtures for the five geometries

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

### MQ03 [x] Prepare admitted mode and firmware transition adapters

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
5. Prepare an explicit deferred-collection path for operator-assisted SD-card
   results when the Author is available. Retain P4 windows and identities during
   execution; keep raw-data receipts pending until copied results validate.
   Withhold the success cue while awaiting collection. Preserve a separately
   authorized serial fallback. The adapter now supplies this explicit optional
   workflow; short admissions retain immediate serial validation.

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
5. Correct the deferred-collection handback notification: after execution and
   safe restoration, leave an explicit persistent execution-finished/results-
   awaiting-collection message and print the same phase to the host terminal.
   Withholding a success cue must not mean silence. Final success/error follows
   raw validation. Refresh future runner inputs without rewriting the frozen run.

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
was stopped pending HDMI-003. The 80-smoke admission and completion
banner checks are unfinished; no ready plan or full campaign is claimed.

The Author subsequently confirms the corrected indexed mode-3 diagnostic box
looks square. Both renderer variants pass bounded mode-0/3 hardware checks and
full source/artifact verification at clean source `c788b668`. Fresh preparation
uses the same frozen r02 fixture bytes with new campaign result paths and exact
corrected renderer manifests. Repeat all 80 short admissions and labeled banner
checks for the new pair; predecessor receipts cannot satisfy the new gate.

The fresh setup-only directory batch created every required directory but did
not return the listener. The Author recovered with one Agon reset. Fresh input,
actual CLI/listener and unchanged ordinary startup readback passed; inspection
found all 367 required directory paths present, with none missing. Continue only
payload deployment, preserving that informative handback failure and avoiding
directory-batch replay. The Author's standing Agon-first/P4-then-Agon recovery
order now governs subsequent monitored failures.

## Author stop and physical card collection — 2026-10-13

The Author stopped staging to avoid holding the shared bench and moved the
mainboard SD card to Oryx. All host preparation workers are stopped; the root
agent releases its bench reservation. Resume only after Author authorization
and a fresh bench/card ownership and state check.

Collected `autoexec.txt` and the complete `agents/extender/results` tree:
2,878 files, 42,374,958 bytes. Source SHA-256 checksums independently verify
every copied file. The host checksum/copy/extract/verification phase took
4.404 seconds; operator travel and card handling are excluded. The card files
were unchanged, and the selected card was unmounted after collection.
Exact host/mount identity, archive hash and receipts remain in ignored local
evidence under `agents/research007/card-collection/`.

The copy contains sixteen predecessor smoke results, no corrected-pair smoke
results and no full-campaign results. The earlier approximately 100-minute
figure estimates future serial result retrieval; it is not time spent
collecting an already-completed full campaign. Do not infer a speedup ratio
between that estimate and this different retained dataset.

The interrupted mixed-package staging checkpoint retains 235 verified entries;
an earlier fresh-package checkpoint retains 383. A pending read-only STAT
request remains preserved in its original SD journal. Do not replay it against
a changed card or listener incarnation. No test, firmware change, reset,
transaction cleanup or renewed SD deployment occurred during card collection.

When the Author is available, physical card collection is an authorized option
for large result sets. Ask directly in chat at a verified safe handback; retain
the files and integrity receipts, safely unmount the selected card, and keep
test execution separate from collection authorization.

## Offline result processing — 2026-10-13

[Processing r01](CARD-RESULTS-R01.md) revalidates sixteen predecessor smokes and
thirty selected mode-20 records against the copied card and frozen host
metadata. The newest corrected-pair comparison remains unmeasured. The control
file audit finds 562 matches, 80 missing indexed smoke files and zero mismatches;
maintained `/extender` fixtures were outside the collection scope. Offline work
is complete for this tranche. Stop for Author confirmation of SD-card access;
do not resume staging or probe a mount/bench automatically.

## Mounted-card staging completed — 2026-10-13

The Author mounted two identically labeled cards on Oryx and required correct
card selection. The host identified the previously collected card by its
filesystem UUID plus startup, retained smoke and fixture hashes. It verified
663 existing package files before writing only the 80 missing indexed smoke
files. Absence/recovery-sibling guards prevented overwriting existing files.

All 743 package files passed full length/SHA-256 verification after filesystem
sync. Ordinary 38-byte startup is unchanged, and all 320 smoke/full result paths
remain absent. The selected card was unmounted by its verified UUID; the other
card was neither written nor unmounted. Exact private identities and receipts
remain under ignored `agents/research007/multimode-r02/mounted-stage-r01/`.

This completes SD deployment, not hardware admission or full-suite readiness.
No bench command, firmware change, reset or fixture invocation occurred. Await
Author confirmation of card return and bench availability before live work;
preserve/reconcile the old read-only pending journal at the new incarnation.
All 80 corrected-pair short admissions and the deferred-collection host work
remain outstanding. The 240-measurement campaign stays unstarted.

## Card returned; preparation resumed — 2026-10-13

The Author returned the card to Agon and reserved the bench for this agent.
One commissioned Agon reset established fresh admitted input. A new explicitly
started foreground listener returned the unchanged ordinary startup and
acknowledged EXIT. The obsolete pending read-only STAT journal remains intact;
its request was not replayed into the new listener incarnation. Exact receipts
and the current reservation remain in ignored local records.

Corrected-pair short admissions and separate bank/banner controls are underway.
The 240 full measurements remain unstarted. The readiness boundary still
requires all short admissions, independently installed initial RGB firmware,
verified mode-0 setup and input/listener readiness, and a frozen ready plan.

The optional `physical-card` adapter path now retains invocation, P4 window and
before/after display sidecars with hashes, records raw validation as pending,
and omits per-job raw downloads. The master records `awaiting_collection`,
restores ordinary startup and acknowledges listener EXIT through its separate
`park` adapter. It withholds analysis and completion banners at this boundary.
The operator must receive an explicit safe-removal report before taking the card.

`scripts/collect_render_qualification.py RUN --card-root COPIED_CARD_ROOT`
validates copied raw files offline against the frozen package and retained
sidecars, including deterministic RGB/indexed trajectory matching. It preserves
execution receipts and prepares every validation product before replacing run
receipts. Missing/corrupt raw results become retained validation failures and disqualify
their matched comparisons. Altered execution receipts/sidecars stop collection; an
interrupted/failed collection is retained for explicit investigation, not
silently resumed. Successful collection records `validated_awaiting_notification`; completed
collection with data failures records `collected_with_errors_awaiting_notification`.

After the card returns and separately authorized bench admission is established,
`scripts/run_render_qualification.py --notify-collected RUN` verifies collected
receipt/raw hashes, performs analysis and invokes the final persistent success
or error banner according to the validated receipts. This is an explicit operation, never an offline collection side effect.
A notification interruption is retained and never automatically replayed.
The serial path remains available only through its explicitly selected plan.

Offline tests cover deferred receipts without raw downloads, withholding passes,
analysis and success cues, sidecar tampering, raw-data failure and its paired-comparison failure, and complete offline collection. This host work is preparation;
it does not establish hardware admission or authorize the full campaign.

## Startup handback failure; card inspection needed — 2026-10-13

Forty-eight corrected-pair short admissions passed: all forty RGB jobs and the
first eight indexed jobs in mode 0. Both renderer mode132 bank controls passed.
RGB mode0/136 and indexed mode0 labeled green/red banner readbacks also passed.
No full measurement was invoked.

The first indexed mode3 job failed during preparation, before its invocation
record or fixture command. The inherited helper had issued MOS RENAME to move
`/autoexec.txt` into its retained startup backup, then failed to re-enter the
listener. Actual on-card rename completion remains unconfirmed. A subsequent
Agon reset did not establish fresh input admission. The standing second attempt
verified P4 reset and initialized services, then reset Agon; input admission also
failed. No worker or fixture remains active. Card inspection and restoration of
the ordinary keyboard-admitting startup now require operator card access.

The maintained adapter now archives the old startup and uses the listener's
existing staged replacement instead of removing startup through MOS RENAME.
It independently reads the activated target and transaction backup before
cleanup. Uncertain activation preserves the journal and backup. Focused host
tests pass for keeping the listener/old startup through staging and retaining
recovery evidence on uncertainty; physical validation remains pending.

Retain all forty-eight passing receipts and the informative pre-invocation
failure. Do not replay the original smoke controller or completed jobs. Resume
through an explicit continuation that verifies retained receipts, admits only
unstarted jobs, and preserves the full-suite stop-before-invocation boundary.
Exact current state, reset evidence and card identity remain in ignored records.

## Mounted-card startup repair — 2026-10-13

The Author mounted both cards on Oryx and powered down the bench. Exact card
identity, retained startup-backup hash and latest indexed smoke result hash
identified the Agon card. Inspection confirmed `/autoexec.txt` absent and no
startup recovery siblings. The saved mode0 startup matched the pre-failure
readback: MOS RENAME had completed before the listener handback failed.

Restored only the original 38-byte keyboard-admitting startup with guarded
creation, filesystem sync and complete SHA-256 verification. The selected card
was unmounted by its verified UUID. The other card remained untouched and
mounted. Existing backup and result files were preserved. No bench operation,
reset, flash or fixture invocation occurred; the bench remains powered down.

Resume hardware preparation only after card return and power availability.
Forty-eight short passes remain retained, thirty-two admissions remain, and the
full campaign is unstarted. Fresh input/CLI admission and physical verification
of the safer startup replacement remain necessary before readiness.

## Full-suite readiness; stopped before invocation — 2026-10-13

All eighty corrected-pair short admissions passed, with identical trajectories
for all forty RGB/indexed mode/workload pairs. Both mode132 bank controls and
all renderer mode0/136 green/red banner controls passed. The revised staged
startup replacement passed physical mode transitions and collection restoration.
The collection handback control restored and verified ordinary startup and
acknowledged listener EXIT, then reopened the listener for initial setup.

The corrected optimized RGB firmware was independently installed and verified
again. Initial mode0 setup-only startup ends in Legacy; fresh input admission,
actual CLI/listener readback and neutral input are verified. All 240 full-result
paths are absent. The frozen ready plan passes the maintained master's offline
240-job/input-integrity check. Exact identities and receipts remain in ignored
local records. Seventeen focused host tests pass.

The agent stops here, with no active preparation worker and no full fixture
invoked. The initial idle foreground listener remains available to the master.
The selected collection path defers raw downloads to physical-card collection
and withholds the final success cue until offline validation and explicitly
admitted notification. Coarse full execution/setup guidance is 2–3 hours plus
operator card handling/collection, based on retained predecessor mode20 runs;
the approximately 97-minute serial retrieval estimate is a separate fallback.
These estimates establish neither deadlines nor additional authorization.

## Master owns initial listener admission — 2026-10-13

The master now invokes the plan's initial admission adapter before any fixture.
With the Author-confirmed CLI precondition, the adapter starts the foreground
listener if offline, verifies startup readback and positive EXIT, preserves the
old journal, binds a fresh session and reopens the listener. An idle online
listener is reused through its canonical journal. Pending operations or uncertain
requests stop admission without resets, discarded journals or fixture launches.
The master requires a validated admission receipt before advancing to job one.

The prepared plan includes this adapter; the existing SSH launch command is
unchanged. Twenty-one focused host tests and the refreshed plan integrity check
pass. This change was verified offline without bench access or campaign launch.

## Full run processed — 2026-10-13

The Author reports execution stopped without a clear completion message and
mounted the Agon card on Oryx. Host summary confirms all 240 jobs finished in
8768.544 host seconds (146.14 minutes), followed by successful startup restoration
and listener EXIT. The actual run includes the improved master's admission step.

Collected all 240 raw result files plus ordinary startup from the exact identified
card: 241 files, 5,733,158 bytes, all source SHA-256 hashes verified. Copy/hash/
extract/verify took 1.900 seconds approximately, excluding operator handling.
The selected card was safely unmounted; other media were untouched.

Offline collection validates all 240 runs and 120 same-repeat trajectory pairs,
with 237,600 measured updates and zero checked output-error deltas. Performance
budget overruns remain measured outcomes, not invalid data. The analyzer produced
40 matched mode/workload comparisons. See the full results report for all tables,
scopes, exact firmware identities and limitations.

The deferred path correctly withheld final success before raw validation, but
omitted the separately needed execution-finished/awaiting-collection message.
Record this as a notification defect, not an incomplete measurement campaign.
Current state is validated-awaiting-notification. No bench call or final display
occurred during processing; card return and fresh admission are required before
any separately authorized hardware notification. Future cue correction remains
MQ04-5; preserve the completed run's pinned source and evidence.

## Visual follow-up gates

1. Mode20 Nurples: Author says all observed runs looked pretty good. Keep
   indexed/software as the timing winner only; verify software sprites near
   the top edge before treating it as the preferred visual/gameplay variant.
   Retain the Author's prior hardware-sprite flicker improvement as scoped
   historical evidence. This is not production-bundle acceptance.
2. 16-colour derivatives: Author reports severe background and sprite flicker.
   Selected 16-colour modes are 0/136; individual observed run identities were
   not specified. Diagnose with explicit mode/renderer/run identity and compare
   background drawing, sprite visibility and bank/pacing separately. Do not
   translate 240 valid timing records into a visual pass or launch a rerun merely
   from this recorded observation.

## Decision register

### MQD01 — Mode-3 HDMI output aspect — transferred

The Author authorized a separate diagnosis and correction task on 2026-10-13.
[HDMI-003](../HDMI-003.md) owns the evidence, presentation decision and repair;
its H03-D01 register replaces this open decision. Stock row repetition is
restored in a verified comparison pair, and the Author confirms the indexed
mode-3 box looks square. Benchmark preparation resumes through fresh short
admission checks. This transfer and visual observation do not accept a
production bundle or authorize the full campaign to start.

## References

1. [Current optimization contract](NURPLES-PERFORMANCE-R01.md).
2. [Renewed results](NURPLES-PERFORMANCE-R02-RESULTS.md).
3. [Test execution](../../procedures/test-execution.md).
4. [Bench constraints](../../qualification/bench-constraints.md).
5. Official `agon-docs/docs/vdp/Screen-Modes.md`: mode geometry, colors and
   supported double buffering. Reference checkout remains read-only.
