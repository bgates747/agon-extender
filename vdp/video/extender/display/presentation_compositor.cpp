// See presentation_compositor.hpp.
//
// The hardware-overlay pixel rules are adapted from immutable vdp-gl
// all-the-plots VGAPalettedController::rawDrawSpriteScanline(). This code emits
// RGB888 and deliberately contains no VGA sync-byte, packed signal-table, DMA,
// GPIO, I2S, interrupt, frame-service, or sink behavior.
#include "extender/display/presentation_compositor.hpp"

#include <limits>

namespace agon::extender::display {
namespace {

bool multiply(std::size_t left, std::size_t right,
              std::size_t &result) noexcept {
  if (left != 0 && right > std::numeric_limits<std::size_t>::max() / left)
    return false;
  result = left * right;
  return true;
}

bool fitsSignedCoordinate(std::size_t value) noexcept {
  return value <= static_cast<std::size_t>(
                      std::numeric_limits<std::int64_t>::max());
}

PresentationRGB888 expandRGB222(std::uint8_t packed) noexcept {
  return {
      static_cast<std::uint8_t>((packed & 3) * 85),
      static_cast<std::uint8_t>(((packed >> 2) & 3) * 85),
      static_cast<std::uint8_t>(((packed >> 4) & 3) * 85),
  };
}

std::uint8_t packRGB222(PresentationRGB888 const &pixel) noexcept {
  return static_cast<std::uint8_t>((pixel.red >> 6) |
                                   ((pixel.green >> 6) << 2) |
                                   ((pixel.blue >> 6) << 4));
}

}  // namespace

CompositionResult PresentationCompositor::composeBase(
    ConstPlaneView plane, ModeDescriptor const &mode,
    PaletteState const &palettes, PresentationRegion const &region,
    PresentationRGB888 *destination,
    std::size_t destination_pixels) noexcept {
  if (mode.width == 0 || mode.height == 0) return CompositionResult::InvalidMode;
  if (palettes.format() != mode.format) return CompositionResult::InvalidPalette;
  if (region.width == 0 || region.height == 0 || region.x >= mode.width ||
      region.y >= mode.height || region.width > mode.width - region.x ||
      region.height > mode.height - region.y)
    return CompositionResult::InvalidRegion;
  std::size_t required_pixels = 0;
  if (!multiply(region.width, region.height, required_pixels))
    return CompositionResult::SizeOverflow;
  if (destination == nullptr || destination_pixels < required_pixels)
    return CompositionResult::InvalidDestination;
  std::size_t minimum_stride = 0;
  if (NativePixelCodec::rowStride(mode.format, mode.width, minimum_stride) !=
      CodecResult::Ok)
    return CompositionResult::InvalidMode;
  std::size_t required_plane = 0;
  if (!multiply(plane.stride, mode.height, required_plane))
    return CompositionResult::SizeOverflow;
  if (plane.data == nullptr || plane.stride < minimum_stride ||
      plane.size < required_plane)
    return CompositionResult::InvalidPlane;

  for (std::size_t dy = 0; dy < region.height; ++dy) {
    std::size_t y = region.y + dy;
    auto const *row = plane.data + y * plane.stride;
    for (std::size_t dx = 0; dx < region.width; ++dx) {
      std::uint8_t logical = 0;
      if (NativePixelCodec::read(row, mode.width, mode.format, region.x + dx,
                                 logical) != CodecResult::Ok)
        return CompositionResult::InvalidPlane;
      destination[dy * region.width + dx] =
          expandRGB222(palettes.presentationColor(y, logical));
    }
  }
  return CompositionResult::Ok;
}

CompositionResult PresentationCompositor::applyOverlay(
    PresentationRegion const &region, PresentationRGB888 *destination,
    std::size_t destination_pixels, OverlayView const &overlay) noexcept {
  if (region.width == 0 || region.height == 0)
    return CompositionResult::InvalidRegion;
  std::size_t required_destination = 0;
  if (!multiply(region.width, region.height, required_destination))
    return CompositionResult::SizeOverflow;
  if (destination == nullptr || destination_pixels < required_destination)
    return CompositionResult::InvalidDestination;
  if (overlay.width == 0 || overlay.height == 0 || overlay.data == nullptr)
    return CompositionResult::InvalidOverlay;
  if ((overlay.format != OverlayPixelFormat::RGBA2222 &&
       overlay.format != OverlayPixelFormat::RGBA8888) ||
      (overlay.paint != OverlayPaint::Overwrite &&
       overlay.paint != OverlayPaint::Xor))
    return CompositionResult::InvalidOverlay;
  if (!fitsSignedCoordinate(region.x) || !fitsSignedCoordinate(region.y) ||
      !fitsSignedCoordinate(region.width) ||
      !fitsSignedCoordinate(region.height) ||
      !fitsSignedCoordinate(overlay.width) ||
      !fitsSignedCoordinate(overlay.height))
    return CompositionResult::SizeOverflow;
  std::size_t source_pixels = 0;
  if (!multiply(overlay.width, overlay.height, source_pixels))
    return CompositionResult::SizeOverflow;
  std::size_t bytes_per_pixel =
      overlay.format == OverlayPixelFormat::RGBA8888 ? 4 : 1;
  std::size_t source_bytes = 0;
  if (!multiply(source_pixels, bytes_per_pixel, source_bytes))
    return CompositionResult::SizeOverflow;
  if (overlay.data_size < source_bytes) return CompositionResult::InvalidOverlay;

  // Signed 64-bit coordinates avoid overflow when a caller supplies an
  // extreme negative position. The visible intersection is converted back to
  // size_t only after both axes are proven nonnegative and in-range.
  std::int64_t region_left = static_cast<std::int64_t>(region.x);
  std::int64_t region_top = static_cast<std::int64_t>(region.y);
  if (static_cast<std::uint64_t>(region_left) + region.width >
          static_cast<std::uint64_t>(
              std::numeric_limits<std::int64_t>::max()) ||
      static_cast<std::uint64_t>(region_top) + region.height >
          static_cast<std::uint64_t>(
              std::numeric_limits<std::int64_t>::max()))
    return CompositionResult::SizeOverflow;
  std::int64_t region_right =
      region_left + static_cast<std::int64_t>(region.width);
  std::int64_t region_bottom =
      region_top + static_cast<std::int64_t>(region.height);
  std::int64_t overlay_left = overlay.x;
  std::int64_t overlay_top = overlay.y;
  if (overlay_left > 0 &&
      static_cast<std::uint64_t>(overlay_left) + overlay.width >
          static_cast<std::uint64_t>(
              std::numeric_limits<std::int64_t>::max()))
    return CompositionResult::SizeOverflow;
  if (overlay_top > 0 &&
      static_cast<std::uint64_t>(overlay_top) + overlay.height >
          static_cast<std::uint64_t>(
              std::numeric_limits<std::int64_t>::max()))
    return CompositionResult::SizeOverflow;
  std::int64_t overlay_right =
      overlay_left + static_cast<std::int64_t>(overlay.width);
  std::int64_t overlay_bottom =
      overlay_top + static_cast<std::int64_t>(overlay.height);
  std::int64_t left = overlay_left > region_left ? overlay_left : region_left;
  std::int64_t top = overlay_top > region_top ? overlay_top : region_top;
  std::int64_t right = overlay_right < region_right ? overlay_right : region_right;
  std::int64_t bottom = overlay_bottom < region_bottom ? overlay_bottom : region_bottom;
  if (left >= right || top >= bottom) return CompositionResult::Ok;

  for (std::int64_t y = top; y < bottom; ++y) {
    std::size_t source_y = static_cast<std::size_t>(y - overlay_top);
    std::size_t destination_y = static_cast<std::size_t>(y - region_top);
    for (std::int64_t x = left; x < right; ++x) {
      std::size_t source_x = static_cast<std::size_t>(x - overlay_left);
      std::size_t source_index = source_y * overlay.width + source_x;
      std::uint8_t packed = 0;
      bool opaque = false;
      if (overlay.format == OverlayPixelFormat::RGBA2222) {
        std::uint8_t source = overlay.data[source_index];
        packed = source & 0x3F;
        opaque = (source & 0xC0) != 0;
      } else {
        auto const *source = overlay.data + source_index * 4;
        packed = static_cast<std::uint8_t>(
            (source[0] >> 6) | ((source[1] >> 6) << 2) |
            ((source[2] >> 6) << 4));
        opaque = source[3] != 0;
      }
      if (!opaque) continue;
      std::size_t destination_x = static_cast<std::size_t>(x - region_left);
      auto &pixel = destination[destination_y * region.width + destination_x];
      if (overlay.format == OverlayPixelFormat::RGBA2222 &&
          overlay.paint == OverlayPaint::Xor)
        packed ^= packRGB222(pixel);
      pixel = expandRGB222(packed);
    }
  }
  return CompositionResult::Ok;
}

}  // namespace agon::extender::display
