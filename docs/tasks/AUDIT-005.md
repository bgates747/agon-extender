# AUDIT-005 — Review stock MOS reuse and EMOS UART execution costs

## State

- Status: W1–W2 complete; benchmark-first sequence accepted for documentation freeze. Implementation not started.
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
documentation freeze on 2026-09-10. W3 must follow that disposition. No repair,
instrumentation, core change, firmware build or bench operation has been
performed. Stop after the documentation commit; executable work awaits the
next instruction.

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

## Work — W1–W2 complete; W3 follows the accepted measurement direction

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
3. [ ] **W3 — Define the smallest paired benchmark increment.** The Author
   selected measurement before repairs. Turn D001–D002 into the bounded
   fixture cases, timing boundaries, CTS evidence and validity checks needed
   for implementation. Retain the stock-reuse findings as candidates to
   evaluate after measurement; do not rank their runtime contribution from
   static call counts. Keep D003's automated game fixture deferred. The
   documentation freeze does not start fixture implementation or execution.

## Deliverables and acceptance

Keep the bounded comparison and findings under `docs/tasks/AUDIT-005/`.
Each finding uses a stable `AUDIT-005-Fnnn` ID and
records exact source/symbols, evidence class, affected behavior, stock reuse
candidate, constraints, recommended owner and any missing measurements.
W1 records paths and provenance. W2 records AUDIT-005-F001 through F005:
transmit duplication/overhead, partial-write recovery, caller/flag differences,
receive adaptations and P4 backpressure boundaries. These findings are
unranked; their runtime contribution to lag remains unmeasured.

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
No implementation checklist outside the owning
tasks, firmware version change or qualification promotion follows implicitly.
