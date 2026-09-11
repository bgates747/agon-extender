// PORT-003 Phase E display endpoint for the future PORT-005 processed-input
// adapter. This owns only mode bounds and the EDP-local cursor overlay. It is
// not a mouse device, event queue, packet source, or input-routing policy.
#pragma once

#include <cstdint>

#if defined(AGON_EXTENDER_STOCK_RUNTIME)
#include "displaycontroller.h"
#else
#include "extender/display/p4_display_controller.hpp"
#endif

namespace agon::extender::display {
#if defined(AGON_EXTENDER_STOCK_RUNTIME)
using CursorDisplayController = fabgl::BitmappedDisplayController;
#else
using CursorDisplayController = P4DisplayController;
#endif

enum class CursorPositionResult : std::uint8_t {
  Ok,
  Unbound,
  InvalidBounds,
  CursorUnavailable,
};

class CursorPositionAdapter final {
 public:
  bool bind(std::uint16_t width, std::uint16_t height,
            CursorDisplayController *controller) noexcept;
  CursorPositionResult set(std::uint16_t x, std::uint16_t y) noexcept;
  std::uint16_t x() const noexcept;
  std::uint16_t y() const noexcept;
  std::uint16_t width() const noexcept;
  std::uint16_t height() const noexcept;

 private:
  CursorDisplayController *controller_{};
  std::uint16_t width_{};
  std::uint16_t height_{};
  std::uint16_t x_{};
  std::uint16_t y_{};
};

CursorPositionAdapter &cursorPositionAdapter() noexcept;

}  // namespace agon::extender::display

// These upstream-shaped free functions let unchanged official callers bind
// and position the project adapter after agon_screen.h removes agon_ps2.h.
inline bool resetMousePositioner(
    std::uint16_t width, std::uint16_t height,
    agon::extender::display::CursorDisplayController *controller) noexcept {
  return agon::extender::display::cursorPositionAdapter().bind(width, height,
                                                               controller);
}

inline bool setExtenderMouseCursorPos(std::uint16_t x,
                                     std::uint16_t y) noexcept {
  return agon::extender::display::cursorPositionAdapter().set(x, y) ==
         agon::extender::display::CursorPositionResult::Ok;
}
