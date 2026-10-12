// RESEARCH-007: default-off physical BGR scanout composition experiment.
// Preserve the stock painter's binary alpha, RGBA8888 XOR exception, scene
// order and bounding-span background quantization, without temporary VGA
// lane-permuted bytes. Scene staging, leases/cache/guard ownership are unchanged.
#pragma once
#include "scene.hpp"

namespace agon_scanout {
inline bool supportsDirectBgr(const Scene &scene) noexcept
{
  // Stock VDP v2.16.0 / retained FabGL rawDrawSpriteScanline computes
  // drawWidth = viewportWidth - spriteX when a sprite crosses the right edge,
  // without subtracting the negative-X offset when it crosses BOTH edges.
  // That can draw/read beyond the intended span. This optimization does not
  // silently repair that inherited source behavior: retain the original full
  // compose path for those scenes, pending a separately authorized correction.
  // See vdp/dsi-strip-test/main/stock_sprite_body.inc for the frozen body.
  for (unsigned i = 0; i < scene.count; ++i) {
    const auto &sprite = scene.sprites[i];
    if (sprite.x < 0 && std::int64_t(sprite.x) + sprite.image.width > scene.width)
      return false;
  }
  return true;
}

inline void quantizeBackground(std::uint8_t *destination)
{
  // Current Scene::compose quantizes every clipped sprite bounding span,
  // including alpha-zero pixels. Do not replace this with an early continue.
  destination[0] = (destination[0] >> 6) * 85;
  destination[1] = (destination[1] >> 6) * 85;
  destination[2] = (destination[2] >> 6) * 85;
}

inline void composeDirectBgr(const agon_scanout::Scene &scene, std::uint8_t *strip,
                          unsigned firstY, unsigned rows)
{
  using agon_scanout::PaintMode;
  using agon_scanout::PixelFormat;
  if (!scene.count) return;
  for (unsigned row = 0; row < rows; ++row) {
    const int y = int(firstY + row) - scene.top;
    if (y < 0 || y >= scene.height) continue;
    auto *pixelsRow = strip + row * scene.outputWidth * 3 + scene.left * 3;
    for (unsigned i = 0; i < scene.count; ++i) {
      const auto &sprite = scene.sprites[i];
      const auto &image = sprite.image;
      if (y < sprite.y || y >= sprite.y + image.height) continue;
      const int firstX = std::max(0, sprite.x);
      const int endX = std::min(scene.width, sprite.x + image.width);
      if (firstX >= endX) continue;
      const int sourceOffset = (y - sprite.y) * image.width + firstX - sprite.x;
      auto *destination = pixelsRow + firstX * 3;
      const int count = endX - firstX;
      if (image.format == PixelFormat::RGBA8888) {
        // Scene::append aligns every arena entry to four bytes, preserving
        // stock's little-endian R,G,B,A uint32_t source read contract.
        const auto *source = reinterpret_cast<const std::uint32_t *>(image.data) + sourceOffset;
        for (int n = 0; n < count; ++n, destination += 3) {
          const std::uint32_t value = *source++;
          if (value & 0xff000000U) {
            destination[0] = ((value >> 22) & 3) * 85;
            destination[1] = ((value >> 14) & 3) * 85;
            destination[2] = ((value >> 6) & 3) * 85;
          } else {
            quantizeBackground(destination);
          }
        }
        // Stock RGBA8888 hardware sprites ignore PaintMode::XOR. Retain it.
      } else if (image.format == PixelFormat::RGBA2222) {
        const auto *source = image.data + sourceOffset;
        if (sprite.paintOptions.mode == PaintMode::XOR) {
          for (int n = 0; n < count; ++n, destination += 3) {
            const unsigned value = *source++;
            if (value & 0xc0) {
              destination[0] = ((destination[0] >> 6) ^ ((value >> 4) & 3)) * 85;
              destination[1] = ((destination[1] >> 6) ^ ((value >> 2) & 3)) * 85;
              destination[2] = ((destination[2] >> 6) ^ (value & 3)) * 85;
            } else {
              quantizeBackground(destination);
            }
          }
        } else {
          for (int n = 0; n < count; ++n, destination += 3) {
            const unsigned value = *source++;
            if (value & 0xc0) {
              destination[0] = ((value >> 4) & 3) * 85;
              destination[1] = ((value >> 2) & 3) * 85;
              destination[2] = (value & 3) * 85;
            } else {
              quantizeBackground(destination);
            }
          }
        }
      } else {
        // Stage currently admits only the two formats above. A future/invalid
        // format still follows the baseline's background-only quantization.
        for (int n = 0; n < count; ++n, destination += 3)
          quantizeBackground(destination);
      }
    }
  }
}

} // namespace agon_scanout
