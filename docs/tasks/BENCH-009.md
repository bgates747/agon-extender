# BENCH-009 — Deterministic rendering load suite

## Executive summary

The Author authorizes a frozen deterministic benchmark contract and goal-driven
implementation and execution, with the Pi/Agon/P4-PC bench available for firmware
flashing, SD deployment and resets. Compare identical application workloads on
mainboard VDP and P4 HDMI, progressively increase rendering load, and distinguish
application-visible completion from drawing and presentation. This is experimental
measurement work, not production qualification or a rendering optimisation.

**Long-campaign state — paused by the Author on2026-10-05.** Finish downloading the
obtained results, then stop and discuss the campaign size and findings. The last
mainboard mode8 pass2 download and validation are complete; both host controllers
have stopped. No further full-campaign test or automatic restoration follows.
The frozen campaign is incomplete and requires an explicit Author resumption.
The Author subsequently authorizes the bounded supplemental static-colour
conversion control below; that does not resume the long workload campaign.
That supplement is now complete: all five charts pass Author visual review,
all five corrected no-scanout controls pass, and ordinary P4 r03 plus the exact
pre-task startup have been restored and independently verified.

The separately authorized [RGB888 experiment](RGB-001.md) has finished its
bounded22-combination measurement windows and restored ordinary firmware/startup.
All88 matched raw results now validate. It does not resume the full campaign. The
Author additionally requests permanent resident fixtures and local-card result
collection under B09-09/B09-10 below. The foreground SD listener and pending jobs
are closed for the Author's card handoff.

The current normative contract is [render-load-r04](../testing/render-load-contract-r04.md)
and its machine-readable [definition](../../tests/performance/render_load/contract-r04.json).
Freeze their exact bytes before implementation. Retain source/build/installed-image
identities, startup preservation, failed cases and raw measurements. Do not silently
change the contract to accommodate a result; revisions must preserve prior evidence.

## Scope and dependencies

1. [HDMI-001](HDMI-001.md) owns the output adapter and unresolved sprite flicker.
   This task supplies controlled measurements without changing ordinary rendering.
2. [BENCH-007](BENCH-007.md) supplies timer/measurement precedents, but its historical
   runners and old startup paths are not executable plans for this bench.
3. The current EMOS owns Legacy/ExCom VDU routing and input admission. The same
   eZ80 fixture calls counted MOS output; it never drives UART, GPIO or routing
   registers. Mode selection occurs only in `/autoexec.txt`, before invocation.
4. Mainboard VDP remains its current ordinary image. P4 diagnostic firmware derives
   from the current r03 source with optional timing/controls. Official reference
   checkouts remain read-only. Do not routinely back up device firmware; preserve
   existing images/source and verify deliberate deployments.
5. Read the ignored local bench record, active bench constraints and SD layout
   before operations. Keep maintained fixtures under `/extender`, results under
   `/agents/extender/results`, and restore startup byte-for-byte at closeout.

## Decision register

| ID | State | Frozen decision |
|---|---|---|
| B09-D01 | Author delegates freeze/implementation | Separate reusable suite from HDMI integration; no game modifications. |
| B09-D02 | Frozen r04 | Pre-generated integer, fixed-seed VDU frames; no per-frame asset loading or SD writes. Equal workload bytes across targets. |
| B09-D03 | Frozen r04 | 8 warm-up frames, indefinite repeated templates, Space/ Escape controls and timed script advances; three paired passes, actual-frame rates and retained failures. |
| B09-D04 | Frozen r04 | Common pixel-reply drawing fence; paced and throughput tests have separate labels. Do not call UART acceptance drawing completion. |
| B09-D05 | Frozen r04 | P4 phase telemetry and diagnostic window markers are optional; quantify instrumentation/visible-marker overhead with controls. |
| B09-D06 | Frozen r04 | Mainboard physical frame delivery is unavailable without independent video capture. Never infer it from a fence or P4 DMA count. |
| B09-D07 | Frozen r04 | Compare full HDMI, held HDMI with conversion suppressed, and native render-only with scanout absent; clearly report timing-source/resource differences. |
| B09-D08 | Author direction,2026-10-05 | Keep a bounded known-working representative fixture selection permanently on SD; reuse exact installed files rather than transfer executable/data for each run. |
| B09-D09 | Author direction,2026-10-05 | For the active RGB888 subset, run measurements first and leave bulk results on SD; the Author will move the card to the Pi for local collection afterward. Closed telemetry alone is not a validated result. |

## Subtasks

### B09-01 [x] Research and freeze the contract

Pin official documentation/source and current component identities. Resolve mode,
completion, timer, sprite and marker semantics. Freeze contract hashes and record
known measurement limits before code changes.

### B09-02 [x] Implement deterministic fixture generation and application

Generate bounded payloads/manifests, use one generic eZ80 executable, validate
mode and payload bounds, retain per-frame submission/completion/pacing clocks,
checkpoint results outside timing, and provide explicit error/overflow records.

### B09-03 [x] Add bounded optional P4 telemetry and output controls

Measure drawing-drain wall time, native-row lock waiting/composition, RGB888
expansion, cache submission and complete output updates independently. Add no
per-frame logging/network operations. Window markers use the existing discarded
buffer carrier identically consumed by mainboard. Keep ordinary builds unchanged.

### B09-04 [x] Qualify clocks, barriers, controls and recovery

