// Host protocol adapter for independent Phase B YAML fixtures.
// Expected bytes are deliberately absent from this program; the Python runner
// compares this production-code output with generate-fixtures.py's oracle.
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

#include "extender/display/native_pixel_codec.hpp"

using agon::extender::display::CodecResult;
using agon::extender::display::NativePixelCodec;
using agon::extender::display::NativePixelFormat;

namespace {

NativePixelFormat parseFormat(std::string const &name) {
  if (name == "PALETTE2") return NativePixelFormat::PALETTE2;
  if (name == "PALETTE4") return NativePixelFormat::PALETTE4;
  if (name == "PALETTE8") return NativePixelFormat::PALETTE8;
  if (name == "PALETTE16") return NativePixelFormat::PALETTE16;
  if (name == "SBGR2222") return NativePixelFormat::SBGR2222;
  std::abort();
}

void require(CodecResult actual, CodecResult expected = CodecResult::Ok) {
  if (actual != expected) std::abort();
}

void printBytes(char const *label, std::vector<std::uint8_t> const &bytes) {
  std::cout << label << '=';
  for (std::uint8_t value : bytes) {
    std::cout << std::hex << std::setw(2) << std::setfill('0')
              << static_cast<unsigned>(value);
  }
  std::cout << std::dec << '\n';
}

}  // namespace

int main(int argc, char **argv) {
  if (argc == 2 && std::string(argv[1]) == "contract") {
    for (NativePixelFormat format : {
             NativePixelFormat::PALETTE2,
             NativePixelFormat::PALETTE4,
             NativePixelFormat::PALETTE8,
             NativePixelFormat::PALETTE16,
             NativePixelFormat::SBGR2222,
         }) {
      std::size_t stride = 0;
      std::uint8_t maximum = 0;
      require(NativePixelCodec::rowStride(format, 9, stride));
      require(NativePixelCodec::maximumValue(format, maximum));
      std::vector<std::uint8_t> row(stride, 0xA5);
      auto unchanged = row;
      require(NativePixelCodec::write(row.data(), 9, format, 9, 0),
              CodecResult::OutOfRange);
      require(NativePixelCodec::write(row.data(), 9, format, 0,
                                      static_cast<std::uint8_t>(maximum + 1)),
              CodecResult::InvalidValue);
      require(NativePixelCodec::write(nullptr, 9, format, 0, 0),
              CodecResult::InvalidBuffer);
      if (row != unchanged) std::abort();
      std::uint8_t value = 0;
      require(NativePixelCodec::read(row.data(), 9, format, 9, value),
              CodecResult::OutOfRange);
      require(NativePixelCodec::read(nullptr, 9, format, 0, value),
              CodecResult::InvalidBuffer);
    }
    std::size_t result = 0;
    require(NativePixelCodec::rowStride(
                NativePixelFormat::SBGR2222,
                std::numeric_limits<std::size_t>::max(), result),
            CodecResult::SizeOverflow);
    std::uint8_t source = 0;
    std::uint8_t destination = 0;
    require(NativePixelCodec::exportNativeSave(
                &source, 1, 1, NativePixelFormat::SBGR2222, 0, &destination, 0),
            CodecResult::BufferTooSmall);
    require(NativePixelCodec::exportNativeSave(
                &source, 1, 1, NativePixelFormat::SBGR2222, 1, &destination, 1),
            CodecResult::InvalidValue);
    std::cout << "contract-pass\n";
    return 0;
  }
  if (argc != 6) return 2;
  std::string operation = argv[1];
  NativePixelFormat format = parseFormat(argv[2]);
  std::size_t width = std::strtoull(argv[3], nullptr, 10);
  std::size_t height = std::strtoull(argv[4], nullptr, 10);
  std::size_t stride = 0;
  std::size_t size = 0;
  require(NativePixelCodec::rowStride(format, width, stride));
  require(NativePixelCodec::planeSize(format, width, height, size));
  std::vector<std::uint8_t> plane(size, 0);

  if (operation == "sequence") {
    std::istringstream operations(argv[5]);
    std::string token;
    while (std::getline(operations, token, ';')) {
      std::istringstream fields(token);
      std::string field;
      std::getline(fields, field, ',');
      std::size_t x = std::strtoull(field.c_str(), nullptr, 10);
      std::getline(fields, field, ',');
      std::size_t y = std::strtoull(field.c_str(), nullptr, 10);
      std::getline(fields, field, ',');
      unsigned value = std::strtoul(field.c_str(), nullptr, 10);
      require(NativePixelCodec::write(plane.data() + y * stride, width, format,
                                      x, static_cast<std::uint8_t>(value)));
    }
  } else if (operation == "clear") {
    unsigned value = std::strtoul(argv[5], nullptr, 10);
    require(NativePixelCodec::clear(plane.data(), width, height, format,
                                    static_cast<std::uint8_t>(value)));
  } else {
    return 3;
  }

  printBytes("bytes", plane);
  std::cout << "pixels=";
  bool first = true;
  for (std::size_t y = 0; y < height; ++y) {
    for (std::size_t x = 0; x < width; ++x) {
      std::uint8_t value = 0;
      require(NativePixelCodec::read(plane.data() + y * stride, width, format,
                                     x, value));
      if (!first) std::cout << ',';
      first = false;
      std::cout << static_cast<unsigned>(value);
    }
  }
  std::cout << '\n';
  if (format == NativePixelFormat::SBGR2222) {
    for (std::uint8_t sync : {std::uint8_t{0x00}, std::uint8_t{0x40},
                              std::uint8_t{0x80}, std::uint8_t{0xC0}}) {
      std::vector<std::uint8_t> saved(size);
      require(NativePixelCodec::exportNativeSave(
          plane.data(), width, height, format, sync, saved.data(), saved.size()));
      std::ostringstream label;
      label << "save" << std::hex << std::setw(2) << std::setfill('0')
            << static_cast<unsigned>(sync);
      printBytes(label.str().c_str(), saved);
    }
  }
  return 0;
}
