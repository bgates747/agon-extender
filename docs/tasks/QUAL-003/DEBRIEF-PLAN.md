# Overnight performance debrief — review contract

## Executive summary

Author-directed on 2026-09-15: audit the completed overnight work, compare
mainboard VDP and Extender graphics performance in milliseconds and applicable
frame rates, research official documentation, and deliver a focused next-action
plan with hardware voice notification. This is a documentation/research goal,
not authorization to resume the paused performance experiments.

QUAL-003 remains the owning task; TODO.md remains the sole queue. Preserve
experimental code, prior evidence and the bench. No firmware changes, new
benchmarks, emulator changes or experimental pushes during this debrief.

1. [x] D01: Inventory current identities and evidence; classify valid, invalid,
   historical, instrumented and non-comparable results. Include Nurples,
   current non-Golem Rally and informative bespoke graphics/transport fixtures.
2. [x] D02: Recompute comparative tables from retained machine results. Separate
   per-operation/batch rendering, queue completion, paced game cycles, uploads,
   snapshots, socket sends and browser delivery. State baseline, counts,
   quantization, instrumentation and percentage convention.
3. [x] D03: Research pinned official Agon/FabGL and Espressif documentation and
   source for scheduling, task priorities/affinity, UART buffering/flow control,
   framebuffer memory and output behavior. Distinguish cause from hypothesis.
4. [x] D04: Write the full debrief, review contradictions and evidence gaps,
   then append ranked first investigations to its executive summary. Put the
   granular proposed actions and decision gates in this task's review plan;
   do not execute them before review.
5. [x] D05: Check calculations/references, commit documentation in discrete
   local steps, notify through the accepted hardware voice path and stop.

Deliverable: `OVERNIGHT-DEBRIEF.md` beside this contract, with reproducible
derived data where useful. Completion means the report and proposed plan are
ready for Author review, not that Nurples parity has been achieved. Report any
unavailable measurement explicitly instead of manufacturing a game FPS or a
single-operation cost from a mixed scene. Human acceptance remains separate.

## Proposed investigation sequence

**P00 complete. P01a/b complete. P02 SW controls collected; review pending. P03–P06 remain proposals.**
These steps refine the open N04ae-iii/N03–N05 work, not a second independent
performance queue. Author clarification: **all Golem testing remains on hold
until further notice**. Only the current eZ80-projection Rally is eligible below.
Review one chunk at a time; an actionable finding is a stopping point for a
hardware voice report, not permission to consume the entire backlog.

### P00 — Audit inherited FabGL timing before selecting scheduling changes

**Author-approved unattended audit**, prompted by official-research item8.
Complete P00a–P00d together and notify by hardware voice for review. No
implementation, performance experiments or downstream task execution is approved
by this audit authorization. Escalate a scope decision or physical intervention.
Complete this audit before choosing P01 instrumentation or P02/P03 scheduling
corrections; retain the existing numbered items and evidence.

1. [x] P00a: Trace the pinned stock Agon vdp-gl/FabGL timing implementation,
   consulting official documentation first. Identify primitive-task wakeups,
   vertical-sync notifications, queue draining/budgets, completion waits,
   suspension/resumption, buffer swaps and foreground execution. Follow the
   relevant controller/base classes and callers, not just VGA64 ISRHandler.
   Record exact revisions, symbols, call paths and execution contexts.
2. [x] P00b: Compare those mechanisms with the retained P4 adapter. Map each
   hardware interrupt, timer, task notification, semaphore, queue and clock to
   its owner and replacement. Identify implicit physical-blanking assumptions,
   phase coupling, notification coalescing, and any omitted or duplicated waits.
   Separate source-confirmed behavior from timing hypotheses. Audit existing
   mechanisms before inventing another scheduler or increasing wake frequency.
3. [x] P00c: Classify which stock mechanisms protect rendering correctness or
   workload ordering, which exist only for VGA scanout, and which can serve the
   current web-output backend without generating VGA. The Author does not want
   bit-banged VGA as the solution; this audit does not authorize adding it.
   Preserve stock rendering/API semantics and the minimal-port rule.
4. [x] P00d: Produce a source-linked stock-versus-P4 timing map and identify
   the smallest discriminating tests or adaptations supported by it. Reconcile
   the proposal with prior failed scheduler controls and the measured
   wire/enqueue/completion gap. Update P01–P03 only where the audit provides a
   concrete reason, then stop for review before implementation or hardware tests.

P00e has been promoted to [AUDIT-007](../AUDIT-007.md), the required exhaustive
Agon FabGL port completeness audit. It is currently **unscheduled pending this
immediate research**. The Author clarified that the dependency controls
sequencing only: the exhaustive audit is required whether or not P00 produces
a fix. AUDIT-007 owns its checklist; do not maintain a duplicate here.

