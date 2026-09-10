# P4 receive and drawing wait attribution

**Accepted work contract for AUDIT-005 W8 — execution authorized 2026-09-10.**
The Author accepted W7 and the revised contract, requested freezing prior
work, and authorized W8. Commit the findings and this contract before execution.
The Author subsequently requested that the stock VDP queue-draining
comparison lead this investigation. That comparison is the first gate below;
instrumentation remains conditional on what it leaves unexplained.

## Question and scope

What prevents P4 from draining ordinary UART graphics traffic promptly, and
what delays its final pixel reply? W7 measured **3.344 seconds of idle while
P4 withheld permission** within a 4.391-second payload transmission, followed
by about 0.684 seconds to complete the reply. Closing the browser made no
material difference to total workload time. Agon permitted reception during
the final-reply wait. These are accepted observations, not an identified
P4 scheduling defect.

The output of W8 is a source-backed explanation reconciled with measured
timing, and one proposed repair or discriminating test. PORT-003 owns any
later drawing-service repair; PORT-008 owns any later UART-service repair.
EMOS continues to own routing and transport. W8 does not optimize either
firmware, change core assignment, or resume browser-input/parallel work.

## Fixed comparison and bounded research

Use the [W7 evidence](browser-disconnected-findings.md) and the
[W1 identities](baseline-and-path-map.md#selected-sources): P4 console r07
source `52479f0ae9653e293031a1eed1b65f0cec9695cd`, installed build
`uart-excom-console-r07-b2026-09-10-06-31-58Z`, and EMOS
`agon-emos-v0.1.12-b2026-09-10-03-50-35Z`. Verify relevant source and saved
build inputs still match before tracing; preserve unexpected differences.

Keep the r03 SD executable, `RUN . trace count points`, its 32,768 payload
bytes, mode 0, USB keyboard, r03 wiring, baud and browser-off condition fixed.
The [W7 contract](browser-disconnected-control.md) owns those exact inputs,
the five-second client-closure settlement and the CSV annotation exception.
W8 changes P4 executable bytes only if the timing-probe branch below is needed.
Such a build receives its own identity and provenance; it cannot be labelled
the original r07 image. No registry or firmware identity changes in this draft.

Consult the selected official [PLOT documentation][plot] and
[pixel/flush commands][system] first. Pixel queries require prior drawing to
complete; VSYNC/frame timing and draining drawing work are distinct contracts.
Use stock VDP v2.16.0 source only where implementation detail is material;
official documentation, MOS and VDP checkouts remain read-only.

The existing [W2 map](differences-and-reuse.md#p4-backpressure-boundary) bounds
the investigation to these paths:

| Owner and source | Question to resolve |
| --- | --- |
| [P4 console loop](../../../vdp/video/extender/transport/console_hardware.inc) and [stream adapter](../../../vdp/video/extender/transport/console_stream.hpp) | How many parser calls consume this payload, when does the loop yield, and when do RX/reply buffers stop progress? |
| Retained parser, Canvas and [primitive queue](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp) | How many actual drawing primitives does each point enqueue, including state operations? Which enqueue or completion calls wait? |
| [Logical frame service](../../../vdp/video/extender/display/logical_frame_service.cpp), [P4 task adapter](../../../vdp/video/extender/display/p4_frame_service.cpp) and [executor](../../../vdp/video/extender/display/p4_display_controller.cpp) | What drains the queue, with what effective budget/cadence, and can any path drain it outside frame service? |
| [Pixel reply](../../../vdp/video/vdu_sys.h) and console TX | How much delay occurs before parsing the query, waiting for drawing, preparing its reply and admitting reply bytes to UART? |

### Stock behavior to compare first

The read-only discussion established these source differences for the
benchmark's single-buffered, 16-colour mode. They nominate a mechanism to
investigate; they do not yet account for the measured workload.

| Operation | Stock VDP v2.16.0 and selected vdp-gl | Current EDP path |
| --- | --- | --- |
| Background drawing | [Screen setup][stock-screen] enables background execution and disables its time limit. The [VGA worker][stock-worker] wakes on refresh and drains until the queue empties or processing is suspended. | [Screen setup](../../../vdp/video/agon_screen.h) constructs the P4 frame service with its default 64-primitive budget. Each logical-frame service pass applies that fixed count limit. |
| Pixel-query completion | `sendScreenPixel` calls `waitPlotCompletion(false)` by default. [Canvas][stock-canvas] processes pending primitives immediately; this differs from an explicit wait for VSYNC. | The same immediate-flush entry remains. Verify its P4 suspension/wait path and all queued work before attributing reply delay to the background budget. |
| Drawing throughput bound | With the background timeout disabled, this worker has no fixed 64-primitive batch limit. Execution and contention still cost time. | At the declared 16,667-microsecond period, 64 primitives per service pass permits roughly 3,840 primitives/s through that background path. Direct flushes and other execution paths must be accounted for separately. |

The console's separate 64-`processNext` budget counts parser invocations, not
drawing primitives. A VDU command may create multiple primitives. W8 must
verify actual configuration, count those operations and examine pending-tick
handling before using either budget to predict elapsed time. Do not raise a
limit merely because the two implementations differ. Preserve logical frame
ticks, explicit VSYNC/swap behavior, ordering and correct pixel replies when
considering any eventual stock-behavior reuse.

## Work sequence

1. **Compare stock and EDP queue-draining behavior first.** Verify the table
   above against the selected source and installed P4 build inputs, including
   the relevant vdp-gl revision. Trace normal background draining, full-queue
   producer blocking, immediate completion and explicit VSYNC waits on both
   paths. Record which limits are stock behavior, which EDP introduced, and
   which differences the P4 hardware actually requires. Consult the existing
   PORT-003 frame-service contract for the fixed budget's rationale; do not
   treat a prior implementation choice as an unavoidable VDP contract. Produce
   this source comparison before designing any timing probe or choosing a
   firmware change.
2. **Account for the observed workload in the installed source.** Trace a
   plotted point and the final pixel request through the paths above. Include
   padding/control bytes, queue capacity, enqueue/dequeue operations, frame
   budgets, actual RTOS tick duration, parser yielding and reply service.
   Separate limits inherited from stock VDP from limits introduced by EDP.
   Calculate what each verified service limit predicts for this exact command
   count, including buffered work remaining at the final query. Compare that
   prediction with both the 4.391-second send and 0.684-second tail, not just
   their sum. Do not charge overlapping work on two cores twice or call
   elapsed time inside a function pure CPU time.
3. **Choose the smallest sufficient evidence.** Use the stock comparison and
   workload calculation from steps 1–2 as a mandatory gate. If they explain
   the measured timing and identify one concrete limiting mechanism, stop
   with the calculation, uncertainty and a proposed controlled validation of
   that mechanism. Numerical agreement is supporting evidence, not proof of
   an unobserved runtime state. Do not add instrumentation merely to fill a
   checklist. If competing waits remain, implement only the bounded probe
   below, after the approved contract is frozen.
4. **Report attribution and stop.** Relate the internal evidence to CTS-high
   idle and final-reply delay. State how much remains unexplained. Recommend
   one change or next test, its owning component, expected effect and required
   correctness checks. Leave the repair for Author review. Do not silently
   expand this work into a renderer rewrite, deadline relaxation, priority
   sweep, new scheduler architecture or full-suite rerun.

## Conditional timing probe

This branch follows the completed stock comparison and workload calculation.
The agent first records the specific competing explanations that remain;
probe only the observations needed to distinguish them. The agent chooses
sites from the verified call path, recording that choice and the
executable/record format before the build. P4 records
bounded, allocation-free RAM counters/timestamps at those sites. Prefer
command, queue-wait and frame-service boundaries over per-byte logging.

1. Distinguish UART/parser progress, primitive enqueue waits, frame wake/drain
   work, and final-query/reply progress. Record primitive counts and queue
   occupancy needed to test the source model. Measure snapshot work only if
   the inspected path shows it can still execute without clients. Preserve
   nested interval boundaries instead of summing inclusive times as though
   they were disjoint. Unobserved scheduler time remains unassigned.
2. Use one monotonic P4 timebase and task-owned bounded records with an
   explicit publication boundary. A record overflow, incomplete interval,
   restart or inconsistent count makes the affected attribution incomplete.
   Freeze the record after completion or a bounded watchdog; never overwrite
   an earlier completed record silently. Diagnostics must not drive GPIOs,
   alter UART packets, reorder commands or change queue sizes/service budgets.
3. Align observations to the existing marker, exact payload and final query;
   use the ordinary wire trace for UART edges and CTS. P4 parsing the marker
   can lag its arrival on the wire: do not equate those timestamps or pretend
   the P4 and analyzer clocks are synchronized. Use event order and matched
   intervals, explicitly recording alignment uncertainty.
4. Retrieve frozen records through a development-only HTTP diagnostic after
   the measured exchange. Arm/configure it before acquisition; the host makes
   no diagnostic requests during the timed window. No video client is opened
   and no log is streamed during measurement. Do not open P4 serial for
   retrieval, because that can reset the board. Export build ID, capture mode,
   completion/drop state and the recorded observations for durable host storage.
5. Allow at most **two hardware runs of the same instrumented P4 image**:
   probe recording disabled, then enabled, both using the existing browser-off
   case. This checks observer effects without a parameter sweep. Compare both
   against W7 and each other, including stage durations and stall pattern;
   report timestamp/recording cost. Two observations do not establish a
   variance estimate or zero probe overhead. If the disabled case no longer
   resembles the baseline, or recording obscures the behavior under study,
   report the discrepancy and stop rather than infer a repair from it.

## Validation and physical handover

1. First validate probe accounting locally with meaningful known-delay,
   nested-wait, overflow and completion cases, limited to the sites actually
   used. Verify the same parser bytes, reply values, ordering and recovery
   with recording off/on. Existing emulator validation remains a functional
   gate; host/emulator timings are not physical P4 timing evidence.
2. Preserve the r07 rollback bundle. Freeze identified instrumented inputs
   before building a physical candidate, record exact outputs and footprint,
   and present the reviewable deployment. Standing identity approval applies;
   firmware deployment follows the existing Author-approved hardware gate.
   Reading this draft, or later freezing it, does not itself request a flash.
3. Reuse the four UART/CTS probes and 24 MHz, 720-million-sample acquisition.
   Record the new procedure/build and probe selection distinctly from W7.
   Keep the closure/settlement gate, unchanged CSV annotation override and
   noninteractive startup. The operator resets only Agon at the host cue;
   no extra P4 reset occurs between the two measurements. The host collects
   frozen diagnostic records after each completed acquisition/exchange.
4. Require full payload/reply coverage, independent decoding, no framing or
   flow-control violation, unchanged SD binary, correct pixels and CSV footer
   with successful Legacy return. Retain first ordinary MOS timeouts. Match
   each new CSV to its capture and diagnostic record, preserve prior files,
   and compare wire/clock boundaries at the clock's actual resolution.
5. Keep physical actions governed by `HARDWARE.local.md` and the active bench
   constraints. Finish preparation before the labelled emulator attention cue.
   The handover supplies one short launcher/instruction set; returned files
   provide evidence without requiring routine screenshots.

## Completion and evidence boundary

Store the source accounting, observations and conclusion in this task silo;
leave one next proposed action in the task detail. Preserve the accepted W7
evidence and its raw manifests unchanged. A source-only result must say so;
an instrumented result must separate measured waits from inferred scheduler
causes and from overhead introduced by the probe. No speedup or qualification
claim follows until a separately approved repair is measured.

The Author authorized W8 on 2026-09-10 after reviewing this sequence. Freeze
W7 acceptance and this contract before workload accounting or the conditional
probe branch. The physical deployment gates above remain in force. The agent
stops after W8 findings for another Author review; repair implementation is
outside this authorization.

[plot]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/PLOT-Commands.md
[system]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md
[stock-screen]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h
[stock-worker]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgabasecontroller.cpp
[stock-canvas]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/canvas.cpp
