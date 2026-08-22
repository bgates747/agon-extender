// Deterministic host qualification for transactional PlaneStorage.
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <unordered_set>

#include "extender/display/plane_storage.hpp"

using namespace agon::extender::display;

namespace {

struct AccountingAllocator {
  std::size_t calls = 0;
  std::size_t fail_on_call = 0;
  std::size_t allocations = 0;
  std::size_t frees = 0;
  std::unordered_set<void *> live;

  static void *allocate(void *opaque, std::size_t size) {
    auto &self = *static_cast<AccountingAllocator *>(opaque);
    ++self.calls;
    if (self.fail_on_call != 0 && self.calls == self.fail_on_call) return nullptr;
    void *result = std::malloc(size);
    if (result != nullptr) {
      ++self.allocations;
      self.live.insert(result);
    }
    return result;
  }

  static void deallocate(void *opaque, void *allocation) {
    auto &self = *static_cast<AccountingAllocator *>(opaque);
    if (allocation == nullptr || self.live.erase(allocation) != 1) std::abort();
    ++self.frees;
    std::free(allocation);
  }

  Allocator contract() { return {this, allocate, deallocate}; }
};

void check(bool condition) {
  if (!condition) std::abort();
}

void checkZero(ConstPlaneView view) {
  for (std::size_t index = 0; index < view.size; ++index) check(view.data[index] == 0);
}

void runFormat(NativePixelFormat format) {
  AccountingAllocator accounting;
  {
    PlaneStorage storage(accounting.contract());
    ModeDescriptor first{17, 3, format, false, 0xC0};
    check(storage.configure(first) == ConfigureResult::Ok);
    check(storage.configured());
    check(storage.drawingPlane().data == storage.visiblePlane().data);
    checkZero(static_cast<PlaneStorage const &>(storage).visiblePlane());
    storage.drawingPlane().data[0] = 0x35;
    auto *old_pointer = storage.visiblePlane().data;
    std::size_t old_size = storage.visiblePlane().size;

    accounting.fail_on_call = accounting.calls + 1;
    ModeDescriptor replacement{19, 4, format, true, 0x40};
    check(storage.configure(replacement) == ConfigureResult::FirstPlaneAllocationFailed);
    check(storage.visiblePlane().data == old_pointer);
    check(storage.visiblePlane().size == old_size);
    check(storage.visiblePlane().data[0] == 0x35);
    check(storage.mode().width == first.width);

    accounting.fail_on_call = accounting.calls + 2;
    check(storage.configure(replacement) == ConfigureResult::SecondPlaneAllocationFailed);
    check(storage.visiblePlane().data == old_pointer);
    check(storage.visiblePlane().data[0] == 0x35);
    check(storage.mode().width == first.width);

    accounting.fail_on_call = 0;
    check(storage.configure(replacement) == ConfigureResult::Ok);
    check(storage.drawingPlane().data != storage.visiblePlane().data);
    checkZero(static_cast<PlaneStorage const &>(storage).drawingPlane());
    checkZero(static_cast<PlaneStorage const &>(storage).visiblePlane());

    PlaneStorage moved(std::move(storage));
    check(!storage.configured());
    check(moved.configured());
    storage = std::move(moved);
    check(storage.configured());
    check(!moved.configured());
    storage.release();
    storage.release();
    check(!storage.configured());
  }
  check(accounting.live.empty());
  check(accounting.allocations == accounting.frees);
  std::cout << "format-pass allocations=" << accounting.allocations
            << " frees=" << accounting.frees << '\n';
}

}  // namespace

int main() {
  for (NativePixelFormat format : {
           NativePixelFormat::PALETTE2,
           NativePixelFormat::PALETTE4,
           NativePixelFormat::PALETTE8,
           NativePixelFormat::PALETTE16,
           NativePixelFormat::SBGR2222,
       }) {
    runFormat(format);
  }

  AccountingAllocator accounting;
  PlaneStorage storage(accounting.contract());
  check(storage.configure({0, 1, NativePixelFormat::PALETTE2, false, 0}) ==
        ConfigureResult::InvalidDimensions);
  check(storage.configure({1, 1, NativePixelFormat::PALETTE2, false, 1}) ==
        ConfigureResult::InvalidSyncBits);
  check(storage.configure({std::numeric_limits<std::size_t>::max(), 2,
                           NativePixelFormat::SBGR2222, false, 0}) ==
        ConfigureResult::SizeOverflow);
  PlaneStorage invalid({nullptr, nullptr, nullptr});
  check(invalid.configure({1, 1, NativePixelFormat::PALETTE2, false, 0}) ==
        ConfigureResult::InvalidAllocator);
  std::cout << "validation-pass\n";
  return 0;
}
