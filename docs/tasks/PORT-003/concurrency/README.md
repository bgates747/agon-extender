# PORT-003 frame-state exclusion and lifetime design

Status: rejected design candidate retained as research. `PORT-003-D011` was
rejected by the Author on 2026-09-01; `PORT-003-D012` is accepted.

Date: 2026-09-01.

Authority: the [PORT-003 task](../../PORT-003.md) owns this design. The
[REMED-002 task](../../REMED-002.md) owns cross-task disposition, and
[`AUDIT-2026-09-01-001`](../../../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md)
owns the evidence and upstream/local provenance for F001, F002, and F022.

This document is the task-local Work 2.a design record. It does not authorize
source edits, assign a fixture or procedure revision, change a qualified
artifact, amend
[ADR-0015](../../../decisions/ADR-0015-p4-display-backend-and-frame-service.md),
start Gate G, build or deploy firmware, or perform a physical operation.

## Author disposition

The Author rejected D011 as an overbroad hardening package. The detailed source
trace, proposed gate, lifetime model, and future fixture ideas below remain a
durable research record; their normative wording describes the rejected
candidate and must not be used as implementation authority.

Accepted D012 sets the current threshold instead:

1. Record inherited defects and plausible P4 amplification with exact upstream
   provenance.
2. Do not correct retained upstream behavior merely because source review finds
   a theoretical defect or possible interleaving.
3. Consider a local correction only after deterministic evidence shows that a
   project-owned Extender transport, scheduler, presentation reader, or other
   selected function reproducibly triggers the failure in a way regular
   official VDP operation does not, or that the defect prevents the selected
   Extender function from working.
4. Prefer containment in project-owned code. Any edit to retained common code
   requires a new, narrow Author decision with its merge-maintenance cost.
5. Defer the isolating regression designs in this record until separately
   prioritized. Current work establishes EMOS-to-EDP forward transport over the
   parallel GPIO interface; it does not build a generally hardened VDP.

F001, F002, F022, and H001 therefore remain recorded observations, not current
correction requirements or forward-transport blockers. No source or fixture
slice below is authorized.

## Rejected candidate outcome

PORT-003 should replace its split suspension/execution atomics with one
project-owned, task-context, recursive frame-state gate. The P4 frame task
should make one role-aware, zero-wait attempt and skip renderer work whenever
any mutation lease exists, including a lease owned by the calling task. The
sole parser/submission actor and explicitly bound synchronous actors should
acquire the same gate in blocking recursive mode for a bounded mutation
transaction; concurrent Canvas queue submission remains outside the contract.
The one explicit command-atomicity exception is counted buffered adjustment
with inline operands: each decoded operand is a generation, so no gate spans
parser ingress and an input timeout preserves the already-applied prefix.

The gate must cover the entire interval in which the frame task can dequeue or
execute a primitive, redraw sprites, borrow a plane, palette, Copper list,
sprite, cursor, or bitmap pointer, compose RGB888 pixels, or finish publishing
a snapshot slot. A completed parser mutation, or one classified decoded
streaming unit, must be indivisible relative to that interval.

Controller-only edits are insufficient. Retained common code executes
ordinary double-buffered primitives immediately without invoking suspension,
and official parser helpers mutate or destroy sprite, bitmap, and cursor
storage outside `P4DisplayController`. Queued bitmap and tile primitives also
retain raw object/backing pointers beyond command submission; direct glyph and
glyph-buffer APIs impose a separate lifetime duty on their callers. The
recommended design therefore
needs narrowly bounded retained-vendor seams, guarded high-level mutation
transactions, and a pre-invalidation drain under the retained VDP's existing
single-submitter contract. P4 selection must not change classic-controller
ISR placement or timing without a separate review.

The retained primitive payload pool is not frame state. Its metadata needs a
second, short-held, nonrecursive mutex so parser allocation attempts and
frame-side releases cannot corrupt the pool or cause the frame actor to skip
merely because an allocator attempt is in progress. That mutex never proves
renderer quiescence and has one lock order: frame-state gate before payload
mutex; no path may acquire them in the reverse order.

This is a correction design, not a new rendering model. It retains immediate
double-buffer drawing, queue depth and ordering, completion waits, swap
notification, dynamic-payload ownership, logical tick advancement, frame
counter advancement, latest-generation consumer notices, and immutable
snapshot leases.

## Reviewed authority and source baseline

The source trace used these immutable upstream identities:

1. `agon-docs` commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, especially
   `docs/vdp/Screen-Modes.md`, `Copper-API.md`, `Bitmaps-API.md`,
   `Buffered-Commands-API.md`, and `System-Commands.md`.
2. Official Agon VDP tag `v2.16.0`, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, especially
   `video/agon_screen.h`, `video/vdu.h`, `video/vdu_sys.h`,
   `video/vdu_sprites.h`, `video/vdu_buffered.h`, `video/sprites.h`, and
   `video/context/cursor.h`.
