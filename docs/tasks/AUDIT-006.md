# AUDIT-006 — Audit stock video-backend fidelity and direct its restoration

## State and authority

Status: **complete, accepted 2026-09-10**. W6 source comparison, W7 repair
contract and W8 disposition review are complete. PORT-003 R1 is authorized.
The [full comparison](AUDIT-006/video-backend-audit.md) and
[accepted PORT-003 contract](PORT-003/stock-backend-restoration.md) recommend
restoring the original concrete depth controllers behind narrow P4 bindings.
W1–W5 remain completed diagnostic
work with preserved failure evidence. Audit closure does not qualify the repair.
The mission is the most faithful practical port of mainboard framebuffer
formats, storage organization and rendering behavior, with exact upstream code
reuse wherever processor and video-output interfaces permit it. PORT-003 owns
the resulting implementation; this task owns the comparison, justification of
every departure, repair priorities and audit closure. QUAL-003's benchmark
proposal waits behind the source audit and remains unapproved for execution.

The Author approved this work contract and directed a work-in-progress commit
of all open changes followed by execution. W6's comparison and W7's proposed
repair contract may proceed without another planning approval. Executable
behavior remains unchanged during the audit; W8 retains the findings and
concrete repair review boundary.

The earlier diagnostic phase was authorized on 2026-09-10: freeze its contract with the preceding results,
then execute without additional planning or version-approval prompts. The
Author explicitly requested the timing investigation following
[AUDIT-005-F007](AUDIT-005/stock-drain-suite-findings.md). PORT-003 owns any
eventual display correction. Its original observation/attribution scope is
preserved below as historical work, not a prohibition on the expanded audit.

The existing r08 point-throughput improvement and the subsequent Nurples
regression must both remain visible. A passing 48-row fixture does not establish
playable game behavior. Browser continuity and hang recovery in the previous
run were not fully observed; do not invent answers or block preparation on
those optional historical observations.

## Accepted direction and decision register

**AUDIT-006-D001 — accepted, 2026-09-10:** fidelity to stock implementation is
the governing requirement. Reuse upstream code exactly as written wherever
possible, including useful algorithms and state embedded in the old concrete
controllers. A different processor facility or video-output interface can
justify a narrow adaptation; generic abstractions, easier testing, convenient
browser serialization or a prior project implementation do not establish that
necessity. Preserve native formats and efficient memory operations as well as
visible results. Do not treat all code inside a physical-driver file as
hardware-specific. ADR-0013, ADR-0015 and the architecture carry this direction.

**AUDIT-006-D002 — accepted, 2026-09-10:** identify the smallest P4 binding and
storage/execution arrangement that preserves the maximum actual upstream code.
The existing generic-controller/flat-plane design is a candidate under audit,
not a fixed constraint on the answer. Determine which row access, native byte
layout, allocation, cache/DMA and scanout dependencies really need adaptation.
The completed source comparison recommends the original five concrete classes
with narrowly adapted lifecycle/output bindings; verbatim method extraction
is a fallback only for a demonstrated source-unit dependency. Preserve row
tables and native byte order, and normalize output only at the sink. The first
repair increment proves this binding with target compilation and stock-derived
row comparisons. No clean-sheet backend or fragmented allocation is required.
The detailed alternatives, dependencies and validation criteria are in the
linked repair contract; R1 proves the accepted source-binding direction before later integration.

**AUDIT-006-D003 — accepted, 2026-09-10:** no upstream bug fixes in the first
pass. If upstream code compiles on the selected target, use it unchanged.
Record suspected or encountered upstream defects; defer fixes. Only necessary
compiler/processor/output binding changes belong in PORT-003 R1. This
supersedes the earlier proposed F009 remedies in the supporting reviews.

The completed audit was read-only with respect to firmware, games, media and running
devices. It does not begin the held benchmark or authorize an unreviewed
framebuffer replacement, mainboard flash, core change or new drawing budget.

## Current work — first priority