Run meaningful host validation and real pilot cases on both endpoints. Check
timer saturation, completion reply, exact payload/result readback, telemetry
correlation, readiness and startup restoration. Measure preparation/runtime/
retrieval separately; use retained pilot timing for later duration estimates.

### B09-05 [ ] Execute paired progressively loaded suite

Run frozen cases and repetitions on both endpoints, including single/double
buffer pairs. Alternate endpoint order by pass. Mark failures, recover, continue
independent work and rerun affected cases without timing instrumentation where
applicable. Do not replace controlled workloads with interactive gameplay.

### B09-06 [ ] Execute P4 output controls and analyse

Replay modes20/8 with conversion held and with scanout absent. Rank worst
performance first, show mainboard/P4 units and explicit baseline/percentage
differences for comparable metrics. Separate application, drawing, conversion
and scanout. Report medians, ranges/tails, missed budgets, failures and limits.

### B09-07 [x] Restore bench and publish current usage/results locally

Restore exact pre-task startup and ordinary P4 r03 image; verify EMOS admission,
HTTP and final mode/readiness. Record results, implementation gotchas and current
operating instructions in durable role-named locations. No commit, production
promotion or remote publication is implied by this benchmark authorisation.
Completed at the supplemental closeout on2026-10-05. A resumed campaign must
perform restoration again before its own closeout.

### B09-08 [x] Measure fixed-source conversion with and without scanout

Draw each mode's complete palette once, obtain Author visual acceptance, collect
three ten-second windows with scanout active and absent using identical fixture
bytes, exclude invalid controls, and retain provenance and an offline report.

### B09-09 [x] Establish the permanent resident selection

Authorized independently of the paused long campaign. Pin the already-tested
render-load-r04 executable/data for20/8/136, the22 selected mode/case combinations,
all five passed colour charts and the passed familiar-art binaries (r01 for20/8,
corrected r02 for136). Document controls and bounded acceptance in the durable
[resident guide](../testing/resident-render-suite.md), with a machine-readable
catalogue. Preserve exact bytes; omit the defective r01 mode136 visual check.
Verify the catalogue against the mounted card after the active run finishes.
Record one installation receipt; future runs change tiny plans/startup only.

`resident-render-suite-r01` now pins12 existing files; exact prior staging/readback
proof covers every selected file. The bounded RGB888 runs and restoration have
finished. The remaining gate is fresh verification against the Author's mounted
Agon card; no executable or asset redeployment is required for an unchanged card.

### B09-10 [x] Validate deferred local-card collection

Preserve result directories on SD and correlated P4 telemetry on the Pi. After
RGB-001 restores ordinary firmware/startup and closes card use, let the Author
move the card to the Pi. The read-only collector must enforce raw identity,
checkpoint order, frame count/error/truncation and telemetry correlation before
changing a pending outcome to pass. Preserve conflicting/missing evidence and
the original deferred receipts. Regenerate the bounded RGB888 report only after
collection; do not resume B09-05/B09-06 or infer full-campaign completion.

## Bounded research précis

