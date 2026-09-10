# AUDIT-005 — Review stock MOS reuse and EMOS UART execution costs

## State

- Status: W1–W7 results accepted. W8 contract accepted and execution authorized after the requested freeze: stock VDP versus EDP queue draining, workload accounting, then conditional instrumentation only if needed. No repair is authorized.
- Task drafted: 2026-09-10
- Started: 2026-09-10
- Finished: --
- Preserved Extender checkpoint: `258d0d9` (partially working RGB222/ExCom)

The Author accepted the plan, then accepted the
[W1 source identities and path map](AUDIT-005/baseline-and-path-map.md) and
authorized W2 on 2026-09-10. The
[W2 difference/reuse report](AUDIT-005/differences-and-reuse.md) is complete,
with five unranked findings and static call-site evidence from the matching
deployed ELF. The Author selected paired measurements before performance
repairs, followed by personal Nurples playtesting, and requested this
documentation freeze on 2026-09-10, recorded in commit `721640c`. The Author
subsequently authorized W3. The
[paired benchmark plan](AUDIT-005/paired-benchmark-plan.md) was reviewed before implementation: one SD application, four output entries, two payloads, paired timings
and a selected ExCom waveform capture. The Author then requested SD deployment,
authorizing implementation. The [fixture and usage instructions](AUDIT-005/README.md)
now implement that plan using the installed firmware. All 48 rows pass local
functional validation with two native VDP references and a raw FAT image;
the 24 ExCom payload windows match the expected bytes. The first physical run
saved eight Legacy rows and stopped before the first ExCom workload. The
short diagnostic identified a late reply, and the r03 measurement revision
now completes all 48 hardware rows. The [paired hardware comparison](AUDIT-005/hardware-baseline.md)
records the results and the remaining attribution boundary. No performance
repair, firmware rebuild or flash has occurred.

## Purpose and review principle

Determine where EMOS can retain or minimally adapt stock MOS's proven code
instead of reimplementing the same work. Start with the ordinary VDU transmit
path that can stall applications during ExCom gameplay. The intended result
is the smallest justified EMOS addition around stock behavior, with each
remaining departure explained by a concrete Extender requirement.

EMOS remains the complete replacement MOS firmware on the eZ80, with sole
ownership of ordinary VDU routing, Extender transport and committed mode.
"Thin wrapper" describes implementation economy, not a separate MOS companion
or permission for applications to access UART1/GPIO directly. The eZ80's UART0
continues to serve mainboard VDP; EMOS uses UART1 over r03 PC0–PC3 wiring for
EDP traffic and return packets. Shared ground and the existing native USB
keyboard path remain as documented by the design and current bench record.

C versus assembly is not itself a finding. Prefer a proven stock routine when
it supplies the required contract; identify unnecessary calls, bookkeeping,
copies and waits by tracing the actual path. Retain necessary UART ownership,
flow control, interrupt handling, mode coordination and recovery behavior.
Do not discard accepted correctness fixes merely to reduce the diff to stock.

## Motivation and evidence limits

