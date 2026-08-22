// PORT-003 Phase B pure native-pixel contract.
//
// This header intentionally has no Arduino, FreeRTOS, FabGL, or ESP-IDF
// dependency so the exact storage contract can be qualified on the host. The
// implementation adapts the immutable vdp-gl all-the-plots packed-pixel
// algorithms recorded in phase-b/evidence/algorithm-provenance.yaml.
#pragma once

#include <cstddef>
#include <cstdint>

namespace agon::extender::display {

enum class NativePixelFormat : std::uint8_t {
  PALETTE2,
  PALETTE4,
  PALETTE8,
  PALETTE16,
  SBGR2222,
};

enum class CodecResult : std::uint8_t {
  Ok,
  InvalidFormat,
  InvalidValue,
  OutOfRange,
  SizeOverflow,
  InvalidBuffer,
  BufferTooSmall,
};

class NativePixelCodec final {
 public:
  static CodecResult bitsPerPixel(NativePixelFormat format,
                                  std::uint8_t &result) noexcept;
  static CodecResult maximumValue(NativePixelFormat format,
                                  std::uint8_t &result) noexcept;
  static CodecResult rowStride(NativePixelFormat format, std::size_t width,
                               std::size_t &result) noexcept;
  static CodecResult planeSize(NativePixelFormat format, std::size_t width,
                               std::size_t height,
                               std::size_t &result) noexcept;
  static CodecResult read(std::uint8_t const *row, std::size_t width,
                          NativePixelFormat format, std::size_t x,
                          std::uint8_t &result) noexcept;
  static CodecResult write(std::uint8_t *row, std::size_t width,
                           NativePixelFormat format, std::size_t x,
                           std::uint8_t value) noexcept;
  static CodecResult clear(std::uint8_t *plane, std::size_t width,
                           std::size_t height, NativePixelFormat format,
                           std::uint8_t value) noexcept;
  static CodecResult exportNativeSave(std::uint8_t const *plane,
                                      std::size_t width, std::size_t height,
                                      NativePixelFormat format,
                                      std::uint8_t inactive_sync_bits,
                                      std::uint8_t *destination,
                                      std::size_t destination_size) noexcept;
};

}  // namespace agon::extender::display
