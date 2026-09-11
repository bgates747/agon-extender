# AUDIT-006 — Frame execution, synchronization and output-clock review

Source review for W6, 2026-09-10. This is supporting evidence for the complete
video-backend audit, not an accepted replacement architecture or a performance
measurement. No firmware, game, media or hardware was changed for this review.

## Bound inputs and official behavior

1. Project source: `047ffe8caade708a4b867381fff7e8f0023f3782`, the frozen WIP and
   expanded audit contract. The actual console closure is
   [p4-console-source-selection.json](../../../vdp/pio/p4-console-source-selection.json).
   It selects the retained `video.ino` through `p4_console.cpp`, common Canvas
   and `displaycontroller.cpp`, and project P4 frame/controller/network code.
   It does **not** compile the stock concrete VGA controllers or their worker
   and scanline ISR implementation.
2. Stock VDP: v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; the reference
   checkout was clean and exactly on that tag. Graphics library: selected
   `all-the-plots`, `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Stock source links
   below use the retained vendor copy at that selection. The parent audit
   provides the complete independent provenance verification.
3. Official documentation selection:
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
   [System commands](../../../../../agon-docs/docs/vdp/System-Commands.md),
   sections `&C3` and `&CA`, distinguish swap/wait-for-VSYNC from forcing the
   drawing queue to complete. [Screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md)
   documents the off-screen drawing and next-VSYNC swap contract. Reading a
   screen pixel is an example of an implicit drawing flush. These are not
   claims that a browser has displayed the completed image.
4. Selected P4 configuration was checked in the existing generated
   `vdp/.pio/build/p4-console/config/sdkconfig.h`, not inferred from a host
   test. It selects two cores, 1,000 Hz FreeRTOS ticks, Arduino loop core 1,
   and the `esp_timer` task on core 0. The local ESP-IDF 5.5.5 definitions set
   `configMAX_PRIORITIES=25` and timer task priority 22. Generated files are
   observations of the existing build, not new tracked authorities.

## Execution map

Stock VDP parser task (`video.ino::processLoop`, core 0, priority 3) processes
commands and keyboard events. In a single-buffer mode Canvas normally admits
primitives to the shared 1,024-entry queue. `VGABaseController::primitiveExecTask`
drains that queue, updates software sprites, then waits for a frame notification.
The official screen facade disables the worker's optional time budget. The
physical depth ISR independently converts/copies and decorates scanlines,
increments `frameCounter`, and notifies the worker near the frame boundary.
The ISR does not wait for the drawing queue to empty.

The stock split is **not** simply “all drawing on one core, all communications
on the other.” `FABGLIB_VIDEO_CPUINTENSIVE_TASKS_CORE` is the opposite of the
configured Wi-Fi task core; the ISR is explicitly allocated there. The drawing
worker is priority 5 on `CoreUsage::quietCore()`. In the official classic-ESP32
Arduino configuration (Wi-Fi core 0), that means ISR/core 1 and drawing
worker/core 0, sharing core 0 with the lower-priority parser. Stock setup uses
Arduino core 1. Sources: official
[`video.ino`, setup/processLoop](../../../../../agon-vdp/video/video.ino),
[`fabglconf.h`](../../../vdp/vendor/vdp-gl/src/fabglconf.h) lines 143–152,
[`fabutils.h::CoreUsage`](../../../vdp/vendor/vdp-gl/src/fabutils.h) lines
1296–1301, and `VGAPalettedController::setResolution` below. Core numbers are
configuration-dependent; the relative relationships and explicit pinning are
the portable facts.

P4 keeps parser core 0/priority 3 but the selected console runs
`runConsole`, not the stock unbounded `processNext` loop. An unpinned
priority-23 `extender-frame` task consumes software timer ticks, advances the
public counter, drains drawings, shows software sprites and composes a requested
snapshot **in that order**. Only afterward does it publish the frame notice.
An independent network worker (unpinned, priority 3) and HTTP service send the
immutable snapshot. `esp_timer` is task-dispatched, not a rendering ISR; its
callback records a tick and notifies the frame task. Browser credits govern
which snapshots are requested, not stock command semantics.

There are additional drawing owners on **both** implementations: common
`processPrimitives()` draws synchronously in its caller while background work
is suspended; in double-buffer mode ordinary primitives execute immediately
in their caller and only `SwapBuffers` is queued. Any “sole renderer owner”
description must account for these paths.

## Coverage and disposition ledger

All stock library anchors in this table refer to commit `ac2dd598`; official
VDP anchors refer to `c7ac293d`. Line numbers describe the reviewed selection.
“Restore” is a proposed disposition for W7, not authorization to edit code.

| ID / region | Stock implementation | Selected P4 counterpart / exactness | Consequence, dependency and proposed disposition |
|---|---|---|---|
| FE-01 Parser/task ownership | Official `video.ino::setup/processLoop` lines 98–157: pinned core 0, priority 3; process one command plus normal housekeeping per iteration. | Project `video.ino::setup/processLoop` lines 254, 377; `console_hardware.inc::runConsole` lines 67–174 retains task placement but replaces loop, with up to 64 command iterations, key processing, bounded preactivation recognizer and `delay(1)`. | UART/session/input adaptation explains a transport seam, not arbitrary video scheduling changes. Keep the EMOS authorization seam; compare batching/yield costs separately. No source evidence here establishes that a 1 ms yield is necessary or the measured bottleneck. |
| FE-02 Queue admission and payload lifetime | `displaycontroller.cpp::setDoubleBuffered/addPrimitive/primitiveReplaceDynamicBuffers` lines 495–584: queue 1,024 in single buffer, 1 in double buffer; FIFO blocking admission; dynamic path/matrix copies retained until executor consumes them. | Same selected common implementation, with P4 virtual primitive methods. | Retain exactly. Blocking queue admission is intentional upstream backpressure. A different consumer changes throughput without changing this source; preserve all dynamic-payload ownership during extraction. |
| FE-03 Background worker | `vgabasecontroller.cpp::primitiveExecTask` lines 781–807: drain until empty or suspension, optional budget disabled by official `agon_screen.h::changeResolution` line 230; showSprites; await notification. | `p4_display_controller.cpp::executeFrameWork` lines 184–210 copies the no-timeout drain and showSprites, then adds full requested snapshot composition under its execution flag. | Drain policy is restored stock behavior. Snapshot completion is an added dependency with measured harm (F001); no processor or browser requirement makes queue emptiness a prerequisite for output time. Restore stock separation, preserving the exact portable worker body wherever feasible. |
| FE-04 Tick notification/backlog | Each depth ISR increments frameCounter and notifies the drawing worker. Worker calls `ulTaskNotifyTake(pdTRUE, portMAX_DELAY)`, coalescing accumulated notification counts into one next drain. | `p4_frame_service.cpp::timerEntry/taskLoop` lines 100–121, `logical_frame_service.cpp::recordTicks/servicePending` lines 45–119: counted/saturating backlog, decrement one edge per full execute call, replay until empty. | This is new execution policy, not a required timer binding. Backlog replay schedules many full frame passes after a stall. Restore separate elapsed frame time and coalesced drawing wakeup semantics; do not retain a full drawing/snapshot pass per missed edge by default. |
| FE-05 Frame counter | `vga2/4/8/16/64controller.cpp::ISRHandler` increments at lines 778/812/777/820/744 respectively, before deciding whether to notify a suspended worker. | `LogicalFrameService::servicePending` line 75 advances the atomic proxy only just before a combined frame pass; timer recording alone leaves it unchanged. | Source-proven semantic departure: elapsed output time stops during a long P4 drain and is later replayed. `Context::checkForVSYNC` uses it for frame waits, idle cursor/paged mode and VSync callbacks. RISC-V atomic access may be justified; moving time ownership into drawing completion is not. Restore independent output-clock advancement. |
| FE-06 Frame/task priority and affinity | `VGABaseController::setResolution` line 435 creates the priority-5 worker pinned to quietCore; `VGAPalettedController::setResolution` lines 164–169 allocates I2S ISR on busiestCore. | `P4FrameService::start` line 36 uses unpinned `xTaskCreate`; config header default priority is `configMAX_PRIORITIES-2` (23), stack 8 KiB. `fabutils_port.cpp` hardcodes the otherwise unused CoreUsage hint to 0. | No documented processor/output necessity was found for the priority jump or removing worker affinity. P4 is dual-core and exposes pinned FreeRTOS tasks. Reuse the stock ownership relationships unless a concrete P4 binding requires a different mapping. Account for Ethernet/USB/IDF tasks before choosing final placement; no speed claim follows from pinning alone. |
| FE-07 Suspend/resume | `VGABaseController::suspendBackgroundPrimitiveExecution/resume...` lines 346–359 increments a nesting count and waits for active drawing; worker tests suspension and sets active before draining. | `P4DisplayController::suspend.../resume...` lines 273–286 uses atomics and `taskYIELD`; executing flag includes snapshot as well as drawing. | Nested suspension contract is retained, but cross-core check/start exclusion is not proven. FE-H1 below is a possible interleaving introduced by changed ownership. Narrowly adapt exclusion to actual processor concurrency, or restore the assumptions supporting the upstream arrangement. Do not confuse atomic variables with an atomic entry protocol. |
| FE-08 Immediate flush/readback | Common `processPrimitives` lines 638–650 suspends, drains synchronously, shows sprites, resumes, queues Refresh. Official `agon_screen.h::waitPlotCompletion(false)` lines 477–479; `vdu_sys.h` invokes it for `&CA` and pixel readback. | Same common flush and retained facade call, dispatching P4 primitives; P4 background snapshot is outside this call. | Retain exact upstream command/queue lifetime behavior. Flush proves execution of pending drawings, not browser presentation. New output ownership must allow this second executor without races, and must not force network completion into MOS replies. |
| FE-09 Wait for VSYNC | Official `switchBuffer` lines 484–490: single buffer queues NoOp then `waitCompletion(true)`; common `primitivesExecutionWait` lines 610–616 spins until queue is empty. | Same facade and common implementation, backed by software frame task instead of independently timed stock worker. | Preserve the selected upstream API behavior; acknowledge queue-empty polling is not a general tagged completion fence (FE-H2). Independent periodic service is needed for faithful timing; do not claim the copied function alone provides an equivalent clock. |
| FE-10 Double-buffer draw and swap | Common `addPrimitive`: ordinary commands execute synchronously when double buffered; swap alone queues and waits task notification. Canvas `swapBuffers` lines 647–654; executor `SwapBuffers` case lines 927–935; VGABase swap lines 769–776 exchanges row tables and, where needed, DMA lists; paletted swap lines 396–401 refreshes ISR row-table aliases. | Same common queue/notify semantics; P4 `swapBuffers` line 288 exchanges two plane identities. Background worker then composes newly visible plane. | Caller execution is intentional and must remain in the ownership map. Retain native pointer/plane swap and explicit notification; adapt only actual output descriptor/alias binding. Snapshot must not race a later visible-buffer change or resurrect retired storage. |
| FE-11 Software sprites/cursors | Common `processPrimitives`/worker calls showSprites; `setSprites` lines 652–684 suspends before replacing sprite set/background buffers. Cursor attributes can also change in parser context. | Common sprite operations retained, with new P4 snapshot reading hardware sprite/cursor state after draw drain. | Retain lifecycle/order. Complete overlay review belongs with the presentation audit; here the ownership obligation is explicit: output readers must not outlive a replaced bitmap/sprite or race unprotected object mutation. “Worker owns rendering” alone does not establish that. |
| FE-12 Physical scanline work, all depths | Five depth ISRs each react to `I2S1.out_eof`, resolve current visible row, copy/decode pixels, apply palette/Copper where applicable, decorate sprites/cursors, increment frame counter and notify. `VGAPalettedController::setResolution/onSetupDMABuffer` binds descriptors/ISR. | No corresponding depth ISRs selected. `PresentationCompositor`, `PaletteState` and `publishSnapshotAtBoundary` recreate final pixels in task context for a separate browser snapshot. | Classic I2S1 registers, DMA descriptors, interrupt allocation, GPIO signals and cache availability checks are concrete output/processor dependencies. Pixel decoding, palette lookup, overlay order and frame-time independence inside those files are not automatically hardware-specific; extract/reuse those portions, with exact differences assigned to the presentation review. |
| FE-13 Cursor, Teletext and callbacks | `Context::checkForVSYNC` lines 1312–1337; `VDUStreamProcessor::processNext` line 599 calls `bufferCallCallbacks(CALLBACK_VSYNC)` when it sees counter change. Cursor/Teletext flash uses FreeRTOS tick time in `context/cursor.h::doCursorFlash` lines 330–345; Teletext draws Canvas glyphs, no dedicated Teletext rendering task. | Same retained facade behavior; custom frameCounter source, parser polling cadence and snapshot schedule change observation/presentation. | Retain these stock paths; do not mistake hardware output cursor refresh, timer-driven text flash, and parser-observed VSync callbacks for one timing owner. Stock callbacks already may coalesce when parser is occupied. Generic host/eZ80 completion callbacks are a different deferred contract; no new callback API is needed for this source-fidelity repair. |
| FE-14 Stop/reconfigure lifecycle | `VGABaseController::end` lines 121–140 suspends drawings, stops GPIO stream, frees ISR/buffers and deletes worker; mode setup owns controller replacement. | `P4FrameService::stop` lines 65–90 stops timer, asks task to finish, waits for task exit, then disables background drawing; facade stops service before configuring storage and starts new timer afterward. | Joining before destroying state is necessary. Exact stop/cancel ordering is different and must survive worker/output separation. Unbounded current drain is not interrupted merely by `stopping_`; concurrent producers or a long primitive can delay the join. Retain safe teardown and prove all drawing/output owners quiescent before freeing rows/overlays. |
| FE-15 Processor-specific execution helpers | Common transformed-bitmap executor has Xtensa FPU save/restore only for `insideISR=true`; generic execution normally passes false. `VGABase` optional budget uses per-core cycle counts; stock facade disables that budget. | Selected worker and immediate execution call `execPrimitive(..., false)`. P4 compatibility header defines no-op xthal symbols and stale text describing a canary-only scope. | A real architecture difference justifies a narrow task-only RISC-V policy. Do not move primitive rendering into a new ISR and assume these no-ops preserve FP state. Keep runtime callsites explicit; correct stale shim documentation in the accepted repair. With stock timeout disabled, no new drawing budget/cycle-counter mechanism is justified. |

## Source hazards requiring a disposition

### FE-H1 — Suspension entry is not an indivisible protocol

This is a source-level possible interleaving, **not** a measured cause of the
Nurples hang. In current P4 code:

1. Frame task reads `suspension_depth_ == 0`, before setting
   `executing_frame_work_`.
2. Parser on the other core increments the depth, sees execution still false,
   returns from suspend and enters stock `processPrimitives()` or `setSprites()`.
3. Frame task sets execution true and enters its own drain/snapshot.

Acquire/release on separate atomics does not close that gap. Stock's similar
flags need to be interpreted in its actual scheduling arrangement: normal
parser and higher-priority worker share the quiet core; a lower-priority parser
does not preempt the higher-priority worker between its test and active flag.
That does not prove arbitrary third-party callers safe, and restoring pinning
alone is not a substitute for reviewing every selected caller. W7 should either
preserve the relevant stock ownership restriction or specify a minimal correct
entry protocol for P4's actual concurrency. Host tests need a forced interleaving
at this boundary; a successful single-thread snapshot test cannot cover it.

### FE-H2 — Keep stock completion semantics distinct from new evidence claims

`primitivesExecutionWait()` observes queue occupancy, not the currently executing
primitive. The consumer removes a primitive before completing it. The original
task priorities/core relationship often prevents the parser from observing this
intermediate state; changing task affinity can expose it. A documented general
“render finished” callback must not use queue-empty polling as sufficient proof.
The immediate flush path obtains suspension and actually executes pending work;
the double-buffer swap has an explicit executor notification. These distinctions
must remain visible when deriving any future benchmark fence. This audit does
not silently fix or redefine inherited upstream API behavior.

### FE-H3 — Frame time and wakeup count are separate contracts

P4 currently couples three quantities: software timer expirations, number of
drain invocations, and completed frame/snapshot generations. Stock allows them
to differ: output frames continue, worker notifications coalesce, parser sees
counter changes when it can run. Source restoration must retain that separation.
The atomic counter proxy can remain useful without making the worker its owner.
The mainboard PB1 60 Hz source used by EMOS remains outside this P4 video clock;
do not infer that the eZ80 clock stopped merely because P4's counter did.

### FE-H4 — Do not move bulk output work into a timer callback as a shortcut

Stock ISR scanline preparation is bounded by a small DMA line group and a fixed
physical deadline. It can read drawing memory while drawing continues; single
buffer tearing is a known property. A browser needs a stable outgoing payload,
but that does not require drawing to run to queue-empty completion first.
Separating output requires explicit row/plane/overlay lifetime and snapshot
ownership; it is not equivalent to running the existing full-frame compositor
inside `esp_timer` or copying all native render work into an ISR. The portable
scanline algorithms and the physical scheduling wrapper should be reviewed
separately.

The smallest proposed ownership arrangement is: the stock-shaped drawing worker
remains responsible for the queue and software sprites; a separately scheduled
output reader performs the retained scanline preparation into exclusively owned
output storage; the network service reads only the completed immutable snapshot.
Browser requests may drop/skip output copies when no slot is available, but must
not stop the independent display clock or drawing. Before mode change frees rows,
the controller must stop/join the drawing and native-memory-reading output owners;
an already leased browser snapshot remains governed by its existing pool lifetime.
Row tables, visible-plane swaps and sprite/bitmap lifetimes require explicit
ownership at the output read boundary. Do not assume a saved base address remains
valid after a scroll, swap, mode change or overlay replacement. Single-buffer
output need not be a globally atomic image—stock scanout is not—but a faithfully
ported reader must still use the selected target's valid shared-memory access
rules. This is an implementation seam to specify and test, not a justification
for holding drawing suspended through a full frame copy.

## Proposed repair ordering for the parent audit

1. Preserve measured [F001](findings.md): a 41.758495-second drain prevented
   snapshot publication while UART progress continued. Neither a new storage
   optimization nor a passing finite graphics suite disposes of that finding.
2. Restore a stock-shaped separation between drawing worker, independent output
   frame clock/refresh and consumer delivery. Retain unchanged common queue,
   payload and direct/swap paths; account for all execution owners. Extract
   the actual stock worker/scanline code before inventing a substitute service.
3. Select the smallest necessary P4 timer/peripheral and row-publication bindings
   alongside the storage/presentation audit. Restore worker notification
   coalescing and independent counter timing; justify priority/affinity with the
   selected full firmware closure. No frame budget is proposed.
4. Resolve FE-H1 and output lifetime before qualifying shared-row operation.
   Verify single-buffer ongoing drawing plus independent refresh, explicit
   flush/readback, swap notification/double buffer, stop/reconfigure, nested
   suspension, frame waits, cursor/Teletext and callback cadence. Measure actual
   latency/throughput only after restoring the source contracts; source review
   alone does not rank CPU costs or prove a particular core assignment faster.

This report does not choose a new public callback ABI, run QUAL-003, replace
EMOS, or authorize a flash. Those work boundaries remain with the parent task.
