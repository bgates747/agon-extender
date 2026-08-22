# PORT-003 implementation and qualification plan

This plan turns the Review Gate 1 proposal into small, reviewable increments.
No phase begins until the preceding gate's artifacts are reviewed. A visible
image or successful compile does not establish compatibility.

## Deterministic oracle and fixture structure

Store future PORT-003 fixtures under this task directory until their role is
stable enough for promotion into the permanent test hierarchy. Every fixture
must identify:

- official source tag and selected build profile;
- mode, color depth, buffering state, palette/Copper state, and frame number;
- exact command/primitive sequence and seeded input data;
- expected logical framebuffer bytes or normalized pixel matrix;
- expected readback and presentation output separately;
- expected queue, swap, callback, and frame-counter event trace; and
- generator/capture version with a deterministic content hash.

Golden data should come from one of three explicitly labeled sources:

1. a pure host reference model for straightforward pixel/palette operations;
2. a captured official VDP `v2.16.0` result for behavior coupled to the stock
   controller; or
3. a reviewed source-derived expectation where stock capture is impractical.

Do not silently regenerate a golden file from the implementation under test.

## Host fixture families

### Mode and allocation

- every standard and legacy mode maps to the documented dimensions, color
  count, cadence, scale, rectangular-pixel flag, and buffering state;
- unsupported mode leaves the documented fallback result;
- injected allocation failure at each plane/metadata allocation preserves or
  restores a valid old/default mode;
- mode change resets contexts, secondary Copper state, and both sides of a
  double buffer; and
- repeated color-depth changes release all old storage and waiters.

### Native pixels and primitives

- encode/decode round trips for every pixel value and byte boundary in all
  five native formats, including normalized 64-color storage and synthesized
  native-save sync bits;
- set/XOR/OR/AND/invert painting, clipping, origins, dotted lines, thick lines,
  rows, scrolls, copies, glyphs, paths, ellipses, arcs, sectors, and flood fill;
- mask, RGBA2222, RGBA8888, native, transformed, scaled, and rotated bitmaps;
- overlapping rectangle copies and edge coordinates; and
- deterministic logical-frame hashes compared with the selected oracle.

### Palette and Copper

- default palettes and RGB222 quantization at channel boundaries;
- duplicate physical colors and reverse palette lookup;
- palette create/delete/all-delete behavior and palette-0 protection;
- signal-list boundaries, omitted rows, invalid palette references, and mode
  reset; and
- presentation hashes for multi-palette scanlines while logical framebuffer
  and readback hashes remain unchanged.

### Sprites and cursors

- software-sprite background save, overlap order, movement, hide/show, and
  single- versus double-buffer behavior;
- hardware sprite/cursor overlay order and clipping;
- hardware overlays absent from logical readback;
- Copper affects software-sprite indices but not separately composed hardware
  overlays; and
- mode change preserves the official visible-cursor outcome.

### Queue, frame, and concurrency

- primitive submission order and dynamic-buffer lifetime;
- wait-for-completion retains upstream queue-depth behavior when a primitive
  has already been dequeued;
- single-buffer no-op waits for the next logical frame;
- double-buffer swap becomes visible and unblocks exactly at a logical frame
  edge;
- frame-counter low/high writes, rollover, and context observation;
- sink-free cadence, disconnected consumer, deliberately slow consumer, and
  consumer reconnection;
- palette/Copper/sprite mutation concurrent with frame publication; and
- forced service backlog verifies one edge per recorded tick, consumer drops,
  and unchanged completion behavior without deadlock or unbounded growth.

## Target qualification families

Run these on the named, versioned P4 bench profile only after host gates pass:

- allocate every supported single- and double-buffer mode from the intended
  memory capabilities; record largest free internal block and PSRAM before,
  during, and after teardown;
- validate cache/alignment operations only for buffers actually consumed by a
  P4 peripheral or DMA engine;
