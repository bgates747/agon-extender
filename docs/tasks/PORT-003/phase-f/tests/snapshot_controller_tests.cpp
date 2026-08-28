// PORT-003 Phase F controller-boundary snapshot integration check.
#include <cstdlib>
#include <iostream>

#include "extender/display/p4_display_controller.hpp"

namespace display = agon::extender::display;

namespace {

void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

void seed(display::P4DisplayController &controller, std::size_t x,
          std::size_t y, std::uint8_t value) {
  auto plane = controller.visiblePlane();
  auto *row = const_cast<std::uint8_t *>(plane.data) + y * plane.stride;
  require(display::NativePixelCodec::write(
              row, controller.logicalWidth(), controller.logicalFormat(), x,
              value) == display::CodecResult::Ok,
          "seed visible logical pixel");
}

}  // namespace

int main() {
  display::P4DisplayController controller(display::defaultDisplayAllocator(),
                                          display::defaultSnapshotAllocator());
  require(controller.snapshotPool().enabled(), "snapshot pool enabled");
  require(controller.configure(
              {2, 1, display::NativePixelFormat::PALETTE4, false, 0}) ==
              display::ConfigureResult::Ok,
          "configure first mode");
  controller.setLogicalFramePeriodMicroseconds(200000);
  controller.enableBackgroundPrimitiveExecution(true);
  controller.executeFrameWork(8);

  display::PresentationSnapshotLease first{};
  require(controller.snapshotPool().tryAcquireLatest(0, first),
          "first boundary published");
  require(first.view().generation == 1 && first.view().width == 2 &&
              first.view().height == 1 && first.view().payload_bytes == 6,
          "first snapshot metadata");
  require(first.view().data[0] == 0 && first.view().data[1] == 0 &&
              first.view().data[2] == 0,
          "cleared logical plane composes black");
  first.release();

  require(controller.setItemInPalette(0, 1, 255, 0, 0),
          "set official red palette entry");
  seed(controller, 0, 0, 1);
  controller.executeFrameWork(8);
  display::PresentationSnapshotLease second{};
  require(controller.snapshotPool().tryAcquireLatest(1, second),
          "second boundary published");
  require(second.view().generation == 2 && second.view().data[0] == 255 &&
              second.view().data[1] == 0 && second.view().data[2] == 0,
          "palette-expanded red is immutable output");
  second.release();

  require(controller.configure(
              {1024, 768, display::NativePixelFormat::PALETTE2, false, 0}) ==
              display::ConfigureResult::Ok,
          "reconfigure maximum mode without snapshot allocation");
  controller.enableBackgroundPrimitiveExecution(true);
  controller.executeFrameWork(8);
  display::PresentationSnapshotLease maximum{};
  require(controller.snapshotPool().tryAcquireLatest(2, maximum),
          "maximum boundary published");
  require(maximum.view().generation == 3 && maximum.view().width == 1024 &&
              maximum.view().height == 768 &&
              maximum.view().payload_bytes ==
                  display::kPresentationSnapshotBytesPerSlot,
          "maximum snapshot metadata");

  std::cout << "snapshot-controller=pass\n";
  return 0;
}
