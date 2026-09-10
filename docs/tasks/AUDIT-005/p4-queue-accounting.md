# W8 — Point workload and P4 drawing-queue accounting

Recorded 2026-09-10 after freeze `71f082e`, under the
[accepted contract](p4-wait-attribution.md). Source-accounting branch complete;
findings accepted 2026-09-10. The Author selected stock queue draining for W9.

## Result: AUDIT-005-F006

EDP's **64 drawing primitives per logical frame** is the concrete limiting
mechanism supported by the source and this workload's measured timing. Each
point queues five primitives. The 4,096-point workload therefore submits
20,480 primitives; the 1,024-entry queue can retain the final portion for the
pixel query's immediate flush. Draining the preceding 19,456 primitives at
64 per 16,667 µs predicts **5.066768 s**, versus **5.075174 s** measured in W7.

The nominal 4,096-byte UART receive buffer also accounts for the split between
Agon's completed transmission and P4's later reply. The saved waveform shows
repeated approximately 60 Hz bursts, providing another independent feature
consistent with the source model. These observations satisfy W8's source-only
stopping gate. No timing probe or additional hardware run was needed.

This is **source-backed attribution with measured wire corroboration**, not a
measurement of queue occupancy, task CPU time or function duration. A controlled
change is still needed to establish the causal response and actual speedup.
PORT-003 owns the proposed display-service change; PORT-008 retains UART and
EMOS ownership. No firmware, frame policy, SD content or hardware state changed.

## Inputs and source verification

