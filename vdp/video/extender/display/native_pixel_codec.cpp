// See native_pixel_codec.hpp.
//
// Provenance: packed bit order is adapted from immutable vdp-gl
// all-the-plots commit ac2dd5986daf496c43ae8e7fe41836274aec54a0:
//   src/dispdrivers/vga2controller.cpp:58-66
//   src/dispdrivers/vga4controller.cpp:58-68
//   src/dispdrivers/vga8controller.cpp:65-75
//   src/dispdrivers/vga16controller.cpp:59-68
//   src/dispdrivers/vga64controller.cpp:82-90 and 552-570
// Exact hashes live in phase-b/evidence/algorithm-provenance.yaml. The P4 port
// uses bounds-safe byte operations; notably, it does not inherit vga8's
// unaligned 32-bit access across a three-byte group.
#include "extender/display/native_pixel_codec.hpp"

#include <cstring>
#include <limits>

namespace agon::extender::display {
namespace {

CodecResult properties(NativePixelFormat format, std::uint8_t &bits,
                       std::uint8_t &maximum) noexcept {
  switch (format) {
    case NativePixelFormat::PALETTE2:
      bits = 1;
      maximum = 1;
      return CodecResult::Ok;
    case NativePixelFormat::PALETTE4:
      bits = 2;
      maximum = 3;
      return CodecResult::Ok;
    case NativePixelFormat::PALETTE8:
      bits = 3;
      maximum = 7;
      return CodecResult::Ok;
    case NativePixelFormat::PALETTE16:
      bits = 4;
      maximum = 15;
      return CodecResult::Ok;
    case NativePixelFormat::SBGR2222:
      bits = 8;
      maximum = 63;
      return CodecResult::Ok;
  }
  return CodecResult::InvalidFormat;
}

}  // namespace

CodecResult NativePixelCodec::bitsPerPixel(NativePixelFormat format,
                                            std::uint8_t &result) noexcept {
  std::uint8_t maximum = 0;
  return properties(format, result, maximum);
}

CodecResult NativePixelCodec::maximumValue(NativePixelFormat format,
                                            std::uint8_t &result) noexcept {
  std::uint8_t bits = 0;
  return properties(format, bits, result);
}

CodecResult NativePixelCodec::rowStride(NativePixelFormat format,
                                         std::size_t width,
                                         std::size_t &result) noexcept {
  std::uint8_t bits = 0;
  std::uint8_t maximum = 0;
  CodecResult status = properties(format, bits, maximum);
  if (status != CodecResult::Ok) return status;
  if (width > (std::numeric_limits<std::size_t>::max() - 7) / bits) {
    return CodecResult::SizeOverflow;
  }
  result = (width * bits + 7) / 8;
  return CodecResult::Ok;
}

CodecResult NativePixelCodec::planeSize(NativePixelFormat format,
                                         std::size_t width,
                                         std::size_t height,
                                         std::size_t &result) noexcept {
  std::size_t stride = 0;
  CodecResult status = rowStride(format, width, stride);
  if (status != CodecResult::Ok) return status;
  if (height != 0 && stride > std::numeric_limits<std::size_t>::max() / height) {
    return CodecResult::SizeOverflow;
  }
  result = stride * height;
  return CodecResult::Ok;
}

CodecResult NativePixelCodec::read(std::uint8_t const *row, std::size_t width,
                                   NativePixelFormat format, std::size_t x,
                                   std::uint8_t &result) noexcept {
  if (row == nullptr) return CodecResult::InvalidBuffer;
  if (x >= width) return CodecResult::OutOfRange;
  std::uint8_t bits = 0;
  std::uint8_t maximum = 0;
  CodecResult status = properties(format, bits, maximum);
  if (status != CodecResult::Ok) return status;
  if (bits == 8) {
    result = row[x] & maximum;
    return CodecResult::Ok;
  }
  result = 0;
  for (std::uint8_t source_bit = 0; source_bit < bits; ++source_bit) {
    std::size_t stream_bit = x * bits + source_bit;
    result = static_cast<std::uint8_t>(
        (result << 1) | ((row[stream_bit / 8] >> (7 - stream_bit % 8)) & 1));
  }
  return CodecResult::Ok;
}

CodecResult NativePixelCodec::write(std::uint8_t *row, std::size_t width,
                                    NativePixelFormat format, std::size_t x,
                                    std::uint8_t value) noexcept {
  if (row == nullptr) return CodecResult::InvalidBuffer;
  if (x >= width) return CodecResult::OutOfRange;
  std::uint8_t bits = 0;
  std::uint8_t maximum = 0;
  CodecResult status = properties(format, bits, maximum);
  if (status != CodecResult::Ok) return status;
  if (value > maximum) return CodecResult::InvalidValue;
  if (bits == 8) {
    row[x] = value;
    return CodecResult::Ok;
  }
  for (std::uint8_t source_bit = 0; source_bit < bits; ++source_bit) {
    std::size_t stream_bit = x * bits + source_bit;
    std::uint8_t mask = static_cast<std::uint8_t>(1U << (7 - stream_bit % 8));
    std::uint8_t bit = static_cast<std::uint8_t>(
        (value >> (bits - 1 - source_bit)) & 1U);
    row[stream_bit / 8] = static_cast<std::uint8_t>(
        (row[stream_bit / 8] & ~mask) | (bit != 0 ? mask : 0));
  }
  return CodecResult::Ok;
}

CodecResult NativePixelCodec::clear(std::uint8_t *plane, std::size_t width,
                                    std::size_t height,
                                    NativePixelFormat format,
                                    std::uint8_t value) noexcept {
  std::size_t stride = 0;
  std::size_t size = 0;
  std::uint8_t maximum = 0;
  CodecResult status = rowStride(format, width, stride);
  if (status != CodecResult::Ok) return status;
  status = planeSize(format, width, height, size);
  if (status != CodecResult::Ok) return status;
  status = maximumValue(format, maximum);
  if (status != CodecResult::Ok) return status;
  if (value > maximum) return CodecResult::InvalidValue;
  if (size != 0 && plane == nullptr) return CodecResult::InvalidBuffer;
  if (size == 0) return CodecResult::Ok;
  std::memset(plane, 0, size);
  if (value == 0) return CodecResult::Ok;
  for (std::size_t y = 0; y < height; ++y) {
    for (std::size_t x = 0; x < width; ++x) {
      status = write(plane + y * stride, width, format, x, value);
      if (status != CodecResult::Ok) return status;
    }
  }
  return CodecResult::Ok;
}

CodecResult NativePixelCodec::exportNativeSave(
    std::uint8_t const *plane, std::size_t width, std::size_t height,
    NativePixelFormat format, std::uint8_t inactive_sync_bits,
    std::uint8_t *destination, std::size_t destination_size) noexcept {
  if ((inactive_sync_bits & 0x3F) != 0) return CodecResult::InvalidValue;
  std::size_t size = 0;
  CodecResult status = planeSize(format, width, height, size);
  if (status != CodecResult::Ok) return status;
  if (destination_size < size) return CodecResult::BufferTooSmall;
  if (size != 0 && (plane == nullptr || destination == nullptr)) {
    return CodecResult::InvalidBuffer;
  }
  if (format == NativePixelFormat::SBGR2222) {
    for (std::size_t index = 0; index < size; ++index) {
      destination[index] = static_cast<std::uint8_t>(
          (plane[index] & 0x3F) | inactive_sync_bits);
    }
  } else if (size != 0) {
    std::memcpy(destination, plane, size);
  }
  return CodecResult::Ok;
}

}  // namespace agon::extender::display
