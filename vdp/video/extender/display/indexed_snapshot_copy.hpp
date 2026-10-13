// RESEARCH-007 NP03: bounded default-off indexed snapshot-copy pilot.
// Only the existing native Mode20, single-buffered, undecorated background
// uses the proven P4 task-context row-copy kernel. Every other geometry keeps
// copyLinearRow unchanged. The caller still owns native exclusion and each
// authoritative row descriptor; this does not flatten or coalesce allocations.
#pragma once

namespace agon::extender::display {

constexpr bool indexedSnapshotPieGeometry(int width, int height,
                                           bool decorate, bool doubleBuffered)
{
  return width == 512 && height == 384 && !decorate && !doubleBuffered;
}

} // namespace agon::extender::display
