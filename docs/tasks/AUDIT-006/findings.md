# Nurples hang attribution

**AUDIT-006-F001 — Sustained drawing postpones frame publication until the
queue empties.** Investigation complete; findings and the proposed PORT-003
correction await Author review. This is a reproduced failure, not a gameplay
PASS. No correction has been implemented.

This is the completed W1–W5 diagnostic finding. The Author subsequently
expanded [AUDIT-006](../AUDIT-006.md) to a priority-one whole-video-backend
fidelity audit. F001 remains evidence within that task; it is not a claim that
the expanded source audit is complete. That audit now precedes the held
QUAL-003 benchmark and selection of the next implementation change.

## What the capture establishes

The Author reports very severe hangs, rare recovery, renewed keyboard attempts
when it recovered, and four manually marked hangs. Run
`AUDIT-006-2026-09-10-23-26-53Z` contains 179 successful HTTP observations over
about 181 seconds and all four markers. File checksums and the verified r09
deployment binding pass. P4 times and valid accumulated counters are monotonic;
no reset/wrap appears in this recording.

[Analysis](evidence/AUDIT-006-2026-09-10-23-26-53Z/analysis.json) and the
[losslessly preserved raw records](evidence/AUDIT-006-2026-09-10-23-26-53Z/records.jsonl.gz)
retain the evidence. The original private bundle also retains exact local
deployment/media bindings; their hash is recorded without publishing private
addresses or paths. [The offline analyzer](scripts/analyze.py) verifies those
inputs, rejects counter/time discontinuities and generates the derived record.

The saved slow history identifies these completed **queue-drain invocations**:

| P4 start, seconds since boot | Drain duration | Primitives executed before returning |
|---|---:|---:|
| 381.807223 | 21.177398 s | 17,812 |
| 417.363013 | 24.462100 s | 95,082 |
| 445.284747 | 9.694773 s | 38,605 |
| 456.380455 | 41.758495 s | 163,069 |

A further invocation starting at 499.264652 seconds was still active at the
last sample, already **9.359149 seconds** old. Its final duration is unknown.
The first long interval is retained without asserting that loading or gameplay
began at an independently observed exact instant.

During a measured **40.762339-second interior** of the longest drain:

1. Snapshot completion count remained **461** throughout all 41 observations;
   frame/queue completion counts also remained unchanged.
2. The retained parser completed **1,356** additional batches and consumed
   **474,404** more UART bytes from Agon.
3. P4 submitted **49,382** more return bytes to UART and observed **1,343**
   additional completed TX batches. These bytes can include keyboard/control
   traffic; the diagnostic does not decode their contents.
4. Every host timing request succeeded. Across the whole capture, median HTTP
   request duration was **4.480 ms**, maximum **15.886 ms**.

This supports publication starvation during continuing command traffic. It
does not prove every key reached the game, normal game speed, successful Escape,
or uninterrupted browser socket/presentation behavior. The network remained
reachable; slow Ethernet delivery alone cannot explain the absence of newly
completed snapshots throughout this interval.

## Markers and other phases

| Marker | Relationship to recorded drawing work |
|---|---|
| 1, 23:28:48.167 UTC | Near recovery after the 24.462 s drain. The preceding sample still saw it active; the following sample saw a new short drain and a 1,497-tick entry backlog. Its aggregate copy was unavailable. Do not label this marker the exact start/end of a 24-second hang. |
| 2, 23:28:53.273 UTC | Samples bracketing it show the drain that eventually lasted 9.695 s. |
| 3, 23:29:05.416 UTC | Samples bracketing it show the drain that eventually lasted 41.758 s. |
| 4, 23:29:52.552 UTC | Samples bracketing it show the final drain, still active when recording ended. |

Completed snapshot composition peaked at **141.683 ms** across the recording;
the snapshot following the longest drain took about **54.6 ms**. Snapshot work
is not free, but was not executing throughout the multi-second queue intervals.
The measured frame-task `showSprites` call peaked at **1.014 ms**, and recorded
suspension waits at **6 µs**. These phase observations do not identify sprite
updates or suspension waits as the cause of these long intervals. Drawing
primitives may themselves perform additional sprite/bitmap work inside `queue`.