6. [x] **W6 — Audit the whole stock video-generation backend first.** Trace
   the selected official mode/command facade through Canvas and the common
   renderer, concrete depth controllers, framebuffer storage and video output;
   compare every applicable region with the actual P4 build selection, not
   merely files present in the vendor tree. Cover all five colour-depth
   families, single/double buffering and official text/Teletext paths. Reuse
   existing provenance inventories as navigation, then verify their present
   source correspondence and claims independently.

   The coverage ledger must include:

   - mode setup/fallback, dimensions, stride, byte/bit order, pixel addressing,
     row tables, allocation/alignment and native bitmap save/readback;
   - clears, row fills/copies, vertical/horizontal viewport scrolling, aligned
     fast paths and overlap handling;
   - clipping/origins, paint operations, glyphs/text, geometric primitives,
     flood fill, ordinary/transformed bitmaps and per-pixel conversion;
   - software/hardware sprites, cursors, background save/restore, palettes,
     Copper, scanline composition and presentation copies;
   - queue admission/draining, batching, synchronization, completion/flush,
     swaps, suspension, task/core/ISR ownership, frame counters and callbacks;
   - the physical output boundary: classic GPIO/I2S/DMA/timer dependencies,
     P4 equivalents and snapshot/encoding/browser handoff. Keep portable
     scanline work distinct from the hardware instructions that schedule it.

   Each ledger row names the stock file/symbol/commit and selected EDP
   counterpart, exact reuse or diff, behavior and memory-work difference,
   target/output dependency claimed, evidence for that dependency and proposed
   disposition. Mark replacements and omitted fast paths explicitly. Include
   unused upstream routines that could replace project code. Byte-identical
   common code does not prove an equivalent backend when different callbacks,
   layouts or executors are supplied. A hash inventory alone is not the audit.
   Deliver `AUDIT-006/video-backend-audit.md` with this coverage ledger, a compact
   execution/storage map and stable findings after the review is performed.
   Separate measured defects, source-proven departures and timing hypotheses.
7. [x] **W7 — Rank departures and contract the smallest faithful repair.**
   Account for every W6 finding: retain exact upstream, narrowly adapt with
   evidenced processor/output necessity, restore upstream code/arrangement,
   or leave an explicitly unresolved finding with owner and missing evidence.
   Reassess the prior generic-controller, native-codec, flat-plane, compositor
   and frame-service contracts; identify exact amendments rather than silently
   inheriting their design choices. Preserve F001's independent publication
   finding. Present a source-backed recommendation and bounded PORT-003 work
   contract before changing executable behavior. Use QUAL-003 selectively to
   verify the chosen boundaries; do not require a new callback infrastructure
   merely to recognize unjustified source divergence.
8. [x] **W8 — Close the audit with traceable dispositions.** The Author reviews
   the full comparison and repair contract. PORT-003 receives each accepted
   implementation item and QUAL-003 receives necessary measurements. Keep
   unresolved or unaccepted findings open here; do not call them completed
   because a build or visual suite passed. Close AUDIT-006 only when coverage
   is complete and every finding has an accepted disposition, linked owner and
   verification criterion. Retain W1–W5 evidence and the final audit together.

## Audit inputs and initial leads

### Completed source review

Work-in-progress checkpoint `047ffe8` froze all prior open changes and this
contract before source review began. The resulting
[audit](AUDIT-006/video-backend-audit.md) consolidates four independent-area
reviews, complete coverage and stable F001–F009 dispositions. Its
[source binding](AUDIT-006/video-source-baseline.json) verifies the selected
sources remain identical to that checkpoint. No firmware, build, SD or hardware
operation occurred during W6/W7. No claim of improved performance follows from
the source audit.

Key departures are native byte layout in two depths, missing row-table and
concrete bulk paths, duplicated palette/scanline algorithms, RGB888 expansion
before RGB222 output, serialized frame-time/publication and changed execution
assumptions. Official command/common rendering/text/Teletext bodies are largely
retained. Possible inherited edge defects receive narrow validation/remedy
requirements rather than becoming excuses for wholesale replacement.

