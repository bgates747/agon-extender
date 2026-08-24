// PORT-003 Phase D pure presentation compositor.
//
// This API deliberately accepts explicit borrowed views and caller-owned RGB
// storage. It owns no framebuffer lifetime and is not the Phase F consumer or
// lease contract. A caller must establish quiescence for every borrowed input.
#pragma once

#include <cstddef>
#include <cstdint>

#include "extender/display/palette_state.hpp"

namespace agon::extender::display {

struct PresentationRGB888 {
  std::uint8_t red;
  std::uint8_t green;
  std::uint8_t blue;
};

struct PresentationRegion {
  std::size_t x;
  std::size_t y;
  std::size_t width;
  std::size_t height;
};

enum class OverlayPixelFormat : std::uint8_t {
  RGBA2222,
  RGBA8888,
};

enum class OverlayPaint : std::uint8_t {
  Overwrite,
  Xor,
};

struct OverlayView {
  std::int32_t x;
  std::int32_t y;
  std::size_t width;
  std::size_t height;
  OverlayPixelFormat format;
  OverlayPaint paint;
  std::uint8_t const *data;
  std::size_t data_size;
};

enum class CompositionResult : std::uint8_t {
  Ok,
  InvalidMode,
  InvalidPalette,
  InvalidPlane,
  InvalidRegion,
  InvalidDestination,
  InvalidOverlay,
  SizeOverflow,
  NotQuiescent,
};

class PresentationCompositor final {
 public:
  static CompositionResult composeBase(
      ConstPlaneView plane, ModeDescriptor const &mode,
      PaletteState const &palettes, PresentationRegion const &region,
      PresentationRGB888 *destination,
      std::size_t destination_pixels) noexcept;

  // Apply exactly one already-ordered hardware overlay to an RGB region.
  // Controller integration calls this for text cursor, ascending hardware
  // sprites, then mouse cursor. Software sprites never enter this function.
  static CompositionResult applyOverlay(
      PresentationRegion const &region, PresentationRGB888 *destination,
      std::size_t destination_pixels, OverlayView const &overlay) noexcept;
};

}  // namespace agon::extender::display
