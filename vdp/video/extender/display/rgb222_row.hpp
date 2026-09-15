// P4 output adapter only: preserve FabGL's x^2 byte order and strip sync bits.
// This does not replace or alter the retained stock scanline/sprite bodies.
#pragma once
#include <cstdint>
#include <cstring>
namespace agon::extender::display {
inline void normalizeRgb222Row(std::uint8_t const *source,
                               std::uint8_t *destination, int width) {
  int x = 0;
  if (((reinterpret_cast<std::uintptr_t>(source) |
        reinterpret_cast<std::uintptr_t>(destination)) & 3u) == 0) {
#if defined(__GNUC__) || defined(__clang__)
    // Runtime check above is essential: callers/host allocators may be unaligned.
    source = static_cast<std::uint8_t const *>(__builtin_assume_aligned(source, 4));
    destination = static_cast<std::uint8_t *>(__builtin_assume_aligned(destination, 4));
#endif
    for (; x + 4 <= width; x += 4) {
      std::uint32_t word;
      // memcpy preserves aliasing rules; alignment permits native word accesses.
      std::memcpy(&word, source + x, sizeof(word));
      word = ((word << 16) | (word >> 16)) & UINT32_C(0x3f3f3f3f);
      std::memcpy(destination + x, &word, sizeof(word));
    }
  }
  // Same scalar behavior for unaligned rows/tails. Native VGA widths are
  // multiples of four; source storage retains the native padded row contract.
  for (; x < width; ++x) destination[x] = source[x ^ 2] & 63;
}
} // namespace agon::extender::display
