#include "extender/display/cursor_position_adapter.hpp"

#include <algorithm>

namespace agon::extender::display {

bool CursorPositionAdapter::bind(std::uint16_t width, std::uint16_t height,
                                 CursorDisplayController *controller) noexcept {
  if (width == 0 || height == 0 || controller == nullptr) {
    controller_ = nullptr;
    width_ = height_ = x_ = y_ = 0;
    return false;
  }
  controller_ = controller;
  width_ = width;
  height_ = height;
  x_ = std::min<std::uint16_t>(x_, width_ - 1);
  y_ = std::min<std::uint16_t>(y_, height_ - 1);
  return true;
}

CursorPositionResult CursorPositionAdapter::set(std::uint16_t x,
                                                std::uint16_t y) noexcept {
  if (controller_ == nullptr) return CursorPositionResult::Unbound;
  if (width_ == 0 || height_ == 0) return CursorPositionResult::InvalidBounds;
  x_ = std::min<std::uint16_t>(x, width_ - 1);
  y_ = std::min<std::uint16_t>(y, height_ - 1);
#if defined(AGON_EXTENDER_STOCK_RUNTIME)
  controller_->setMouseCursorPos(x_, y_);
  return CursorPositionResult::Ok;
#else
  return controller_->setDisplayCursorPosition(x_, y_)
             ? CursorPositionResult::Ok
             : CursorPositionResult::CursorUnavailable;
#endif
}

std::uint16_t CursorPositionAdapter::x() const noexcept { return x_; }
std::uint16_t CursorPositionAdapter::y() const noexcept { return y_; }
std::uint16_t CursorPositionAdapter::width() const noexcept { return width_; }
std::uint16_t CursorPositionAdapter::height() const noexcept { return height_; }

CursorPositionAdapter &cursorPositionAdapter() noexcept {
  static CursorPositionAdapter adapter;
  return adapter;
}

}  // namespace agon::extender::display
