# PORT-003 Review Gate 1 proposal

Status: accepted by delegated Author approval on 2026-08-22. ADR-0015 is the
normative decision record; this document preserves the detailed design and
alternatives that informed it.

## Proposed boundary

Retain the official `agon_screen.h` facade, Canvas, primitive dispatcher,
common renderer, and generic geometry. Replace the entire classic VGA physical
controller inheritance branch with one Extender-owned controller whose runtime
configuration selects the stock native pixel codec for 2, 4, 8, 16, or 64
colors.

The proposed controller derives from
`fabgl::GenericBitmappedDisplayController`. It satisfies the retained
`BitmappedDisplayController` contract but does not derive from
`VGABaseController` or `VGAPalettedController`; doing so would preserve the
GPIO/I2S/DMA/VSYNC machinery the accepted boundary explicitly excludes.

Conceptually the replacement contains four cooperating parts:

1. `P4DisplayController` — the Canvas-facing concrete controller, paint/raw
   operation implementation, mode state, and official frame-counter seam.
2. Native framebuffer storage and depth-specific pixel codecs — authoritative
   logical pixels, one or two drawing/visible planes according to the stock
   mode.
3. Logical frame service — sink-independent cadence, primitive execution,
   swap completion, frame publication, and completion sequencing.
4. Presentation compositor — converts a frozen logical frame into requested
   output rows/regions, applying Copper and non-framebuffer overlays exactly
   once for every sink.

Network, RGB, and MIPI-DSI implementations are consumers outside this core.
They may have different staging buffers and physical completion events but do
not own official VDP time or rendering semantics.

## Narrow official-facade adaptation

Keep these official names and responsibilities recognizable in
`video/agon_screen.h`:

- `canvas`, `_VGAController`, `_VGAColourDepth`, `palette`, `canvasW`,
  `canvasH`, `logicalScaleX`, `logicalScaleY`, `rectangularPixels`, and
  `videoMode`;
- `getVGAController()`, palette/Copper helpers, `updateVGAController()`,
  `changeResolution()`, `changeMode()`, `isDoubleBuffered()`,
  `waitPlotCompletion()`, `switchBuffer()`, and `setMouseCursorPos()`; and
- the complete official mode table and fallback behavior.

Required narrow changes are:

- bind `_VGAController` to the project-owned concrete controller instead of
  `VGABaseController`;
- make the factory configure one controller implementation rather than
  instantiate five old VGA classes;
- delegate palette/Copper calls to the project controller rather than
  downcast to `VGAPalettedController`;
- preserve a writable 32-bit `frameCounter` seam that advances modulo 32 bits
  between explicit official context writes; and
- route the mouse position call through the separately selected input/cursor
  adapter without importing the old PS/2 controller type.

The first implementation should not opportunistically add cleaner accessors
through all official source. Familiar upstream names and a small merge diff
are more valuable here than eliminating every global or direct field access.

## Native logical storage

### Recommendation

Preserve the five upstream native pixel encodings initially:

- `PALETTE2`, `PALETTE4`, `PALETTE8`, and `PALETTE16` packed index formats;
- an `SBGR2222`-compatible six-bit fixed-color contract for 64-color modes;
  logical storage keeps the low RGB222 bits, while legacy H/V sync bits are
  synthesized only where an internal native-save contract requires them; and
- the upstream native bitmap save/readback byte contract.

Use one controller class with depth-specific codec strategies/templates rather
than preserving five physical controller classes. Adapt useful per-depth raw
algorithms with exact upstream provenance. Large row storage belongs in PSRAM;
small metadata and synchronization state remain internal unless measurement
justifies otherwise.

This choice minimizes compatibility variables during the port. A canonical
one-byte index framebuffer would simplify new code and fit in PSRAM, but it
would simultaneously change native bitmap format, packed write behavior,
memory pressure, and copied upstream algorithms. That is a possible later
performance profile only after the compatible backend is proven.

