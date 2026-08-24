// PORT-003 Phase D palette and Copper state.
//
// This replaces vdp-gl's classic-VGA packed signal maps, not their observable
// palette contract. Exact upstream spans and dispositions are recorded in
// docs/tasks/PORT-003/phase-d/evidence/presentation-provenance.yaml.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "extender/display/plane_storage.hpp"

namespace agon::extender::display {

struct CopperSpan {
  std::uint32_t end_row;
  std::uint16_t palette_id;
};

class PaletteState final {
 public:
  explicit PaletteState(Allocator allocator) noexcept;
  ~PaletteState();

  PaletteState(PaletteState const &) = delete;
  PaletteState &operator=(PaletteState const &) = delete;

  // Reset is allocation-free and therefore cannot destroy a valid mode on an
  // allocation failure. Secondary palettes and dynamic signal spans are
  // released only after the caller has successfully installed new planes.
  void reset(NativePixelFormat format) noexcept;

  bool paletted() const noexcept;
  NativePixelFormat format() const noexcept;
  std::size_t paletteSize() const noexcept;
  bool paletteExists(std::uint16_t palette_id) const noexcept;
  std::size_t secondaryPaletteCount() const noexcept;

  bool createPalette(std::uint16_t palette_id) noexcept;
  void deletePalette(std::uint16_t palette_id) noexcept;
  bool setItemInPalette(std::uint16_t palette_id, std::uint8_t index,
                        std::uint8_t red, std::uint8_t green,
                        std::uint8_t blue) noexcept;
  void updateRGB2PaletteLUT() noexcept;

  bool updateSignalList(std::uint16_t const *raw_pairs,
                        std::size_t entries) noexcept;
  std::size_t signalCount() const noexcept;
  CopperSpan signalAt(std::size_t index) const noexcept;

  std::uint8_t drawingIndex(std::uint8_t red, std::uint8_t green,
                            std::uint8_t blue) const noexcept;
  std::uint8_t palette0Color(std::uint8_t index) const noexcept;
  std::uint8_t presentationColor(std::size_t row,
                                 std::uint8_t index) const noexcept;
  bool copyPalette(std::uint16_t palette_id, std::uint8_t *destination,
                   std::size_t destination_size) const noexcept;

 private:
  struct SecondaryPalette {
    std::uint16_t id;
    std::array<std::uint8_t, 16> colors;
    SecondaryPalette *next;
  };

  SecondaryPalette *findSecondary(std::uint16_t palette_id) noexcept;
  SecondaryPalette const *findSecondary(
      std::uint16_t palette_id) const noexcept;
  std::uint8_t const *palette(std::uint16_t palette_id) const noexcept;
  void releaseSecondaryPalettes() noexcept;
  void releaseDynamicSignals() noexcept;

  Allocator allocator_;
  NativePixelFormat format_{NativePixelFormat::SBGR2222};
  std::size_t palette_size_{};
  std::array<std::uint8_t, 16> primary_{};
  std::array<std::uint8_t, 64> drawing_lut_{};
  SecondaryPalette *secondary_{};
  CopperSpan embedded_signal_{};
  CopperSpan *signals_{&embedded_signal_};
  std::size_t signal_count_{1};
};

}  // namespace agon::extender::display
