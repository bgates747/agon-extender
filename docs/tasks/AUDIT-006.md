# AUDIT-006 — Measure P4 frame work during Nurples hangs

## State and authority

Status: Authorized 2026-09-10; freeze this contract with the preceding results,
then execute without additional planning or version-approval prompts. The
Author explicitly requested the timing investigation following
[AUDIT-005-F007](AUDIT-005/stock-drain-suite-findings.md). PORT-003 owns any
eventual display correction; this task owns observation and attribution.

The existing r08 point-throughput improvement and the subsequent Nurples
regression must both remain visible. A passing 48-row fixture does not establish
playable game behavior. Browser continuity and hang recovery in the previous
run were not fully observed; do not invent answers or block preparation on
those optional historical observations.

## Question and fixed behavior

Determine whether a reported hang coincides with P4 queue draining, sprite
updates, browser-snapshot preparation, or a caller waiting for frame work.
Distinguish lack of new browser images from Agon-facing command progress as
far as these measurements allow. Wall-clock time includes preemption and
waits; do not label it pure drawing CPU time or prove eZ80 execution from a
P4 counter alone.

Keep r08's stock drain-until-empty-or-suspended rule, task placement/priorities,
logical tick handling, UART buffers/baud/flow control, retained renderer,
browser pixel format/credits and keyboard policy unchanged. No speculative
repair, new drawing budget, scanline transport, core pinning, EMOS rewrite,
game modification or automated keyboard controller belongs to this task.

## Research bounds

Review the official PLOT, bitmap/sprite and screen-pixel/VSYNC documentation
in the read-only Agon documentation checkout, then the selected stock worker
where scheduling detail matters. Reuse the exact stock identities in
[AUDIT-005 W1](AUDIT-005/baseline-and-path-map.md) and
[W8 source accounting](AUDIT-005/p4-queue-accounting.md), rather than changing
upstream selections. Record the specific source relationships in a bounded
précis before instrumenting them.

The initial local observation is that `P4DisplayController::executeFrameWork`
retains `executing_frame_work_` through queue draining, `showSprites` and
`publishSnapshotAtBoundary`; suspension callers wait for that flag. The
frame task services pending ticks individually. These are candidates to
measure, not the diagnosed cause of the game regression.

## Work

1. [x] **W1 — Add bounded diagnostic timing.** Timestamp drawing-queue work,
   sprite updates, snapshot preparation and whole frame execution. Record
   suspension-wait durations and enough parser/reply progress to relate
   stalled output to the frame work. Include frame backlog/context, sample
   counts, accumulated/max durations, active phase and bounded slow-event
   history. Use P4 monotonic time, fixed memory and nonblocking recording;
   record any dropped or inconsistent observations explicitly. Do not log,
   allocate, write storage or perform network I/O in these measured paths.
   Compile instrumentation only into the selected diagnostic console.
2. [x] **W2 — Validate and prepare the identified image.** Use deterministic
   clock tests for interval arithmetic, in-flight states, wrap, history and
   recorder contention/loss. Run the affected frame/controller/snapshot checks
   and compile the real P4 console. Preserve prior evidence. Reuse the existing
   build/deployment toolchain and unchanged dependencies. Standing version
   approval covers console r09 and registry r65; the new task owns its host
   recorder directly, without inventing another firmware or fixture lineage.
   Freeze deployable inputs and retain exact manifest/image hashes.
3. [x] **W3 — Deploy diagnostics and prepare reproduction.** The Author's
   instruction to proceed without further prompting authorizes this bounded
   P4 diagnostic deployment after the checks above. Verify stable device
   identity, image readback and startup with the established private bench
   procedure, then close serial. Retain r07 and r08 rollback bundles. Leave
   EMOS and the current SD Nurples executable/assets unchanged. Back up
   autoexec and prepare ordinary Extender keyboard input and the game directory
   so the operator can reset Agon and launch the existing game manually.
4. [ ] **W4 — Record one reproduction.** Expose a read-only diagnostic endpoint
   on the existing HTTP service. A host collector samples it at a modest fixed
   rate for a bounded session, saving raw replies, host times, failed requests,
   exact deployment binding and any operator hang marker. HTTP polling is a
   declared perturbation, not a claim of zero overhead. No serial open or P4
   reset occurs during the reproduction. The operator keeps video connected,
   starts Nurples, reports a hang/recovery and ends the recorder. Timing data
   must remain interpretable if HTTP itself stops answering; loss of HTTP
   access alone does not establish that the renderer stalled.
5. [ ] **W5 — Attribute and stop.** Compare phase durations, active-phase ages,
   drawing/parse/reply progress, frame backlog and recorder losses around the
   reported hang. Preserve raw records and informative failures. State which
   cause is supported, which boundaries remain unobserved, and the smallest
   next correction or measurement. Do not implement that correction within
   this diagnostic task.

The ready cue is a labelled notification-only emulator, launched after all
independent checks, deployment and media preparation are complete. No screenshot
or additional approval is required; physical game interaction remains the
operator's part. Keep host addresses, device identities and media paths in
`HARDWARE.local.md` and ignored local receipts.

## Implementation checkpoint

W1 is implemented in the selected console only; exact boundaries and limitations
are in [measurement.md](AUDIT-006/measurement.md). The private bounded research
record is `agents/precis/p4-frame-timing.md`. W2 recorder and serialized-scope
checks pass under ASan/UBSan, including concurrent sampling, forced record loss,
active timing and wrap. Two host acquisition tests pass; retained frame and
presentation checks pass, and the complete P4 diagnostic compiles. See
[AUDIT-006 local validation](AUDIT-006/local-validation.json).

Review caught the need for a seventh HTTP route slot before deployment. The
selected console now supplies it while other builds keep their existing count.
The aggregate version validator remains blocked by the pre-existing held-r02
connectivity hash mismatch; this task does not alter that hardware design.
Candidate inputs were frozen in `cfae7d7`; the final identified build and W3
deployment now pass. W4 still requires the operator's physical game reproduction;
these checks are not a gameplay result.


## Hardware test ready

[Deployment receipt summary](AUDIT-006/deployment.json) binds the clean candidate
build to independent flash readback, native USB and HTTP startup, and a valid
read-only timing response. Serial is closed. Both prior rollback bundles remain.
The local host recorder also passed a complete replay run with sampling, a marker,
operator finish and verified output hashes; that run is not hardware evidence.

SD autoexec now selects mode 3, enables Extender keyboard and changes into the
existing Nurples directory. The prior autoexec is backed up; every Nurples and
benchmark file checked before/after is unchanged, and the card is safely
unmounted. The private launcher is `agents/run-frame-timing`, with exact local
binding and evidence under `agents/audit-006/`. W4 is ready for one manual run;
no new flash, reboot of P4 or game change is needed. W5 remains unperformed.
