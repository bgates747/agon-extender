// RGB-001: preserve six-bit VDU/GCOL semantics in packed HDMI-order B,G,R rows.
#pragma once
#include <cstdint>
#include <cstring>

namespace agon::extender::display {
inline bool rgb888ExperimentGeometry(int colours, int width, int height) noexcept {
  return colours == 64 && (
#ifdef AGON_EXTENDER_HDMI_AUTO
      (width == 848 && height == 480) ||
#endif
      (width == 512 && height == 384) || (width == 320 && height == 240));
}
class Rgb888PixelRef {
 public:
  explicit Rgb888PixelRef(std::uint8_t *p) : p_(p) {}
  operator std::uint8_t() const noexcept {
    return 0xc0 | (p_[2] >> 6) | ((p_[1] >> 6) << 2) | ((p_[0] >> 6) << 4);
  }
  Rgb888PixelRef &operator=(std::uint8_t value) noexcept {
    p_[0] = ((value >> 4) & 3) * 85;
    p_[1] = ((value >> 2) & 3) * 85;
    p_[2] = (value & 3) * 85;
    return *this;
  }
  Rgb888PixelRef &operator=(Rgb888PixelRef const &other) noexcept {
    return *this = static_cast<std::uint8_t>(other);
  }
  Rgb888PixelRef &operator|=(std::uint8_t v) noexcept { return *this = std::uint8_t(*this) | v; }
  Rgb888PixelRef &operator&=(std::uint8_t v) noexcept { return *this = std::uint8_t(*this) & v; }
  Rgb888PixelRef &operator^=(std::uint8_t v) noexcept { return *this = std::uint8_t(*this) ^ v; }
 private:
  std::uint8_t *p_;
};

inline void fillRgb888(std::uint8_t *p, int count, std::uint8_t colour) noexcept {
  if(count <= 0)return;
  Rgb888PixelRef{p} = colour;
  // Repeat an already-expanded pixel by doubling the initialized prefix. This
  // avoids three channel expansions and three tiny stores for every fill pixel.
  int written = 1;
  while(written < count) {
    const int n = written < count-written ? written : count-written;
    std::memcpy(p+written*3,p,n*3);
    written += n;
  }
}
} // namespace agon::extender::display
