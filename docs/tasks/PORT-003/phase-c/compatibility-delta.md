# PORT-003 Phase C compatibility delta

Phase C adds logical frame scheduling to the qualified Phase B renderer. This
record distinguishes behavior retained from official VDP/vdp-gl, narrow
patched-vendor integration, project-owned P4 behavior, and behavior deferred
to later PORT-003 phases. Exact source spans and hashes are generated in
`evidence/frame-lifecycle.yaml`; build inclusion is generated in
`evidence/build-closure.yaml` and the canonical dependency graph.

## Retained behavior

- Official Canvas primitive construction and common primitive execution remain
  the rendering path.
- Asynchronous single-buffer commands retain FIFO queue order.
- Double-buffer drawing remains immediate against the drawing plane; queued
  `SwapBuffers` remains the frame-bounded visibility operation.
- Copied path and transformation payloads retain upstream allocation,
  execution, and normal cleanup behavior.
- The compatibility frame counter remains writable and wraps modulo 2^32.
- Non-P4 vdp-gl controllers retain their prior behavior because every added
  common-code lifecycle hook has a default no-op or false implementation.

## Audited patched-vendor seam

`PORT-003-D008` permits local changes only to
`vdp/vendor/vdp-gl/src/displaycontroller.h` and `displaycontroller.cpp`.
The patch exposes reservation, successful enqueue, start, completion,
cancellation, swap-notification deferral, queue cancellation, and a virtual
completion wait. It corrects the P4 queue-empty race without copying the whole
common translation unit or interposing toolchain-specific symbols.

The canonical source-baseline validator requires these two paths to differ
from pinned vdp-gl `all-the-plots`, records both hashes and the decision ID, and
rejects every undeclared vendored difference. Remove or revise this seam only
when a later reviewed upstream baseline provides an equivalent auditable
completion contract.

## Project-owned behavior

- `LogicalFrameService` accounts for all elapsed ticks, coalesces stale work
  into one newest-state pass, and owns monotonic publication generations.
- `P4FrameService` binds that logic to one `esp_timer` notifier and one
  FreeRTOS owner task; timer callbacks never render, swap, publish, or complete
  work.
- `P4DisplayController` owns lifecycle-local sequence accounting, explicit
  completion waits, logical plane identity exchange, teardown cancellation,
  and the writable P4 compatibility counter.
- Publications are immutable metadata notices delivered through eight bounded
  latest-state mailboxes. Consumers poll independently, so no sink code runs
  on the frame-service task. This is a qualification seam, not the frozen
  production sink API.
- The P4 controller explicitly contains an inherited vdp-gl disable-ordering
  quirk that otherwise leaves a trailing queued `Refresh`; comments at the
  workaround state its provenance and removal condition.

## Deferred or excluded

Phase C neither implements nor claims compatibility for palette mutation,
Copper, sprite/cursor presentation overlays, official mode/fallback facade,
callbacks, Teletext, VDU/MOS routing, output pixels, physical sinks, network,
audio, input, storage, or updater behavior. Classic VGA/CVBS GPIO, I2S, DMA,
VSYNC ISR, and Xtensa timing machinery remains vendored but excluded from the
P4 build.

Target compilation proves closure only. Cadence, jitter, rollover,
coalescing, teardown, and memory claims require the committed Phase C physical
qualification run.