Parser batches reached **2.041 s** elsewhere in the run. That is a separate
latency observation; this recording does not assign its entire duration to a
specific VDU command or CPU computation. Frame entry backlog reached **1,661**
ticks, corroborating delayed logical-frame service rather than steady servicing
of every tick during the long draw pass. This is an entry observation, not a
continuous measurement of the maximum pending count.

## Source-supported mechanism and stock distinction

[P4DisplayController::executeFrameWork](../../../vdp/video/extender/display/p4_display_controller.cpp)
drains using nonblocking `getPrimitive(..., 0)` until empty or suspended, then
calls `showSprites` and `publishSnapshotAtBoundary`. The common
[queue implementation](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp)
and [P4 time conversion](../../../vdp/video/extender/port/fabutils_port.cpp)
confirm that zero is a zero-tick receive, not an unintended waiting timeout.
Executing 163,069 primitives exceeds the 1,024-entry queue capacity: new work
was being admitted during that invocation. Returning from a finite batch of
previously queued work is not what this loop guarantees under sustained input.

[LogicalFrameService](../../../vdp/video/extender/display/logical_frame_service.cpp)
cannot publish that service pass or begin the next one until the executor
returns. The [timer callback](../../../vdp/video/extender/display/p4_frame_service.cpp)
continues recording pending ticks, but does not independently advance the
compatibility frame counter or produce a browser surface. P4 therefore ties
these visible-frame opportunities to drawing-queue emptiness.

The selected stock [paletted VGA drawing worker](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp)
also drains until empty/suspended. However, the stock
[VGA64 interrupt path](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp)
feeds output scanlines and increments `frameCounter` separately, then notifies
the worker. Physical output does not wait for that worker to return before
reading the visible framebuffer. Restoring the stock draw loop did not also
restore this surrounding separation of drawing, refresh and clock service.

The official [VSYNC and flush contracts][system-doc] distinguish a refresh wait
from explicitly completing queued drawing. They do not require every display
refresh to await global queue emptiness. This finding exposes a limitation in
the existing Phase C service/publication ordering; it does not silently amend
that accepted contract.

## Evidence limits and next correction

There was one unavailable aggregate copy, no inconsistent live observations,
no overlapping calls, and six lost completion records during this capture
(12 already existed at its first sample, 18 at its last). Valid count deltas
contain 68,135 completions. The bounded history overwrote 3,939 older events;
the raw sequence preserves everything the collector actually observed, not
every event ever recorded. The long durations above have completed records
corroborated by repeated observations of the same active invocation. Their
duration is wall time including preemption; per-primitive cost, task CPU time
and exact queue occupancy were not measured. Diagnostic overhead remains a
perturbation, and this run does not quantify r09 versus r08 game timing.

**Proposed next action, PORT-003:** separate periodic frame/visible-surface
servicing from the requirement that drawing first drain to an empty queue.
P4 should be able to present current output during a sustained stream, retaining
FIFO drawing and correct explicit flush/swap semantics. Review the stock
interrupt/worker separation and the existing Phase C/snapshot ownership contract
before choosing a coherent publication boundary. An independently reading
consumer must not see torn internal ownership or a mutable leased snapshot.
No arbitrary primitive/time quota, core-pinning change or scanline protocol is
selected by this finding. Rendering speed and snapshot cost can be considered
after the demonstrated dependency is corrected.

This observation/attribution task stops here. Firmware, EMOS, game, SD and bench
state were not changed while collecting these results. Escape behavior remains
unreported; no additional reproduction is required to establish this dependency.

[system-doc]: ../../../../../agon-docs/docs/vdp/System-Commands.md


The Author subsequently proposed automated deterministic graphics-suite timings
using completion callbacks and temporary instrumented mainboard/P4 firmware.
QUAL-003 records that next measurement direction and the required EMOS receive
integration review. It does not change this capture's attribution or authorize
a speculative repair within AUDIT-006.

### Game provenance clarification

After the Author identified `nurples-repair` as the modern checkout, read-only
hash comparison confirmed that the executable used here matches its committed
`dev` state `4a52199870f5177d8fd65622566725418364ef84`, including the optional
joystick fix. The recorded game and UI containers also match that commit.
The [benchmark contract](../QUAL-003/benchmark-contract.md#source-selection-and-existing-evidence)
records those hashes and distinguishes ongoing uncommitted artwork changes.
This capture was already using the repaired game; its evidence is not relabelled
as a run of the older known non-working checkout.
