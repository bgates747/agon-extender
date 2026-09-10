# W9 — Restore stock drawing-queue draining and measure it

**Accepted work contract, 2026-09-10.** The Author accepted the W8 findings,
rejected the proposed 64-to-128 experiment, and directed EDP to mirror stock
queue draining. Commit prior progress and this revised contract before coding.
PORT-003 owns the display implementation; AUDIT-005 owns the controlled
comparison and resulting performance attribution.

## Decision and fixed scope

The [W8 source accounting](p4-queue-accounting.md) identifies the installed
64-primitive frame limit as the dominant mechanism in the point benchmark.
Stock VDP v2.16.0 disables background primitive timeouts. Its pinned vdp-gl
`VGABaseController::primitiveExecTask` drains FIFO work until the queue empties
or processing is suspended. It then waits for a refresh notification. There
is no fixed primitive count or wall-time cutoff in this selected stock path.

Implement that drain termination policy in the P4 frame executor. Remove the
primitive-budget parameter from the production frame-service interfaces rather
than replacing 64 with another number or introducing a tuning option. Check
suspension between primitive executions as stock does; retain the existing
P4 suspension handshake around frame work. Do not copy the VGA task's Xtensa
cycle counter, physical interrupt setup or core number.

This amends PORT-003-D013 and ADR-0015: the old bounded drawing opportunity is
superseded. Each elapsed P4 logical tick is still accounted for independently;
this increment does not redesign clock ownership, notification catch-up or
publication. It restores the selected stock **drawing drain policy**, not a
claim that all stock scheduling/physical timing is now identical. Sustained
producers may keep a drain busy, as in stock. Do not quietly add a fairness
cap if that becomes a problem; report the observed behavior for review.

Keep FIFO ordering, unchanged common queue submission/completion and dynamic
payload ownership, immediate pixel-query flush, immediate double-buffered
drawing and queued swap notification. Browser snapshots/credits, parser's
separate 64-call budget, UART rings, RTS/CTS, core affinity/priorities, USB input,
EMOS and the SD workload stay fixed. No retained vdp-gl patch, EMOS rewrite,
browser-input revival, parallel transport or general concurrency hardening.

## Bounded implementation and validation

1. Recheck the cited official PLOT/pixel/flush contracts and pinned stock
   worker, then change only the P4 drawing drain and the interfaces/callers
   needed to remove its count budget. Mark the rationale beside that code.
2. Update the independent frame oracle and affected host harnesses to the
   accepted drain rule. Preserve historical qualification records. Add a
   regression with more than 128 queued primitives that all complete on one
   service opportunity, plus deterministic suspension during a drain and
   resumption in FIFO order. Check immediate completion, queued swaps,
   accumulated ticks, stop/restart and dynamic payload release with the
   existing sanitizer-backed frame/controller tests. Compile affected callers.
3. Build a draft P4 console with standing identity approval: console r08,
   capture procedure r03 and registry r64. Preserve the r07 rollback bundle.
   Verify source closure, unchanged common code and dependency selections.
   Keep EMOS v0.1.12 and the existing r03 benchmark executable unchanged.
4. Complete independent preparation before an emulator attention cue. The
   existing accepted EMOS/native-VDP benchmark review still covers the unchanged
   workload; it does not execute or validate the physical P4 task. No fresh
   visual assets or emulator behavior are introduced by this repair. Use a
   labelled notification-only emulator for review of the P4 change, local
   checks and concrete deployment. Physical flashing still requires the
   explicit gate in HARDWARE.local.md. Freeze candidate inputs and build from
   a clean commit before physical deployment; preserve exact output hashes.
5. After the authorized P4-only flash, require matching startup identity and
   healthy USB/UART/display service. Close the deployment serial session and
   never reopen it during the timed test. Allow at least five seconds after
   closing all video clients before acquisition. The operator then resets
   only Agon at the existing analyzer-ready cue.

## One physical comparison

Use the [W7 browser-off run](browser-disconnected-findings.md) as the reference.
Procedure **uart-path-capture-r03** retains r02's acquisition mechanics:
24 MHz, 720 million samples, four UART/flow-control probes, unchanged raw-first
packing and independent decoders. It changes the selected P4 image and records
the drain policy, exact build/manifest and deployment receipt. No serial or
diagnostic network traffic occurs during the window. The operator confirms
browser closure; do not claim independent server client-count measurement.

The unchanged SD fixture is `uart-path-benchmark-r03-b2026-09-10-18-21-38Z`,
invoked with `RUN . trace count points`: mode 0, 512 counted 64-byte writes,
32,768 bytes, keys released. `/autoexec.txt` selects video mode; the fixture
does not. Its compiled CSV annotations still name the original r07 image and
connected browser condition. Preserve those raw bytes and explicitly override
both stale annotations in the host comparison record using the verified r08
deployment and operator-confirmed browser-off condition. Neither stale text
is a live observation. Reject a comparison missing this binding.

Return the SD after the final result and MOS prompt. Preserve all earlier CSVs.
Require correct marker, exact payload and final pixel reply; no framing or
flow-control violations; independent decode agreement; unchanged fixture hash;
correct pixels, first ordinary MOS timeout status, clock arithmetic and
successful Legacy return. Require keyboard usability after completion, outside
the timed interval. No routine screenshot is needed.

Report send/tail/total times, CTS-high and CTS-low idle, burst cadence and
final-reply permission against W7. Removing the frame-count throttle predicts
loss of its sustained approximately 60 Hz/102-byte burst pattern and a material
drop in point-workload time. **Do not retain the abandoned 2.533-second forecast:**
that applied only to doubling the budget. UART overhead, parsing, drawing and
other contention now determine the observed duration; no exact new time is
claimed in advance.

Stop after this one measured comparison. A pass does not qualify all drawing
loads, game responsiveness, browser fps or full stock timing parity. Present
the result and one next recommendation for Author review. No silent retry,
budget sweep, core change or full-suite/game modification. The deferred
[affinity review](../PORT-003.md#deferred-core-affinity-review) becomes diagnostic
only if the current investigations leave the slowdown unresolved; otherwise
it waits for optimization after implementation is substantially complete.

## References

1. [W8 source comparison and exact pinned references](p4-queue-accounting.md).
2. [Amended frame contract](../PORT-003/phase-c/contracts.md) and
   [ADR-0015](../../decisions/ADR-0015-p4-display-backend-and-frame-service.md).
3. [W7 procedure](browser-disconnected-control.md) and unchanged evidence.
4. [Bench constraints](../../qualification/bench-constraints.md); private bench
   identity, media paths and staging live only in ignored local records.
