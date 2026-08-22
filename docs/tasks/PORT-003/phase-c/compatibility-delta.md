# PORT-003 Phase C compatibility delta

Phase C adds logical frame scheduling to the qualified Phase B renderer. This
record distinguishes behavior retained from official VDP/vdp-gl, narrow
P4 physical-executor replacement, project-owned output infrastructure, and behavior deferred
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
  execution, draining, and cleanup behavior.
- The compatibility frame counter remains writable and wraps modulo 2^32.
- Queue-depth completion waiting, immediate swap notification after logical
  visibility changes, background enable/disable ordering, and the trailing
  single-buffer `Refresh` remain unchanged upstream behavior.

## Pristine vendored common code

`PORT-003-D009` supersedes the former D008 lifecycle patch. The strict P4
baseline carries byte-identical vdp-gl `all-the-plots`
`displaycontroller.h` and `displaycontroller.cpp`. The P4 frame task invokes
the existing protected task-context dequeue and primitive executor; inherited
queue state and public Canvas completion behavior remain owned by common code.

The canonical source-baseline validator now requires every managed vdp-gl path
to match the pinned release. The rejected stronger completion candidate remains
recoverable from commit `8aecb0e` and is tracked by `UPSTREAM-001` for A/B
regression testing; it is not product source.

## Project-owned behavior

- `LogicalFrameService` records elapsed ticks and services each as a distinct
  logical frame edge, preserving the upstream one-VSYNC-event/one-edge model.
  It also owns monotonic publication generations.
- `P4FrameService` binds that logic to one `esp_timer` notifier and one
  FreeRTOS owner task; timer callbacks never render, swap, or publish work.
- `P4DisplayController` owns logical plane identity exchange, P4 task
  suspension, and the writable P4 compatibility counter. The unchanged common
  controller owns queue waits, swap notification, background draining, and
  dynamic payload execution/release.
- Publications are immutable metadata notices delivered through eight bounded
  latest-state mailboxes. Consumers poll independently, so no sink code runs
  on the frame-service task. This is a qualification seam, not the frozen
  production sink API.

## Deferred or excluded

Phase C neither implements nor claims compatibility for palette mutation,
Copper, sprite/cursor presentation overlays, official mode/fallback facade,
callbacks, Teletext, VDU/MOS routing, output pixels, physical sinks, network,
audio, input, storage, or updater behavior. Classic VGA/CVBS GPIO, I2S, DMA,
VSYNC ISR, and Xtensa timing machinery remains vendored but excluded from the
P4 build.

Target compilation proves closure only. Cadence, jitter, rollover,
per-edge backlog handling, teardown, and memory claims require the committed Phase C physical
qualification run.
