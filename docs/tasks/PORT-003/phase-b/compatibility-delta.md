# PORT-003 Phase B compatibility delta

Phase B qualifies synchronous logical storage and rendering only. It does not
claim official mode/facade integration, frame timing, presentation, output, or
physical P4 behavior.

## Retained behavior

- Vendored vdp-gl `Canvas`, common `BitmappedDisplayController`, and generic
  renderer execute unchanged from `all-the-plots`.
- `PALETTE2`, `PALETTE4`, `PALETTE8`, `PALETTE16`, and logical `SBGR2222`
  retain their packed pixel order, legal values, readback colors, and native
  save representation.
- Common paint, clipping, origin, row, copy, scroll, glyph, flood-fill,
  ellipse, arc, segment, sector, bitmap, and transformed-bitmap behavior is
  exercised through the real Canvas/primitive dispatcher at every depth.
- The controller remains usable through the accepted
  `BitmappedDisplayController` base-pointer factory shape.

## Project-owned replacements and adaptations

- `P4DisplayController` replaces the classic concrete VGA controller family
  with sink-free logical storage and synchronous primitive execution.
- `NativePixelCodec` provides bounds-checked packed-bit operations without
  unaligned overreads. In particular, three-bit `PALETTE8` is treated as an
  MSB-first bitstream rather than an unchecked word load.
- `PlaneStorage` replaces VGA viewport allocation with injected,
  transactional one/two-plane ownership. Failed replacement preserves the
  old mode and bytes.
- The narrow `fabutils_port.cpp` closure now includes the exact line,
  rectangle, memory-pool, integer-square-root, bit-reader, quadrant, and arc
  helpers proved necessary by the linked renderer. Broad classic-ESP32
  `fabutils.cpp` remains excluded.
- Host qualification supplies a test-only synchronous queue, inert task
  wrappers, host allocation, and 3×3 matrix operations. These are bounded
  harness facilities, not firmware platform substitutions.

## Deliberately deferred

- Background primitive execution, retained completion behavior, frame cadence and
  counter, swap-at-frame-edge, and frame consumers are Phase C.
- Mutable palettes, Copper, sprites, cursors, and presentation composition are
  Phase D.
- Official mode lookup/fallback, contexts, callbacks, Teletext, and
  `agon_screen.h` integration are Phase E.
- Every physical output sink, EDU/VDU routing, MOS integration, deployment,
  and hardware qualification remains outside this phase.

Direct `P4DisplayController::swapBuffers()` fails visibly. Canvas swap queue
semantics belong to Phase C and are outside the passing Phase B fixture matrix.
The host glyph fixture provides three safe trailing bytes because the retained
upstream narrow-glyph fast path performs a four-byte lookahead over byte-stride
rows; no vendored source was changed.
