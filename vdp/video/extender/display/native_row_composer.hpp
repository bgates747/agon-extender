// Task-context producer for the P4 DPI strip ring. Stock owns the logical rows,
// colour-depth decoding and overlays. Only the final panel triplets live here.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include "extender/display/hdmi_geometry.hpp"
#include "extender/display/rgb222_bgr_lut.hpp"

namespace agon::extender::display {

struct NativeExpand {
  template<class Expand> void operator()(Expand expand) const { expand(); }
};

class NativeRowComposer {
 public:
  static constexpr unsigned slots = 3;
  static constexpr unsigned maximum_width = 1024;

  bool configure(int width, int height, int carrier_width, int carrier_height) {
    if (width <= 0 || width > static_cast<int>(maximum_width) || height <= 0 ||
        carrier_width <= 0 || (carrier_width & 3) || carrier_height <= 0) return false;
    doubled_ = width == 320 && height == 240;
    repeat_y_ = doubled_ ? 2 : hdmiVerticalRepeat(width, height);
    geometry_ = centeredHdmiGeometry(doubled_ ? width * 2 : width, height * repeat_y_,
                                     carrier_width, carrier_height);
    output_width_ = carrier_width;
    output_height_ = carrier_height;
    previous_ = {};
    return geometry_.valid() && geometry_.width % (doubled_ ? 2 : 1) == 0;
  }

  // first_y/count are physical rows in a single DMA-owned slot. The driver
  // hands out complete 32-row strips. In the two repeated geometries both
  // physical occurrences share a slot and one lease on the sampled pixels.
  template<class PrepareRow, class MeasureExpand = NativeExpand>
  bool fill(std::uint8_t *pixels, unsigned first_y, unsigned count, unsigned slot, bool &slot_black,
            PrepareRow prepare_row, MeasureExpand measure_expand = {}) {
    if (!pixels || slot >= slots || count == 0 || first_y >= unsigned(output_height_) ||
        count > unsigned(output_height_) - first_y) return false;
    const int first = static_cast<int>(first_y);
    const int rows = static_cast<int>(count);
    const int top = std::clamp(geometry_.destination_y - first, 0, rows);
    const int end = std::clamp(geometry_.destination_y + geometry_.height - first, 0, rows);
    if (repeat_y_ == 2 && ((end - top) % 2 ||
        (end > top && (first + top - geometry_.destination_y + geometry_.source_y) % 2))) return false;
    const unsigned stride = output_width_ * 3;
    const unsigned left_bytes = geometry_.destination_x * 3;
    const unsigned image_bytes = geometry_.width * 3;
    const unsigned right_start = left_bytes + image_bytes;
    const Coverage prior = previous_[slot];
    if (!prior.initialized || top != prior.top || end != prior.end) {
      // The DMA owner already cleared and synchronized newly allocated slots.
      // On a quick same-carrier rebind the retired slot may still contain the
      // old geometry. Clear only the spans that the incoming image won't write.
      if (!slot_black) {
        if (!prior.initialized && top == end) {
          std::memset(pixels, 0, std::size_t(rows) * stride);
        } else {
          for (int row = 0; row < rows; ++row) {
            auto *line = pixels + row * stride;
            if (!prior.initialized) {
              if (left_bytes) std::memset(line, 0, left_bytes);
              if (right_start < stride) std::memset(line + right_start, 0, stride - right_start);
            }
            if ((row < top || row >= end) &&
                (!prior.initialized || (row >= prior.top && row < prior.end)))
              std::memset(line + left_bytes, 0, image_bytes);
          }
        }
      }
      previous_[slot] = {top, end, true};
    }
    slot_black = top == end;
    for (int row = top; row < end; row += repeat_y_) {
      const int image_y = first + row - geometry_.destination_y;
      const int source_y = (image_y + geometry_.source_y) / repeat_y_;
      prepare_row(source_y, image_y == 0 && source_y > 0, signal_);
      auto *destination = pixels + row * stride + left_bytes;
      auto *second = repeat_y_ == 2 ? destination + stride : nullptr;
      measure_expand([&] {
        if (doubled_)
          expandRow<true>(destination, second, geometry_.source_x / 2, geometry_.width / 2);
        else
          expandRow<false>(destination, second, geometry_.source_x, geometry_.width);
      });
    }
    return true;
  }

 private:
  struct Coverage { int top{}, end{}; bool initialized{}; };
  HdmiGeometry geometry_{};
  int output_width_{}, output_height_{}, repeat_y_{};
  bool doubled_{};
  std::array<Coverage, slots> previous_{};
  // Native low-depth palettes use aligned wide stores. Keep this private to
  // the one refill task; never borrow a logical row after releasing its guard.
  alignas(8) std::uint8_t signal_[maximum_width];

  template<bool Double>
  void expandRow(std::uint8_t *out, std::uint8_t *second, int x, int logical_width) {
    const int end = x + logical_width;
    const auto colour = [&](int at) { return rgb222_bgr_detail::colours[signal_[at ^ 2] & 63]; };
    const auto put = [](std::uint8_t *to, std::uint32_t value) {
      to[0] = value; to[1] = value >> 8; to[2] = value >> 16;
    };
    const auto single = [&](std::uint8_t *to, std::uint32_t value) {
      put(to, value);
      if constexpr (Double) put(to + 3, value);
    };
    const auto emit = [&](std::uint32_t value) {
      single(out, value);
      out += Double ? 6 : 3;
      if (second) { single(second, value); second += Double ? 6 : 3; }
    };
    // Four output pixels pack into three aligned 32-bit stores. Sharing their
    // words with the second physical row avoids a second RGB-row read/copy.
    while (x < end && (reinterpret_cast<std::uintptr_t>(out) & 3)) emit(colour(x++));
    constexpr int group = Double ? 2 : 4;
    for (; x + group <= end; x += group) {
      const auto a = colour(x);
      const auto b = Double ? a : colour(x + 1);
      const auto c = colour(x + (Double ? 1 : 2));
      const auto d = Double ? c : colour(x + 3);
      const std::uint32_t first_word = a | (b << 24);
      const std::uint32_t mid_word = (b >> 8) | (c << 16);
      const std::uint32_t last_word = (c >> 16) | (d << 8);
      const auto write_group = [&](std::uint8_t *to) {
        // The scalar prefix aligned out; both admitted strides preserve that
        // alignment on the repeated row. Keep the words in registers on P4.
        auto *aligned = static_cast<std::uint8_t *>(__builtin_assume_aligned(to, 4));
        __builtin_memcpy(aligned, &first_word, 4);
        __builtin_memcpy(aligned + 4, &mid_word, 4);
        __builtin_memcpy(aligned + 8, &last_word, 4);
      };
      write_group(out);
      out += 12;
      if (second) {
        write_group(second);
        second += 12;
      }
    }
    while (x < end) emit(colour(x++));
  }
};

} // namespace agon::extender::display