### Allocation and mode changes

Mode setup should be transactional inside the replacement controller:

1. derive a logical mode descriptor from the official mode/modeline input;
2. validate color depth, dimensions, cadence, and supported buffering;
3. allocate and initialize all required planes and metadata before publishing
   them;
4. start or reconfigure the frame service;
5. atomically install the new mode state; and
6. release the old state only after successful installation.

Official `VDU 22` fallback still remains in the facade. Transactional setup
prevents a failed new allocation from needlessly damaging the old mode before
that fallback is attempted. Compatibility fixtures must determine whether any
observable stock failure behavior requires a narrower emulation.

## Logical frame lifecycle

### Clock

Use an `esp_timer` periodic source at the nominal cadence encoded by the
selected official mode. Its callback performs no rendering: it increments or
records a logical tick and notifies a dedicated frame-service task.

The clock runs whenever a valid display mode exists, including with zero
sinks. A sink VSYNC or completion callback can release that sink's buffers but
cannot advance `frameCounter`, execute primitives, or unblock an official swap.

### Per-tick ordering

The initial compatibility target is:

1. record the logical frame edge and advance the writable 32-bit frame count;
2. execute the frame-bounded primitive work permitted by retained queue
   semantics;
3. execute a queued buffer swap against logical drawing/visible planes;
4. refresh software-sprite state and freeze the presentation metadata;
5. publish a new presentation generation.

This mirrors the stock fact that the physical frame interrupt increments the
counter before processing its primitive batch. Exact callback observation and
overrun behavior remain fixture-driven.

### Single and double buffering

In a single-buffered mode, drawing and visible storage are the same plane.
Ordinary background primitives retain ordered queue execution. Presentation
may observe stock-like tearing unless an output consumer requests and can
afford an atomic presentation snapshot; readback always addresses the logical
plane.

In a double-buffered mode, ordinary Canvas drawing retains its immediate
execution against the drawing plane. The swap primitive waits until a logical
frame edge, exchanges drawing and visible planes, and immediately notifies its
caller through unchanged common execution before Phase C publishes metadata.

The strict-compatible implementation retains upstream queue-depth completion
waiting, including its treatment of already-dequeued work. `UPSTREAM-001`
separately evaluates stronger submitted/completed sequencing as a possible
upstream correction.

### Overrun policy

Logical time must not block on a sink. Every recorded timer event receives a
distinct logical frame edge and bounded renderer opportunity, preserving the
upstream physical-VSYNC event model. Exact backlog, frame-wait, and callback
behavior under deliberate overload must be measured against stock firmware.

## Presentation composition

The presentation compositor is the single semantic implementation used by all
sinks. Given a frozen frame generation and requested rows/region, it:

1. decodes native logical pixels;
2. applies palette 0 or the Copper-selected palette for each scanline;
3. emits RGB output in the sink-requested supported format;
4. overlays hardware sprites, mouse cursor, and text cursor without modifying
   logical framebuffer state; and
5. reports the frame generation and dirty/full region represented.

Software sprites remain in the retained common framebuffer path. Hardware
overlays remain absent from `readScreen()` and native bitmap copy operations.
Copper recolors framebuffer indices, including software sprites, but does not
recolor separately composed hardware overlays.

Presentation storage is deliberately not fixed at this gate. The compositor
API supports rows/regions so an encoder can avoid a mandatory full RGB copy,
while a physical sink can maintain RGB565/RGB888 driver buffers. A concrete
consumer must never retain a mutable logical-frame pointer indefinitely.

## Sink-neutral consumer contract

The first implementation should expose a small project-owned contract with
these concepts, without exposing FabGL classes to output modules:

- `FrameGeneration`: monotonically increasing publication identity distinct
  from the writable compatibility `frameCounter`;
- `FrameDescription`: dimensions, logical color depth, nominal cadence,
  buffering state, dirty/full region, and supported presentation formats;
