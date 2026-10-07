// Borrowed pixel storage: the LCD owner retains allocations and DMA lifetime.
// The swap callback returns only after DMA has released the previous front.
#pragma once
#include <cstddef>
#include <cstdint>
namespace agon::extender::display {
struct Rgb888PanelStorage {
  std::uint8_t *buffers[2]{};
  unsigned count{}, front{};
  int width{}, height{};
  std::size_t stride{};
  void *context{};
  bool (*swap)(void *, unsigned){};
};
} // namespace agon::extender::display
