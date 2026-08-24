#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <unordered_set>

#include "extender/display/palette_state.hpp"

namespace display = agon::extender::display;

namespace {

struct TrackingAllocator {
  std::size_t calls{};
  std::size_t fail_on{};
  std::unordered_set<void *> live;

  static void *allocate(void *context, std::size_t size) {
    auto &self = *static_cast<TrackingAllocator *>(context);
    ++self.calls;
    if (self.fail_on != 0 && self.calls == self.fail_on) return nullptr;
    void *result = std::malloc(size);
    if (result != nullptr) self.live.insert(result);
    return result;
  }
  static void release(void *context, void *allocation) {
    auto &self = *static_cast<TrackingAllocator *>(context);
    if (allocation == nullptr || self.live.erase(allocation) != 1) std::abort();
    std::free(allocation);
  }
  display::Allocator interface() {
    return {this, allocate, release};
  }
};

void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

}  // namespace

int main() {
  TrackingAllocator allocator;
  {
    display::PaletteState state(allocator.interface());
    state.reset(display::NativePixelFormat::PALETTE4);
    std::array<std::uint8_t, 16> values{};
    require(state.copyPalette(0, values.data(), values.size()), "copy primary");
    require(values[0] == 0x00 && values[1] == 0x30 && values[2] == 0x0C &&
                values[3] == 0x3F,
            "default palette4");
    require(state.setItemInPalette(0, 5, 255, 0, 255), "wrapped primary set");
    require(state.createPalette(42), "create copied palette");
    require(state.setItemInPalette(0, 1, 0, 0, 255), "replace primary");
    require(state.copyPalette(42, values.data(), values.size()), "copy secondary");
    require(values[1] == 0x33, "secondary copied pre-mutation primary");
    require(state.setItemInPalette(7, 6, 255, 255, 0), "implicit palette");
    state.updateRGB2PaletteLUT();
    require(state.drawingIndex(0, 85, 85) == 2, "integer HSV LUT fidelity");

    std::uint16_t pairs[] = {0, 42, 2, 99, 1, 7};
    require(state.updateSignalList(pairs, 3), "signal update");
    require(state.signalAt(0).palette_id == 42 &&
                state.signalAt(1).palette_id == 0 &&
                state.signalAt(2).palette_id == 7,
            "signal resolution");
    require(state.createPalette(99), "late create");
    require(state.signalAt(1).palette_id == 0, "late create does not retarget");
    state.deletePalette(42);
    require(state.signalAt(0).palette_id == 0, "delete retargets signal");
    state.deletePalette(65535);
    require(state.secondaryPaletteCount() == 0, "delete all secondary");

    std::uint16_t old_pair[] = {2, 0};
    require(state.updateSignalList(old_pair, 1), "install old signal");
    allocator.calls = 0;
    allocator.fail_on = 1;
    std::uint16_t replacement[] = {1, 0, 1, 0};
    require(!state.updateSignalList(replacement, 2), "signal allocation fails");
    require(state.signalCount() == 1 && state.signalAt(0).end_row == 2,
            "failed signal update preserves old state");
    allocator.fail_on = 0;

    state.reset(display::NativePixelFormat::PALETTE4);
    allocator.calls = 0;
    allocator.fail_on = 1;
    require(!state.createPalette(77), "palette allocation fails");
    require(state.secondaryPaletteCount() == 0, "failed palette leaves old state");
    allocator.fail_on = 0;

    state.reset(display::NativePixelFormat::SBGR2222);
    require(!state.paletted() && !state.createPalette(1), "fixed mode rejects palettes");
    require(state.drawingIndex(255, 85, 170) == 0x27, "fixed RGB222 conversion");
  }
  require(allocator.live.empty(), "all palette allocations released");
  std::cout << "palette-state=pass\n";
  return 0;
}