The [PORT-003 checkpoint](PORT-003.md#partially-working-checkpoint--2026-09-10)
preserves working USB input, ExCom entry, slideshow and RGB222 presentation,
but the Author reports severe typing and Nurples lag. During rapid fire,
Nurples' laser bolts appear closer together on EDP than on mainboard VDP.

The preceding read-only scan of Nurples repair commit `4a52199` found an
elapsed-MOS-time firing cooldown, movement of four pixels per game update,
and recharge per six updates. A slower game loop relative to MOS time could
produce that spacing. The game reads the held-key map for continuous fire and
waits on MOS time for VBlank pacing. These are inherited investigation notes,
not completed findings from this audit or a measured cause of the slowdown.

The prior EMOS scan identified synchronous transmission with per-byte C
calls, deadline checks and interrupt bookkeeping. P4 receive backpressure,
EMOS execution overhead and P4 rendering/presentation cost remain hypotheses
or possible contributors. Existing logs without a UART timeout do not exclude
shorter CTS stalls. Configured baud rate does not establish effective command
throughput. Do not label any path slow solely because it is written in C.

## Accepted measurement sequence — 2026-09-10

The Author wants measurements before choosing performance repairs. The
following decisions supersede proceeding directly from static overhead to a
code change; they do not change the W1/W2 evidence or establish a cause of lag.

| ID | State | Decision |
| --- | --- | --- |
| AUDIT-005-D001 | Accepted | First run a paired Legacy/ExCom pathway benchmark. Use its measurements to choose a bounded improvement, repeat the benchmark, then have the Author playtest Nurples for a subjective assessment. |
| AUDIT-005-D002 | Accepted | The initial fixture sends identical data through single-byte output, counted blocks, delimited strings and C `putch`, in both modes. Separate foreground sending time from a verified drawing-completion/reply boundary, and capture CTS to identify receiver backpressure. Buffer measurements in RAM and save to SD after the timed sections. |
| AUDIT-005-D003 | Accepted; deferred | Automated Nurples testing waits until the paired benchmarks and the Author's subsequent playtest establish whether it is useful. If resumed, EDP must generate ordinary press/release keyboard packets over its UART to EMOS; EMOS updates its normal keyboard state and Nurples reads it normally. A game-internal control replay omits the return traffic/receiver work being investigated and is not the selected approach. |

The paired comparison uses the same EMOS build, with Legacy routing to
mainboard VDP and ExCom routing to EDP. Record the selected EMOS, mainboard VDP,
EDP and fixture identities. Timing the output call includes any UART wait;
it must not be labelled pure EMOS CPU cost. Likewise, drawing completion is
distinct from browser presentation. Reuse the completion-boundary research in
[QUAL-003](QUAL-003.md#completed-visual-review-and-performance-request--2026-09-10)
without making generalized callbacks a prerequisite for the first benchmark.

For a later Nurples fixture, retain the proposed fixed random seed,
repeatable movement/fire schedule and buffered game-loop/output/firing
diagnostics. EDP owns scheduled event emission; the Agon game must receive
normal EMOS keyboard effects. Keep collision detection running but suppress
player damage/death in that test variant, preserving the collision-processing
workload. Record the actual event timing rather than claiming an identical
game trajectory merely because the input schedule repeats. No Nurples changes
or scripted-input firmware work are part of the immediate increment.

[MicroPython support](PORT-016.md) remains an independent future capability;
neither it nor [P4-local SD access](PORT-007.md) is a prerequisite for these
measurements. The initial fixture can save its results to the Agon's own SD.

## Scope and boundaries

1. Compare stock MOS and active EMOS single-byte and counted-stream output,
   from application/CLI entry through routing, CTS/TX readiness and the UART
   write. Include terminated strings where they share that path.
2. Check the interrupt and return-packet side for stock-code reuse: packet
   framing, keyboard effects, sysvars, virtual key map and callbacks. Follow
   CLI and mode-selection code only as needed to explain ownership and shared
   transmission paths; separate infrequent transitions from per-byte work.
3. Inspect the P4 receive/parser/render boundary only far enough to identify
   where EDP can exert backpressure. Record those dependencies under PORT-003
   or PORT-008; do not turn this into a second full VDP port audit.
4. Preserve stock application ABI, character/VDU ordering, keyboard behavior,
   mainboard clock service and existing failure/recovery guarantees. Identify
   any guarantee that stock reuse alone cannot provide before proposing code.
5. Exclude gameplay changes, parallel transfer, browser keyboard input, audio,
   USB schematic work, relocatable modules, new APIs and broad MOS refactoring.
   Do not re-audit unrelated storage or peripheral code.

## Existing authorities and starting references

1. [AUDIT-004 baseline and research map](AUDIT-004/baseline-and-research-map.md)
   pins stock MOS v3.0.2 at `8336409351ee5314e02801a7b72a4f1bb5282519`,
   VDP v2.16.0 at `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, and the
   official documentation snapshot. Its
   [MOS traces](AUDIT-004/trace-mos-interfaces.md) and
   [primary protocol traces](AUDIT-004/trace-primary-protocol.md) provide
   existing contracts to reuse, not an instruction to repeat the inventory.
2. Read official `agon-docs/docs/mos/API.md`, `docs/mos/Keyboard.md` and
   `docs/vdp/System-Commands.md` before following implementation. In stock
   `agon-mos`, begin with `src/serial.asm`, `src/uart.c`, `src/interrupts.asm`
   and the packet/effect routines identified in AUDIT-004. W1 verifies the
   official release references without modifying those checkouts.
3. In project-owned `agon-emos`, begin with `src/serial.asm`,
   `src/emos_console.c`, `src/emos_keyboard.c`, `src/emos_keyboard_io.asm`
   and `src/uart.c`. The installed identity recorded by the checkpoint is
   `agon-emos-v0.1.12-b2026-09-10-03-50-35Z`; W1 must recover and record its
   exact source/build provenance instead of assuming the current checkout
   matches the deployed binary.
4. P4 r07 source is `52479f0ae9653e293031a1eed1b65f0cec9695cd`.
   Begin with [console reception](../../vdp/video/extender/transport/console_hardware.inc),
   [frame service](../../vdp/video/extender/display/p4_frame_service.cpp)
   and [display execution](../../vdp/video/extender/display/p4_display_controller.cpp).
   [Deployment and observation evidence](../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-33-58Z/README.md)
   records the installed candidate and the limits of functional acceptance.
5. [PORT-008](PORT-008.md) owns transport implementation/qualification;
   [PORT-003](PORT-003.md) owns P4 display execution/presentation;
   [QUAL-003](QUAL-003.md) retains graphics comparison and benchmark work.
   Reconcile existing defects and accepted remedies before creating new ones.
   Keep checkout locations and private deployment details in ignored records.

## Work — W1–W7 accepted; W8 authorized

1. [x] **W1 — Pin the comparison and map the active paths.** Verify exact
   stock release, EMOS deployed/source and P4 source identities, documenting
   any mismatch or local changes. Official checkouts remain read-only.
   Produce one compact stock-versus-EMOS call-path table for ordinary byte,
   stream and return-packet handling, with entry symbols and execution
   contexts. Stop expansion into unrelated MOS subsystems. Completed:
   [source identities and path map](AUDIT-005/baseline-and-path-map.md).
2. [x] **W2 — Account for differences and reusable stock code.** For each
   added operation on those paths, record its purpose, frequency (per byte,
   packet or transition), blocking/interrupt effects, stock equivalent and
   reuse constraints. Review register/flag preservation, UART0/UART1 register
   and flow-control differences, buffering, ordering, callback context and
   failure handling. Use already available matching listings if they help;
   distinguish static instruction/call counts from measured time. Identify
   definite duplication separately from necessary adaptations and unmeasured
   performance suspects. No new build or instrumentation is part of W2.
   Completed: [difference/reuse report](AUDIT-005/differences-and-reuse.md).
3. [x] **W3 — Define the smallest paired benchmark increment.** The Author
   selected measurement before repairs. Turn D001–D002 into the bounded
   fixture cases, timing boundaries, CTS evidence and validity checks needed
   for implementation. Retain the stock-reuse findings as candidates to
   evaluate after measurement; do not rank their runtime contribution from
   static call counts. Keep D003's automated game fixture deferred. The
   documentation freeze does not start fixture implementation or execution.
   Completed: [paired benchmark plan](AUDIT-005/paired-benchmark-plan.md).
   The existing resident C `putch` is exercised through the public `VDU` CLI
   command, with parser/caller cost explicitly included; no new firmware API
   is proposed. Current probes measure ExCom UART1, not internal Legacy UART0.
4. [x] **W4 — Implement and locally validate the SD benchmark.** Author
   authorized through the request to deploy the reviewed plan. Added the
   independently built application, identity/provenance, raw-FAT emulator
   review, result validation and scoped SD deployment. Full 48-row review and
   exact ExCom byte checks pass; these are functional, not P4 timing results.
   The Author approved freezing the reviewed source, profiles and hardware
   evidence on 2026-09-10. The requested exploratory SD test
   does not require a new EMOS or EDP build.
5. [x] **W5 — Collect the paired hardware baseline.** Deploy the identified
   application, obtain the Author's completed run and return of the SD, retain
   valid CSV results, then choose a relevant ExCom waveform capture. All 48
   r03 hardware rows validate; [results and interpretation](AUDIT-005/hardware-baseline.md)
   select counted point output for the next trace. Keep emulator timings
   separate. The independent filesystem issue
   is tracked in [REMED-003](REMED-003.md); it does not authorize a MOS change.
6. [x] **W6 — Separate sender time from P4 backpressure.** Author-authorized
   on 2026-09-10 after freezing the completed baseline: capture the existing `trace count points` invocation
   with the UART1 data and flow-control probes. Validate marker/payload/reply
   coverage and compare eZ80 TX gaps with P4 CTS state. Preserve the current
   firmware and workload. Use that evidence to recommend the smallest repair;
   this item does not authorize a speculative firmware optimization. Prepare
   and check the acquisition/analysis tools and an exact operator run sheet,
   including full-window coverage, before the physical reset cue. Preserve
   prior SD results and use the existing executable; the operator resets
   Agon after the analyzer is ready. No P4 serial open or reset is required. The executable
   [capture procedure](AUDIT-005/uart-cts-capture.md) records exact preparation,
   invocation, coverage and attribution checks. Preparation passes six
   synthetic waveform tests, five result tests, the one-row emulator review
   and two full passive acquisitions. The physical
   [counted-point capture](AUDIT-005/uart-cts-findings.md) now passes exact
   payload/reply/framing checks: 3.407 of 4.456 payload-wire seconds are
   inter-byte idle with P4 withholding CTS permission. The returned one-row
   CSV records 4.450 s send and 0.617 s tail, agrees with wire intervals within
   one clock quantum, and confirms successful Legacy return. Measurement is
   complete. Recommend one same-workload browser-disconnected control before
   choosing a specific P4 service repair. The Author accepted these findings
   and authorized W7 on 2026-09-10.

7. [x] **W7 — Compare the same workload with browser video disconnected.**
   The Author approved the [formal control contract](AUDIT-005/browser-disconnected-control.md)
   and execution on 2026-09-10. Commit the completed W6 result and contract,
   prepare the recorded browser-off condition, then capture one unchanged
   counted-point run. Keep P4 up, Ethernet and keyboard connected, and all
   video clients closed through acquisition and normal Legacy return. Compare
   the returned CSV and UART/CTS measurements with the connected W6 run.
   Record the fixed CSV browser-annotation override explicitly. Stop with
   the comparison and a recommended next action; do not implement a repair.
   Preparation is ready: r02 condition metadata, closure/settlement gate,
   distinct launcher, hash-verified Pi staging and unchanged SD all pass.
   Fifteen local preparation tests pass. Run
   `AUDIT-005-2026-09-10-20-03-35Z` and returned `00000005.CSV` now pass
   acquisition, exact waveform, condition, integrity, clock and Legacy-return
   validation. The [comparison](AUDIT-005/browser-disconnected-findings.md)
   measures 5.075 s total versus 5.081 s connected, with 3.344 s still idle
   under P4 backpressure. Longest gaps shrink from 154 to 14 ms; this does not
   remove the throughput bottleneck. The Author accepted this test on
   2026-09-10, agreeing there is no material difference in total time with the
   browser disconnected. No further capture, firmware change or repair has
   started. The original collection record retains its at-collection review
   state; acceptance is recorded separately.

8. [ ] **W8 — Attribute P4 receive and drawing waits.**
   The [accepted work contract](AUDIT-005/p4-wait-attribution.md) first compares
   stock VDP's background drain and immediate-flush behavior with EDP's fixed
   primitive budget. This is a mandatory gate before instrumentation. Then
   count parser/primitive operations and predict send and final-reply timing
   for the exact W7 workload, distinguishing the two unrelated 64-operation
   budgets. Examine reuse of stock behavior before new scheduling machinery.
   If ambiguity remains after that comparison and calculation, use bounded RAM
   timing and at most two browser-off hardware runs of one probe image,
   recording disabled/enabled, to distinguish internal waits and observer
   effects. Keep EMOS and the SD workload fixed. Stop with attribution and
   one proposed repair or discriminating test; implementation of that repair
   remains outside W8. The Author approved freezing W7 findings and this
   contract, then proceeding, on 2026-09-10. The existing emulator and
   physical deployment gates still apply.

## Deliverables and acceptance

Keep the bounded comparison and findings under `docs/tasks/AUDIT-005/`.
Each finding uses a stable `AUDIT-005-Fnnn` ID and
records exact source/symbols, evidence class, affected behavior, stock reuse
candidate, constraints, recommended owner and any missing measurements.
W1 records paths and provenance. W2 records AUDIT-005-F001 through F005:
transmit duplication/overhead, partial-write recovery, caller/flag differences,
receive adaptations and P4 backpressure boundaries. W2 left those findings
unranked. W6 now measures P4 backpressure as the dominant idle component of
counted-point output; the internal P4 contributor and individual EMOS costs
remain unisolated. W3 provides
the concrete cases, autoexec, timing/reply boundaries, SD records and capture
coverage requirements for the next increment; it is not benchmark evidence.

Acceptance requires a source-backed path comparison, an explicit reason for
each material EMOS departure, and a reviewable next increment small enough to
implement and test independently. The Author selected the paired benchmark
as that next direction. Claims about speed require appropriate
evidence; a smaller source diff alone proves neither performance nor semantic
equivalence. List expected checks for any later repair, including byte/stream
ordering and ABI, CTS pause/resume, return-packet/keyboard effects, clock
continuity and mode/failure recovery. Any subsequently authorized executable
change inherits the existing emulator review and hardware qualification gates.

The Author accepted the plan before W1 and reviews each authorized work item's
result before proceeding. A repair or measurement requires separate disposition.
No firmware version change or qualification promotion follows implicitly.

## Implementation notes — 2026-09-10

The first physical attempt saved eight valid Legacy rows, then timed out
before the first ExCom workload. The browser showed row 9; the saved footer
reports status 15 and successful Legacy return. The preserved
[CSV and collection record](AUDIT-005/evidence/first-hardware-attempt/)
contain no invented run-start timestamp. Source inspection locates the
timeout at the pre-workload pixel query; EMOS transmit timeout is status 2,
whereas MOS reply-wait timeout is 15. No paired performance conclusion is
available. This does not demonstrate an SD failure despite MOS's generic
`Volume timeout` message.

The r02 SD application added a short `probe` invocation to record initial,
post-clear and post-point queries, with unchanged firmware. On the first
timeout it observes the same request for nine further bounded API calls,
records any late reply, and still returns the original failure. It does not
substitute a permissive deadline into the benchmark. The retained MOS
`wait_VDP` uses a 250,000-iteration CPU loop, not a wall-clock deadline;
the probe records actual clock deltas. Normal/late/absent emulator checks
pass, including failure preservation, prior-file preservation and Legacy
recovery. A combined raw-image startup also runs the independent filesystem
probe before the pixel diagnostic. At that preparation W5 remained incomplete
pending physical observations; no firmware remedy was selected.

The returned physical [r02 diagnostic](AUDIT-005/evidence/pixel-probe-hardware/)
now records successful initial ExCom pixel/mode replies, followed by a
post-clear pixel first timeout at 30 ticks and successful eventual reply at
66 ticks. At the selected nominal 120 units/s these are about 250 and 550 ms.
The pixel is correctly black; Legacy return succeeds. This identifies the
benchmark's premature abort but does not isolate the underlying P4 delay.

The r03 measurement revision uses a common 600-tick reply observation bound
for both routes, checking after each stock API call, with at most 24 calls as
a stopped-clock backstop. It saves the first wait status and actual setup/
completion intervals, rejects a reply beyond the measurement bound, and never
retransmits. This is a fixture methodology change, not a firmware performance
fix or a claim that stock API deadlines are satisfied. Probe mode retains its
first-timeout-fails semantics. The returned r03 file now supplies the complete
paired matrix: all 48 rows pass final status/pixel/clock/mode checks and Legacy
return. Raw CSV, hashes, per-case ranges and interpretation are retained in
the [hardware baseline](AUDIT-005/hardware-baseline.md). All 24 ExCom setup
queries and 18 direct-output completion queries exceeded the ordinary MOS
wait; none did in Legacy. Measurement completion does not remove those misses.
W5 is complete; W6 holds the selected waveform measurement before a repair.

The raw FAT image is deliberate: Fab's directory-backed filesystem does not
honour create-new exclusivity and does not implement mapped-file sync. The
standalone REMED-003 probe reproduces both failures in unchanged upstream Fab;
the same probe passes in raw-image mode and now on physical hardware. Its
unchanged deployed executable hash and saved sentinel contents were verified.
The report is ready for Author review and remains unsubmitted.
The application retains real sync/close checks instead of working around the
emulator defect in hardware code. FatFS timestamp queries are permitted in
the review peer outside measured intervals.

Targeted version-record validation passes. The full repository validator
still rejects the pre-existing r02 connectivity hash mismatch; its current
content is identical to HEAD. This unrelated, held hardware definition was
not altered or silently requalified by the benchmark work.
