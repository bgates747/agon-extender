// RESEARCH-007 default-off RGB888 bitmap experiment: one-byte RGB222/Native pixels remain the
// asset and saved-background ABI; this table expands only physical B,G,R rows.
// This is hardware adaptation, not a palette-semantic change. Every RGB222
// value and every alpha class produces the same quantized BGR as before.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "RGB222 BGR word packing requires a little-endian target"
#endif
#if defined(ESP_PLATFORM)
#include "esp_attr.h"
#define AGON_EXTENDER_LUT_DATA DRAM_ATTR
#else
#define AGON_EXTENDER_LUT_DATA
#endif

namespace agon::extender::display {
namespace rgb222_bgr_detail {
constexpr std::array<std::uint32_t, 64> makeTable() noexcept {
  std::array<std::uint32_t, 64> table{};
  for (unsigned colour = 0; colour < table.size(); ++colour)
    table[colour] = (((colour >> 4) & 3) * 85u) |
        ((((colour >> 2) & 3) * 85u) << 8) | ((colour & 3) * 85u << 16);
  return table;
}
// P4 internal SRAM, not a PSRAM lookup per pixel; initialized as constant data.
// The 256-byte cost is explicit and no allocation or runtime setup is required.
alignas(16) AGON_EXTENDER_LUT_DATA static constexpr auto colours = makeTable();
} // namespace rgb222_bgr_detail

inline void storeRgb222Bgr(std::uint8_t *destination, std::uint8_t colour) noexcept {
  const auto pixel = rgb222_bgr_detail::colours[colour & 63];
  destination[0] = pixel;
  destination[1] = pixel >> 8;
  destination[2] = pixel >> 16;
}

inline void storeRgba2222BgrSpan(std::uint8_t *destination,
                               const std::uint8_t *source,
                               std::size_t pixels) noexcept {
  const auto d = reinterpret_cast<std::uintptr_t>(destination);
  const auto s = reinterpret_cast<std::uintptr_t>(source);
  // Match the generic forward traversal for callers whose source aliases the
  // framebuffer. Otherwise reading four pixels ahead could change later input.
  const bool overlap = d < s ? s - d < pixels * 3 : d - s < pixels;
  if (overlap) {
    for (; pixels; --pixels, ++source, destination += 3)
      if (*source & 0xc0) storeRgb222Bgr(destination, *source);
    return;
  }
  while (pixels && (reinterpret_cast<std::uintptr_t>(destination) & 3)) {
    if (*source & 0xc0) storeRgb222Bgr(destination, *source);
    ++source;
    destination += 3;
    --pixels;
  }
  if (!pixels) return;
  auto *out = static_cast<std::uint8_t *>(__builtin_assume_aligned(destination, 4));
  for (; pixels >= 4; pixels -= 4, source += 4, out += 12) {
    const auto p0 = source[0], p1 = source[1], p2 = source[2], p3 = source[3];
    // Stock RGBA2222 alpha is binary: each nonzero two-bit class is opaque.
    // Fully opaque groups use the same bounded packing as Native restoration;
    // mixed groups must leave every transparent destination byte untouched.
    if ((p0 & 0xc0) && (p1 & 0xc0) && (p2 & 0xc0) && (p3 & 0xc0)) {
      const auto a = rgb222_bgr_detail::colours[p0 & 63];
      const auto b = rgb222_bgr_detail::colours[p1 & 63];
      const auto c = rgb222_bgr_detail::colours[p2 & 63];
      const auto d = rgb222_bgr_detail::colours[p3 & 63];
      const std::uint32_t first = a | (b << 24);
      const std::uint32_t middle = (b >> 8) | (c << 16);
      const std::uint32_t last = (c >> 16) | (d << 8);
      __builtin_memcpy(out, &first, 4);
      __builtin_memcpy(out + 4, &middle, 4);
      __builtin_memcpy(out + 8, &last, 4);
    } else {
      if (p0 & 0xc0) storeRgb222Bgr(out, p0);
      if (p1 & 0xc0) storeRgb222Bgr(out + 3, p1);
      if (p2 & 0xc0) storeRgb222Bgr(out + 6, p2);
      if (p3 & 0xc0) storeRgb222Bgr(out + 9, p3);
    }
  }
  for (; pixels; --pixels, ++source, out += 3)
    if (*source & 0xc0) storeRgb222Bgr(out, *source);
}

inline void storeNativeRgb222BgrSpan(std::uint8_t *destination,
                                    const std::uint8_t *source,
                                    std::size_t pixels) noexcept {
  const auto d = reinterpret_cast<std::uintptr_t>(destination);
  const auto s = reinterpret_cast<std::uintptr_t>(source);
  // Native data normally belongs to a separate one-byte saved-background or
  // bitmap allocation. Keep the original per-pixel order even for a caller
  // supplying overlapping memory; bulk reads must not change alias behaviour.
  const bool overlap = d < s ? s - d < pixels * 3 : d - s < pixels;
  if (overlap) {
    for (; pixels; --pixels, ++source, destination += 3)
      storeRgb222Bgr(destination, *source);
    return;
  }
  // BGR advances by three bytes. At most three head pixels align the output
  // to a word without overreading source or overwriting destination guards.
  while (pixels && (reinterpret_cast<std::uintptr_t>(destination) & 3)) {
    storeRgb222Bgr(destination, *source++);
    destination += 3;
    --pixels;
  }
  if (!pixels) return;
  auto *out = static_cast<std::uint8_t *>(__builtin_assume_aligned(destination, 4));
  for (; pixels >= 4; pixels -= 4, source += 4, out += 12) {
    const auto a = rgb222_bgr_detail::colours[source[0] & 63];
    const auto b = rgb222_bgr_detail::colours[source[1] & 63];
    const auto c = rgb222_bgr_detail::colours[source[2] & 63];
    const auto d = rgb222_bgr_detail::colours[source[3] & 63];
    const std::uint32_t first = a | (b << 24);
    const std::uint32_t middle = (b >> 8) | (c << 16);
    const std::uint32_t last = (c >> 16) | (d << 8);
    // ESP32-P4 is little endian. memcpy preserves aliasing rules and compiles
    // to three aligned word stores; host tests also run on little endian.
    __builtin_memcpy(out, &first, 4);
    __builtin_memcpy(out + 4, &middle, 4);
    __builtin_memcpy(out + 8, &last, 4);
  }
  for (; pixels; --pixels, ++source, out += 3)
    storeRgb222Bgr(out, *source);
}
} // namespace agon::extender::display
#undef AGON_EXTENDER_LUT_DATA
