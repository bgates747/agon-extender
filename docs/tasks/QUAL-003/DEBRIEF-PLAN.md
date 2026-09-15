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

**AGENT-PROPOSED for this Author-requested review; not yet approved for execution.**
These steps refine the open N04ae-iii/N03–N05 work, not a second independent
performance queue. Author clarification: **all Golem testing remains on hold
until further notice**. Only the current eZ80-projection Rally is eligible below.
Review one chunk at a time; an actionable finding is a stopping point for a
hardware voice report, not permission to consume the entire backlog.

### P01 — Establish current comparison and diagnostic accounting

1. [ ] P01a: Verify current P4/EMOS/mainboard identities and actual memory/task
   settings, source/assets/fixture hashes, safe startup and rollback. Select
   the archived r43 behavior parent, retaining optional completion observation
   but excluding the r44 native-acquisition probe for the reference. No MOS
   experiment. Do not infer installed options from repository defaults.
2. [ ] P01b: Run the existing r05 SW fixture with a fresh nonce and full180second
   wired production observer, then the same fixture without output. Record
   completion spacing, enqueue spacing, pending counts, whole-game coverage,
   terminal pixels and service health. Reverse order for one repeat if the
   contrast is material or apparently passing. Earlier output-off data used
   different firmware/query timing; it cannot answer this current comparison.
3. [ ] P01c: If pre-enqueue variation remains, define one bounded diagnostic
   build that measures the missing intervals: parser/owner runnable and blocked
   time, RX driver buffered work, software reply-gate duration, UART driver
   activity, foreground/native/input-lock acquisition, timer wake lateness.
   Prefer existing SDK task tracing or a bounded event buffer; determine its
   actual support, memory cost and interruption overhead before selecting it.
   Aggregate around owner batches, not a timestamp or print per UART byte.
   Record task names, priorities, affinities and relevant ISR placement.
4. [ ] P01d: Validate the probe against the same unmodified reference condition;
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

### P02 — Separate output composition from network scheduling, if warranted

1. [ ] P02a: On one frozen diagnostic image, compare four explicitly labelled
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
   dominates instead, investigate that measured path. No blanket priority raises.

**Decision gate:** Reproduce or remove the pre-enqueue tail while accounting for
unchanged work. Return to the baseline after a failed control. Do not retry the
already rejected same-core snapshot priority2/4 configurations without new
contradictory evidence. No renderer redesign based solely on task priority lists.

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
   road and audio/HUD regressions as correctness gates.
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

### P06 — Separate browser-delivery optimization, only if selected

1. [ ] P06a: Decide with the Author what unique visible frame cadence is required
   after rendering parity. Existing goal requires streaming active; it does not
   turn nominal60Hz metadata into60 distinct browser frames.
2. [ ] P06b: Measure actual link rate, full payload/header bytes, snapshot count,
   socket acceptance, browser receipt/presentation and host scheduling. Reuse
   drained-credit controls. At512×384×1byte×60, payload alone is94.37Mbit/s;
   output bandwidth must be budgeted rather than inferred from renderer speed.
3. [ ] P06c: Any encoding/damage/credit change is a separately reviewed output
   contract. Never obtain a rendering-parity pass by reducing game workload,
   resolution, sprite count or silently displaying stale frames.

## Debrief delivery

D01–D05 complete. The report, official-source audit, reproducible tables and
P01–P06 proposals are committed locally. The accepted British hardware voice
completed with a fresh replacement receipt; unchanged startup and neutral
keyboard readiness verified, SD service exited to Legacy MOS. See
`debrief/notification.json`. Human hearing/review is pending. No performance
experiment, firmware flash/reset, Golem test, emulator change or push occurred.
Only the documentation/research goal is complete; parity remains unproved.