The [W1 identities](baseline-and-path-map.md#selected-sources) and
[W7 evidence](browser-disconnected-findings.md) remain fixed. P4 source is
`52479f0ae9653e293031a1eed1b65f0cec9695cd`, installed build
`uart-excom-console-r07-b2026-09-10-06-31-58Z`; EMOS remains
`agon-emos-v0.1.12-b2026-09-10-03-50-35Z`. The r03 SD workload is unchanged.
This calculation uses the accepted browser-off trace and returned CSV, not
emulator timing or a new physical run.

[Source verification](evidence/p4-queue-accounting/source-verification.json)
records 35 relevant files matching the saved P4 build manifest, all four saved
output hashes, and a current build ELF identical to the saved ELF. Its generated
configuration and the manifest-matched defaults both specify FreeRTOS at
1,000 Hz: a one-tick delay is nominally 1 ms. Official MOS and VDP checkouts
remain clean at their selected release commits; the EMOS checkout is also clean.

The official [PLOT contract][plot-doc] identifies command 69 as an absolute
foreground point. The [pixel/flush contract][system-doc] requires preceding
drawing to complete for a pixel reply. Source implementation detail below is
material to the audit. The selected stock VDP is v2.16.0; its selected vdp-gl
dependency is the `all-the-plots` tag at
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`, as recorded by PORT-001. Relevant
library files were retrieved at that exact commit into ignored research storage
and their hashes recorded. An incidental local dependency cache is not substituted
for the pinned revision.

## Stock behavior and EDP's introduced limit

| Path | Verified implementation and implication |
| --- | --- |
| Stock single-buffer background worker | [Screen setup][stock-screen] enables background execution and disables its time limit. The pinned [VGA worker][stock-worker] executes until the queue empties or processing is suspended, then waits for another refresh notification. There is no fixed 64-primitive cap; actual drawing still costs CPU time. |
| EDP background worker | [Screen setup](../../../vdp/video/agon_screen.h) constructs `P4FrameService` with its default budget of 64. [Logical service](../../../vdp/video/extender/display/logical_frame_service.cpp) consumes one pending tick per pass; [P4 executor](../../../vdp/video/extender/display/p4_display_controller.cpp) processes at most that many primitives. [Task adapter](../../../vdp/video/extender/display/p4_frame_service.cpp) services every pending tick distinctly, including catch-up after delayed scheduling. Mode 0 selects 60 Hz; the mode binding computes 16,667 µs. Nominal saturated background throughput is about 3,840 primitives/s. |
| Full single-buffer queue, both paths | Retained [common queue code](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp), `addPrimitive`, uses blocking `xQueueSendToBack(..., portMAX_DELAY)`. Capacity is 1,024. A full queue blocks the calling VDU parser, which then cannot consume UART bytes. |
| Immediate completion, both paths | `sendScreenPixel → waitPlotCompletion(false) → Canvas::waitCompletion(false) → processPrimitives` drains queued work synchronously, without the 64 cap. P4 suspension waits for an active frame execution to finish, then the retained common loop drains to empty and queues a trailing `Refresh`. The parser must first **reach** the query. |
| Explicit VSYNC and double buffering | `waitCompletion(true)` retains stock queue-depth waiting. Ordinary double-buffered drawing executes immediately; the one-element swap queue remains frame-bound. This benchmark is single-buffered, so those paths do not bypass its saturated queue. |

The original [Phase C contract](../PORT-003/phase-c/contracts.md) introduced
a bounded rendering opportunity per logical tick, with FIFO ordering, frame
counting, swaps and publication ownership. It does **not** prescribe the number
64. No inspected stock contract or P4 hardware requirement mandates that value.
Retaining a bounded opportunity and revisiting its count are separate from
changing VSYNC semantics. The Author's subsequent PORT-003-D013 decision
explicitly amends Phase C to restore stock-style draining; W9 implements it.

## Exact workload accounting

The [fixture](fixture/src/main.c), `prepare_payload` and `measure`, sends 512
blocks of 64 bytes. Each block contains eight cells:
`25, 69, x, 0, 24, 0, 0, 0`, with x from 8 to 64. Each cell is one six-byte
point command followed by two NULs. Thus there are 4,096 points, 8,192 NULs,
32,768 payload bytes and 12,288 payload `processNext` calls. The point decoder
consumes its five parameter bytes inside the same call. NULs draw nothing.

For each point, retained [Context graphics](../../../vdp/video/context/graphics.h),
`plot`, performs these unconditional submissions through
[Canvas](../../../vdp/vendor/vdp-gl/src/canvas.cpp):

1. `SetClippingRect` from `setGraphicsOptions`.
2. `SetPenColor` for the foreground operation.
3. `SetPaintOptions` for the foreground operation.
4. `SetPixel` from `plotPoint`.
5. `MoveTo` at the end of `plot`, updating the drawing cursor position.

Repeated colour or clipping values do not suppress these queue entries.
There is no pending path draw for this point command. The screen setup disables
the text cursor; keys remain released and echo is disabled. Setup and the
marker query precede the timed payload; the marker's flush can leave a trailing
`Refresh`, so a perfectly empty initial queue is an approximation of at most
one such entry, not an observed runtime state.

The console's **other** budget of 64 counts parser calls, not primitives.
[Its loop](../../../vdp/video/extender/transport/console_hardware.inc) yields
with `delay(1)`. At least 192 outer passes are needed for these payload calls.
Those sleeps and drawing on another task overlap full-queue waiting; adding
192 ms to the frame calculation would double-charge overlapping elapsed time.

P4 installs a 4,096-byte UART RX ring, hardware RTS/CTS and a 64-byte RTS FIFO
threshold. When the drawing queue blocks the parser, receive storage fills and
hardware flow control eventually withholds Agon's sending permission. The
console's separate reply ring does not hold thousands of replies for this
workload: the relevant final reply is six bytes, serviced by the console after
the parser returns. The 64-byte RTS threshold is not a 64-byte RX-ring capacity.

## Calculation reconciled with the wire

Let N = 20,480 primitives, Q = 1,024 queue entries, B = 64 per pass and
T = 0.016667 seconds. Nominal RX look-ahead R = 4,096 bytes represents
R / 8 × 5 = 2,560 primitives still awaiting parsing. The approximate saturated
queue model is:

| Interval | Frame passes | Model | W7 wire measurement | Measurement minus model |
| --- | ---: | ---: | ---: | ---: |
| First payload byte through final reply | (N − Q) / B = 304 | 5.066768 s | 5.075174 s | +8.406 ms |
| First through last payload byte | (N − Q − 2,560) / B = 264 | 4.400088 s | 4.390836 s | −9.252 ms |
| End of payload through final reply | 2,560 / B = 40 | 0.666680 s | 0.684338 s | +17.658 ms |

The final queueful is flushed synchronously once P4 parses the query; it does
not require another 16 nominal background passes. The 684 ms tail includes
waiting for the parser to reach that query through buffered point commands.
Agon's RTS permits the first reply throughout that wait. Calling the whole
tail a pixel-read computation or UART TX permission delay would be incorrect.

The source model leaves about 8.4 ms of total elapsed time unassigned. The
send/tail partition differs by roughly a frame: actual usable driver storage,
FIFO/stashed bytes, partially parsed commands, initial frame phase, ongoing
primitive execution and reply scheduling are not observed. The final drain's
CPU time is also not measured. These are residual uncertainties; the fit does
not justify assigning every microsecond or treating 4,096 bytes as measured
occupancy. Agon's 120 Hz result clock reports 608 ticks (5.0667 s); wire timing
provides the finer comparison. W6's connected total, 5.081191 s, is also close
to the same service-budget prediction, with a different distribution of gaps.

The [offline arithmetic](evidence/p4-queue-accounting/accounting.json) also
counts **all 249 payload gaps longer than 1 ms**. Across the 248 intervals
between resumptions, transfers contain either 64 bytes (100 intervals) or
128 bytes (148 intervals), averaging 102.19 bytes. A 64-primitive opportunity
corresponds to 64 / 5 × 8 = **102.4 workload bytes**. Intervals range from
16.104 to 17.014 ms, averaging **16.669 ms**, near the source's 16.667 ms cadence. Grouping into 64-byte
and 128-byte bursts is observed on the wire, not evidence of an exact driver
dequeue size. The initial 7,360-byte burst includes startup buffering and concurrent
draining; it is not a measurement of ring capacity.

Reproduce the arithmetic with [the offline script](scripts/account_point_queue.py),
passing W7's saved `analysis.json`, `frames.json` and a new output path. It
requires the accepted acquisition/decode flags and checks every payload byte
against the r03 workload. Input hashes and model assumptions are in its output.

## Accepted continuation — restore stock draining

The Author accepted the findings and directed PORT-003 to restore stock's
queue-draining policy directly. The suggested 64-to-128 experiment was rejected
before implementation. [W9's accepted contract](stock-queue-drain.md) removes
that fixed budget, retains empty/suspended termination and the other existing
frame/completion contracts, then repeats the unchanged browser-off workload.
No exact new elapsed time is predicted without the count-based throttle.

W8 is complete. Its measurements and calculation describe the unchanged r07
image; subsequent source and firmware changes belong to W9. The core-affinity
review remains conditional and deferred as recorded in PORT-003.

[plot-doc]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/PLOT-Commands.md
[system-doc]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md
[stock-screen]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h
[stock-worker]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgabasecontroller.cpp
