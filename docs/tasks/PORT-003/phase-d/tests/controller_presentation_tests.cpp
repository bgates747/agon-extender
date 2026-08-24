// PORT-003 Phase D retained-controller presentation integration test.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>

#include "extender/display/p4_display_controller.hpp"
#include "extender/display/logical_frame_service.hpp"

namespace display = agon::extender::display;

namespace {

void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

bool equals(display::PresentationRGB888 value, int red, int green, int blue) {
  return value.red == red && value.green == green && value.blue == blue;
}

void seedLogical(display::P4DisplayController &controller, std::size_t x,
                 std::size_t y, std::uint8_t value) {
  auto plane = controller.visiblePlane();
  auto *row = const_cast<std::uint8_t *>(plane.data) + y * plane.stride;
  require(display::NativePixelCodec::write(
              row, controller.logicalWidth(), controller.logicalFormat(), x,
              value) == display::CodecResult::Ok,
          "seed logical pixel");
}

void seedDrawing(display::P4DisplayController &controller, std::size_t x,
                 std::size_t y, std::uint8_t value) {
  auto plane = controller.drawingPlane();
  auto *row = const_cast<std::uint8_t *>(plane.data) + y * plane.stride;
  require(display::NativePixelCodec::write(
              row, controller.logicalWidth(), controller.logicalFormat(), x,
              value) == display::CodecResult::Ok,
          "seed drawing pixel");
}

void configureBitmap(fabgl::Bitmap &bitmap, std::uint8_t *data) {
  bitmap.width = 1;
  bitmap.height = 1;
  bitmap.format = fabgl::PixelFormat::RGBA2222;
  bitmap.data = data;
  bitmap.dataAllocated = false;
}

}  // namespace

int main() {
  display::P4DisplayController controller(display::defaultDisplayAllocator());
  require(controller.configure(
              {4, 2, display::NativePixelFormat::PALETTE4, false, 0}) ==
              display::ConfigureResult::Ok,
          "configure controller");
  for (std::size_t y = 0; y < 2; ++y)
    for (std::size_t x = 0; x < 4; ++x) seedLogical(controller, x, y, 1);

  require(controller.createPalette(10), "create secondary palette");
  require(controller.setItemInPalette(10, 1, 255, 255, 0),
          "set secondary palette");
  std::uint16_t signals[] = {1, 0, 1, 10};
  require(controller.updateSignalList(signals, 2), "install Copper signals");

  std::uint8_t text_data = 0xF0;      // opaque blue
  std::uint8_t hardware_data = 0xCC;  // opaque green
  std::uint8_t mouse_data = 0xC3;     // opaque red
  fabgl::Bitmap text_bitmap;
  fabgl::Bitmap hardware_bitmap;
  fabgl::Cursor mouse{};
  configureBitmap(text_bitmap, &text_data);
  configureBitmap(hardware_bitmap, &hardware_data);
  configureBitmap(mouse.bitmap, &mouse_data);

  fabgl::Sprite text;
  text.addBitmap(&text_bitmap)->moveTo(1, 0);
  text.hardware = true;
  controller.setTextCursor(&text);

  fabgl::Sprite hardware;
  hardware.addBitmap(&hardware_bitmap)->moveTo(1, 0);
  hardware.hardware = true;
  controller.setSprites(&hardware, 1);

  mouse.hotspotX = 0;
  mouse.hotspotY = 0;
  controller.setMouseCursor(&mouse);
  controller.setMouseCursorPos(1, 0);

  std::array<display::PresentationRGB888, 8> output{};
  display::PresentationRegion full{0, 0, 4, 2};
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "compose controller output");
  require(equals(output[0], 0, 0, 255), "palette zero base");
  require(equals(output[1], 255, 0, 0), "mouse is final overlay");
  require(equals(output[4], 255, 255, 0), "Copper changes presentation row");

  controller.setMouseCursor(nullptr);
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "compose without mouse");
  require(equals(output[1], 0, 255, 0), "hardware sprite follows text cursor");
  hardware.allowDraw = false;
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "compose text cursor only");
  require(equals(output[1], 0, 0, 255), "text cursor precedes sprite array");

  std::array<fabgl::RGB888, 8> logical{};
  controller.readScreen(fabgl::Rect(0, 0, 3, 1), logical.data());
  require(logical[4].R == 0 && logical[4].G == 0 && logical[4].B == 255,
          "readScreen ignores Copper and overlays");
  require(controller.setItemInPalette(0, 1, 255, 0, 0),
          "mutate primary palette");
  controller.readScreen(fabgl::Rect(0, 0, 3, 1), logical.data());
  require(logical[4].R == 255 && logical[4].G == 0 && logical[4].B == 0,
          "readScreen follows palette zero");
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "compose after primary mutation");
  require(equals(output[4], 255, 255, 0),
          "secondary Copper palette remains independent");

  display::LogicalFrameService service(controller, 8);
  require(service.start(), "start frame service");
  controller.enableBackgroundPrimitiveExecution(true);
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::NotQuiescent,
          "reject unsuspended service composition");
  controller.suspendBackgroundPrimitiveExecution();
  require(controller.composeVisibleRegionQuiescent(
              full, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "accept explicitly suspended composition");
  controller.resumeBackgroundPrimitiveExecution();
  service.stop();

  controller.setTextCursor(nullptr);
  controller.setMouseCursor(nullptr);
  controller.removeSprites();
  require(controller.configure(
              {2, 1, display::NativePixelFormat::PALETTE8, true, 0}) ==
              display::ConfigureResult::Ok,
          "configure double buffer");
  seedLogical(controller, 0, 0, 1);
  seedDrawing(controller, 0, 0, 2);
  std::array<display::PresentationRGB888, 2> double_output{};
  display::PresentationRegion double_region{0, 0, 2, 1};
  require(controller.composeVisibleRegionQuiescent(
              double_region, double_output.data(), double_output.size()) ==
              display::CompositionResult::Ok,
          "compose visible plane");
  require(equals(double_output[0], 170, 0, 0),
          "composition selects visible plane");
  std::array<fabgl::RGB888, 2> double_readback{};
  controller.readScreen(fabgl::Rect(0, 0, 1, 0), double_readback.data());
  require(double_readback[0].R == 0 && double_readback[0].G == 170 &&
              double_readback[0].B == 0,
          "readScreen selects drawing plane");

  require(controller.configure(
              {2, 1, display::NativePixelFormat::SBGR2222, false, 0xC0}) ==
              display::ConfigureResult::Ok,
          "configure software sprite mode");
  std::uint8_t software_data = 0xC3;
  fabgl::Bitmap software_bitmap;
  configureBitmap(software_bitmap, &software_data);
  fabgl::Sprite software;
  software.addBitmap(&software_bitmap)->moveTo(0, 0);
  software.hardware = false;
  controller.setSprites(&software, 1);
  std::array<display::PresentationRGB888, 2> software_output{};
  require(controller.composeVisibleRegionQuiescent(
              double_region, software_output.data(), software_output.size()) ==
              display::CompositionResult::Ok,
          "compose software sprite");
  require(equals(software_output[0], 255, 0, 0),
          "software sprite is stored before composition");
  std::array<fabgl::RGB888, 2> software_readback{};
  controller.readScreen(fabgl::Rect(0, 0, 1, 0), software_readback.data());
  require(software_readback[0].R == 255 && software_readback[0].G == 0 &&
              software_readback[0].B == 0,
          "software sprite appears in logical readback");
  controller.removeSprites();

  std::cout << "controller-presentation=pass\n";
  return 0;
}