- measure 60/70/75 Hz logical cadence, jitter, drift, missed deadlines, and
  frame-counter behavior over sustained runs;
- stress primitive throughput and transformed bitmaps at the qualified 360 MHz
  CPU setting with PSRAM load;
- run mode-change and allocation-failure loops under heap tracing;
- run with null, fast mock, slow mock, disconnecting, and reconnecting frame
  consumers;
- compare target framebuffer/readback/presentation hashes with host goldens;
- measure presentation composition by dirty region and full frame at all mode
  maxima; and
- separately qualify each later network, RGB, or MIPI consumer's buffers,
  callbacks, cache behavior, and drop policy without changing logical timing.

Qualified target runs use the project run-ID and version vocabulary. Test
firmware, fixtures, hardware, wiring, and procedures must be committed or
otherwise content-identified before qualification, as required by
`docs/versions/README.md`.

## Implementation phases and gates

### Phase A — Contract canary

- Add the project-owned controller declarations and minimum facade binding.
- Compile the retained Canvas/common renderer and identify only concrete
  unresolved methods and architecture seams.
- Add compile-time assertions for pixel and mode descriptor assumptions.

Gate A: P4 build succeeds with a null controller lifecycle; no old VGA
physical translation unit is linked; dependency selection and compatibility
delta are updated.

### Phase B — Native storage and synchronous renderer

- Implement mode descriptors, transactional allocation, native codecs, and
  raw operations.
- Run all primitives synchronously with no background frame service.
- Implement logical readback and deterministic host pixel fixtures.

Gate B: all native codec and primitive goldens pass for every color depth;
allocation failure leaves a valid controller state.

### Phase C — Logical frame service

- Add timer notification, frame-service task, unchanged common queue/completion
  behavior, single-buffer queue behavior, double-buffer swaps, and frame
  counter.
- Add null and slow mock consumers.

Gate C: host concurrency tests and target cadence/backlog tests pass without a
physical sink, deadlock, or unbounded queue growth.

### Phase D — Palette, Copper, and overlays

- Port palette state and quantization.
- Add the central row/region compositor and Copper signal-list interpretation.
- Complete software/hardware sprite and cursor distinctions.

Gate D: logical readback and composed presentation fixtures independently
match expected results across all depths and buffering states.

### Phase E — Official mode integration

- Complete the narrow `agon_screen.h` adaptation.
- Restore full mode/fallback/context/callback/mode-information lifecycle.
- Integrate Teletext and the input-owned cursor-position seam without adding
  excluded input drivers.

Gate E: all documented modes, fallback injections, context resets, buffer
swaps, and official VDU display fixtures pass.

### Phase F — Consumer contract handoff

- Freeze the project-owned frame-consumer interface after mock qualification.
- Provide the null/mock reference consumer and integration documentation.
- Hand network/browser delivery and later physical sinks their separately
  owned implementation tasks.

Gate F: a slow or failed consumer demonstrably cannot change official VDP
frame progress, queue completion, memory bounds, or command responsiveness.

### Phase G — Integrated P4 qualification

- Build the selected production profile and run the complete host plus target
  matrix.
- Record compatibility deltas, performance limits, and remaining sink-specific
  work.

Gate G: Author reviews qualified evidence before PORT-003 is marked complete.

## Stop and rollback rules

Stop the active phase for review if any of these occurs:

- satisfying the controller requires retaining old GPIO/I2S/DMA/VSYNC code;
- a proposed facade change spreads beyond the bounded upstream-shaped seam;
- native format or readback behavior must change;
- a sink must control logical frame time or block rendering;
- a test result requires an EDU/VDU operating-mode decision from SETUP-005;
- memory or cadence limits invalidate the proposed architecture; or
- a compatibility delta cannot be made explicit and measurable.

Each phase should begin from a clean committed state and end with reviewable
code, fixtures, evidence, and task/log updates before its qualification commit.
