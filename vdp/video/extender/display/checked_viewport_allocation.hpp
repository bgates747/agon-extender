#pragma once

// AUDIT-010 RP05 local remedy for inherited FabGL allocation behavior.
//
// The selected FabGL allocator published member pointers and a shortened height
// while a viewport was still being assembled, then dereferenced unchecked row
// tables.  Keep the allocation algorithm here so production and host fault
// injection exercise one implementation.  Remove this adapter only after an
// accepted upstream release provides equivalent all-or-nothing allocation and
// the selected display family has been requalified against it.

#include <cstddef>
#include <cstdint>
#include <limits>

namespace agon::extender::display {

struct PreparedViewport {
  uint8_t ** pools = nullptr;
  volatile uint8_t ** drawing_rows = nullptr;
  volatile uint8_t ** visible_rows = nullptr;
  int pool_count = 0;
  int height = 0;
  bool double_buffered = false;
};

template <typename Heap>
void releasePreparedViewport(Heap & heap, PreparedViewport & viewport)
{
  if (viewport.pools) {
    for (int index = 0; index < viewport.pool_count; ++index)
      heap.release(viewport.pools[index]);
    heap.release(viewport.pools);
  }
  if (viewport.drawing_rows)
    heap.release(const_cast<uint8_t **>(viewport.drawing_rows));
  if (viewport.double_buffered && viewport.visible_rows)
    heap.release(const_cast<uint8_t **>(viewport.visible_rows));
  viewport = {};
}

template <size_t PoolLimit, typename Heap>
bool prepareViewport(
  Heap & heap,
  int requested_height,
  int row_bytes,
  bool double_buffered,
  uint32_t pool_caps,
  uint32_t table_caps,
  size_t reserve_bytes,
  PreparedViewport & output)
{
  if (output.pools || output.drawing_rows || output.visible_rows ||
      requested_height <= 0 || row_bytes <= 0)
    return false;

  const size_t height = static_cast<size_t>(requested_height);
  const size_t copies = double_buffered ? 2u : 1u;
  if (height > std::numeric_limits<size_t>::max() / copies)
    return false;
  const size_t total_rows = height * copies;
  if (total_rows > static_cast<size_t>(std::numeric_limits<int>::max()))
    return false;

  PreparedViewport candidate{};
  candidate.height = requested_height;
  candidate.double_buffered = double_buffered;
  candidate.pools = static_cast<uint8_t **>(
    heap.allocate(sizeof(uint8_t *) * (PoolLimit + 1), table_caps));
  if (!candidate.pools)
    return false;
  for (size_t index = 0; index <= PoolLimit; ++index)
    candidate.pools[index] = nullptr;

  int line_counts[PoolLimit]{};
  size_t remaining_rows = total_rows;
  while (remaining_rows && candidate.pool_count < static_cast<int>(PoolLimit)) {
    const size_t largest = heap.largest(pool_caps);
    if (largest <= reserve_bytes)
      break;
    const size_t affordable = (largest - reserve_bytes) / static_cast<size_t>(row_bytes);
    if (!affordable)
      break;
    const size_t rows = affordable < remaining_rows ? affordable : remaining_rows;
    if (rows > std::numeric_limits<size_t>::max() / static_cast<size_t>(row_bytes))
      break;
    auto * pool = static_cast<uint8_t *>(
      heap.allocate(rows * static_cast<size_t>(row_bytes), pool_caps));
    if (!pool)
      break;
    candidate.pools[candidate.pool_count] = pool;
    line_counts[candidate.pool_count] = static_cast<int>(rows);
    ++candidate.pool_count;
    remaining_rows -= rows;
  }

  if (remaining_rows) {
    releasePreparedViewport(heap, candidate);
    return false;
  }

  const size_t row_table_bytes = height * sizeof(uint8_t *);
  if (double_buffered) {
    candidate.visible_rows = static_cast<volatile uint8_t **>(
      heap.allocate(row_table_bytes, table_caps));
    if (!candidate.visible_rows) {
      releasePreparedViewport(heap, candidate);
      return false;
    }
  }
  candidate.drawing_rows = static_cast<volatile uint8_t **>(
    heap.allocate(row_table_bytes, table_caps));
  if (!candidate.drawing_rows) {
    releasePreparedViewport(heap, candidate);
    return false;
  }
  if (!double_buffered)
    candidate.visible_rows = candidate.drawing_rows;

  size_t line = 0;
  for (int pool_index = 0; pool_index < candidate.pool_count; ++pool_index) {
    uint8_t * row = candidate.pools[pool_index];
    for (int index = 0; index < line_counts[pool_index]; ++index, ++line) {
      if (line < height)
        candidate.drawing_rows[line] = row;
      else
        candidate.visible_rows[line - height] = row;
      row += row_bytes;
    }
  }

  output = candidate;
  return true;
}

template <typename Heap>
void releasePreparedRows(Heap & heap, volatile uint8_t ** rows, int row_count)
{
  if (!rows)
    return;
  for (int index = 0; index < row_count; ++index) {
    if (rows[index]) {
      heap.release(const_cast<uint8_t *>(rows[index]));
      rows[index] = nullptr;
    }
  }
}

template <typename Heap>
bool prepareRows(
  Heap & heap,
  volatile uint8_t ** rows,
  int row_count,
  size_t row_bytes,
  uint32_t caps)
{
  if (!rows || row_count <= 0 || !row_bytes)
    return false;
  for (int index = 0; index < row_count; ++index)
    rows[index] = nullptr;
  for (int index = 0; index < row_count; ++index) {
    rows[index] = static_cast<uint8_t *>(heap.allocate(row_bytes, caps));
    if (!rows[index]) {
      releasePreparedRows(heap, rows, row_count);
      return false;
    }
  }
  return true;
}

} // namespace agon::extender::display