PORT-003's first proposed increment is original-class binding and native-row
comparison, followed by independent output integration and qualification.
QUAL-003's broad callback benchmark remains on hold. The Author accepted this concrete contract and D002, directed its freeze and
R1 execution, and explicitly prohibited upstream bug fixes in the first pass.
F009 remains a deferred observation with no first-pass remedy. F001–F008 have
accepted PORT-003 owners and verification criteria; R1/R2/R3 track actual
implementation and qualification.

### Pinned inputs

Use the selected reference identities already bound by AUDIT-005 and the
QUAL-003 draft: official VDP v2.16.0 at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, vdp-gl `all-the-plots` at
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`, and official documentation at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Keep official checkouts read-only.
Bind the EDP source commit/worktree and selected build closure at audit start;
the installed diagnostic is recorded in the deployment receipt below.

Start with PORT-003's existing Phase B algorithm, Phase D presentation, Phase E
mode and Phase F source provenance, plus the actual console source manifest.
Those records locate the comparison surface; earlier labels such as
`adapt-depth-algorithm` are claims to review, not proof that adaptation was
unavoidable. Record any uncovered region rather than claiming whole-backend
coverage from the existing test inventory.

Initial source checks found stock VGA64 row-pointer scrolling versus P4's
per-pixel copy helper; shared stock bitmap clipping but additional P4 pixel
conversion/access work; and fixed `base + y * stride` access in the P4 plane
and compositor. Contiguous allocation and fixed logical row order are distinct
choices. Browser snapshots are already separate from drawing storage and do
not inherently require fixed-order drawing rows. These leads do not rank
runtime costs and are not a substitute for W6's complete comparison.

## Original diagnostic question and fixed behavior (W1–W5)

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

## Original diagnostic research bounds (W1–W5)

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

## Completed diagnostic work (stable W1–W5 identifiers)

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
4. [x] **W4 — Record one reproduction.** Expose a read-only diagnostic endpoint
   on the existing HTTP service. A host collector samples it at a modest fixed
   rate for a bounded session, saving raw replies, host times, failed requests,
   exact deployment binding and any operator hang marker. HTTP polling is a
   declared perturbation, not a claim of zero overhead. No serial open or P4
   reset occurs during the reproduction. The operator keeps video connected,
   starts Nurples, reports a hang/recovery and ends the recorder. Timing data
   must remain interpretable if HTTP itself stops answering; loss of HTTP
   access alone does not establish that the renderer stalled.
5. [x] **W5 — Attribute and stop.** Compare phase durations, active-phase ages,
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
deployment now pass. The subsequent physical reproduction is recorded below; these build/deployment
checks remain distinct from gameplay results.


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
binding and evidence under `agents/audit-006/`. This was the W4 handover; the completed reproduction and W5 attribution follow.


## Reproduction and attribution — 2026-09-10

[AUDIT-006-F001](AUDIT-006/findings.md) records the Author's four hang markers
and severe, rarely recovering gameplay. All 179 HTTP requests succeeded; 178
aggregate copies and all sampled live-phase records are valid. A drawing-drain
invocation lasted 41.758495 seconds and executed 163,069 primitives. Within its
40.762339-second observed interior, snapshot/frame completions did not advance,
while P4 consumed another 474,404 UART bytes and observed 1,343 completed TX
batches. This identifies frame publication waiting on sustained queue draining;
it does not establish normal game/input speed or successful Escape.

W5 stops with a proposed PORT-003 correction: separate periodic frame/output
service from queue-empty completion while retaining FIFO, flush/swap and safe
snapshot ownership. No new quota, core assignment, firmware or hardware change
was made. The Author subsequently proposed returning to the deterministic
Shapes/Bitmaps suite with Pingo-style completion callbacks and temporary custom
mainboard/P4 firmware. QUAL-003 records that benchmark direction separately;
this investigation's captured result is not replaced by the proposal. The
subsequent Author-directed fidelity audit above now precedes that benchmark.
