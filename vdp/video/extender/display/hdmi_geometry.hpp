// HDMI-001: output placement and format conversion only. Logical rendering,
// palettes and Copper remain in the original stock scanline implementation.
#pragma once
#include <cstdint>

namespace agon::extender::display {
constexpr int kHdmiWidth = 1280;
constexpr int kHdmiHeight = 720;
constexpr int kHdmiBytesPerPixel = 3;
constexpr int kHdmiStride = kHdmiWidth * kHdmiBytesPerPixel;

struct HdmiGeometry {
  int source_x{}, source_y{}, destination_x{}, destination_y{}, width{}, height{};
  bool valid() const noexcept { return width > 0 && height > 0; }
};

inline HdmiGeometry centeredHdmiGeometry(int width, int height) noexcept {
  if (width <= 0 || height <= 0) return {};
  HdmiGeometry result;
  result.width = width < kHdmiWidth ? width : kHdmiWidth;
  result.height = height < kHdmiHeight ? height : kHdmiHeight;
  result.source_x = (width - result.width) / 2;
  result.source_y = (height - result.height) / 2;
  result.destination_x = (kHdmiWidth - result.width) / 2;
  result.destination_y = (kHdmiHeight - result.height) / 2;
  return result;
}

inline std::uint8_t expandTwoBits(std::uint8_t value) noexcept {
  value &= 3;
  return static_cast<std::uint8_t>(value | (value << 2) | (value << 4) | (value << 6));
}

// FabGL stores four signal bytes in x^2 lane order. After stripping sync,
// RGB222 is 00BBGGRR. IDF 5.5.5 color_pixel_rgb888_data_t is B,G,R in memory;
// this differs from the browser protocol's RGB888 byte order.
inline void expandSignalRowToHdmi(std::uint8_t const *signal,
                                  std::uint8_t *destination,
                                  int source_x, int width) noexcept {
  for (int x = source_x; x < source_x + width; ++x) {
    const std::uint8_t colour = signal[x ^ 2];
    destination[0] = expandTwoBits(colour >> 4);
    destination[1] = expandTwoBits(colour >> 2);
    destination[2] = expandTwoBits(colour);
    destination += kHdmiBytesPerPixel;
  }
}
} // namespace agon::extender::display
