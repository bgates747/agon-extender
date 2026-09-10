# PORT-003 Phase C contracts

These contracts freeze logical frame behavior before implementation. They
extend the qualified Phase B renderer without defining presentation pixels, an
official mode facade, or an output sink.

Amended 2026-09-10 by PORT-003-D013: stock-style queue draining replaces the
original bounded primitive batch. Earlier qualified images and evidence retain
their original behavior; this amendment does not retroactively requalify them.

## Execution ownership and clock boundary

One frame-service owner performs every frame-boundary state transition. A host
test invokes it deterministically; the P4 adapter runs it in one FreeRTOS task.
The `esp_timer` callback only records elapsed logical ticks and wakes
that task. It never renders, dequeues work, swaps storage, publishes mutable
state, or signals primitive/swap completion.

The service clock exists whenever a valid configured mode exists, with or
without consumers. Its configured positive cadence is explicit Phase C input;
official modeline/mode lookup remains Phase E. Start, reconfigure, and stop are
transactional. Stop first disables the timer, wakes and joins the sole owner
task, then invokes unchanged upstream background-disable processing to drain
queued work and return Canvas to synchronous execution. This deliberately
retains upstream dynamic-payload cleanup, swap notification, and trailing
single-buffer `Refresh` behavior. Consumer registration
changes are permitted only while stopped, and storage release or
reconfiguration is permitted only after stop completes.

## Ticks and frame count

Each logical tick advances the writable compatibility frame counter modulo
2^32. An explicit write replaces its current 32-bit value; later elapsed ticks
continue from that value. The counter is distinct from a monotonic 64-bit
presentation generation that user software cannot write.

The notification boundary accumulates elapsed tick count rather than merely a
boolean wake. Each pending tick is consumed as a distinct logical frame edge,
increments the compatibility counter by one, receives one queue-draining
opportunity, and publishes one generation. This preserves the upstream
one-VSYNC-event/one-frame-edge model rather than replacing several elapsed
events with one newest-state pass. It records `elapsedTicks` and
`servicedEdges`. Target measurements qualify cadence, jitter, drift, and
backlog behavior rather than inferring them from host tests.

For each service pass the normative order is:

1. consume one elapsed tick and advance the compatibility frame count by one;
2. drain eligible primitives in FIFO order until the queue empties or
   processing is suspended, checking suspension between executions;
3. let unchanged common execution perform an encountered logical swap and
   notify its submitter;
4. freeze Phase C frame metadata (pixels are not composed yet); and
5. publish one newer generation.

## Primitive submission and completion

The retained official Canvas path and common queue code are unchanged. Phase C
does not promise concurrent Canvas submissions beyond upstream's contract.
`addPrimitive()` retains its blocking send, immediate double-buffered drawing,
dynamic-buffer replacement, and one-element swap-queue behavior.

`waitCompletion(true)` retains upstream queue-depth polling. A primitive that
has already been dequeued is no longer represented in the queue and may still
be executing when the wait returns. `waitCompletion(false)` retains upstream
synchronous draining. Path and transform buffers remain owned and released by
the unchanged common execution paths. Correcting or otherwise strengthening
these semantics belongs to `UPSTREAM-001`, not the strict-compatible baseline.

Ordinary single-buffer primitives execute in FIFO order on logical frame
service passes, without a fixed primitive-count or elapsed-time budget. This
matches the selected stock worker with its background timeout disabled. A
queued `Flush` used by official single-buffer `switchBuffer`
therefore leaves the queue at the next logical edge. Ordinary
double-buffer drawing retains immediate Phase B execution against the drawing
plane; the queued swap is the frame-bounded operation.

## Logical swaps and storage

Single-buffer drawing and visible views remain identical and cannot exchange.
In a double-buffered mode, a successful logical swap atomically exchanges the
drawing and visible plane indices without copying bytes. The newly visible
identity is established before unchanged common execution notifies the
submitting task. That notification occurs before Phase C metadata publication.
A second swap cannot overtake the first; the retained one-element double-buffer
queue provides backpressure.

A failed reconfiguration leaves the previous mode, planes, clock, and
identities valid. Successful reconfiguration stops the old lifecycle and
resets drawing/visible identity to the Phase B initial state before starting
the new clock. Teardown never lets a waiter or consumer access released plane
storage.

## Provisional frame publication and consumers

A Phase C publication contains immutable metadata only: generation,
compatibility frame count, dimensions, native format, buffering state, and
visible-plane identity. Presentation composition and durable read leases begin
later. This prevents Phase C mocks from establishing an accidental output API.

Consumer registration has a fixed configured capacity. Each consumer owns one
latest-notice mailbox, not a queue of every generation, and polls it from its
own task. The frame service never invokes consumer or sink code. Publishing
tries each mailbox lock once; a busy reader or unconsumed older notice causes
a reported drop rather than a wait, then the newest notice replaces prior
state when the mailbox is available. Null, disconnected, stalled, or slow
consumers therefore never block the service and hold no mutable logical
pointer. Disconnect invalidates pending and future notification without
changing frame time; reconnect begins from the newest subsequent generation.

## Required unchanged common-code contract

Pinned upstream `BitmappedDisplayController::primitivesExecutionWait()` polls
only `uxQueueMessagesWaiting()`, while dequeue and execution are separate.
`Canvas` calls that non-virtual method through the common base. Queue and
background state remain private and authoritative.

`PORT-003-D009` requires the P4 subclass to use the existing protected
task-context dequeue and primitive executor without changing those common
semantics. No lifecycle hook, virtual completion override, notification
deferral, queue interception, symbol interposition, or copied common
translation unit belongs in the strict baseline. The former D008 candidate is
preserved in commit `8aecb0e` and tracked by `UPSTREAM-001`.
