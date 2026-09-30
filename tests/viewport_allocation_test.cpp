#include "extender/display/checked_viewport_allocation.hpp"

#include <cassert>
#include <cstdlib>
#include <limits>
#include <unordered_set>

using agon::extender::display::PreparedViewport;
using agon::extender::display::prepareRows;
using agon::extender::display::prepareViewport;
using agon::extender::display::releasePreparedRows;
using agon::extender::display::releasePreparedViewport;

namespace {

struct FaultHeap {
  int fail_at = -1;
  int allocation_calls = 0;
  size_t largest_block = 0;
  std::unordered_set<void *> live;

  void * allocate(size_t bytes, uint32_t)
  {
    const int ordinal = allocation_calls++;
    if (ordinal == fail_at)
      return nullptr;
    void * pointer = std::malloc(bytes);
    assert(pointer);
    assert(live.insert(pointer).second);
    return pointer;
  }

  void release(void * pointer)
  {
    assert(pointer);
    assert(live.erase(pointer) == 1);
    std::free(pointer);
  }

  size_t largest(uint32_t) const { return largest_block; }
};

int successfulViewportAllocationCount(bool double_buffered)
{
  FaultHeap heap;
  constexpr size_t reserve = 64;
  heap.largest_block = reserve + 3 * 16;
  PreparedViewport viewport;
  assert(prepareViewport<16>(heap, 7, 16, double_buffered, 1, 2, reserve, viewport));
  assert(viewport.pools && viewport.drawing_rows && viewport.visible_rows);
  assert(viewport.height == 7);
  assert(viewport.double_buffered == double_buffered);
  assert(viewport.pools[viewport.pool_count] == nullptr);
  for (int row = 0; row < viewport.height; ++row) {
    assert(viewport.drawing_rows[row]);
    assert(viewport.visible_rows[row]);
  }
  const int calls = heap.allocation_calls;
  releasePreparedViewport(heap, viewport);
  assert(!viewport.pools && !viewport.drawing_rows && !viewport.visible_rows);
  assert(heap.live.empty());
  return calls;
}

void injectEveryViewportFailure(bool double_buffered)
{
  const int allocation_count = successfulViewportAllocationCount(double_buffered);
  for (int failure = 0; failure < allocation_count; ++failure) {
    FaultHeap heap;
    heap.fail_at = failure;
    heap.largest_block = 64 + 3 * 16;
    PreparedViewport viewport;
    assert(!prepareViewport<16>(heap, 7, 16, double_buffered, 1, 2, 64, viewport));
    assert(!viewport.pools && !viewport.drawing_rows && !viewport.visible_rows);
    assert(viewport.pool_count == 0 && viewport.height == 0);
    assert(heap.live.empty());
  }
}

void injectEveryDmaRowFailure()
{
  constexpr int row_count = 4;
  for (int failure = 0; failure < row_count; ++failure) {
    volatile uint8_t * rows[row_count]{};
    FaultHeap heap;
    heap.fail_at = failure;
    assert(!prepareRows(heap, rows, row_count, 320, 4));
    for (auto row : rows)
      assert(!row);
    assert(heap.live.empty());
  }

  volatile uint8_t * rows[row_count]{};
  FaultHeap heap;
  assert(prepareRows(heap, rows, row_count, 320, 4));
  for (auto row : rows)
    assert(row);
  releasePreparedRows(heap, rows, row_count);
  assert(heap.live.empty());
}

void rejectIncompleteAndInvalidRequests()
{
  FaultHeap heap;
  heap.largest_block = 64 + 16;
  PreparedViewport viewport;
  assert(!prepareViewport<2>(heap, 3, 16, false, 1, 2, 64, viewport));
  assert(heap.live.empty());
  assert(!prepareViewport<2>(heap, 0, 16, false, 1, 2, 64, viewport));
  assert(!prepareViewport<2>(heap, 3, 0, false, 1, 2, 64, viewport));
  assert(!prepareViewport<2>(heap, std::numeric_limits<int>::max(), 16,
                             true, 1, 2, 64, viewport));
  assert(heap.live.empty());
}

} // namespace

int main()
{
  injectEveryViewportFailure(false);
  injectEveryViewportFailure(true);
  injectEveryDmaRowFailure();
  rejectIncompleteAndInvalidRequests();
  return 0;
}
