# ADR-0001 — Place Extender code under `vdp/video/extender/`

- Status: Accepted
- Date: 2026-08-20

## Context

The official Agon VDP configures `video/` as its PlatformIO source directory.
Agon Extender intends to mirror the official VDP's directory names, filenames,
and relative source locations so the P4 firmware remains recognizable as a
port and future upstream changes remain tractable.

Extender also needs a clear ownership boundary for networking, additional
transports, browser presentation, P4-local storage, media, and other functions
that do not belong to the stock compatibility baseline.

Two placements were considered:

1. `vdp/extender/`, as a sibling of the official `video/` source directory; and
2. `vdp/video/extender/`, as an added module beneath that source directory.

The sibling placement would keep the mirrored `video/` tree literally free of
new directories, but it would require additional source discovery through
PlatformIO, CMake, library paths, or source filters.

## Decision

Place new Extender implementation under:

```text
vdp/video/extender/
```

Preserve all existing upstream files at their official relative locations.
Integrate Extender modules through small, documented insertion points rather
than moving stock behavior into the new subtree.

## Reasons

1. The directory is naturally beneath the official PlatformIO `src_dir`, so
   source discovery remains simple.
2. Existing upstream filenames and locations remain unchanged.
3. Includes can use direct, recognizable paths such as
   `extender/<subsystem>.h`.
4. The added directory produces an obvious and reviewable upstream delta.
5. It avoids maintaining a second source-tree mechanism merely to preserve a
   visually pure copy of the upstream directory.

## Consequences

1. A direct tree comparison with official `agon-vdp` will show one additional
   directory beneath `video/`.
2. The subtree needs internal subsystem organization so it does not become a
   miscellaneous collection of unrelated features.
3. Optional modules may require compile-time guards or deliberate source
   selection if PlatformIO would otherwise compile them unconditionally.
4. Changes to upstream-shaped files that call Extender code must remain narrow,
   documented, and attributable to accepted architecture or features.
5. Future upstream synchronization tooling must treat `video/extender/` as a
   project-owned addition, not an upstream conflict.