Author's rationale: the Author reports that human experts maintaining Agon's
fork describe FabGL as notoriously convoluted. Machine-assisted tracing can
follow long call chains, but that does not guarantee recognition of implicit
contracts or subtle cross-subsystem effects. The audit must explicitly look
for those effects and challenge earlier omissions instead of assuming that
successful compilation, visible output or the present feature scope proves
that all necessary code was ported. This records the Author's assessment and
required follow-up; the exhaustive audit has not started, and no execution
begins with this documentation change.

Deliverable: a focused FabGL timing section in the official-research writeup,
with explicit unresolved questions and proposed tests. Finding two row
preparations per ISR is not sufficient evidence that the pertinent inherited
scheduling mechanisms have been fully audited. Golem remains on hold.

P00a–P00d completed: [source-linked timing audit and next checks](debrief/OFFICIAL-RESEARCH.md#9-p00--focused-fabgl-timing-audit).
No immediate fix is established. Author approved P01a/b and conditional P01c/d
unattended, with hardware voice notification at an actionable conclusion or
need for assistance. Preserve original startup, known firmware rollback and
existing fixtures. No Golem, MOS experiment or downstream execution.

### P01 — Establish current comparison and diagnostic accounting

1. [x] P01a: Verify current P4/EMOS/mainboard identities and actual memory/task
   settings, source/assets/fixture hashes, safe startup and rollback. Select
   the archived r43 behavior parent, retaining optional completion observation
   but excluding the r44 native-acquisition probe for the reference. No MOS
   experiment. Do not infer installed options from repository defaults.
2. [x] P01b: Run the existing r05 SW fixture with a fresh nonce and full180second
   wired production observer, then the same fixture without output. Record
   completion spacing, enqueue spacing, pending counts, whole-game coverage,
   terminal pixels and service health. Reverse order for one repeat if the
   contrast is material or apparently passing. Earlier output-off data used
   different firmware/query timing; it cannot answer this current comparison.
Author authorized bounded P01c/d implementation and execution;
[execution contract](debrief/P01cd/README.md) owns this tranche. It precedes RLE.

3. [x] P01c (bounded selection; see result limitations): If pre-enqueue variation remains, define one bounded diagnostic
   build that measures the missing intervals: parser/owner runnable and blocked
   time, RX driver buffered work, software reply-gate duration, UART driver
   activity, foreground/native/input-lock acquisition, timer wake lateness. Include foreground admission, dynamic-payload/queue
   waits and worker notification-take/gate outcomes where applicable; distinguish
   callback lateness from runnable delay (P00 findings).
   Prefer existing SDK task tracing or a bounded event buffer; determine its
   actual support, memory cost and interruption overhead before selecting it.
   Aggregate around owner batches, not a timestamp or print per UART byte.
   Record task names, priorities, affinities and relevant ISR placement.
   Include allocation/memory considerations from RESEARCH-001 C1-M: distinguish
   preallocated snapshot access from runtime network allocation; record buffer
   capabilities, alignment and lifetimes. Consider bounded allocation counts and
   bytes by caller/task, internal/PSRAM free and largest-free-block measurements,
   and startup allocation order. These are hypotheses, not established causes.
   Select only probes needed for attribution; no per-allocation logging or heavy
   heap tracing without measuring its overhead against the same control.
4. [x] P01d (overhead evaluated; attribution limited): Validate the probe against the same unmodified reference condition;
   a probe which makes the failure disappear gives only limited attribution.
   Save RAM records only after the terminal fence. No live SD, per-frame UART
   logs, open serial tool that resets the board, or browser polling during the
   measured window. Show every new measured interval's owner and start/end.

**Decision gate:** Produce a same-run account separating active parser work,
reply admission, lock acquisition, runnable delay and queue service. Do not
subtract unrelated medians/p95s as if they were exclusive CPU costs. If the
stream-off contrast is absent, drop the presumption that web output is the
cause and follow the earliest measured divergence. Stop for review if a clear
fix is identified. Estimated existing controls:3minutes observer each, about
40seconds game work, plus setup/retrieval; diagnostic preparation has no tested
duration yet. Do not turn estimates into resets.

**Historical P01a/b review checkpoint (superseded by P01c/d below):** [matched-run results](debrief/P01/README.md).
Two output-off controls remove the tail; both streamed controls worsen it.
P01c/d remain unchecked and deferred: recommend existing P02a/b isolation before
adding broad instrumentation. This is an evidence-driven sequencing proposal,
not authorization to start P02. No immediate fix or parity pass is claimed.

**P01c/d review checkpoint:** [six paired hardware controls](debrief/P01cd/README.md)
complete. Streaming native waits/holds reach22–23ms; probe effects materially
alter output timing. No exclusive CPU/runnable attribution or performance fix.
Broad unmeasured items above remain possible follow-ups, not completed probes.
The result proposes narrower owner/scheduler correlation before optimization.
Original r43/startup restored; no experimental push. Await Author review.

### P02 — Separate output composition from network scheduling, if warranted

Author approved unattended P02 execution with hardware voice notification.
[Diagnostic execution contract](debrief/P02/README.md) freezes the four controls,
measurement limits, rollback and review boundary before implementation.


1. [x] P02a: On one frozen diagnostic image, compare four explicitly labelled
   controls: output off; complete snapshot composition with local discard;
   full-sized prebuilt-frame network streaming; normal composition+streaming.
   Hold seed, work, resolution and target request cadence fixed. Preserve full
   pixel counts and report realized rates/byte counts; if achieved output work
   differs, report that mismatch instead of assuming equal load.
2. [ ] P02b: Keep normal browser credit/ownership/takeover and bounded memory.
   A prebuilt-frame/discard control is diagnostic only, never a parity result or
   a product that omits sprite output. Match hardware-sprite row composition
   explicitly before interpreting its cost. Run SW first; add HW when the
   distinction is established, not a broad matrix before learning anything.
3. [ ] P02c: Use P01 task/interval evidence to select at most one next change.
   If network task preemption aligns with stalls, first consider a single
   TCP/IP affinity control while preserving parser/draw/snapshot placement.
   Verify the actual SDK task and Ethernet interrupt placement; moving lwIP
   alone need not move the driver or network worker. If snapshot/memory work
   dominates instead, investigate that measured path. No blanket priority raises. P00 found no missing active stock blanking budget;
   do not restore that disabled policy or increase wake frequency without
   measured justification.

**Decision gate:** Reproduce or remove the pre-enqueue tail while accounting for
unchanged work. Return to the baseline after a failed control. Do not retry the
already rejected same-core snapshot priority2/4 configurations without new
contradictory evidence. No renderer redesign based solely on task priority lists.

P02 result: six valid SW controls plus one retained pre-marker query failure.
Normal streaming p9529.238ms; off17.049ms; prebuilt25.026/21.428ms;
discard17.318/45.509ms. The contradictory discard repeat prevents network-only
attribution. See `debrief/P02/README.md`. P02b HW extension and P02c scheduling
change remain unexecuted; stop for review before adding instrumentation or
changing affinity. Agent-recommended next boundary: matched boot/order and
pool-placement/lock evidence, then measured networking task interference.

Author-requested [RESEARCH-001](../RESEARCH-001.md) now supplies a P4-first
internet review and ranked follow-up checks. It clarifies that the selected
snapshot allocator explicitly uses PSRAM; only addresses/alignment/runtime
interactions remain unmeasured. No matching upstream fix or new experiment
is established. Reuse its findings in P02c/P01c/P06 instead of duplicating work.

### P03 — Audit/fix the evidenced owner or scheduling path

1. [ ] P03a: If owner/RX/reply time dominates, compare the exact current parser,
   Stream and UART driver paths with the pinned stock equivalents, including
   command frequency and full reply framing. The7772 mode replies are required
   behavior. Do not suppress them, bypass EMOS or disable native keyboard.
2. [ ] P03b: If a UART threshold/ISR delay is implicated, inspect current
   registers/driver settings and trace first. Passive wire capture must meet
   its actual extent gate and contain both complete nonce markers. Digital
   traces are not an analogue signal-integrity test. Wiring changes remain a
   later evidence-driven branch, not the current default suspect.
3. [ ] P03c: Freeze one minimal correction, host-check its ordering/ownership
   and negative cases, commit clean candidate inputs, build/hash/verify, then
   run the unchanged failing workload first. Retain rollback. Stop after a
   reproduced actionable fix for Author review rather than stacking changes.

**Invariants:** Stock command bytes, return packet order, mode/viewport behavior,
keyboard release/admission, SD availability, bounded memory, no partial image,
no additional application work omitted, no Golem. Preserve upstream bugs as
follow-up notes except a demonstrated portability adaptation needed for parity.

### P04 — Qualification of a candidate that actually passes

1. [ ] P04a: Reuse N05a/N05b exactly: two fresh full-stream runs per sprite path,
   all2400states and completions, matching hashes, no increasing backlog or
   lost work, complete pixels, sustained browser coverage and post-run input/SD.
   Mean≤1.05×stock, p95≤stock+8.333ms. Report maxima and browser cadence too.
2. [ ] P04b: Repeat matched stock baselines only after candidate repetitions
   pass; use the same validated minimal observer, verify actual original flash
   before writing, restore exact affected stock sectors immediately afterward.
   Compare every candidate repeat with both stock repeats, not the best pair.
3. [ ] P04c: Distinguish microsecond command-completion qualification from
   unmodified Nurples visual review. Check live SW/HW sprites and responsiveness
   with the Author before ordinary firmware promotion or experimental push.

### P05 — Current non-Golem Rally and missing operation costs

1. [ ] P05a: Pin the current `rally-game` binary/source, eZ80 projection, assets,
   track/poses/traffic/audio settings and mode136. Make a deterministic fixed-pose
   fixture without timing-dependent trajectory changes. Keep existing RX06
   road and audio/HUD regressions as correctness gates. Include a bounded
   alternating-frame swap/snapshot-coherence control if evaluating double-buffer
   output: P00 found row-batch safety does not establish whole-frame coherence.
2. [ ] P05b: Start with the most informative full-scene/curve cases on Legacy
   and ExCom with the same image/workload. Separate eZ80 preparation/submission,
   renderer completion, protected horizontal scrolling, buffered section
   transforms, traffic plots and buffer swap. No unverified general-poll or
   emulator-wide30Hz assumption; validate the chosen completion boundary.
3. [ ] P05c: Add only the isolated operation fixtures required by observed
   gaps: e.g. resident bitmap plot at exact dimensions/format/clipping, horizontal
   viewport scroll, fixed triangle/span sequence, software refresh and complete
   hardware-sprite row composition. Report count/geometry and both batch total
   and amortized cost; measure a true isolated call only with adequate precision.
4. [ ] P05d: Report paired physical milliseconds/FPS and differences with output
   coverage separately. Then Author plays Rally and Nurples. A normal game run
   and a synthetic torture test each have their own limits; neither replaces
   the other. Full suite rerun is downstream of informative cases, not step1.

### P06 — Browser-delivery audit and isolated pattern benchmark

Author-requested follow-up, awaiting execution scheduling. This extends the
existing output investigation; it does not create another performance task.
P02 owns the four composition/network isolation controls. Reuse those results
here rather than repeat them. P00 owns FabGL timing; AUDIT-007 owns exhaustive
port coverage. This section owns network API/protocol and client delivery.

**Author clarification — packing and the hard output goal:** performant full-frame
512×384 output at 60 Hz with **one byte per pixel (8 bits/pixel)** remains the
hard target, including eventual 256-colour palettes. The Author's conversational
"1bpp" here means one **byte**, not one bit. Six-bit packing for current 64-colour
modes is only an optional experiment; it cannot satisfy or replace the eight-bit
target. Sparse redraw is not an assumed prerequisite or an accepted substitute.
The target remains unproven: 94.37 Mbit/s pixel payload leaves very little margin
on a 100 Mbit/s link once framing is included. Report any measured physical or
protocol limit explicitly rather than silently reducing the acceptance target.

1. [ ] P06a: Record each receiving host and wired/wireless path, negotiated link
   rate, payload/header bytes and credit policy. The Author reports this
   workstation has used Wi-Fi for several days after earlier wired operation:
   possible latency/jitter confounder, not an established cause. Recent r43/r44
   approximately28FPS browser measurements used the wired Pi, so this change
   cannot be assigned as their explanation. Earlier laptop/Pi comparisons
   changed both host and network. Where useful, isolate wired versus wireless
   on the same host, binary, client and workload.
2. [ ] P06b: Audit the actual pinned Espressif Ethernet, lwIP/socket and HTTP
   server/WebSocket APIs against official documentation and examples. Trace our
   custom framing, buffering/copies, send completion, backpressure/credit,
   worker scheduling and client handling. Distinguish supported transport APIs
   from custom video payload conventions; do not assume one officially approved
   video protocol exists. Document adaptations and discrepancies before fixes.
   As preparation for any separately reviewed packing experiment, inventory
   supported mode widths and colour depths against whole-byte packing groups.
   Six-bit pixels pack four-to-three bytes: independently packed rows have
   `ceil(width * 6 / 8)` bytes, with no padding when width is divisible by four.
   At512 pixels this is384 bytes/row. Define row stride, bit order and final-byte
   padding explicitly; height imposes no extra alignment constraint for that
   row-based format. Account for P4 packing and browser unpacking costs, and
   retain the independent eight-bit full-frame baseline and acceptance goal.
3. [ ] P06c: Extend P02's prebuilt-frame control with a deterministic animated
   pattern generated locally by the P4, visually distinct from the browser-local
   pattern. Bypass Agon submission and VDP drawing, retain the tested resolution,
   pixel format and full-frame payload, and include unique frame identifiers and
   a content oracle. Compare pre-generated and live-generated frames to isolate
   generation cost. Compare the current sender with a minimal official-example
   based sender only with matched transport, payload, receiver and credit policy.
   A browser-local animation alone cannot exercise P4 output or the wire.
4. [ ] P06d: Report generation/composition/copy time, socket acceptance time,
   wire throughput, client receipt and unique presentation cadence separately.
   Reuse P02 and drained-credit evidence. A raw transport throughput control is
   not a browser-video result. At512×384×1byte×60, payload alone is94.37Mbit/s;
   measure negotiated link speed and account for protocol overhead before
   interpreting a limit. Label whole-window versus game-only FPS explicitly.

Author-proposed pressure-relief candidate: lossless RLE of frame differences.
[AGM source inspection](../RESEARCH-001/AGM-RLE.md) records the existing codecs,
payload size proof, representation hazards, full-frame recovery rules and
proposed matched controls. This changes transport only; raw eight-bit output
remains a hard goal. Source inspection is complete; codec/protocol implementation
and firmware testing still require review under P06e. **Author-directed order:
exhaust the five initial RESEARCH-001 candidates C1–C5 before resuming the RLE
investigation, including its host prototype.** Record each candidate's findings
and disposition; initial scouting alone does not satisfy this dependency.

5. [ ] P06e: Review the demonstrated bottleneck and desired visible cadence with
   the Author before changing encoding, damage updates or credit contracts.
   Never obtain a rendering-parity pass by reducing game workload, resolution,
   sprite count or silently displaying stale frames. Golem remains excluded.

**Author-requested fallback — explicit browser frame-rate targets:** if the
current investigation and its resulting measurements fail to yield sufficient
improvement, consider a selectable sustainable output cadence (for example
30 Hz; no rate selected yet). P06e owns review before implementation. Pace
snapshot creation/admission, not merely socket transmission after expensive
composition has already occurred. Bound pending work and prefer the freshest
available frame rather than accumulating latency. Keep game rendering cadence
separate and unchanged; a lower browser target is not a rendering-parity pass
or a replacement for the existing full-frame eight-bit60Hz goal.

Choose any fallback target from repeatable worst-case/tail timings and visual
frame pacing under representative heavy scenes, with explicit headroom. A cap
cannot itself cure a long individual capture stall. Report render completions
and browser presentation separately. This is a deferred contingency, not an
authorized implementation or a change to C1–C5/RLE investigation sequencing.

**Additional Author-requested fallback ideas:** investigate only if we cannot
meet the current **512×384, 64-colour, 60 Hz** output target. This does not
withdraw the longer-term 256-colour/eight-bit transport goal. P06e owns review;
these are ideas, not authorized implementations or performance acceptance.

1. Compare sustainable non-divisor capture rates such as24,32 and45 FPS with
   evenly divisible30 or20 FPS on the Author's fixed60Hz monitor. Use absolute
   deadlines with fractional time carried forward; distinguish throughput from
   visible cadence. Assess uneven frame holds/judder using moving scenes.
2. Evaluate refresh-synchronized browser presentation of complete frames first.
   Verify actual browser/compositor behavior; do not assume automatic frame
   interpolation, tear-free presentation or exact display synchronization.
3. Consider optional client-side frame blending versus motion-estimated
   interpolation. Measure added latency, client CPU/GPU cost, ghosting,
   occlusion artifacts, HUD/palette fidelity and behavior on newly exposed
   scenery. Synthesized frames must be reported separately from real captures
   and must not count as60Hz rendering or transport parity.
4. Game-state interpolation is a separate application-aware possibility, not
   directly available to the generic pixel-only VDP viewer. Do not expand the
   viewer/game protocol without a separately reviewed contract.

Preserve actual game/render cadence and input responsiveness as independent
metrics. No browser technique here establishes faster P4 rendering. Candidate
review and the agreed subsequent RLE investigation retain their sequencing.

## Debrief delivery

D01–D05 complete. The report, official-source audit, reproducible tables and
P01–P06 proposals are committed locally. The accepted British hardware voice
completed with a fresh replacement receipt; unchanged startup and neutral
keyboard readiness verified, SD service exited to Legacy MOS. See
`debrief/notification.json`. Human hearing/review is pending. No performance
experiment, firmware flash/reset, Golem test, emulator change or push occurred.
Only the documentation/research goal is complete; parity remains unproved.
