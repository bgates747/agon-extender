#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>

#include "extender/display/native_pixel_codec.hpp"
#include "extender/display/palette_state.hpp"
#include "extender/display/presentation_compositor.hpp"

namespace display = agon::extender::display;

namespace {
void *allocate(void *, std::size_t size) { return std::malloc(size); }
void release(void *, void *value) { std::free(value); }
void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}
bool equals(display::PresentationRGB888 value, int red, int green, int blue) {
  return value.red == red && value.green == green && value.blue == blue;
}
}  // namespace

int main() {
  display::Allocator allocator{nullptr, allocate, release};
  display::PaletteState palettes(allocator);
  palettes.reset(display::NativePixelFormat::PALETTE4);
  require(palettes.createPalette(10), "create copper palette");
  require(palettes.setItemInPalette(10, 1, 255, 255, 0), "set copper item");
  std::uint16_t signals[] = {1, 0, 1, 10};
  require(palettes.updateSignalList(signals, 2), "set copper rows");

  display::ModeDescriptor mode{4, 2, display::NativePixelFormat::PALETTE4,
                               false, 0xC0};
  std::array<std::uint8_t, 2> native{};
  for (std::size_t y = 0; y < mode.height; ++y)
    for (std::size_t x = 0; x < mode.width; ++x)
      require(display::NativePixelCodec::write(native.data() + y, mode.width,
                                                mode.format, x,
                                                static_cast<std::uint8_t>(x)) ==
                  display::CodecResult::Ok,
              "encode source");
  display::ConstPlaneView plane{native.data(), native.size(), 1};
  display::PresentationRegion region{0, 0, 4, 2};
  std::array<display::PresentationRGB888, 8> output{};
  require(display::PresentationCompositor::composeBase(
              plane, mode, palettes, region, output.data(), output.size()) ==
              display::CompositionResult::Ok,
          "compose base");
  require(equals(output[1], 0, 0, 255), "row zero palette0");
  require(equals(output[5], 255, 255, 0), "row one copper palette");

  std::array<std::uint8_t, 4> xor_data{{0xC3, 0x00, 0xCC, 0xFF}};
  display::OverlayView overlay{-1, 1, 4, 1,
                               display::OverlayPixelFormat::RGBA2222,
                               display::OverlayPaint::Xor, xor_data.data(),
                               xor_data.size()};
  require(display::PresentationCompositor::applyOverlay(
              region, output.data(), output.size(), overlay) ==
              display::CompositionResult::Ok,
          "compose clipped xor overlay");
  require(equals(output[4], 0, 0, 0), "transparent pixel unchanged");
  require(equals(output[5], 255, 0, 0), "xor applied after copper");
  require(equals(output[6], 255, 0, 255), "opaque xor second pixel");

  auto invalid_format = overlay;
  invalid_format.format = static_cast<display::OverlayPixelFormat>(99);
  require(display::PresentationCompositor::applyOverlay(
              region, output.data(), output.size(), invalid_format) ==
              display::CompositionResult::InvalidOverlay,
          "reject invalid overlay format");

  display::PresentationRegion invalid{4, 0, 1, 1};
  require(display::PresentationCompositor::composeBase(
              plane, mode, palettes, invalid, output.data(), output.size()) ==
              display::CompositionResult::InvalidRegion,
          "reject invalid region");
  std::cout << "presentation-compositor=pass\n";
  return 0;
}