1. Official VDP v2.16.0 is `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, MOS v3.0.2
   is `8336409351ee5314e02801a7b72a4f1bb5282519`, docs are
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. VDP/MOS are clean references.
2. [Screen modes](../../../../agon-docs/docs/vdp/Screen-Modes.md) excludes148;
   compare20/8,8/136 and21/149. Mode selection must be verified, not inferred.
3. Official `video/vdu_sys.h::sendScreenPixel` calls `waitPlotCompletion()` before
   returning pixel data. `video/agon_screen.h` delegates that fence to Canvas.
   A reply establishes prior ordinary drawing completion plus round-trip cost;
   it does not establish physical scanout or recurring hardware-sprite cost.
4. [Bitmap/sprite API](../../../../agon-docs/docs/vdp/Bitmaps-API.md) defines RGBA2222,
   software/hardware sprite selection, move and refresh semantics. Explicitly
   identify sprite kind; refresh once after all sprite moves.
5. [MOS API](../../../../agon-docs/docs/mos/API.md) documents sysvars, counted output,
   pixel reply flag, loading and file operations. Its centisecond wording for
   sysvar_time is misleading at60Hz: `src/interrupts.asm` increments by2 per
   mainboard vblank, giving120 raw units/s at60Hz, with16.67ms granularity.
   Calibrate against PRT1 and host wall time; never use100 CLOCKS_PER_SEC.
6. PRT1 uses the existing BENCH-007 register precedent with /256 for this suite:
   nominal72,000 counts/s,13.889µs/count and0.9102s single-pass saturation. Leave
   PRT0, source selector, IRQ vectors and normal interrupts unchanged.
7. The VDP buffered-write carrier with buffer65535 consumes and discards payload
   in ordinary firmware. Existing project trace hooks use this boundary. Optional
   benchmark hooks use a different bounded magic; no new ordinary VDU bypass.
8. IDF5.5.5 and Olimex bridge dependencies remain pinned as in HDMI-001. On P4
   v1.3 DMA frame completion is a scanout proxy, not a true-vsync event. No PPA,
   LVGL, new palette/Copper behavior or renderer optimisations are included.

## Historical r01 freeze receipt

Frozen 2026-10-05T02:50:45Z, registry r130. Contract Markdown SHA256
`9899fe369b01a0dcfe3100566af466c8e05b7b4b88fbb3ef976749aec5816da9`;
JSON SHA256 `5df6680d749b115d42253463269d0cf15d7f5bc684d00b0fbe9c4ba763a464e9`.
Implementation and bench runs remain pending.

## Implementation notes

1. The Pi-native assembler is built in ignored project-local tooling from
   `agon-ez80asm` commit `5dc733c286b7864e3eb05ef93462c7e1637ba51e`;
   the migrated x86 binary is unsuitable.
2. An incidental P4 restart requires an Agon reset to renew EMOS admission.
   A visible P4 cursor and HTTP keyboard readiness alone do not establish an
   idle SD-service poll. No rejected mutation is blindly replayed.
3. Current card support roots were absent. The SD utility deliberately refuses
   NEW mutations of exact `/extender` and `/emos` roots, including MKCOL.
   Bootstrap `/extender` through the admitted MOS CLI, then use ordinary
   WebDAV for its child fixture directory. This preserves the service contract.
4. Keep a short gap between completed finite SD jobs during preparation.
   Fixture timing contains no SD or network calls; startup changes MOVE the
   prior file into task-owned evidence before PUT to an absent target, avoiding
   unresolved replacement backup siblings.

## Preparation progress

The generator emits94 cases/mode (all40 frames preloaded, <65,536 bytes/case),
with exact JSON/frame hashes. Native ARM assembly and host deterministic/bounds
checks pass. The P4 normal and hold builds pass full source snapshot, compile and
link validation. The real StockP4Service scheduling regression and optional
telemetry boundary/probe-control tests pass. No performance runs yet.

A checked SD upload of the1.17MB raw mode stream was deliberately cancelled
before response after small transfers showed slow service. Keep unresolved
staging; do not blindly replay. Hold output is selected for preparation to
remove RGB conversion interference, with normal output restored for paired P4
measurement. Untimed LZ4 packing was prepared and round-trip checked as a
fallback; it is not part of the executable or measured workload.

P4 hold control is installed. The write tool verified the entire merged image;
independent bootloader/application/partition digests match. Initial OTA metadata
changed after boot, as IDF5.5.5 `bootloader_utility.c::set_actual_ota_seq` writes
its selected slot when no factory partition exists. Future deployment checks
verify all four segments before allowing boot; do not treat this expected
metadata initialization as firmware corruption or bypass application verification.

## Author execution revision — 2026-10-05

The Author requires longer measurements and visual fixtures that repeat until
Space advances or Escape exits. The same fixture is automated through admitted
keypresses at wall-clock intervals. r02 preserves the workload definitions and
r01 evidence; its exact hashes are recorded below. Normal automated windows
are10seconds with a20second startup allowance; fewer than64 frames require an
explicit longer rerun. Source/build and actual window durations remain part of
each receipt. Indefinite visual operation is separate from automatic measurement.

docs/testing/render-load-contract-r02.md: `e3590f2337c1cb29664798302616d58d5563fba8bf57ed14c2fea0dffa1d0644`
tests/performance/render_load/contract-r02.json: `f4d2fc21769dd919cba891a6ccfec216c91ea3bf785324865413da1d70a74883`

The first r01 mainboard and held-HDMI pilots both passed two cases/64 measured
frames, matching mode20 geometry and clock calibration without saturation. P4
windows matched tags and closures. Fast pilot deployment took2.09s upload and
2.91s for its single readback (6,969bytes). These are qualification checks only.

## r03 memory qualification correction

The first continuous prototype wrongly allocated records outside module-safe
Agon user RAM. Diagnostic unpacking bounds matched, but the pilot produced no
valid case checkpoint. r03 freezes the documented0x040000–0x0AFFFF limit and
a31,402-record two-region allocation, reusing untimed unpacking buffers only
after case restoration. It preserves the user-requested indefinite controls
and repeated workloads. Record truncation remains explicit.

docs/testing/render-load-contract-r03.md: `a97a30e15199a1cfd5ef3d3ee1f8e2d3a2d09d3a8f202857a7c42c4a8c8e10e4`
tests/performance/render_load/contract-r03.json: `0a7dff869da242cb06ebc758e5ca11f243c5413a161e83b7abfb7816b9737bf9`

## Continuous pilot and recovery results

Mainboard mode20: paced671 frames/11.183s, throughput11,775 frames/9.850s.
Held-HDMI P4 mode20: paced668 frames/11.133s, throughput16,112 frames/9.800s.
No saturation/fence failures, exact deployed/readback hashes and closed matching
P4 windows. These are static clock/control qualification, not rendering-load
rankings or physical displayed FPS. The P4 throughput case exercised both
record RAM regions.

A subsequent startup lost P4 keyboard admission before a fresh benchmark
window. Preserve that failure; no Escape result was inferred. After verified
P4 reinstallation and Agon reset, Escape closed/checkpointed the active case
and returned to the fast listener. Admission failure cause remains unproven.
Independent flash verification now uses USB reset to enter the bootloader
before verification, then hard reset to boot; esptool5.1.0 no-reset opening
left unsuitable DTR/RTS state despite all four segment digests matching.

Current usage lives in `docs/testing/render-load.md`. Full workload deployment
and paired/control measurements remain pending. No production promotion.

Author is unavailable for visual inspection or physical bench intervention
until morning (2026-10-05). Continue authorized automated work, preserve
failures and leave visual acceptance pending; this is not a goal pause.

## Full-stream qualification and controller corrections

All five packed mode streams were fast-deployed and verified once by full-file
readback. Total deployment time was810.71s; each packed stream is247–253kB
and restores the original1.17–1.18MB VDU bytes exactly. Normal HDMI firmware
was independently verified across all four flash segments before boot.

The first normal-HDMI full-stream subset completed its two selected static
windows (681 and12,709 frames), then failed while decoding an unselected empty
control later in the stream: I/O error5, stage9, raw length108. The eZ80 unpacker
wrongly rejected a zero drawing length. Zero-length frames now restore their
forty length words and skip delta columns. Counted MOS output also explicitly
skips a zero byte count, because RST18 with BC=0 otherwise means a terminated
string and can read beyond the final empty frame. No frozen drawing bytes change.
Retain the error receipt, checkpoint, telemetry and corrected build identities.

Guarded restart preserved the checkpoint and rendered an existing-result message
at the ExCom CLI. Automatic SD admission nevertheless returned503: this boot
had entered ExCom directly from startup and had never negotiated Legacy SD
capabilities. `emos_admission_idle()` deliberately forbids that bootstrap in
ExCom. A503 alone therefore cannot establish that RUN is active. The controller
now uses the rendered benchmark error plus MOS prompt as positive CLI evidence
before requesting EMOS Legacy and starting the fast listener. Keyboard readiness
and closed phase windows alone remain insufficient. No ordinary EMOS routing or
transport contract changes.

The normal pilot measured60Hz DMA completion and roughly26–27 complete
conversions/s, with RGB888 expansion dominating conversion wall time. This is
static pilot evidence only; it is not a workload ranking or physical monitor FPS.

The corrected four-control P4 pilot passes: cases90–93 recorded1,606/23,353/
498/16,125 frames, with no short/truncated/failing records and all matching
windows closed. Disabled timing produced no phase calls. Retrieval of499,208
bytes took297.89s; fixture startup/execution/return took76.87s, separately from
18.96s preparation. The r03 normal-HDMI campaign was subsequently superseded; its partial results remain evidence.

The SD-only archival utility initially built for silicon3.1 despite a requested
minimum1.0: IDF5.5.5 requires `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y` before the
old-silicon minimum choice is admitted. Its bootloader failed before application
execution. Ordinary benchmark firmware was independently restored and bootstrap
readiness verified. The corrected utility and bootloader headers both declare
1.0–1.99; deployment helpers now reject incompatible image ranges before bench
mutation. The corrected archival utility subsequently passed in a confirmed gap between campaigns. The failed
utility is not benchmark failure evidence or a new chip defect.

## r04 sprite qualification and preserved failures — 2026-10-05

The official selected-sprite API applies hardware/software selection and paint
mode to the current sprite. The r03 generator configured the kind only once;
r04 explicitly configures every active sprite and deactivates old sprites before
resetting their frame lists. Setup is untimed. All 18,800 generated per-frame
streams across the five modes match r03 byte-for-byte. No prior sprite result is
relabeled as an r04 comparison.

Frozen at 2026-10-05T05:55:22.070135Z, before changing implementation:

| Contract | SHA-256 |
|---|---|
| `docs/testing/render-load-contract-r04.md` | `2e0061139a3f620481377c6089c51627c922bb66c5d2d5c9152f04fd02d46396` |
| `tests/performance/render_load/contract-r04.json` | `8843965a47b40e8571efb4efb0269b10ba8d8b6eff487953a5a729aec2dd177c` |

The first full r03 mainboard mode20 attempt retained 43 complete cases, then
failed its warm-up drawing fence entering case43. Its cause remains unproven;
this setup correction is not evidence that the failure is fixed. The subsequent
continuation was deliberately stopped once the generator defect was identified.
Both runs and prior contract/source/payload identities remain retained.

The corrected SD-only utility independently verified the sealed interrupted
upload's record ownership and digest, renamed the owned P4 spool into its result
archive, and recreated an empty spool. It reported `ARCHIVE PASS`; no card was
formatted and no file was deleted. The ordinary normal-output diagnostic image
was independently restored across all four flash segments, followed by verified
EMOS bootstrap/listener readiness. The initial incompatible utility failed before
its application ran; its concise silicon-selection lesson remains recorded.

The r04 executable is installed and hash-verified. Five revised packed streams
are being deployed using fast transfer and one untimed full readback per file.
Qualify sprite boundaries on both endpoints, then run the frozen three-pass
paired and output-control campaigns. The Author is asleep: automated operations
remain authorized, while physical visual review and interventions wait until morning.

Duration evidence: the r03 mainboard partial run took 23.30s preparation,
456.38s fixture execution/return and 732.69s retrieval. The complete frozen
campaign contains 3,948 case executions; nominal fixture windows alone total
about 11 hours, before preparation, recovery and retrieval. This estimate does
not authorize an implicit reset or replace explicit run deadlines.

Host checks after the r04 setup correction: deterministic generation, lossless
packing, RAM bounds, per-sprite selected-API semantics and continuous result
validation pass (five tests). Python compilation and analysis checks against
retained real pilot records pass, including baseline percentage signs, explicitly
incomplete paired passes and marker/timing controls. The general version-record
validator still fails on the pre-existing light2-harness-r02 connectivity hash;
that unrelated controlled wiring profile was not changed for this task.

All five r04 packed streams now pass their single full readback (990.91s total
preparation transfer time). The local owner has started sprite-boundary
qualification, followed by individually receipted mode/pass groups for the
normal, held-conversion and scanout-absent variants. Each group retains its own
failures and analysis; no timed SD work occurs. The owner releases and reloads
foreground listener journals when handing control to the maintained runner,
and records final ordinary-image/startup/readiness restoration separately.

The r04 mainboard sprite pilot passes cases42–57: all16 checkpoints, no fence
errors, short samples or truncation. It includes the previously failing case43
boundary but does not isolate the cause of the r03 failure. Preparation took
21.56s, fixture execution/return176.87s and retrieval165.29s. Its raw result
SHA-256 is `ca4feb1b7b4282918990957f2c9cf5e98f1d5c14f77dcda527cc3e14284f3587`.
The matching normal-HDMI P4 pilot is underway. These are qualification records,
not three-pass comparison rankings or physical frame delivery measurements.

The matching r04 normal-HDMI P4 mode20 sprite pilot passes all16 cases, with
closed matching tagged phase windows and no short/truncated/failing samples.
Preparation21.14s, execution/return178.73s and retrieval193.93s. Raw result SHA-256:
`e6b9d06e63782c44a6ddb0ff6d21e20a1138c4dae66dfaf3b986459784ca9f89`.
P4 double-buffer mode136 cases42/43 also pass (568/580 frames), with both windows
closed and matching. Preparation20.78s, execution/return36.14s, retrieval6.45s;
raw SHA-256 `17cb7f7572662d2a23b8daba9a8129c7b7e6d39e83f2997095481193cf093c75`.
Clock/barrier/control/recovery pilots are complete; output-off cadence is checked
as part of the pending output-control campaign. The full first normal mode20
paired pass has started. No physical visual acceptance is inferred.

## First r04 full-pass failure and control history

The first full mainboard mode20 pass retained72 complete cases (IDs0–71), all
without frame errors, short sampling or truncation. Its next case72, hardware
sprites with64-way overlap, failed an untimed warm-up drawing fence: code4,
decoder stage9, restored raw length30,194 bytes. The cause remains unproven.
The result is1,516,340 bytes, SHA-256
`f6e8a8ff2cb744c5f4313c933698ef5bca252839c44063de44674d250948ddd7`.
Execution/return745.65s; retrieval786.96s. The controller continued from73
with a fresh startup/reset and retained the failed case for its control.

A matching control must replay the failed invocation's preceding case setup
order at its original key cadence, with timing probes suppressed. A fresh
single-case replay changes history and cannot distinguish diagnostic interference
from an earlier sprite-state dependency. The maintained runner now records that
prefix/context before invocation. The already-running first group loaded its
older controller before this correction; retain any isolated replay as limited
control evidence and perform a supplementary matching-history replay at a safe
campaign boundary. Do not stop or restart the live job merely to load new code.

Reporting now audits all3,948 required case executions, rejects duplicate pass
selection, validates result identities/flags and P4 window correlation, and
retains incomplete/failing run metadata separately from valid prior checkpoints.
Hardware-sprite API commands also require a scope warning: the P4's RowCompose
performs their presentation composition in CPU code. Hold/off suppress it with
conversion; their hardware-sprite rows measure pose-command processing with
composition absent, not hardware-sprite rendering throughput. The ordinary
pixel-query fence omits recurring mainboard scanline composition as well.

The fresh mainboard continuation passes all21 remaining cases73–93, without
frame errors, short samples or truncation. This includes the64-way hardware
overlap throughput case, whose warm-up drawing bytes match case72. Startup and
preceding case history differ, so this is evidence of successful independent
continuation, not an isolated cause diagnosis. Its raw SHA-256 is
`167ea495e32930235c3958bbf0b9620e3dcf54068bc2ad8417da62dd6de51db4`.

Host recovery tests pass for preserving prior checkpoints, continuing after a
warm-up fence failure, replaying the failed invocation's entire setup prefix at
its original key cadence, and marking a missing P4 phase window for a control.
The full first P4 mode20 run is now active.

## Overnight campaign and reviewed continuation — 2026-10-05

The first normal-output pass attempted all five modes. The P4 retains all94
valid cases in each mode. Mainboard valid counts are93/94/64/94/62 in
modes20/8/136/21/149 respectively. Several mainboard sprite cases failed
drawing fences; matching-history timing-probe controls reproduce the failures
in modes136/149. This is not a rendering-cause diagnosis. The initial controller
also stopped those modes after three recovered warm-up failures, incorrectly
treating case-specific failure as global preparation failure. Preserve those
receipts; separately execute only their unperformed suffixes72–93 and70–93.
The maintained controller now continues independent cases after a recovered,
explicit warm-up fence failure. Explicit mode/load/timer failures and repeated
opaque preparation failures still stop the affected preparation.

Normal mode20 pass2 also finished with retained evidence:94 P4 cases and93
mainboard cases; mainboard case84 failed and its timing-probe control completed.
Analysis currently has1,064 valid unique scheduled executions out of3,948.
Controls and qualification records remain separate from that coverage count.

Mode8 pass2 stopped at its first scheduled key because P4 keyboard admission
was unavailable. Pre-reset telemetry contains only the preceding run's tag,
so no original measurement window is established. Recovery rebooted both
processors but sent Escape before the new fixture installed its callback.
Morning inspection found the new invocation still in case0 with input admitted.
An explicit Escape then returned to the foreground SD listener. Its31,299-frame
post-reset checkpoint is retained as recovery-only evidence, without assigning
it to the interrupted paired pass. The original failure and terminal receipts
remain immutable evidence; the admission failure's cause is unproven.

Recovery now requires this invocation's tagged active window before sending
Escape, and records the window/case. Ten host tests pass, including that startup
ordering, continuation without repeating a completed prefix, and continuing
after consecutive recovered warm-up failures. The frozen fixture, contracts,
measured VDU bytes and20s/10s measurement-key schedule are unchanged.

The reviewed owner resumes mode8 pass2 with a fresh group receipt and preserves
the stopped owner/group records. Completed groups are skipped. It additionally
owns the two unperformed mainboard suffixes and the previously required mode20
pass1 matching-history control before ordinary firmware/startup restoration.
Held-conversion/scanout-off comparisons and remaining paired passes are pending.

## Presentation attempts and ordinary-image controls

First-pass normal mode149 case0 is a useful separation: the eZ80 application
advances at60 updates/s,268 complete diagnostic conversion scopes average
35.176ms, and the tagged window records zero accepted HDMI framebuffer
submissions. Mode149 has81 zero-submission case windows in this pass; mode136
has one, case86. These are output outcomes, not missing application drawing
throughput. The diagnostic conversion scope closes on aborted publication as
well as success; its call count must not be described as completed output.

`HdmiOutput::publish` samples the native visible generation before its row pass
and rejects a double-buffer publication if a swap changes that generation
before it finishes. A35ms attempt can span multiple60Hz swaps. This is a source-
supported explanation candidate; no rejection-reason counter or physical video
observation has isolated the cause in these windows. Renderer changes remain
outside this measurement task.

The maintained analysis now exports matching-pass completion p95/ranges and
over16.667ms percentages, per-phase window aggregates, and exact zero-submission
run/case identities. Phase scopes have different granularity and overlap; do
not add their means or describe them as exclusive CPU time. Compare completed
submissions separately from conversion attempts and DMA frame completions.

After the scheduled campaign restores the ordinary r03 image, run supplemental
controls with its benchmark-specific hooks absent. The preparation verifies
the immutable compilation manifest and absence of benchmark definitions; the
runner also requires its verified installation receipt and a404 diagnostic
endpoint. Suppress eZ80 timing probes, preserve affected invocations' case setup
prefixes and20s/10s key cadence, retain ordinary serial output, then restore the
original startup and verify admission again. Freeze the selection from the final
zero-submission inventory before execution; the current draft selects mode136
cases0–86 and mode149 cases0–93. These records use a separate control-suite
identity and cannot silently enter paired scheduled comparisons.

Ordinary r03 logging suppresses a report when no successful submission exists.
Consequently, silence cannot establish zero submissions in the control. Retain
application completion/responsiveness and ordinary output/panic logs, reporting
output observation as inconclusive where necessary. Do not infer physical FPS
or claim a negative control proves instrumentation caused a fault. The13 host
tests pass, including tail/budget aggregation, aborted-versus-submitted output,
and the guard against omitting diagnostic windows from scheduled comparisons.

The bounded local follow-on owner is queued behind the exact campaign PID
incarnation. It requires the campaign's terminal success and verified restoration
before creating its final selection or accessing the bench; a stopped campaign
leaves controls unstarted. Fourteen host tests now pass, including preservation
of post-reset checkpoints as recovery-only evidence. These bytes never supply
an original paired-pass measurement or replace pre-reset telemetry. The resumed
P4 mode8 pass2 has returned after all94 transitions; result retrieval is live.

## Raw provenance and execution accounting

The resumed P4 mode8 pass2 result is now retrieved:94 complete cases, no bad
frames, short samples or truncation, and94 closed matching telemetry windows.
Raw bytes2,509,196; SHA-256
`be4006a1d21773e8a1be258927a7daee45aac157d3e957ff3be0efad65d529f7`.
Execution/return956.63s; retrieval2,202.82s. The matching mainboard run is active.

The maintained `qualification/render_load_audit.py` verifies raw result hashes,
mode/tag/geometry/build identity, contiguous selected checkpoints and exact
agreement with decoded records. It separately counts valid measurements,
failed/invalid executions and unperformed cases. Fence failures at a case
boundary are explicitly inferred from prior checkpoints; corrupt checkpoint
provenance cannot support that inference. Controls and restoration remain
independent closeout requirements.

The current audit accounts for1,176/3,948 scheduled executions:1,158 valid
measurements and18 retained failed/invalid outcomes. All inspected raw evidence
passes provenance checks. Remaining executions and supplemental controls are
pending. Sixteen host tests pass, including preserving failed-case accounting
without claiming subsequent cases ran and rejecting altered decoded records.

## Remaining-duration estimate — 2026-10-05T17:26Z

The Pi retains a duration receipt under ignored `agents/bench009/`, derived from
nine completed full r04 runs. Median fixture execution/return is956.90s;
preparation spans19.28–23.85s and result retrieval394.60–2,202.82s. These are
host monotonic wall seconds, separate from the eZ80 rendering clocks. The
current mainboard mode8 pass2 has finished execution and is still downloading.

| Remaining work at this snapshot | Invocations | Cases | Execution planning basis |
|---|---:|---:|---|
| Paired normal-output groups | 16 | 1,504 | Observed full-run median |
| Held/off P4 controls | 12 | 1,128 | Normal-output median proxy; no completed held/off baseline yet |
| Unperformed mainboard first-pass suffixes | 2 | 46 | Declared20s startup and10s case schedule |
| Matching-history mainboard timing control | 1 | 73 | Declared20s startup and10s case schedule |
| Current ordinary-image presentation control selection | 2 | 181 | Draft selection; final failure inventory can enlarge it |

These planned invocations total about8.3 hours of execution, before the current
download, subsequent retrieval, preparation, flashing, failure recovery and final
restoration. Transfer volume depends on completed sample counts; the measured
retrieval range is not a promised future bound. Held/off comparisons and further
failure controls lack a full duration baseline. This estimate neither changes
the frozen contract nor creates a reset or collection deadline.

## Author-requested pause after retrieval — 2026-10-05T17:38Z

The Author considers the remaining8.3h execution estimate excessive and requests
discussion after obtaining the existing results. The Pi stopped the scheduling
parent while its current download child continued, and cancelled the waiting
ordinary-image follow-on. The download child completed normally; the Pi then
terminated the stopped parent. No new fixture invocation, device reset or flash
occurred after the request.

Mainboard mode8 pass2 passes all94 cases, with no bad frames, short samples or
truncation. Raw result2,244,872bytes, SHA-256
`96fc02b6fdc791b5e3a226f43cc5dc4307e62b86cb5b36e4f92163f98b3f1974`;
execution/return955.43s, retrieval1,971.19s. Fresh analysis and raw audit account
for1,270/3,948 scheduled executions:1,252 valid and18 failed/invalid. Inspected
raw provenance passes. First-pass normal comparisons cover all five modes;
modes20/8 additionally have second-pass comparisons. Repetitions, failure-control
closeout, held/off controls and ordinary-image controls remain incomplete.

The ignored `agents/bench009/paused-results-r04-2026-10-05-17-38-01Z/` snapshot
retains the report, detailed tables, raw-provenance audit and file-hash manifest.
The original raw results remain in their individual run folders. No evidence is
relabelled as a completed three-pass campaign.

The bench is parked at the foreground fast SD listener with the normal diagnostic
P4 image and benchmark startup retained. Original startup/ordinary r03 restoration
has not run. A fresh Agon boot would invoke that retained benchmark startup;
check this state deliberately before any resumed bench use. No automatic run or
follow-on controller remains.

## Offline visualization first cut

The Author requests a script and local webpage to explore retained completion
measurements. This authorizes offline plotting work while the bench goal stays
paused. `qualification/render_load_plots.py` and its maintained templates under
`qualification/render_load_web/` generate a self-contained HTML page plus
provenance hashes. Current usage is in the rendering-load guide.

The page provides paired mainboard-X/P4-Y scatter plots, equal-time/budget lines,
family colours and load connections; selectable load curves; mode/pacing/family/
statistic/scale filters; matching-pass counts; run references and separate P4
presentation counters. Missing levels remain gaps. It supports SVG/CSV exports
and preserves the distinction between incomplete evidence and zero submissions.

The first cut uses the frozen paused-results snapshot and396 paired workload
points. Chromium checks40 filter combinations, source-coordinate agreement,
missing-data gaps, selection, exports and mobile layout, with no JavaScript
errors or external requests. No bench invocation, reset, flash, startup change,
goal resumption, commit or production promotion occurs. Author review is pending.

## Supplemental static-colour conversion control — 2026-10-05

The Author requests fixed-content conversion measurements for all five existing
modes, using a static pattern exercising every available colour. This supplemental
control leaves the r04 workload contract and retained results unchanged.

1. Build the experimental `render-load-static-r01` fixture with the maintained
   generator/assembly under `tests/performance/render_load/static_conversion.*`.
   Startup selects modes20,8,136,21,149 through EMOS; the fixture never changes
   mode or routing. Explicit palettes show all64 RGB222 colours, or all16 stock
   palette colours, in numbered cells. Reference SVGs record expected RGB values.
2. The eZ80 draws once, hides the cursor, disables sprites, fences setup and waits
   five nominal seconds. A double-buffered mode swaps once to expose the chart;
   no drawing, swaps, queries, animation or SD operations follow during sampling.
   Three consecutive ten-second P4 windows use the existing diagnostic carrier.
   The chart stays visible afterward until Escape returns to the fast listener.
3. `qualification/static_conversion.py` stages exactly one mode, verifies the
   deployed executable by one full readback, collects small HTTP telemetry and
   stops for the Author's visual reply before another mode. It uses the existing
   installed normal diagnostic P4 image; no P4 code change/flash is needed.
4. Report row lock waiting, native-row read/composition, RGB888 expansion, cache
   submission, complete conversion-attempt scope and accepted submissions/DMA
   cadence separately. Normalize mean row wall times by mode height. These are
   phase-instrumented wall means, not uninstrumented CPU times or per-frame
   percentile distributions. The conversion-attempt scope includes its leading
   buffer wait and excludes submission/trailing reuse wait.
5. First collect colour checks with HDMI active, then repeat all five modes with
   the supplemental `convert-off` diagnostic build. It retains the same two
   RGB888 PSRAM allocations, uses the existing software60Hz clock, and executes
   the same row reader/expander without creating DSI/DMA scanout or submitting a
   framebuffer. No accepted HDMI updates are counted. Original `off` remains
   drawing-only; ordinary/normal builds remain unchanged. Compare expansion and
   row preparation separately, disclosing different pacing and absent cache
   submission. Neither control establishes physical displayed FPS.
6. Retain exact source/binary, installation receipt, startup, raw telemetry,
   duration, derived phase values and visual replies under ignored local evidence.
   The fixed pattern and disabled cursor/sprites bound source stability; no HDMI
   output capture or per-pixel scanout verification is claimed.

Research relies on official VDU18/19/20, cursor control, native coordinates and
buffer swapping in `agon-docs/docs/vdp/VDU-Commands.md` and `System-Commands.md`,
and MOS keyboard callback, sysvars and response flags in `docs/mos/API.md`.
The existing reference baseline remains stock VDPv2.16.0 and MOSv3.0.2, read-only.

Mode20's three ten-second windows have completed with its fixed64-colour chart.
The medians of window means are: RGB888 expansion27.280ms/image, native-row
read/composition3.288ms/image, row-lock waiting1.206ms/image, full conversion
attempt34.539ms and cache/submission0.640ms. Accepted submissions27.573/s;
DMA cadence60.040Hz. Row values are normalized over384 rows; phase boundaries
can drop an in-flight scope, retained in raw telemetry. No rendering command or
swap occurs during these windows. This demonstrates a substantial presentation
preparation cost on a fixed source; it does not distinguish CPU arithmetic from
scanout/memory contention. Visual colour verification is pending, and the Pi
leaves mode20 unchanged before proceeding to modes8/136/21/149.

Author visual checks pass mode20 and mode8 (steady chart, correct colours) and
mode136. Mode8 normalized expansion10.947ms (91.35 equivalent frames/s), full
preparation14.586ms (68.56 equivalent frames/s), accepted submissions59.941/s.
Mode136 expansion10.848ms (92.18 equivalent frames/s), preparation14.558ms
(68.69 equivalent frames/s), submissions40.060/s. Equivalent frames/s means
1000 divided by the phase's milliseconds, not observed displayed FPS. The
double-buffered gap is outside the timed preparation interval; buffer handoff
and scheduling are investigation candidates, not a proven isolated cause.

All five static colour charts now pass Author visual review, including21/149.
Mode21 expansion27.331ms (36.59 equivalent frames/s), preparation34.488ms
(29.00 equivalent frames/s), submissions27.573/s. Mode149 expansion26.961ms
(37.09 equivalent frames/s), preparation34.068ms (29.35 equivalent frames/s),
submissions19.881/s. DMA cadence remains approximately60Hz in all five modes.

The initial supplemental no-scanout build completed controls20/8/136, then was
stopped before21/149: its conversion-only return omitted initialized-geometry
metadata and cleared the entire720p framebuffer every pass. Those three runs
and the exact failed build are retained as **invalid controls**, outside the
scanout comparison. The corrected branch records geometry after conversion and
alternates both allocations for double-buffered modes without synthesizing a
DMA event or accepted HDMI update. This diagnostic-only bug does not affect the
five normal-image measurements or ordinary builds. A fresh build and all five
fresh no-scanout runs are required; no invalid sample substitutes for one.

### Completed supplemental results

The corrected image completed all five fresh no-scanout controls. Each result
below is the median of three ten-second window means, normalized per image.
Ranked by scanout-active expansion time, worst first. Expansion is RGB888
conversion/write work alone; equivalent frames/s is1000/ms, not displayed FPS.
The percentage baseline is scanout-active expansion time; negative means less
time with scanout stopped. No-scanout controls also omit cache submission and
DMA ownership waits and use the software clock, so this is not a pure bandwidth
experiment isolating one hardware resource.

| Mode | Native image / buffers | Expansion with scanout ms (equiv fps) | Expansion without scanout ms (equiv fps) | Time difference | Accepted HDMI submissions/s |
|---|---|---:|---:|---:|---:|
|21|512×384 / single|27.33 (36.59)|23.60 (42.38)|−13.66%|27.57|
|20|512×384 / single|27.28 (36.66)|23.60 (42.37)|−13.48%|27.57|
|149|512×384 / double|26.96 (37.09)|23.59 (42.40)|−12.52%|19.88|
|8|320×240 / single|10.95 (91.35)|9.40 (106.44)|−14.18%|59.94|
|136|320×240 / double|10.85 (92.18)|9.40 (106.41)|−13.37%|40.06|

DMA scanout remains approximately60Hz with output enabled. At512×384, expansion
alone exceeds the16.67ms budget even without scanout. Full preparation including
native-row reading/composition and lock waiting costs approximately34ms with
scanout (29 equivalent frames/s) or30ms without (33 equivalent frames/s).
At320×240 it costs approximately14.6ms with scanout (68.6 equivalent frames/s)
or13.0ms without (77 equivalent frames/s). Lower double-buffer submission rates
remain a handoff/scheduling investigation; these controls do not isolate that
cause. Static submissions repeat the same image rather than delivering new
animation frames.

The Pi restored the exact ordinary r03 image, verified its flash segments,
restored pre-task startup byte-for-byte, and verified EMOS input admission,
HTTP startup readback and mode0 at logical640×480 with720p HDMI output. The
supplemental owner records `completed-and-restored`. The initial three invalid
controls and failed image remain diagnostic evidence and are excluded from
results. Raw receipts, source hashes, CSV/JSON, self-contained HTML and browser
checks are retained in the ignored local evidence store. B09-05/B09-06 remain
incomplete; the long campaign stays paused. No production promotion or commit.

## Resident and local-card collection closeout —2026-10-05

B09-09/B09-10 complete independently of the paused campaign. All12 pinned
resident files pass exact hashes on the Author-mounted card; original startup
also matches. Read-only SSH retrieval into a verified local snapshot is necessary
because the Pi has no spare reader port. All88 bounded RGB888 timed combinations
and four no-probe controls validate; four original failures stay excluded.
The collector correctly preserves three additional recovery-only groups as
failed instead of converting them to performance passes. Offline plots pass
Chromium checks and are copied exactly to the Author's host for review. Card
contents and ordinary installed firmware remain unchanged during collection.
No long-campaign resumption or production promotion follows this closeout.