- `FrameReadLease`: bounded access to one frozen generation and its compositor;
- `FrameConsumer`: non-blocking notification that a newer generation exists;
  and
- explicit dropped/overwritten-generation counters.

Consumers pull or request composition into storage they own. Notification is
latest-state, not an unbounded queue of every frame. A slow or disconnected
consumer can drop presentation generations; it cannot hold the renderer,
change logical timing, or exhaust memory. A consumer that requires every frame
must provide its own bounded recording policy and report when it cannot keep
up.

The guaranteed network/browser implementation and future local-display
implementations will separately qualify their encoding, buffer ownership,
cache operations, and completion callbacks against this contract.

## Concurrency ownership

- The frame-service task owns frame-boundary state changes, queued primitive
  execution, logical swaps, and presentation publication.
- Immediate double-buffer drawing enters the controller under a render-state
  mutex; no sink callback shares that lock.
- The timer callback and sink ISR callbacks only update atomic/event state and
  wake tasks.
- Consumers never call Canvas or mutate controller state.
- Palette, Copper, and hardware-overlay changes are captured into a coherent
  presentation generation at a frame boundary.
- Mode teardown first prevents new submissions, then wakes/cancels waiters,
  detaches consumers from the old generation, stops the old clock, and releases
  storage after leases expire or are invalidated by the bounded contract.

Exact task affinity, priority, stack size, queue depth, and lock type remain
implementation measurements. No classic-ESP32 core number or ISR budget is
carried forward.

## Alternatives considered

### Continue deriving from `VGABaseController`

Rejected. It would make the new backend inherit excluded modeline parsing,
sync-bit pixels, GPIO routing, I2S1, DMA descriptors, physical VSYNC, and
classic allocation assumptions. Stubbing those members would produce a large
false compatibility shell and a poor upstream merge boundary.

### Implement a second renderer outside Canvas

Rejected. It would duplicate the official VDP behavior being preserved and
turn future upstream imports into semantic reimplementation exercises.

### One-byte logical pixels for every mode

Deferred as an optional non-strict build/profile optimization. It simplifies
P4 code but changes too many variables before the faithful port is qualified.

### Let the first physical sink drive frames

Rejected. It makes VDP behavior depend on whether a browser, LCD, HDMI bridge,
or no display is attached and directly contradicts the accepted sink-neutral
boundary.

### Compose and retain a full RGB frame every tick

Not required by the core. It is simple and fits in PSRAM, but maximum-size
full-frame conversion can consume substantial bandwidth even when little has
changed. Consumers may select full-frame staging after measurement; the common
contract remains row/region capable.

## Decisions accepted at Review Gate 1

The Author accepted these decisions by delegation on 2026-08-22 and authorized
the Agent to commit the package without personal diff review.

- `PORT-003-D001` — Accepted one project-owned
  `GenericBitmappedDisplayController` implementation with configured native
  pixel codecs, rather than inheritance from classic VGA controllers.
- `PORT-003-D002` — Accepted preserving upstream packed native formats for the
  initial compatible backend; reserve canonical one-byte storage for a later
  qualified profile.
- `PORT-003-D003` — Accepted sink-independent nominal mode cadence from
  `esp_timer`, with physical sink callbacks limited to sink completion.
- `PORT-003-D004` — Accepted the proposed tick, swap, completion, and overrun
  model, subject to stock/P4 fixture results.
- `PORT-003-D005` — Accepted one central presentation compositor that applies
  Copper and hardware overlays while keeping readback logical.
- `PORT-003-D006` — Accepted the latest-generation, non-blocking consumer
  contract and allow slow sinks to drop presentation generations.
- `PORT-003-D007` — Accepted the phased implementation and qualification plan
  in `qualification-plan.md`.

## Review boundary

ADR-0015 promotes the accepted material architecture. This acceptance does not
decide EDU/VDU operating modes, MOS routing, input ownership, network protocols,
or any particular physical sink.
