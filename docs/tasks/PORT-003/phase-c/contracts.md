# PORT-003 Phase C contracts

These contracts freeze logical frame behavior before implementation. They
extend the qualified Phase B renderer without defining presentation pixels, an
official mode facade, or an output sink.

## Execution ownership and clock boundary

One frame-service owner performs every frame-boundary state transition. A host
test invokes it deterministically; the P4 adapter runs it in one FreeRTOS task.
The `esp_timer` callback only computes/records elapsed logical ticks and wakes
that task. It never renders, dequeues work, swaps storage, publishes mutable
state, or signals primitive/swap completion.

The service clock exists whenever a valid configured mode exists, with or
without consumers. Its configured positive cadence is explicit Phase C input;
official modeline/mode lookup remains Phase E. Start, reconfigure, and stop are
transactional. Stop first disables the timer, wakes and joins the sole owner
task, then prevents new asynchronous execution, cancels queued work, resolves
owned dynamic payloads, and wakes cancelled waiters. Consumer registration
changes are permitted only while stopped, and storage release or
reconfiguration is permitted only after stop completes.

## Ticks, frame count, and overruns

Each logical tick advances the writable compatibility frame counter modulo
2^32. An explicit write replaces its current 32-bit value; later elapsed ticks
continue from that value. The counter is distinct from a monotonic 64-bit
presentation generation that user software cannot write.

The notification boundary accumulates elapsed tick count rather than merely a
boolean wake. When more than one tick is pending, the service advances the
compatibility counter by the full elapsed count but performs one newest-state
service pass and publishes at most one generation. It records `elapsedTicks`,
`servicedEdges`, `coalescedTicks`, and `overruns`; it never emits a burst of
stale presentations. Target measurements qualify cadence, jitter, drift, and
the exact deadline threshold rather than inferring them from host tests.

For each service pass the normative order is:

1. consume elapsed ticks and advance the compatibility frame count;
2. execute the bounded eligible primitive batch in FIFO order;
3. perform an encountered queued logical swap;
4. freeze Phase C frame metadata (pixels are not composed yet);
5. publish one newer generation; and
6. mark executed submissions complete and wake waiters outside the state lock.

## Primitive submission and completion

The retained official Canvas path is a serialized single producer. Phase C
does not promise concurrent Canvas submissions from arbitrary application
tasks. Every asynchronous primitive first reserves a monotonically increasing
64-bit position before the blocking queue send, then becomes submitted only
after that send succeeds. If the worker dequeues during this narrow handoff,
it waits until the corresponding submission is published before marking the
same position started. The sequence is completed only after `execPrimitive()`,
publication, and all dynamic-payload cleanup return. Sequence values are local
to one started lifecycle and reset only after the prior owner task has joined
and all queued work has been resolved.

`waitCompletion(true)` snapshots the latest submitted sequence and waits until
that sequence is completed or the lifecycle returns an explicit stopped/
cancelled result. Queue emptiness is not completion: an already-dequeued item
remains outstanding. `waitCompletion(false)` drains eligible work
synchronously and applies the same started/completed accounting. Path and
transform buffers remain owned until their associated execution or explicit
teardown cancellation releases them.

Ordinary single-buffer primitives execute in FIFO order on logical frame
service passes. A queued `Flush` used by official single-buffer `switchBuffer`
therefore completes no earlier than the next logical edge. Ordinary
double-buffer drawing retains immediate Phase B execution against the drawing
plane; the queued swap is the frame-bounded operation.

## Logical swaps and storage

Single-buffer drawing and visible views remain identical and cannot exchange.
In a double-buffered mode, a successful logical swap atomically exchanges the
drawing and visible plane indices without copying bytes. The newly visible
identity is observable before the swap sequence completes and before its
submitting task is notified. A second swap cannot overtake the first; the
retained one-element double-buffer queue provides backpressure.

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

## Required common-code seam

Pinned upstream `BitmappedDisplayController::primitivesExecutionWait()` polls
only `uxQueueMessagesWaiting()`, while dequeue and execution are separate.
`Canvas` calls that non-virtual method through the common base, and the queue
plus background fields are private. The P4 subclass therefore cannot meet the
explicit completion contract by overriding its existing virtual physical
hooks.

The Author accepted `PORT-003-D008` on 2026-08-22. Its minimal patch leaves all
old-controller defaults unchanged while exposing no-op reservation, enqueue,
started, completed, cancellation, and notification-deferral hooks plus a
virtual completion wait for the P4 controller. The exact upstream
spans and race are fingerprinted in `evidence/frame-lifecycle.yaml`;
symbol interposition, queue interception, and whole-translation-unit copying
are rejected.
