# PORT-003 Phase B contracts

This document freezes the project-owned contracts required before Phase B
implementation. It is scoped to synchronous logical storage and rendering;
later phases may extend these contracts without weakening the behavior below.

## Logical mode

`ModeDescriptor` contains positive `width` and `height`, one of `PALETTE2`,
`PALETTE4`, `PALETTE8`, `PALETTE16`, or `SBGR2222`, a `double_buffered` flag,
and the two inactive-sync bits used only when exporting legacy SBGR2222 native
save bytes. Phase B does not accept a modeline or official mode number.

The native row stride is the smallest whole-byte stride that contains the
logical row: `ceil(width × bits_per_pixel / 8)`. Checked multiplication must
reject row, plane, or two-plane size overflow before calling an allocator.
There is no hidden width quantization. This intentionally permits odd and
boundary-straddling fixture widths while preserving upstream packed-bit order.

## Native pixel codecs

The codec is pure, allocation-free, and independent of FabGL, Arduino, and
FreeRTOS. A logical pixel is an unsigned value whose legal range is determined
by the format: 0–1, 0–3, 0–7, 0–15, or 0–63. Out-of-range coordinates and
values return an explicit error and do not alter storage.

Packed formats use one MSB-first bitstream per row:

- `PALETTE2`: eight one-bit pixels per byte, pixel 0 in bit 7;
- `PALETTE4`: four two-bit pixels per byte, pixel 0 in bits 7–6;
- `PALETTE8`: eight three-bit pixels per 24 bits, pixel 0 in bits 23–21;
- `PALETTE16`: two four-bit pixels per byte, pixel 0 in the high nibble; and
- `SBGR2222`: one byte per pixel, logical `BBGGRR` in bits 5–0.

Unused low-order tail bits in the last packed byte remain zero after clear and
all whole-plane operations. SBGR2222 storage never carries timing state: bits
7–6 remain zero. Legacy native-save export ORs the mode's validated inactive
sync bits into each saved SBGR2222 byte; logical readback ignores those bits.

Phase B uses the immutable upstream default palette and its reviewed RGB222
nearest-entry mapping only to convert renderer `RGB888` colors into logical
indices. Palette mutation, alternate palettes, Copper lists, and presentation
quantization remain Phase D work.

## Transactional plane storage

`PlaneStorage` owns zero, one, or two independently allocated contiguous
planes. Allocation is injected through an `Allocator` contract carrying
allocate/deallocate callbacks plus opaque context. The default target adapter
may select P4 memory capabilities; pure host tests inject deterministic
failures and accounting.

`configure(mode)` is transactional:

1. validate and calculate all sizes without changing current state;
2. allocate every required new plane;
3. zero every byte deterministically;
4. only then atomically replace the old mode and planes; and
5. release the old planes after the new state is complete.

Any validation or allocation failure releases only new temporary allocations
and leaves the old valid state byte-for-byte unchanged. `release()` is
idempotent. Move construction/assignment transfer ownership; copying is
forbidden. Destruction releases every owned allocation exactly once.

In single-buffer mode, drawing and visible access name the same plane. In
double-buffer mode, visible is plane 0 and drawing is plane 1. Phase B exposes
both identities for tests and consumers but does not swap them: logical
swap-at-frame-edge belongs to Phase C.

## Synchronous controller

The concrete controller remains constructible through a factory returning
`std::unique_ptr<fabgl::BitmappedDisplayController>`. A project `configure`
method returns a typed result and installs a logical mode only after
`PlaneStorage` succeeds. The inherited modeline-based `setResolution` is not
the official facade and must reject unsupported modeline interpretation rather
than silently guess; Phase E will bind official modes.

After configuration, the controller initializes FabGL dimensions, viewport,
paint state, and queue metadata, then permanently selects immediate primitive
execution for Phase B. Suspend/resume are balanced synchronous no-ops. No
timer, task, ISR, frame counter, consumer callback, physical driver, or sink is
created. Calling deferred buffer swap or presentation-only behavior fails
visibly.

Renderer entry points use the drawing plane and project codec. `readScreen`
uses logical pixels and the immutable Phase B default palette; native bitmap
save uses the exact codec/native-save rules above. Common clipping, origins,
paths, ellipses, arcs, sectors, glyphs, bitmap transforms, and primitive
dispatch remain upstream code where the provenance inventory marks them
`retain-common`. Only depth/storage seams marked `adapt-depth-algorithm` may be
ported into project source, with the exact upstream span named inline.

## Results and invariants

Configuration distinguishes at least: success, invalid dimensions, invalid
format/sync bits, size overflow, first-plane allocation failure, and
second-plane allocation failure. Codec operations distinguish success,
invalid format/value, and out-of-range coordinate. Host evidence must prove:

1. failure never changes an installed mode or plane bytes;
2. no failure leaks or double-frees;
3. clear/release/reconfigure are deterministic;
4. drawing and visible identity obey single/double rules;
5. deferred operations cannot be mistaken for success; and
6. no implementation output is used as its own expected result.