3. Pinned vdp-gl tag `all-the-plots`, commit
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0`, especially
   `src/canvas.cpp`, `src/displaycontroller.{h,cpp}`,
   `src/fabutils.{h,cpp}`, `src/dispdrivers/vgabasecontroller.{h,cpp}`,
   `src/dispdrivers/vgapalettedcontroller.cpp`, and
   `src/dispdrivers/vga16controller.cpp`.
4. Pinned pioarduino `55.03.311` / ESP-IDF `5.5.5+sha.b774170ff46`,
   especially the architecture-bundle
   `freertos/FreeRTOS-Kernel/include/freertos/semphr.h:292-306,735-871`
   recursive/static mutex contract and ESP-IDF
   `components/pthread/pthread.c:622-659` allocation path.

The relevant current P4 surfaces are:

1. `vdp/video/extender/display/p4_display_controller.{hpp,cpp}`;
2. `vdp/video/extender/display/p4_frame_service.cpp` and
   `logical_frame_service.cpp`;
3. `vdp/video/extender/display/palette_state.{hpp,cpp}`;
4. `vdp/video/extender/display/presentation_compositor.cpp` and
   `presentation_snapshot_pool.cpp`;
5. `vdp/video/agon_screen.h`, `video/sprites.h`,
   `video/context/{cursor,graphics}.h`, `video/agon_fonts.h`,
   `video/vdu_sprites.h`, `video/vdu_buffered.h`, and `video/vdu_layers.h`;
   and
6. the retained `vdp/vendor/vdp-gl/src/{canvas,displaycontroller}.{h,cpp}`.

Official documentation defines observable command behavior, not a concurrency
implementation. Double-buffer drawing remains immediate against the drawing
plane; a swap remains a frame-boundary operation. Copper updates remain
immediate rather than deferred to a new command queue. Palette deletion still
redirects affected Copper references to palette 0. Sprite and bitmap commands
retain their documented replacement and deletion effects.

For concurrency, “immediate” means that the parser does not create a deferred
semantic queue: if the frame task owns the gate first, it publishes one
coherent old generation; if the parser mutation owns the gate first, the frame
task skips that renderer opportunity and the next successful snapshot observes
one coherent new generation. No snapshot may mix the two generations.

## Defect and integration boundary

### F001

`P4DisplayController::executeFrameWork()` currently reads
`suspension_depth_` and later stores `executing_frame_work_`.
`suspendBackgroundPrimitiveExecution()` increments the depth and waits only
when execution is already marked active. A frame can therefore pass the first
check, a parser task can complete suspension, and the escaped frame can then
mark itself active and use supposedly quiescent state.

Pinned upstream vdp-gl has the same check/suspend/mark structure in
`VGABaseController`, using `volatile` fields. The P4 port replaced those fields
with atomics, removing the formal flag races but retaining the exclusion gap.
The P4 browser publisher enlarged the consequence by adding full-frame palette
and overlay traversal. The product correction belongs in independent P4 code
regardless of an upstream change.

The retained common `BitmappedDisplayController::addPrimitive()` creates a
second P4 integration boundary. In ordinary double-buffer mode it directly
calls `execPrimitive()` and `showSprites()` without invoking suspension. A
controller-only replacement of the two atomics would leave that path able to
overlap frame publication.

### F002

Official parser code calls palette and Copper operations synchronously.
Current P4 facade methods forward them into `PaletteState` without exclusion.
`PaletteState` can deallocate secondary-palette nodes or a dynamic Copper array
while the frame task traverses that storage during snapshot composition.

Pinned upstream vdp-gl has the same ownership omission between parser-driven
palette/Copper mutation and the scanline reader. P4 reimplemented the state and
added another independent reader, so local correction is mandatory.

The same P4 presentation traversal borrows active sprite arrays, sprite frame
pointers, bitmap bytes, and text- and mouse-cursor state. Official high-level
helpers mutate those objects directly, outside palette/controller wrappers.
Official counted buffer adjustment can also mutate bytes used by an active
bitmap/sprite one inline operand at a time; its target span must not survive the
next blocking operand read. This is F002 transaction evidence, not F022 owner-
destruction evidence.
The rejected D011 candidate treated transactional safety at those call sites as
an F001/F002 closure condition. D012 instead records the observation and
defers correction pending Extender-specific trigger evidence. Queued and
persistent post-command lifetime is the separate upstream-origin F022
observation recorded below.

## Rejected proposal `PORT-003-D011`

D011 proposed the following bounded correction direction:

1. Replace `suspension_depth_` and `executing_frame_work_` as synchronization
   authorities with one project-owned recursive frame-state gate.
2. Use a statically allocated FreeRTOS recursive mutex on the P4 target and a
   real `std::recursive_mutex` backend in host fixtures.
3. Make frame acquisition role-aware and nonrecursive: one zero-time attempt
   fails whenever a frame, mutation, or read role owns the gate, including any
   role on the same task. Contention skips only that edge's
   primitive/sprite/snapshot work; the logical frame service retains its
   existing tick, frame-counter, service-generation, and notice progression
   using the last metadata generation captured under the gate.
4. Let the sole parser/submission task and explicitly bound synchronous actors
   acquire the gate in blocking, same-task recursive mode for bounded in-memory
   mutations; this does not authorize concurrent Canvas queue submission.
5. Permit a narrowly default-preserving patch to retained
   `displaycontroller.{h,cpp}` and `canvas.cpp` for:
   1. one overridable immediate-primitive execution boundary enclosing the
      existing `execPrimitive()` plus `showSprites()` pair; and
   2. one default-preserving synchronous paint-position read boundary used by
      `Canvas::getPosition()`; and
   3. one-at-a-time dynamic primitive-payload allocation and release
      boundaries, so P4 can serialize only pool metadata access through a
      dedicated nonrecursive payload mutex without retaining the frame gate
      across an allocation retry or queue send; and
   4. one P4-selected submission-owner validation boundary at the beginning of
      `addPrimitive()`, defaulting to a no-op for non-P4 controllers. It rejects
      a producer other than the currently designated owner before the queue,
      immediate-execution, or payload paths are entered.
6. Self-acquire the P4 frame-state gate recursively for `readScreen()` and
   restrict every public raw plane view to an explicitly retained caller read
   or mutation lease, except after permanent ingress close under the exclusive
   lifecycle owner. Merely stopping the frame service is insufficient because
   synchronous mutation and reconfiguration remain possible. Preserve the
   official automatic drawing-FIFO flush before a screen-pixel read; the flush
   occurs outside the read lease, then the lease returns one complete generation
   current when it is acquired. It may not be a C++ data race.
7. Preserve accepted common FIFO, queue depth, swap notification, background,
   logical-time, and payload-copy/release semantics except for one explicit
   compatibility correction: before a managed operation invalidates queued
   bitmap/buffer/tile storage or an oversized official Context path, the
   retained VDP's sole command submitter synchronously drains every earlier
   raw-pointer primitive. On the parser/submission task, that operation executes
   the complete older FIFO, calls `showSprites()`, and submits the retained one
   trailing single-buffer `Refresh` before the invalidating mutation/clear. It
   publishes no snapshot and advances no logical frame or service counter, but
   it can move work from future logical edges, alter sprite-redraw and backlog
   scheduling, cause later contention skips, and increase invalidating-command
   latency and parser throughput cost. It does not cancel, reorder, or defer an
   accepted command.
8. Put P4 palette, Copper, active-sprite, sprite-frame, bitmap/font/tile
   backing, and cursor mutation under high-level transaction scopes using the
   same frame-state gate. Deletion must detach every persistent raw user before
   its backing storage can be released. If product inspection finds more than
   one concurrent Canvas submitter, stop rather than relying on the drain.
   Treat documented counted buffered-adjust commands as an explicit streaming
   exception: an inline operand is read without a lease, then its target is
   resolved and that already-decoded unit commits under a bounded mutation
   lease. A timeout can leave the already-applied prefix visible, matching the
   official one-byte-at-a-time behavior; no target pointer crosses an ingress
   read.
9. Construct both gate backends in the controller constructor before any
   configure, begin, or primitive submission. Add an executor preflight that
   validates their readiness and captures the complete initial renderer
   metadata under the frame-state gate before
   `LogicalFrameService` publishes `running=true`. Make gate/controller-not-
   ready and later task/timer start failures explicit. Rollback restores the
   gate/background state present at start entry and removes only levels acquired
   by that attempt. Capture subsequent notice renderer metadata
   while the frame-state gate is owned and return it with the frame-work result.
   A skipped edge
   copies the sole frame actor's last successful value;
   `LogicalFrameService` must not read mutable plane identity after the gate is
   released.
10. Make snapshot completion explicit: `finish()` may publish, cancel, or defer
    a transition. A deferred producer and its metadata belong to the snapshot
    pool after frame release; the next producer attempt finalizes it first and
    reports the exact generation actually published. One edge can then finish
    a new producer, so the bounded frame result carries up to two ordered
    transition records. Stop/reconfigure must settle or cancel pending producer
    state before changing mode storage.
11. Treat these seams and the managed-invalidation drain as an explicit narrow
    amendment to `PORT-003-D009`, ADR-0015 decision items 5 and 10, and
    ADR-0015 consequences 7 and 9. If accepted, update those authorities
    before implementation and record exact upstream provenance, patch hashes,
    rationale, and removal condition.

D011 would also have assigned `INTEGRITY-AUDIT-F022` correction to PORT-003
Work 2.a. The Author rejected that assignment and correction package; D012
retains F022 as a deferred research observation.

## Frame-state gate contract

### G001 — One exclusion authority

One `FrameStateGate` instance belongs to each `P4DisplayController`. No second
atomic flag, depth counter, cursor lock, palette lock, or snapshot-borrow flag
may independently claim frame-state quiescence.

The gate records an owning task plus separate frame, mutation, read, and
explicit-suspension counts. Legal nesting is
frame-to-read and mutation-to-read-or-mutation; an explicit suspension is a
distinguished mutation role so quiescent composition can prove that stronger
precondition. A read-only owner cannot upgrade to mutation or suspension.
Every release must match the owner and a nonzero count for that lease role, then
decrement exactly that count and one underlying recursive level. The effective
role is derived from the remaining counts; the final matching release clears
the owner. This counter representation is allocation-free and imposes no new
fixed role-stack capacity on retained recursive `beginUpdate()` use. Cross-
owner, illegal upgrade, and role over-release operations are fatal contract
failures and never unlock for a waiter.

The target and host backends update shared owner/role metadata only while
holding the underlying mutex. A per-task ownership record—host thread-local
state and a target task-local record or verified kernel mutex-holder query—is
used only to reject same-owner frame recursion before attempting a recursive
mutex take. Foreign contention is learned solely from the zero-time mutex take
result. Diagnostic snapshots use an explicit gate-owned copy or atomics that
are not treated as synchronization authority. A read called from primitive
execution may recurse beneath that task's frame role.
`tryAcquireFrame()` is nonrecursive by role and returns failure before taking
another recursive level whenever the calling task already owns any frame,
mutation, or read lease. This distinction is required
because a raw FreeRTOS recursive-mutex take by its current owner succeeds; it
would otherwise let the host `servicePending()` path render inside
`Canvas::beginUpdate()`.

`frame_service_running_` may remain an atomic lifecycle indicator for legal
start/configure/compose operations; it is not evidence that a frame actor is or
is not inside the protected state interval.

The target implementation uses `xSemaphoreCreateRecursiveMutexStatic()` with
controller-owned `StaticSemaphore_t` storage. The pinned P4 configuration
enables mutexes, recursive mutexes, and static allocation. The target must not
use `std::recursive_mutex`: its ESP pthread backend allocates backing state and
does not provide a suitable failure path to this exception-disabled firmware.

The host implementation may use `std::recursive_mutex`, but it must track and
assert owner and recursion depth. The existing Phase C no-op semaphore shim is
not a valid test implementation of this contract.

One auxiliary `PrimitivePayloadGate` protects only `LightMemoryPool` metadata.
It uses a statically allocated ordinary FreeRTOS mutex on target and a real
`std::mutex` on host. Allocation code takes it for one attempt and releases it
before copying bytes, yielding, retrying, or submitting; execution takes it
only for each release operation. A frame or mutation actor may therefore take
frame state and then payload metadata, but no allocation path may retain the
payload mutex while acquiring frame state. The payload gate is not a second
renderer-quiescence authority.

Both target handles are created in the controller constructor, before any
configure, begin, or primitive submission, from controller-owned storage. An
executor preflight validates them and returns an explicit result containing
either the initial configured renderer metadata or gate/controller-not-ready
failure.
`LogicalFrameService::start()` calls preflight before publishing `running=true`;
the existing void `setFrameServiceRunning()` order is not sufficient. P4 start
maps preflight failures into explicit start-result values, and any later task,
timer creation, or timer-start failure restores the entry gate/background state
on the same lifecycle task, removing only levels introduced by that attempt. A
pre-existing stopped-mode disabled-background level can therefore remain
explicitly retained for same-owner retry/close. Code never falls back to
unlocked execution.

### G002 — Frame acquisition and release

The P4 frame-service task is the only frame actor. At the first instruction of
`executeFrameWork()` that can access renderer state, it attempts the gate with
zero timeout.

If acquisition fails, the frame actor:

1. dequeues no primitive;
2. executes no primitive or sprite operation;
3. reads no mutable plane bytes, palette, Copper, sprite, bitmap, or cursor
   storage in the renderer path;
4. begins or finishes no snapshot slot;
5. returns zero executed primitives; and
6. increments a saturating contention-skip diagnostic.

The owning `LogicalFrameService` still consumes the tick, advances the
compatibility frame counter, advances its service generation, and publishes a
metadata notice. It reuses the last complete renderer metadata captured while
the gate was owned; it does not call plane-identity or renderer-state getters
after a failed try. This matters because synchronous draining can execute a
queued swap under a mutation lease even though mode reconfiguration is
prohibited. The rule matches the current meaning of a suspended renderer
opportunity without permitting a notice/data race or changing Phase C time
semantics.

`executeFrameWork()` returns one value object for every outcome with two
distinct metadata domains. First, it carries current renderer metadata captured
on this acquired edge, or the last captured renderer metadata on a skipped
edge; that domain drives the Phase C frame notice. Second, it carries an
an ordered array of zero, one, or two snapshot transition records, each with
disposition, exact finalized/published generation if any, and the producer
metadata stored when that snapshot was composed. Two is the strict bound: one
record can finalize the prior deferred producer before `tryBegin()`, and one can
record the current producer's `finish()`. These values can differ: an older
deferred plane-A snapshot may finalize on an edge whose
current renderer plane is B. The sole frame actor owns its last-successful
renderer value. A failed try copies that value into the result immediately, so
no multi-field cache is read concurrently and no later scheduler ordering can
change the notice for that edge.

Before the service becomes running, the lifecycle owner obtains the executor
preflight value described in G001. That value makes a skipped first edge
well-defined; start returns a controller-not-ready result without publishing
running state if the controller has no valid configured generation.

If acquisition succeeds, the frame actor holds the gate through:

1. every zero-time dequeue in the bounded batch;
2. every `execPrimitive()` call, including swap and dynamic-payload release;
3. `showSprites()` and common renderer bookkeeping;
4. selection and traversal of visible-plane, palette, Copper, sprite, bitmap,
   and cursor state;
5. base and overlay composition into the selected snapshot slot; and
6. `PresentationSnapshotPool::finish()` and capture of its published,
   cancelled, or deferred disposition; and
7. capture of current renderer dimensions, format, buffering state, and
   visible-plane identity separately from any completed producer metadata.

`finish()` returning `Deferred` is not a complete abort: the pool retains one
`Producer` slot and `pending_action_`. The frame may release the gate because
that slot contains finished RGB bytes and no borrowed renderer pointer, but the
frame result reports `Deferred` and no new published generation. On the next
successful frame, `tryBegin()` must first finalize the pending action and return
its exact generation and stored producer metadata before beginning another
producer. Pool APIs therefore need a result shape that exposes this transition;
post-gate generation getters are invalid. If cadence permits, that edge may
also publish its new producer, yielding two ordered publication records. The
edge still captures its current renderer metadata after finalization. A
deferred cancel similarly records no publication when finalized.

The frame actor releases the gate only after it retains no mutable or
deallocatable frame-state pointer. A browser/network consumer subsequently
uses only the existing immutable snapshot lease and never acquires this gate.
The logical service publishes the returned current-renderer metadata rather
than reading the controller again after release. Snapshot consumers use the
separate pool generation and producer metadata.

### G003 — Mutation acquisition and release

One retained VDU submission/lifecycle task owns parser reads, Canvas command
submission, destructive commands, background transitions, and configuration.
It acquires blocking recursive mutation leases for bounded work. Other actors
may use explicitly bound synchronous read or nonqueue mutation entry points;
they do not gain concurrent `addPrimitive()` authority. A parser transaction
begins only after the owner has consumed all command bytes and resolved any
input buffer that may wait for external data, except for the classified
streaming buffered-adjust rule below. It ends after all reader-visible
pointers, counts, indices, and backing lifetimes form one valid generation.

That sole-submitter property is structurally enforced, not inferred from a
source-text search. The P4-selected `addPrimitive()` owner-validation boundary
checks the current task before any submission work. A checked-in compiled actor
inventory identifies every producer and call site, while host fixtures and the
later target canary record the accepted actor ID at runtime. Ownership may be
transferred only while parser ingress is closed, no pointer-bearing primitive
or dynamic payload remains, and the frame-state gate is quiescent. The FIFO may
contain at most the retained owner-neutral trailing `Refresh` produced by the
synchronous drain; its ID and lack of payload are asserted before transfer.

Current P4 boot creates `processLoop` before calling `boot_screen()`
(`vdp/video/video.ino:189-206`), so it cannot simply assert that both are the
same producer. Implementation must start the process task behind a barrier:
the bootstrap task owns submission, completes `boot_screen()`, synchronously
drains its submissions, acquires the quiescent gate, transfers the owner token
to the process task, then releases the barrier. Reordering creation is an
acceptable equivalent if the compiled inventory and runtime evidence prove
that no overlapping producer exists.

The same task may nest leases. This is required by retained paths in which
background disable calls `processPrimitives()`, `processPrimitives()` suspends
again, or `setSprites()` owns an internal suspension interval. Only the owning
task may release a level. An unbalanced or cross-task release is a visible
fatal contract failure in qualification builds and must never unlock the gate.

Newly introduced high-level mutation transactions must release the gate
before:

1. a parser ingress read or incomplete-command wait;
2. a potentially blocking queue send;
3. a completion wait, task join, callback, or retry delay;
4. network, browser, socket, or transport work;
5. arbitrary diagnostic output; or
6. any operation whose completion requires the frame task to acquire the gate.

The one retained exception is the existing background-disable sequence:
`enableBackgroundPrimitiveExecution(false)` retains its outer suspension while
`processPrimitives()` recursively drains the just-observed queue and appends
the trailing single-buffer `Refresh`. Phase C already assumes no concurrent
Canvas submitter, and the just-drained queue provides space. Work 2.a must test
that exact path and must not generalize the exception to new mutation scopes.
Likewise, a high-level sprite helper may guard its direct field changes but
must call retained `setSprites()` or `removeSprites()` without an outer lease;
those paths release their internal suspension before submitting their own
refresh.

Bounded allocation for a replacement object may occur before the transaction.
The mutation actor then acquires the gate, atomically installs the replacement
and detaches the old object, and releases or destroys the now-unreachable old
object within the proven lifetime boundary. Allocation failure leaves the old
generation valid and unwinds every acquired lease.

Official buffered adjust/reverse operations can modify storage used by active
bitmaps and sprites. For multi-target inline operands, the parser reads exactly
one operand byte with no frame-state lease, then acquires mutation, resolves the
current target span inside that lease, applies the decoded byte, and releases
before the next ingress read. It never retains `targetSpan`, bitmap, sprite, or
backing pointers across `readByte_t()`. An incomplete command therefore exposes
only the prefix the official one-byte-at-a-time command has already applied.
For the single-target/multi-operand form, the actor accumulates into a local
scalar while reading and performs the one target write only after all requested
operands arrive, preserving its existing timeout behavior. Buffer-fetched and
constant-operand forms need no ingress wait and may use one count-bounded
transaction. Qualification records prefix length and exact old/new bytes; this
streaming exception is not generalized to descriptor replacement or pointer-
lifetime mutation.

Before a buffer-clear or replacement operation can invalidate an object named
by a queued primitive, the sole retained VDU command submitter calls the
existing synchronous drain outside the destructive mutation lease. After the
drain's `showSprites()` completes and its one trailing single-buffer `Refresh`
has been submitted, the same actor acquires one mutation lease, detaches
persistent raw users, removes descriptor ownership, releases backing bytes,
and releases the lease. The drain publishes no snapshot and changes no logical
frame or service counter. The drain is invalid if any
other product actor can submit Canvas work concurrently; discovery of such an
actor is a stop condition requiring an ownership-bearing queue design.

### G004 — Legacy suspension API

`suspendBackgroundPrimitiveExecution()` acquires and retains one explicit-
suspension role. `resumeBackgroundPrimitiveExecution()` releases exactly one
such role from the same task. An ordinary mutation lease does not satisfy an
API that requires explicit suspension. The old globally decrementable depth
semantics are not retained as an authority.

One designated submission/lifecycle task owns every matched
`Canvas::beginUpdate()`/`endUpdate()` pair and every retained
background-disable/background-enable transition. Retained
`enableBackgroundPrimitiveExecution(false)` intentionally leaves one outer
suspension level owned after it drains; a later enable on the same task
releases that level. Cross-task restart is a contract failure, not a reason to
make recursive ownership globally releasable.

`composeVisibleRegionQuiescent()` preserves its accepted Phase D behavior. If
the frame service is running and the calling task does not already own an
explicit suspension lease, the method returns `NotQuiescent` without waiting.
Otherwise it recursively acquires the gate for the whole synchronous
composition. It must not infer quiescence by reading replacement flags.

### G005 — Start, stop, configure, and teardown

Ordinary stopped mode change and final controller destruction are distinct.
For an ordinary mode change:

1. the submission/lifecycle owner closes new parser and mutation ingress and
   lets any existing non-lifecycle mutation return without holding the gate;
2. the P4 frame-service owner stops its timer, wakes and joins its sole frame
   task;
3. before `LogicalFrameService::stop()` retains a disabled-background level,
   a new executor post-join/pre-disable hook uses the bounded snapshot
   transition operation to settle or cancel any pending producer without
   holding frame state; and
4. only then does the lifecycle owner disable retained background execution,
   retain its explicit-suspension level, and perform protected mode mutation.

The browser/network worker may continue holding an immutable lease to the old
slot during an ordinary mode change; no slot storage is destroyed or reused
until that lease is released. Final pool/controller destruction additionally
requires the browser/network owner to stop and join its worker and release every
immutable lease while no frame-state lease is held.

Plane, palette, Copper, sprite, bitmap, and cursor storage may be reconfigured
or destroyed only after the frame join and while the teardown actor owns the
gate.

Snapshot slots have a separate immutable-consumer lifetime. Joining the frame
task prevents new publication but does not revoke a lease already held by the
browser/network owner. Snapshot-pool storage reconfiguration or destruction
requires the later frame join and zero outstanding leases; ordinary mode
change may leave old immutable storage alive until release. No frame-state
lease may span an external stop, join, or consumer transition wait.

Current `P4FrameService::stop()` joins and immediately calls
`LogicalFrameService::stop()`, so implementation must split those phases or add
the executor hook between them. The hook returns an explicit settled,
cancelled, retryable-consumer-contention, or invariant-failure result. Stop may
retry the bounded transition without frame state; it must not proceed to
retained background disable while a producer action remains pending.

Before stopped reconfiguration changes dimensions or storage, the lifecycle
owner must settle the pool's pending producer action after the frame task is
joined. A bounded transition operation finalizes a complete pending
publication or cancels a failed one and returns its exact disposition. No
`Producer` or pending action crosses into the new mode. Contention with a live
consumer is reported and retried without a frame-state lease; once final
destruction has also joined that consumer, inability to obtain the transition
lock is a fatal invariant failure.

Every configure/start/rollback exit is balanced on the same lifecycle owner.
In particular, the current facade can stop and retain the disabled-background
level, fail the new configure/start, and restart the prior mode while
`changeResolution()` only re-enables after a successful outer return
(`screen_facade_adapter.cpp:79-97`; `agon_screen.h:241-249`). A successful new-
mode or restored-old-mode restart releases the retained level on that same
owner before reporting running. A failed restart remains stopped with one
explicitly recorded retained level for same-owner retry or final close. No
recursive-mutex lease is transferred between tasks, and reported `running=true`
at a completed start/rollback boundary while the lifecycle-owned disabled-
background level remains is forbidden. Ordinary balanced
`Canvas::beginUpdate()` suspension while the service runs remains supported.

Before controller destruction, the lifecycle owner closes every frame-state
acquisition ingress, including reads and raw-view helpers; rejects or drains
waiters; joins the frame and external consumer workers; releases all snapshot
leases; settles/cancels pending producer state; closes payload allocation and
release ingress; and explicitly closes the retained disabled-background level
without re-enabling queue execution. It then closes the payload gate and proves
no payload owner or waiter remains.
Only gates at recursion depth zero with no waiters may have their host mutex or
static FreeRTOS storage destroyed. Reconfiguration while stopped may recurse
beneath the lifecycle owner's retained level, but restart must occur on that
same owner.

The frame task uses zero-time acquisition so it cannot block a stop/join while
the stopping parser task owns a mutation lease. Code must nevertheless avoid
calling external waits or stop/join from inside a newly introduced mutation
scope. A deterministic defensive test covers that ordering.

The `esp_timer` callback and every ISR only record events and wake tasks. They
never acquire the frame-state gate. A requirement to acquire it from an ISR is
a stop condition, not permission to substitute a spin lock.

### G006 — Synchronous reads and raw views

The official screen-pixel path first calls its existing synchronous drawing-
queue flush with no newly introduced read lease. Only after that drain returns
does P4 `readScreen()` acquire one read lease for its complete rectangle when
the caller does not already own frame state; common fill/primitive code already
under a frame or mutation lease performs no repeated mutex operation per
pixel. `Canvas::getPixel()` already reaches that virtual method. A new
default-preserving retained-common position-read seam lets
`Canvas::getPosition()` reach a P4 override that applies the same owner check
before copying the paint position. Non-P4 defaults retain their present direct
read.

The automatic flush required by official `System-Commands.md` remains
observable. If another explicitly bound mutation actor commits after the flush
and before the read lease, the pixel read returns the complete generation
current at lease acquisition; that is the project concurrency rule, not an
upstream stale-read guarantee. The sole parser submitter prevents a later FIFO
submission from overtaking its own flush/read sequence.

Public `drawingPlane()` and `visiblePlane()` views borrow raw storage. Every
caller retains an explicit read or mutation lease for the entire borrow, even
while the frame service is stopped, because synchronous mutation and
reconfiguration can still run. The only exception is the lifecycle owner after
permanent acquisition-ingress close, when it has exclusive closed-state
authority. The returned pointer must not escape that interval. Tests that
merely take a view and later use it without a lease must be converted to
bounded inspection helpers. No network or browser path may receive either
view.

## State and actor map

| State or operation | Writer/owner | Frame reader | Required boundary |
|---|---|---|---|
| primitive dequeue/execution and common paint state | frame task or synchronous Canvas caller | frame task | one frame or recursive mutation lease |
| ordinary double-buffer primitive plus `showSprites()` | parser/Canvas caller | frame task | retained common immediate-execution seam under a mutation lease |
| synchronous paint-position or pixel read | Canvas/parser caller | frame task or synchronous caller | retained position seam or P4 `readScreen()` override under a recursive read lease |
| drawing/visible plane bytes and identities | primitive or swap executor | compositor | same lease through execution and snapshot finish |
| raw drawing/visible plane view | qualification or lifecycle actor | none while borrowed | explicit caller-retained read/mutation lease, or permanently closed exclusive lifecycle phase; pointer cannot escape |
| palette 0, secondary palettes, drawing LUT | parser palette helpers | primitive executor and compositor | one complete palette transaction |
| Copper signal array and referenced palette IDs | parser Copper helpers | compositor | one complete list replacement/deletion transaction |
| active sprite pointer/count and saved backgrounds | parser sprite activation/reset | common sprite renderer and compositor | detach/replace under one mutation lease |
| sprite frame array/current frame/visibility/position/paint/hardware flag | parser sprite helpers | common sprite renderer and compositor | high-level sprite transaction; refresh submission after release when it can block |
| bitmap object and backing stream bytes | buffered-command parser | primitive executor, sprites, cursors, compositor | detach all raw users before backing release |
| counted inline buffer-adjust bytes | sole parser reads one operand, then writes one target unit | primitive executor, active sprite, compositor | no lease or target pointer across ingress read; each decoded unit is one bounded mutation generation and an incomplete prefix remains visible |
| text-cursor sprite, bitmap, bytes, position, and visibility | context/parser actor | compositor | allocate first where possible, then atomic replace/delete transaction |
| mouse-cursor pointer, bitmap, position, and visibility | input/parser actor | compositor | guarded P4 wrappers; no ISR gate access |
| managed queued bitmap/tile/oversized-path operand or copy destination | sole retained VDU submitter | later primitive executor | synchronous pre-invalidation drain, then detach and destroy/clear under mutation lease; generic borrowed API lifetime remains with caller |
| primitive dynamic-payload pool metadata | parser allocator or primitive executor | not frame state | separate short-held payload mutex; frame-state-before-payload lock order only |
| finished RGB888 snapshot slot | snapshot publisher | browser/network consumer | existing immutable snapshot lease only |
| logical tick, frame counter, and service generation | logical frame service | consumers | existing atomics/mailboxes; not the frame-state gate |
| notice renderer metadata | frame task | logical-service consumers | capture under frame gate; skipped edge reuses last captured value |

## Retained common-code seam

The common `addPrimitive()` queue branch must remain outside a persistent
frame-state lease. `xQueueSendToBack(..., portMAX_DELAY)` can wait for the frame
task to consume an item; retaining the gate across that call would make the
frame task skip forever and deadlock the sender.

The preferred common patch adds default-preserving boundaries in the
P4-selected build:

1. A submission-owner validation method called at the first instruction of
   `addPrimitive()`. Its non-P4 default is a no-op; P4 rejects any actor other
   than the designated bootstrap or parser owner before allocation, immediate
   execution, or queue submission.
2. An immediate-execution method whose default implementation performs the
   existing local update-rectangle construction, `execPrimitive()`, and
   `showSprites()` calls. `P4DisplayController` overrides it only to hold one
   blocking mutation lease while invoking that unchanged default body.
3. A public controller paint-position read method whose default returns the existing
   `paintState().position`. `Canvas::getPosition()` calls this method, and P4
   overrides it only to copy the value under a recursive read lease. It cannot
   be merely protected unless `Canvas` becomes an explicit friend; the public
   value-returning wrapper is preferred because it exposes no raw state.
4. A one-attempt primitive-payload allocation method and a payload-release
   method whose defaults directly use the existing `LightMemoryPool`.
   `P4DisplayController` overrides each method only to serialize that one pool
   metadata access through the dedicated payload mutex. The existing caller
   retains its allocation retry and `taskYIELD()` loop outside the lease;
   queue send also remains outside it. The helper acquires no new frame lease,
   but can inherit a surrounding mutation lease such as `beginUpdate()`, in
   which case the order is frame state then payload. Frame or synchronous
   execution releases payload storage while already owning frame state,
   establishing the sole frame-state-before-payload lock order.

Classic controllers can execute the affected releases from ISR/IRAM paths.
Work 2.a may not claim non-P4 equivalence merely because a virtual default has
the same C++ body. The implementation must either compile these hooks only for
the P4-selected closure or complete a separate IRAM, dispatch, and timing
review before changing classic source selection. No classic-controller build
is part of the Work 2.a correction authority.

This seam is narrower and safer than these rejected alternatives:

1. Holding the gate around `VDUStreamProcessor::processNext()` would include
   blocking command reads and allow an incomplete command to stall frames.
2. Holding it around all of `addPrimitive()` would deadlock on a full queue or
   an exhausted dynamic-payload pool.
3. Replacing immediate double-buffer execution with frame-queued execution
   would change accepted application-visible behavior.
4. Copying or interposing the common controller translation unit would create
   a divergent lifecycle authority and a larger merge surface.
5. Another atomic handshake would still have to reinvent task ownership,
   recursion, waiter management, and priority inheritance, and would not guard
   high-level pointer lifetime.
6. Per-object locks would permit mixed-generation composition and introduce
   lock ordering across plane, palette, Copper, sprite, cursor, and snapshot
   state.
7. Leaving `Canvas::getPosition()` as a direct `paintState()` read would retain
   a formal race even if pixel readback self-guards.
8. Using the frame-state gate for allocator attempts would let rapid parser
   retries repeatedly force zero-wait frame skips, preventing the actor that
   releases exhausted pool storage from making progress.

When implemented, the retained vdp-gl source selection changes from
`vendored` to `vendored-patched`. The dependency graph, source-selection
manifests, task implementation manifest, and patch inventory must identify the
exact upstream commit and local patch. The removal condition is an accepted
upstream release that provides an equivalent exclusion/lifetime boundary and
passes this task's deterministic and compatibility fixtures.

## Mutation transactions

### Palette and Copper

The P4 controller's single-operation palette and Copper methods self-acquire a
recursive mutation lease. A multi-call palette reset or logical-palette update
also owns one outer transaction so the frame task cannot publish an
intermediate palette. The parser releases the transaction before invoking a
buffer callback capable of nested command processing.

Deleting a palette retains the documented palette-0 substitution. Replacing a
Copper list retains immediate command semantics, but the old list remains live
until an already-acquired frame completes. The next successful frame observes
the complete replacement.

### Sprites and bitmaps

High-level sprite helpers own transactions around active-list count/pointer
changes and direct mutations of frame arrays, current frame, visibility,
position, paint mode, hardware/software selection, and saved backgrounds.
Operations that enqueue a refresh release their outer transaction before the
potentially blocking submission. A helper that needs retained `setSprites()`
first commits its direct-field transaction, releases it, and then invokes
`setSprites()` unwrapped; that method's own suspend/drain/refresh phases remain
authoritative and are tested separately.

Before a project-controlled operation can invalidate bitmap descriptors,
bitmap backing streams, font bytes supplied from a replaceable buffer, or tile
member bitmap/backing storage, the sole retained VDU submitter synchronously
drains the preceding FIFO. Reachable cases include `DrawBitmap`,
`DrawTransformedBitmap`, raw `CopyToBitmap` destinations, buffer clear/replace,
bitmap descriptor reset/recreation, and tile free/re-initialization. The parser
then acquires the gate and detaches every active sprite, text cursor, mouse
cursor, character mapping, and other persistent raw frame-visible user. Only
after detach may it erase the descriptor, owning `shared_ptr`, buffer stream,
tile backing, or other bytes. Guarding the map erase while leaving a queued or
persistent dangling pointer is a failed correction.

The official `Context::plotPath()` is another reachable invalidation: for a
path of at least `FABGLIB_PRIMITIVES_DYNBUFFERS_SIZE` bytes, retained
`primitiveReplaceDynamicBuffers()` does not copy `Path::points`, yet the
context clears its vector immediately after `fillPath()`. Before that clear,
the same sole submitter must synchronously drain the queued path. This adds the
same disclosed parser-latency and logical-edge scheduling change for oversized
paths; smaller paths retain pool-owned copy behavior.

This does not turn borrowed glyph or path APIs into owning APIs. A direct
caller of `Canvas::drawGlyph()` owns `Glyph::data` through execution; a direct
caller of `renderGlyphsBuffer()` owns its `GlyphsBuffer` and bytes; and a
direct caller of `drawPath()` or `fillPath()` outside the managed Context path
owns oversized point storage. No current `vdp/video` caller of
`renderGlyphsBuffer()` was found. Bare `clearFont()` does not release the
selected `Context`'s `FontInfo` backing and therefore does not receive an
unconditional drain. Implementation keeps a compiled inventory of actual
project-controlled invalidation paths; discovery of another reachable
invalidation is a stop condition.

The all-buffer clear path currently clears owning buffers before
`resetBitmaps()`, even though `resetBitmaps()` states that sprites have already
been reset; it does not reset those sprites at all. Individual `clearBitmap()`
also erases bitmap ownership before clearing registered sprite frames. The
rejected candidate would have corrected both orders and the queued-operand
lifetime before a deletion fixture could support closure. These paths are
present in official VDP `v2.16.0`
and were not created by the P4 port. They are now recorded as
`INTEGRITY-AUDIT-F022`; D012 records and defers them, and they are not claimed
corrected.

### Text and mouse cursors

Text-cursor allocation and initialization should occur before acquisition when
possible. The context actor then acquires the gate, swaps the complete bitmap
and sprite generation, publishes the pointer to the controller, and detaches
the old generation before release. Size/color update, position, visibility,
flash, deletion, and mode-reset helpers all use the same boundary.

P4 controller wrappers guard common cursor setters and position changes. The
current P4 input adapter does not make mouse presentation reachable, but the
controller contract must remain safe for the later selected input binding.

## Adjacent lifetime hazards that forbid a shallow closure

### `PORT-003-W2A-H001` — primitive payload pool

Retained `LightMemoryPool` metadata is not synchronized. Parser-side dynamic
path/matrix copying allocates from it while frame execution can free into it.
This structure and concurrency originate in pinned vdp-gl; P4 retains the
common implementation. Exact current evidence is
`vdp/vendor/vdp-gl/src/displaycontroller.cpp:544-580,1493-1494,1567-1568,1803-1805,1844-1846`
and `vdp/vendor/vdp-gl/src/fabutils.{h:747-768,cpp:1416-1485}`; those paths
match pinned upstream `all-the-plots`. Merely holding the frame gate around the
existing blocking allocation helper can prevent the frame task that releases
pool space from entering, and per-attempt use of that gate can repeatedly turn
allocator contention into skipped frames.

The dedicated short-held payload mutex and per-attempt allocation/release seams
in D011 are the proposed bounded remedy. Qualification must separately prove
allocator metadata integrity, exhaustion behavior without an outer suspension,
the documented upstream deadlock warning when a caller submits too much work
inside `beginUpdate()`, and queue forward progress. This is added evidence and
a closure condition for F001, not a claim that the frame gate itself fixes the
pool.

### `PORT-003-W2A-H002` / `INTEGRITY-AUDIT-F022` — deletion and queued raw users

The gate prevents concurrent access; it cannot cure a raw pointer that remains
dangling after the mutation releases the gate. Retained
`BitmapDrawingInfo`/`BitmapTransformedDrawingInfo` store raw bitmap pointers in
queued primitives (`vdp/vendor/vdp-gl/src/displaycontroller.h:558-577,738-760`;
submission is `canvas.cpp:604-610` and `displaycontroller.cpp:525-530`). The
same primitive union can carry borrowed `Glyph::data` and
`GlyphsBufferRenderInfo::glyphsBuffer` (`displaycontroller.h:392-400,473-489`),
and direct callers must retain them; there is no current `vdp/video`
`renderGlyphsBuffer()` caller. Dynamic replacement copies path points only when
their byte count is smaller than `FABGLIB_PRIMITIVES_DYNBUFFERS_SIZE`, while
official `Context::plotPath()` clears its submitted vector immediately
(`canvas.cpp:657-675`; `displaycontroller.cpp:544-562`;
`vdp/video/context/graphics.h:345-366`). It does copy transform matrices.
`CopyToBitmap` retains a raw destination,
and retained tile-layer draws can queue member bitmaps with separately owned
backing. The official individual delete erases bitmap ownership before
clearing registered sprite frames (`vdp/video/sprites.h:74-88`), and the
all-buffer clear destroys
backing streams and bitmap ownership without first resetting sprites
(`vdp/video/vdu_buffered.h:403-415`; `vdp/video/sprites.h:39-42,238-249`). The
same order exists in official VDP `v2.16.0`.

F022 is therefore a definite upstream-origin lifetime defect for reachable
bitmap, buffer, tile, oversized-path, and persistent-user paths, not merely a
prospective port hazard. Generic glyph, glyph-buffer, and direct Canvas path
APIs remain upstream caller-lifetime obligations rather than evidence that the
current VDP parser frees those pointers. D011 proposes a sole-submitter drain
before managed invalidation, then detach-before-destroy under the frame-state
gate. The rejected fixture would have inspected
the state after the command, executed a later frame, and proved that queued
operands were consumed before destruction. F022 remains recorded under D012
without present correction or fixture work.

`PORT-003-W2A-H001` remains a task-local design handle under F001; H002 now
cross-references stable audit finding F022. If implementation review exposes a
behavior change beyond the transaction and drain rules in D011, PORT-003 must
stop and return it for Author disposition.

## Deterministic fixture contract

The fixture exercises the real production gate and production mutation entry
points. A nullable, non-owning qualification probe may report and pause at
named events, but it may not acquire, release, or bypass the product gate.
The same nullable probe branch remains in probe-driven and null-probe builds;
production binds no probe. Compiling the calls out of the tested logic would
make the two binaries different synchronization implementations.

Gate events have exact placement:

1. `frame-before-try` is emitted immediately before the one zero-time gate
   operation. `frame-acquired` is emitted immediately after success;
   `frame-skipped` immediately after failure.
2. `mutation-attempt` is emitted before a zero-time probe. After a failed
   probe, `mutation-contended` is mandatory before the actor performs its
   blocking acquisition. `mutation-acquired` follows successful ownership.
3. `frame-before-release` and `mutation-before-release` are emitted while the
   actor still owns the reported level, immediately before each release. The
   event records pre-release depth; no oracle depends on scheduler order after
   an unlock.
4. `before-primitive`, `before-snapshot-compose`, `payload-attempt`,
   `payload-unavailable`, `payload-acquired`, and `payload-released` identify
   the bounded operations named by the event. `payload-attempt` occurs after
   taking the payload mutex and immediately before `alloc()`;
   `payload-unavailable` or `payload-acquired` occurs immediately after that
   result while the mutex is still held. `payload-released` occurs after
   `free()` and before payload-mutex release. The allocation helper acquires no
   new frame lease; its events may nevertheless inherit an outer mutation lease
   such as `beginUpdate()`, always in frame-state-before-payload order.
5. Every event carries actor ID, actor-local sequence, current gate role and
   recursion depth, and a fixture-controlled rendezvous ID. Service generation
   is present only when supplied by the logical-service owner; snapshot
   generation/transition is present only when supplied by the frame/pool owner.
   A probe never calls an unsynchronized getter or takes the snapshot transition
   lock merely to decorate an event. If cross-actor generation observation is
   needed, implementation adds dedicated atomic diagnostic mirrors that are not
   synchronization authorities. Payload events also carry allocation ID and
   pool transition.

Every managed-lifetime case also records these production events and edges:

1. `operand-enqueued(old-generation, primitive-id)` occurs before the
   invalidating operation's `before-drain`, with that operand still present in the
   FIFO and gate depth zero. The oracle proves no earlier frame tick or
   `before-primitive` consumed it.
2. `drain-primitive(primitive-id)` records every older FIFO ID exactly once in
   order, followed by `drain-show-sprites`, `drain-refresh-submitted`, and
   `drain-returned`. The one `Refresh` rule applies to the specified single-
   buffer, background-enabled setup.
3. Only after `drain-returned` may `mutation-acquired`,
   `persistent-user-detached`, `descriptor-released`, `backing-freed`, and
   `mutation-before-release` occur in that order where each object exists.
4. Actor IDs prove that enqueue, drain, and destructive mutation use the same
   designated submission owner. A post-delete edge executes only the trailing
   `Refresh` and traverses the detached persistent-user set.

Draw oracles bind unique old-generation pixels and reviewed hashes to each
primitive. `CopyToBitmap` cases allocate distinct old and replacement
destinations with different addresses, generations, and canary bytes; the FIFO
write must reach the old still-live destination before its free and must never
touch replacement or poisoned storage.

Condition variables, barriers, or latches establish every relevant ordering.
Sleeps, scheduler luck, and an elapsed interval in which something “did not
happen” are not correctness oracles. A bounded process timeout is only a hang
detector. A worker that exits without reaching its required event reports
`completed-without-required-event`, so missing instrumentation fails
immediately instead of masquerading as a timeout.

The canonical trace is one ordered sequence per actor plus explicit required
happens-before edges created by rendezvous. A raw merged thread log is
diagnostic only because post-release scheduling is nondeterministic.

### Independent oracle authority

Each case has a checked-in, reviewed expectation record independent of the
runner and production result. It fixes:

1. required per-actor event sequences and happens-before edges;
2. exact old/new RGB values or snapshot bytes and their reviewed hashes;
3. primitive execution and contention counts;
4. logical frame counter and service-generation transitions;
5. snapshot-pool generation and slot transitions; and
6. allocation, release, and payload-pool transitions.

The values are hand-derived from accepted Phase C, D, and F contracts plus the
named official behavior. The runner may compare observations with this file;
it may never populate expected bytes, counts, or hashes from the production
output it is validating. In the escaped-frame case, logical frame count and
service generation advance while snapshot generation does not, and the notice
uses the last gate-captured renderer metadata.

### Required cases

#### Gate, parser, and immediate-rendering cases

| Case | Forced order | Decisive expectation |
|---|---|---|
| old-handshake negative control | a test-local model pauses after the old depth check; mutation suspends; frame resumes | the model deterministically overlaps, proving that the choreography detects F001 |
| raw-read negative control | a test-local old path queues a bitmap read, frees the named backing, then executes | isolated ASan child reports heap-use-after-free READ with expected executor and free-site symbols, then exits nonzero |
| stale-destination negative control | a test-local old path queues `CopyToBitmap`, frees its destination, then executes | isolated ASan child reports heap-use-after-free WRITE with expected copy and free-site symbols, then exits nonzero |
| oversized-path negative control | old official Context path submits above the copy threshold, clears, then a legal longer path forces vector reallocation before queued execution | isolated ASan child reports heap-use-after-free READ with the expected path executor and vector reallocation/free symbols; a separate no-reallocation case uses exact stale-point/hash rather than expecting `clear()` alone to free storage |
| persistent-user negative control | a test-local old clear order frees backing before a registered sprite traversal | isolated ASan child reports the expected stale backing read, or a reviewed poison/introspection oracle proves the stale registration decisively |
| escaped frame, foreign owner | production frame pauses before try; parser owns a nested mutation lease; frame resumes | frame skips, dequeues and composes nothing; logical time advances; next edge executes once after release |
| escaped frame, same host owner | the host service call occurs on the thread that already owns `beginUpdate()` | role-aware frame try fails rather than recursively entering; the accepted suspension/counter behavior remains |
| active frame versus synchronous drain | frame pauses after acquisition; synchronous actor calls `waitCompletion(false)` | mutation reports contention and later completes; drain neither double-executes nor double-frees |
| two mutation actors | one mutation pauses after acquisition; a second attempts | the second reports contention and enters only after the first release |
| nesting and final release | one task acquires mutation, recursive read, and mutation levels, then releases each | ownership persists until the final balanced release and another actor then enters |
| misuse fatality | child processes perform cross-task release and same-task over-release | each exits through the expected fatal contract path and never unlocks for a waiter |
| incomplete parser prefix | retained parser receives only a prefix of a palette, Copper, or sprite command; final bytes arrive later | no lease spans input waiting, frames continue, and exactly one complete mutation begins after the final byte |
| inline multi-target buffer adjust | active bitmap/sprite target receives counted inline operands with a frame rendezvous between bytes | each byte is read outside the gate, target is re-resolved inside one mutation lease, and a frame observes only an exact applied prefix or later complete result |
| inline adjust timeout | operand ingress ends after a reviewed prefix | multi-target form retains exactly the already-applied prefix; single-target accumulator performs no backing write; neither path retains a pointer or lease across the wait |
| buffer-fetched/constant adjust | count-bounded adjust uses no parser ingress after transaction start | one mutation transaction completes exact target bytes while a frame skips; later frame observes the complete result |
| bootstrap-to-parser handoff | process task is blocked; bootstrap owns and submits boot screen, drains, then transfers the token under quiescence and releases the barrier | compiled inventory names all producers; runtime assertion accepts bootstrap before and parser after handoff and rejects overlap; no pointer/payload remains and FIFO is empty or contains exactly the named owner-neutral trailing `Refresh` |
| double-buffer immediate draw | frame owns the old-generation exclusion interval before composition; parser submits an ordinary immediate primitive | retained `execPrimitive()` plus `showSprites()` contends as one unit; old/new outputs are complete |
| direct reads | a primitive/palette mutation owns the gate while another actor calls `getPixel()` and `getPosition()` | both reads enter through production seams after release and return one complete reviewed generation |
| palette-0/LUT versus primitive | palette-0 change and LUT rebuild contend with an immediate or queued primitive | primitive color conversion sees the complete old or new palette/LUT pair, never a mixed pair |

#### Payload and queue cases

| Case | Forced order | Decisive expectation |
|---|---|---|
| full queue | queue is full while a submitter blocks and the frame actor runs | queue send owns no newly introduced frame-state or payload lock; frame drains FIFO and sender proceeds |
| exhausted payload pool | every pool block is owned while a path allocation retries | each failed attempt releases the payload mutex; frame entry is not skipped by allocator contention and execution frees space |
| dynamic path lifecycle | one queued copied path executes normally and once during stop drain | allocation and exactly one release occur in both paths; reviewed primitive result is unchanged |
| oversized managed path | official Context submits a path at or above the retained copy threshold, then reaches its production clear | synchronous owner drain consumes the exact old points before clear, adds one `Refresh`, and advances no logical frame or snapshot generation |
| transformed bitmap lifecycle | two matrix allocations are forced around an early and a successful composition path | both allocations are independently recorded and both are released exactly once on every exit |
| retained begin-update warning | a bounded child deliberately exhausts the queue/pool while retaining `beginUpdate()` | the documented upstream deadlock precondition is detected as an expected-invalid use, not claimed as forward progress |

#### Palette, Copper, overlay, and lifetime cases

| Case | Forced order | Decisive expectation |
|---|---|---|
| secondary-palette deletion | frame owns the old palette-generation interval; parser deletes it | deallocation waits; old snapshot is complete and next snapshot uses palette 0 |
| Copper replacement/reset | frame owns a dynamic Copper-list generation; parser replaces or resets it | old allocation remains live until frame release; successive row maps are complete old/new values |
| all-secondary-palette deletion | parser deletes palette ID `65535` while Copper references secondary IDs | affected references redirect to palette 0 as documented; this is not conflated with Copper-list reset |
| sprite list/frame replacement | frame owns active sprite/frame state; parser replaces or removes it | current overlay is complete old state; next is complete replacement or absent |
| software-sprite saved background | single-buffer software sprite reallocates or frees saved background while a frame/drain is scheduled | allocation lifetime is excluded, released once, and later hide/show uses no stale pointer |
| sprite refresh with full queue | high-level direct fields commit, then unwrapped `setSprites()`/`removeSprites()` reaches a full queue | no outer high-level lease remains; frame drains space and retained refresh submission completes |
| bitmap descriptor replacement | `DrawBitmap` names the old descriptor before its production recreation path | single-buffer/background-enabled drain consumes old pixels and hash, calls `showSprites()`, adds one `Refresh`, then releases old descriptor/backing |
| bitmap backing clear | `DrawBitmap` names old backing before the individual production clear command | same exact drain/destruction trace; post-clear frame executes the sole `Refresh` and no stale persistent user |
| transformed bitmap early exit | transformed draw owns two matrix payloads and old bitmap, then production execution takes each early result path | old pixels are consumed before invalidation and both matrices are released once on every exit |
| transformed bitmap success | transformed draw reaches the successful production path before backing clear | old-generation image hash is exact; matrices release once; destruction follows drain return |
| `CopyToBitmap` stale destination | queued copy names distinct old destination before production replacement or clear | old live canary changes exactly before free; replacement and poison canaries remain unchanged |
| managed font backing invalidation | only an inventoried buffer replace/clear actually releases bytes used by a queued glyph | exact glyph bytes are consumed before the real invalidation; bare `clearFont()` performs no unnecessary drain |
| borrowed glyph inventory | direct glyph and glyph-buffer interfaces are compiled without a current parser-side owner invalidation | inventory records caller-lifetime obligation; no parser closure is claimed for absent `renderGlyphsBuffer()` use |
| tile free/re-init | queued tile member bitmap names old backing before real tile free or re-initialization | exact old tile pixels are consumed, then old member and backing release; later frame uses only replacement/absent state |
| destructive drain with full FIFO | a production clear/recreate command starts with the FIFO full and gate depth zero | the same submitter drains the complete FIFO without an outer gate, submits exactly one trailing `Refresh`, returns, then mutates |
| individual bitmap deletion | frame owns the old bitmap generation; parser clears its buffer | registered sprites/cursors/charmaps detach before owner release; a post-delete frame has no stale raw user |
| all-buffer deletion | queued operands and persistent users exist before ID `65535` clear | drain occurs first, every persistent user resets before backing owners, and a post-clear frame is clean |
| text cursor lifecycle | frame owns cursor bitmap state while parser replaces, disables, moves, or deletes it | current frame is complete old state; next frame is complete new/absent state |
| mouse cursor lifecycle | frame owns mouse cursor while the input/parser actor replaces, disables, or moves it | no ISR takes the gate and each later frame observes one complete cursor generation |
| mutation failure unwind | nested palette, Copper, cursor, or replacement allocation fails | every acquired level unwinds, old state remains valid, and a later frame enters |

#### Snapshot and lifecycle cases

| Case | Forced order | Decisive expectation |
|---|---|---|
| deferred publication | one `Latest`, one `Leased`, and one `Producer` exist while consumer transition-lock contention makes `finish()` defer publication | frame releases with `Deferred`; next acquired edge records old producer metadata/generation first, while its frame notice carries separately captured current renderer metadata |
| deferred recovery plus new publication | contention persists beyond snapshot cadence, then next acquired edge finalizes the old producer and successfully finishes a new producer | bounded result contains exactly two ordered publication records with distinct generations and stored producer metadata; current renderer notice remains its separate field |
| deferred cancellation | composition failure plus transition-lock contention makes `finish()` defer cancel | next acquired edge frees the producer before begin; no publication occurs and every slot transition is exact |
| defensive no-free state | a checked internal model injects the otherwise unreachable three-slot no-free invariant | `NoFreeSlot` remains a defensive result; production fixture does not falsely claim normal latest/leased state can exhaust three slots |
| composition failure | compositor returns each defined early failure after slot acquisition | slot is cancelled or explicitly deferred; following frame finalizes it and a later frame/mutation succeeds |
| quiescent composition | unsuspended caller invokes the Phase D seam while service runs | `NotQuiescent` remains authoritative; explicit same-task suspension permits recursive composition |
| frame active, external stop | frame pauses while the lifecycle owner begins stop | timer stops, frame finishes, owner joins without holding a new mutation scope, then retained drain occurs |
| foreign mutation, external stop | mutation actor owns the gate while lifecycle owner joins and a woken frame skips | join completes without waiting for the gate; mutation is released before mutable teardown |
| background disable/re-enable | lifecycle owner disables, recursively drains, retains one level, then re-enables on the same task | trailing `Refresh` is preserved, depth returns to zero after re-enable, and no cross-task release occurs |
| initial preflight failure | gate construction or configured-metadata validation fails before logical start | `running` is never published; explicit controller-not-ready result returns and every level remains balanced |
| partial service-start failures | task creation, timer creation, and timer start fail one at a time after preflight | logical running state rolls back, started resource is joined/destroyed, and same owner leaves no accidental retained level |
| failed new mode, old restart succeeds | facade stops old mode, new configure/start fails, and rollback starts old mode | same lifecycle owner releases disabled level before reporting old mode running; frames no longer skip permanently |
| failed new and old restart | both requested start and rollback restart fail | service reports stopped with exactly one explicit disabled level retained for same-owner retry or close |
| ordinary stopped reconfigure | frame joins while browser retains an immutable old snapshot lease | pending producer settles without frame state; old lease remains valid; new mode cannot reuse its storage |
| stopped reconfigure/destruct | reconfiguration waits for stop/final mutation; destruction also waits for consumer stop and all snapshot leases | no mutable storage changes before join; frame and payload gates close at depth zero with no owners/waiters; no leased slot is destroyed |
| skipped-edge metadata | a synchronous swap owns mutation while a frame edge fails its try | notice reuses last captured renderer metadata rather than racing the current controller; snapshot transition is none and no generation publishes |

Every case records the independent-oracle fields above. Lifetime cases also
record destructor/free counters and a post-operation frame; pool cases record
every allocation ID and transition. Null-probe regression reruns the production
logic without rendezvous to prove the nullable probe does not become a hidden
execution dependency.

The two-mutation-actor case qualifies gate exclusion only. It does not expand
the supported actor model to concurrent `addPrimitive()`, parser submission,
background transitions, configuration, or destructive-buffer commands; those
remain owned by the one retained VDU submission/lifecycle task.

## Sanitizer, runner, and evidence requirements

The new host closure includes the actual controller, Canvas, retained
`displaycontroller.cpp`, palette state, compositor, snapshot pool, and the
high-level parser/sprite/bitmap/font/cursor helpers used by each tested command.
A toy gate, a fixture that manually locks around an unguarded production helper,
or a source-text-only call-site assertion is invalid.

The implementation must choose one executable host entry strategy:

1. compile the real retained header-defined parser/helper closure under a
   bounded host compatibility layer; or
2. extract platform-neutral production transaction functions, make every
   retained helper call those exact functions, execute the functions in the
   fixture, and validate every retained call-site binding and branch order in a
   compiled/link closure. Linkage alone is insufficient: the fixture must feed
   real command bytes or compiled instrumented production branches for
   individual clear, all-clear, bitmap recreation, backing invalidation,
   oversized Context path clear, and tile free/re-init, proving end-to-end
   drain/detach/release order.

If the first source slice shows that neither strategy can execute the named
commands without replacing their behavior, work stops for design review.

The runner performs at least these distinct builds:

1. AddressSanitizer plus UndefinedBehaviorSanitizer with
   `-fsanitize=address,undefined` and
   `-fno-sanitize-recover=undefined`. It sets
   `ASAN_OPTIONS=detect_leaks=1:abort_on_error=1` and
   `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`, fails on nonzero status,
   and also rejects sanitizer diagnostics in captured output. Leak closure
   requires every tracked descriptor/backing generation to reach zero
   outstanding ownership; any necessary suppression is narrow, checked in,
   reviewed, and named in evidence.
2. ThreadSanitizer with `-fsanitize=thread` in a separate binary. The runner
   attempts the exact host invocation proved by exploratory feasibility work
   (currently `setarch x86_64 -R`) and distinguishes the expected
   `ThreadSanitizer: data race` diagnostic from compiler failure,
   `unexpected memory mapping`, or another infrastructure error. It must not
   reuse the current Phase C thread-local notification stub if that stub's
   teardown races independently; fake task handles have stable lifetime or
   non-notification scenarios are isolated.

The runner merges known-safe sanitizer variables with the inherited
environment and records the effective values. It rejects inherited
suppressions or controls that neutralize checks or successful failure status,
including disabled leak checking, `exitcode=0`, or disabled abort/halt behavior.
Separate isolated expected-failure executables prove the oracles:

1. the bitmap, stale `CopyToBitmap` destination, capacity-reallocated oversized
   managed path, and persistent-user controls must emit the exact expected heap-
   use-after-free category, READ or WRITE direction, and reviewed victim/free
   symbols, then exit nonzero; `vector::clear()` alone is never accepted as a
   deallocation oracle, and its retained-capacity case uses exact stale-point/
   pixel hashes instead;
2. a deliberate UBSan violation must emit the expected `runtime error`
   category and exit nonzero; and
3. a deliberate race must emit `ThreadSanitizer: data race` and the expected
   TSan status.

The production ASan/UBSan executable must exit zero without any sanitizer
diagnostic. The production TSan executable must exit zero without any TSan
warning. A nonzero result from an expected-failure probe counts only when the
required diagnostic, access direction, and named symbols are present;
arbitrary failure is not success.

Recorded diagnostic summaries normalize PIDs, addresses, temporary paths, and
stack locations. Evidence records exact source hashes, dependency identities,
compiler identity and flags, inherited-plus-added sanitizer environment,
negative-control result, canonical event traces, allocation/release counts,
frame/snapshot counters, and deterministic output hashes.

No fixture or procedure revision is assigned during this design pass. Runs
before identity approval are explicitly exploratory and cannot support
qualification. Each exploratory result still records repository commit, dirty
state, fixture identity status, and per-input-file hashes. Before controlled
evidence, work stops for Author approval of the fixture artifact ID and
revision under `docs/versions/README.md`; committed inputs are then rerun and
the controlled result records the approved fixture identity, procedure,
commit, dirty state, and per-file hashes. A later clean build cannot
retroactively promote exploratory output.

## Compatibility and regression boundary

Implementation must retain all existing Phase B through F deterministic
coverage and add the new runner to the nonphysical Phase F regression
orchestrator. Nonphysical build validation covers the P4 frame-service,
presentation, official-display, and browser-VDP closures.

The former dirty PORT-008 forwarding prototype was outside Work 2.a and has
since been rejected and superseded. Its `p4-forward-vdp` selector now fails
closed; do not build, rewrite, stage, or use that closure as Work 2.a evidence.

A later P4 target run uses a dedicated synthetic two-FreeRTOS-task concurrency
canary/profile: one task owns retained command/mutation entry points and one is
the real frame-service task. The canary must exercise the same production gate,
payload hooks, parser transaction bindings, and snapshot pool. It cannot use
`p4-browser-vdp`, whose current P4 ingress is disconnected, or the retired
`p4-forward-vdp` prototype. Its firmware, fixture, and procedure IDs and
revisions remain pending Author approval.

That run must measure:

1. contention-skipped renderer opportunities and longest skip streak;
2. worst observed parser mutation latency;
3. frame cadence, backlog, and snapshot publication under mutation stress;
4. queue and payload-pool forward progress; and
5. clean stop/reconfigure behavior on both cores.

It requires separately approved firmware, canary/profile, fixture, and
procedure identities plus explicit deployment and physical-run authorization.
Host sanitizers and a clean target compile cannot pass REMED-002 Gate 2 by
themselves.

## Deferred research slices — not authorized

1. The rejected candidate would first have promoted D011 into ADR-0015, the
   Phase C/D/F contracts, dependency provenance, F022 disposition, and the
   current development log before editing source.
2. Implement and unit-test role-aware `FrameStateGate` and short-held
   `PrimitivePayloadGate` with host and statically allocated FreeRTOS backends,
   recursion/lock-order rules, lifecycle close, ownership queries, diagnostics,
   and fatal misuse handling.
3. Add only the accepted P4-selected, default-preserving retained-common
   submission-owner, immediate-execution, public paint-position-read, and
   payload-attempt/release boundaries; record their exact patch and removal
   condition.
4. Convert `P4DisplayController` frame execution, legacy suspension, quiescent
   composition, synchronous reads, palette/Copper methods, cursor wrappers,
   snapshot publication/result metadata, raw-view contract, and teardown checks
   to the accepted authorities.
5. Bind the real retained parser helpers or extracted production transactions;
   enforce bootstrap-to-parser submission handoff; add the sole-submitter
   pre-invalidation drain for managed bitmap/buffer/tile and oversized Context
   path cases; refactor counted inline buffer adjustment to resolve/apply each
   decoded target unit under the gate without retaining a pointer across
   ingress; and refactor sprite, bitmap, font-backing, tile, and cursor mutations
   for detach-before-destroy and failure unwind.
6. Add independent checked-in oracles, deterministic negative controls and
   production interleavings, null-probe regression, and strict sanitizer
   runners.
7. Run the unaffected Phase B--F host regressions and clean nonphysical P4
   builds, excluding the dirty PORT-008 forward target. All pre-identity
   results remain exploratory.
8. Stop for Author review of source results and approval of fixture,
   canary/profile, procedure, and firmware identities. Commit the controlled
   inputs and rerun them before any evidence claim, deployment, or physical
   qualification.

These slices were part of rejected D011. They cannot proceed without new
Extender-specific trigger evidence satisfying D012 and a separately approved,
narrow replacement decision.

## Rejected candidate stop conditions

Stop and return to the Author if:

1. correction requires changing official VDU bytes, grammar, documented
   palette/Copper/sprite effects, immediate double-buffer behavior, swap or
   notification ordering, queue depth, cancellation, or logical tick
   semantics beyond the disclosed synchronous managed-invalidation drain: all
   older work executes on the parser task, `showSprites()` runs, one `Refresh`
   is appended, no snapshot/logical counter publishes, and parser latency,
   backlog, sprite-redraw scheduling, and later frame skips may change;
2. common-code edits exceed the accepted submission-owner,
   immediate-execution, public paint-position-read, or per-attempt payload
   boundaries, or cannot be kept
   out of classic ISR/IRAM execution without a new decision;
3. any ISR or timer callback would need the gate;
4. a required transaction cannot exclude parser ingress, blocking queue sends,
   callbacks, network work, or task joins, and is not the explicitly selected
   per-decoded-unit buffered-adjust streaming rule;
5. product inspection finds a second concurrent Canvas submitter, a lifecycle
   transition on a different owner task, an escaping raw plane borrow, or a
   managed queued pointer-bearing operand not covered by the drain/ownership
   rule;
6. any path acquires frame state while retaining the payload mutex, or teardown
   cannot reach frame-gate depth zero and zero snapshot leases;
7. detach-before-destroy requires an application-visible behavior choice not
   selected by D011 or fixed by official documentation;
8. source inventory finds another command that waits for ingress while
   retaining a frame-visible pointer or after applying an unclassified partial
   mutation;
9. the existing PORT-008 dirty files overlap a required edit or build claim;
10. sanitizer or deterministic negative-control evidence is inconclusive; or
11. work reaches artifact revision, controlled-evidence status, deployment,
    emulator qualification, or physical-target authority.

## Decision disposition

`PORT-003-D011` is rejected. The project does not select its gate, retained-
common seams, pre-invalidation drain, mutation rewrites, or comprehensive
fixture program for current implementation.

`PORT-003-D012` is accepted. Upstream-origin observations remain recorded for
possible future isolating regression design, but correction requires
reproducible Extender-specific activation or obstruction of a selected
Extender function. The next implementation focus is forward transport over the
parallel GPIO interface. No further Work 2.a action is requested now.
