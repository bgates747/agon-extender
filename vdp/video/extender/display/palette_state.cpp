// See palette_state.hpp.
//
// Observable rules are adapted from immutable vdp-gl all-the-plots
// VGAPalettedController. Linked palette nodes and compact row spans replace
// upstream's DMA-oriented signal tables because those tables encode VGA sync
// bytes and are not usable on ESP32-P4. Do not "simplify" the explicit LUT
// rebuild or its integer-truncated HSV comparison: both are upstream behavior.
#include "extender/display/palette_state.hpp"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>

namespace agon::extender::display {
namespace {

constexpr std::array<std::uint8_t, 2> kPalette2{{0x00, 0x3F}};
constexpr std::array<std::uint8_t, 4> kPalette4{{0x00, 0x30, 0x0C, 0x3F}};
constexpr std::array<std::uint8_t, 8> kPalette8{{
    0x00, 0x02, 0x08, 0x20, 0x03, 0x0C, 0x30, 0x3F,
}};
constexpr std::array<std::uint8_t, 16> kPalette16{{
    0x00, 0x02, 0x08, 0x0A, 0x20, 0x22, 0x28, 0x2A,
    0x15, 0x03, 0x0C, 0x0F, 0x30, 0x33, 0x3C, 0x3F,
}};

void rgb222ToHsv(int red, int green, int blue, double &hue,
                 double &saturation, double &value) noexcept {
  // Exact arithmetic structure from vdp-gl all-the-plots fabutils.cpp
  // rgb222_to_hsv(). The palette LUT below intentionally truncates the final
  // squared distance to int, as upstream does.
  double r = red / 3.0;
  double g = green / 3.0;
  double b = blue / 3.0;
  double maximum = std::fmax(std::fmax(r, g), b);
  double minimum = std::fmin(std::fmin(r, g), b);
  double difference = maximum - minimum;
  if (maximum == minimum)
    hue = 0;
  else if (maximum == r)
    hue = std::fmod(60.0 * ((g - b) / difference) + 360.0, 360.0);
  else if (maximum == g)
    hue = std::fmod(60.0 * ((b - r) / difference) + 120.0, 360.0);
  else
    hue = std::fmod(60.0 * ((r - g) / difference) + 240.0, 360.0);
  saturation = maximum == 0 ? 0 : (difference / maximum) * 100.0;
  value = maximum * 100.0;
}

std::uint8_t packRGB222(std::uint8_t red, std::uint8_t green,
                        std::uint8_t blue) noexcept {
  return static_cast<std::uint8_t>((red >> 6) | ((green >> 6) << 2) |
                                   ((blue >> 6) << 4));
}

}  // namespace

PaletteState::PaletteState(Allocator allocator) noexcept : allocator_(allocator) {
  reset(NativePixelFormat::SBGR2222);
}

PaletteState::~PaletteState() {
  releaseDynamicSignals();
  releaseSecondaryPalettes();
}

void PaletteState::reset(NativePixelFormat format) noexcept {
  releaseDynamicSignals();
  releaseSecondaryPalettes();
  format_ = format;
  primary_.fill(0);
  drawing_lut_.fill(0);
  switch (format) {
    case NativePixelFormat::PALETTE2:
      palette_size_ = kPalette2.size();
      std::copy(kPalette2.begin(), kPalette2.end(), primary_.begin());
      break;
    case NativePixelFormat::PALETTE4:
      palette_size_ = kPalette4.size();
      std::copy(kPalette4.begin(), kPalette4.end(), primary_.begin());
      break;
    case NativePixelFormat::PALETTE8:
      palette_size_ = kPalette8.size();
      std::copy(kPalette8.begin(), kPalette8.end(), primary_.begin());
      break;
    case NativePixelFormat::PALETTE16:
      palette_size_ = kPalette16.size();
      std::copy(kPalette16.begin(), kPalette16.end(), primary_.begin());
      break;
    case NativePixelFormat::SBGR2222:
      palette_size_ = 0;
      break;
  }
  embedded_signal_ = {0, 0};
  signals_ = &embedded_signal_;
  signal_count_ = 1;
  updateRGB2PaletteLUT();
}

bool PaletteState::paletted() const noexcept { return palette_size_ != 0; }
NativePixelFormat PaletteState::format() const noexcept { return format_; }
std::size_t PaletteState::paletteSize() const noexcept { return palette_size_; }

PaletteState::SecondaryPalette *PaletteState::findSecondary(
    std::uint16_t palette_id) noexcept {
  for (auto *item = secondary_; item != nullptr; item = item->next)
    if (item->id == palette_id) return item;
  return nullptr;
}

PaletteState::SecondaryPalette const *PaletteState::findSecondary(
    std::uint16_t palette_id) const noexcept {
  for (auto const *item = secondary_; item != nullptr; item = item->next)
    if (item->id == palette_id) return item;
  return nullptr;
}

bool PaletteState::paletteExists(std::uint16_t palette_id) const noexcept {
  return paletted() && (palette_id == 0 || findSecondary(palette_id) != nullptr);
}

std::size_t PaletteState::secondaryPaletteCount() const noexcept {
  std::size_t result = 0;
  for (auto const *item = secondary_; item != nullptr; item = item->next) ++result;
  return result;
}

bool PaletteState::createPalette(std::uint16_t palette_id) noexcept {
  if (!paletted()) return false;
  if (palette_id == 0) return true;
  SecondaryPalette *item = findSecondary(palette_id);
  if (item == nullptr) {
    if (allocator_.allocate == nullptr || allocator_.deallocate == nullptr)
      return false;
    item = static_cast<SecondaryPalette *>(
        allocator_.allocate(allocator_.context, sizeof(SecondaryPalette)));
    if (item == nullptr) return false;
    item->id = palette_id;
    item->next = secondary_;
    secondary_ = item;
  }
  item->colors = primary_;
  return true;
}

void PaletteState::deletePalette(std::uint16_t palette_id) noexcept {
  if (!paletted() || palette_id == 0) return;
  SecondaryPalette **link = &secondary_;
  while (*link != nullptr) {
    SecondaryPalette *item = *link;
    if (palette_id == 65535 || item->id == palette_id) {
      *link = item->next;
      for (std::size_t index = 0; index < signal_count_; ++index)
        if (signals_[index].palette_id == item->id) signals_[index].palette_id = 0;
      allocator_.deallocate(allocator_.context, item);
      if (palette_id != 65535) return;
    } else {
      link = &item->next;
    }
  }
}

bool PaletteState::setItemInPalette(std::uint16_t palette_id,
                                    std::uint8_t index, std::uint8_t red,
                                    std::uint8_t green,
                                    std::uint8_t blue) noexcept {
  if (!paletted()) return false;
  if (!paletteExists(palette_id) && !createPalette(palette_id)) return false;
  std::uint8_t packed = packRGB222(red, green, blue);
  std::size_t wrapped = index % palette_size_;
  if (palette_id == 0)
    primary_[wrapped] = packed;
  else
    findSecondary(palette_id)->colors[wrapped] = packed;
  return true;
}

void PaletteState::updateRGB2PaletteLUT() noexcept {
  if (!paletted()) return;
  for (int red = 0; red < 4; ++red)
    for (int green = 0; green < 4; ++green)
      for (int blue = 0; blue < 4; ++blue) {
        double h1 = 0, s1 = 0, v1 = 0;
        rgb222ToHsv(red, green, blue, h1, s1, v1);
        std::uint8_t best_index = 0;
        int best_distance = 1000000000;
        for (std::size_t index = 0; index < palette_size_; ++index) {
          std::uint8_t packed = primary_[index];
          double h2 = 0, s2 = 0, v2 = 0;
          rgb222ToHsv(packed & 3, (packed >> 2) & 3, (packed >> 4) & 3,
                      h2, s2, v2);
          double dh = h1 - h2, ds = s1 - s2, dv = v1 - v2;
          int distance = static_cast<int>(dh * dh + ds * ds + dv * dv);
          if (distance <= best_distance) {
            best_index = static_cast<std::uint8_t>(index);
            best_distance = distance;
            if (distance == 0) break;
          }
        }
        drawing_lut_[red | (green << 2) | (blue << 4)] = best_index;
      }
}

bool PaletteState::updateSignalList(std::uint16_t const *raw_pairs,
                                    std::size_t entries) noexcept {
  if (!paletted()) return false;
  if (entries == 0) {
    CopperSpan first = signals_[0];
    releaseDynamicSignals();
    embedded_signal_ = first;
    signals_ = &embedded_signal_;
    signal_count_ = 1;
    return true;
  }
  if (raw_pairs == nullptr ||
      entries > std::numeric_limits<std::size_t>::max() / sizeof(CopperSpan))
    return false;
  CopperSpan *replacement = &embedded_signal_;
  if (entries > 1) {
    if (allocator_.allocate == nullptr || allocator_.deallocate == nullptr)
      return false;
    replacement = static_cast<CopperSpan *>(
        allocator_.allocate(allocator_.context, entries * sizeof(CopperSpan)));
    if (replacement == nullptr) return false;
  }
  std::uint32_t row = 0;
  for (std::size_t index = 0; index < entries; ++index) {
    row += raw_pairs[index * 2];
    std::uint16_t requested = raw_pairs[index * 2 + 1];
    replacement[index] = {
        row, static_cast<std::uint16_t>(paletteExists(requested) ? requested : 0)};
  }
  releaseDynamicSignals();
  if (entries == 1) embedded_signal_ = replacement[0];
  signals_ = entries == 1 ? &embedded_signal_ : replacement;
  signal_count_ = entries;
  return true;
}

std::size_t PaletteState::signalCount() const noexcept { return signal_count_; }

CopperSpan PaletteState::signalAt(std::size_t index) const noexcept {
  return index < signal_count_ ? signals_[index] : CopperSpan{};
}

std::uint8_t PaletteState::drawingIndex(std::uint8_t red, std::uint8_t green,
                                        std::uint8_t blue) const noexcept {
  return paletted() ? drawing_lut_[packRGB222(red, green, blue)]
                    : packRGB222(red, green, blue);
}

std::uint8_t PaletteState::palette0Color(std::uint8_t index) const noexcept {
  return paletted() ? primary_[index % palette_size_] : index & 0x3F;
}

std::uint8_t const *PaletteState::palette(std::uint16_t palette_id) const noexcept {
  if (palette_id == 0) return primary_.data();
  auto const *item = findSecondary(palette_id);
  return item == nullptr ? primary_.data() : item->colors.data();
}

std::uint8_t PaletteState::presentationColor(std::size_t row,
                                             std::uint8_t index) const noexcept {
  if (!paletted()) return index & 0x3F;
  std::size_t signal = 0;
  while (signal + 1 < signal_count_ && row >= signals_[signal].end_row) ++signal;
  return palette(signals_[signal].palette_id)[index % palette_size_];
}

bool PaletteState::copyPalette(std::uint16_t palette_id,
                               std::uint8_t *destination,
                               std::size_t destination_size) const noexcept {
  if (!paletteExists(palette_id) || destination == nullptr ||
      destination_size < palette_size_)
    return false;
  std::memcpy(destination, palette(palette_id), palette_size_);
  return true;
}

void PaletteState::releaseSecondaryPalettes() noexcept {
  while (secondary_ != nullptr) {
    SecondaryPalette *next = secondary_->next;
    if (allocator_.deallocate != nullptr)
      allocator_.deallocate(allocator_.context, secondary_);
    secondary_ = next;
  }
}

void PaletteState::releaseDynamicSignals() noexcept {
  if (signals_ != &embedded_signal_ && allocator_.deallocate != nullptr)
    allocator_.deallocate(allocator_.context, signals_);
  signals_ = &embedded_signal_;
  signal_count_ = 1;
}

}  // namespace agon::extender::display
