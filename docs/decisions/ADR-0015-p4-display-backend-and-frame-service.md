# ADR-0015 — P4 display backend and logical frame service

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-22
- Related task: PORT-003

## Context

ADR-0013 retains the official VDP screen facade, FabGL Canvas, common
bitmapped rendering behavior, and generic geometry while excluding the
classic-ESP32 concrete VGA physical engine. PORT-003 Review Gate 1 traced the
remaining compatibility contracts and the facilities available in the pinned
ESP32-P4 framework.

The retained official code depends on more than visible pixels. It expects the
stock mode table and fallback behavior, packed native pixel formats, palette
quantization, Copper scanline interpretation, logical versus hardware sprite
composition, logical readback, primitive completion, frame-boundary buffer
swaps, callbacks, and a directly readable and writable 32-bit frame counter.

The old implementation fuses those contracts to GPIO routing, I2S1, VGA sync
bits, classic DMA descriptors, a physical VSYNC ISR, Xtensa coprocessor state,
and cycle budgets tied to one core. None of those physical mechanisms is an
appropriate P4 display abstraction. The P4 must also support no output sink,
the guaranteed network/browser sink, and later local display sinks without
creating separate VDP renderers or clocks.

## Decision

1. Implement one Extender-owned concrete controller derived from
   `fabgl::GenericBitmappedDisplayController`. Configure it with depth-specific
   native pixel codecs rather than deriving it from the old
   `VGABaseController`, `VGAPalettedController`, or five concrete VGA classes.
2. Preserve the upstream `PALETTE2`, `PALETTE4`, `PALETTE8`, and `PALETTE16`
   packed formats for the initial compatible backend. Preserve the logical
   RGB222 and native-save contract for 64-color modes while excluding physical
   H/V sync bits from authoritative logical storage. A canonical one-byte
   storage profile may be considered later only as an explicitly qualified
   non-strict optimization.
3. Keep the official `agon_screen.h` facade, names, mode table, fallback,
   globals, and responsibilities recognizable. Narrowly replace its concrete
   controller type, factory binding, palette/Copper downcasts, writable frame
   counter seam, and input-owned cursor-position type coupling where required.
4. Advance official display time from a sink-independent periodic logical
   frame clock using the pinned P4 `esp_timer` substrate. The short timer
   callback records ticks and wakes a frame-service task; it performs no
   rendering. Physical sink callbacks report only sink progress and buffer
   availability.
5. Let the frame-service task own frame-boundary state, queued primitive
   execution, logical buffer swaps, presentation publication, and explicit
   completion sequencing. Preserve immediate drawing into the drawing plane
   for double-buffered modes. Do not use queue emptiness alone as proof that an
   already dequeued primitive has completed.
6. At each logical frame edge, advance the writable 32-bit compatibility
   counter, execute frame-bounded work, apply a queued logical swap, freeze
   presentation state, publish the newest generation, and notify waiters
   outside the state lock. Exact overload behavior remains fixture-qualified;
   rendering may coalesce stale ticks, but sinks never block logical time.
7. Implement one central presentation compositor for every sink. It decodes
   native logical pixels, selects palette state by Copper scanline, converts
   to a requested output format, and adds hardware sprites and cursors without
   modifying logical framebuffer state. Logical readback excludes those
   overlays. Software sprites remain in the retained framebuffer path.
8. Expose a project-owned, sink-neutral consumer contract consisting of frame
   generation and description, bounded read/composition access, fixed-capacity
   latest-generation mailboxes, and explicit drop counters. The frame service
   never invokes sink code; consumers poll independently. Slow or absent
   consumers may drop presentation generations but may not retain mutable
   logical storage indefinitely, block rendering, or change VDP timing.
9. Implement and qualify the backend through the phased gates defined by
   PORT-003: contract canary, synchronous native renderer, logical frame
   service, palette/Copper/overlays, official mode integration, consumer
   handoff, and integrated P4 qualification. Each gate requires its own
   deterministic evidence; compilation or a visible image alone is
   insufficient.
10. Replace queue-emptiness completion on the P4 through a minimal auditable
    patch to the vendored common controller: default-no-op primitive
    queued/started/completed hooks plus a virtual completion wait. Project code
    supplies the sequence policy. Non-P4 controllers retain their existing
    behavior, and future upstream imports expose the change as a small direct
    compatibility diff rather than linker interposition or a copied common
    translation unit.

## Rationale

One upstream-shaped Canvas backend preserves the largest body of official
behavior and minimizes future tagged-release merge work. Retaining native
formats bounds the initial compatibility variables. Separating logical time,
logical storage, presentation composition, and physical consumers prevents a
browser, LCD, HDMI bridge, or disconnected cable from redefining official VDP
behavior.

Task-context rendering and explicit completion remove dependencies on the old
VGA ISR and close a queue-empty race without requiring a new renderer. A
central compositor prevents Copper and hardware-overlay behavior from being
reimplemented differently for each output path.

## Consequences

1. The P4 build will not link the classic VGA physical controllers even though
   their complete tagged source remains vendored for provenance and merge
   review.
2. `agon_screen.h` requires a small, prominent P4 binding patch, and official
   frame-counter and cursor-position couplings require explicit compatibility
   seams.
3. Native pixel-codec and raw-operation code adapted from old controllers must
   carry exact upstream provenance and remain distinguishable from new
   project-owned scheduling, memory, composition, and consumer code.
4. Logical rendering must work and advance frames with no sink installed.
5. Every output sink owns its physical buffers, encoding, cache/DMA rules, and
   completion callbacks but consumes the same presentation semantics.
6. Slow consumers cause reported presentation drops rather than command-path
   stalls or unbounded queues.
7. Strict compatibility, optional performance profiles, single-buffer tearing,
   overload handling, and exact callback ordering are claims to qualify with
   recorded fixtures rather than infer from the design.
8. This decision does not choose EDU/VDU routing, MOS integration, input
   ownership, network protocols, or a physical display implementation.
9. The vdp-gl compatibility delta includes a narrow common-code patch. Its
   exact upstream spans, rationale, local behavior, and removal condition must
   remain mechanically auditable for every imported release.
