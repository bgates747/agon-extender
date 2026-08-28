// PORT-003 Phase F no-device input adapter.
//
// Physical PS/2 acquisition and input routing belong to PORT-005. The retained
// parser still names the official input helpers throughout header-defined VDU
// code, so this bounded adapter supplies the same call surface without
// constructing a PS2Controller, reading GPIO, or emitting an event. It is not
// evidence that keyboard or mouse commands are qualified.
#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>

#include "agon.h"
#include "extender/compat/p4_vdp_gl.hpp"
#include "extender/display/cursor_position_adapter.hpp"

inline std::uint8_t _keycode = 0;
inline std::uint16_t kbRepeatDelay = 500;
inline std::uint16_t kbRepeatRate = 100;
inline std::uint8_t kbRegion = 0;
inline bool kbEnabled = false;

inline bool mouseEnabled = false;
inline bool mouseVisible = false;
inline std::uint8_t mSampleRate = MOUSE_DEFAULT_SAMPLERATE;
inline std::uint8_t mResolution = MOUSE_DEFAULT_RESOLUTION;
inline std::uint8_t mScaling = MOUSE_DEFAULT_SCALING;
inline std::uint16_t mAcceleration = MOUSE_DEFAULT_ACCELERATION;
inline std::uint32_t mWheelAcc = MOUSE_DEFAULT_WHEELACC;
inline std::uint16_t mCursor = MOUSE_DEFAULT_CURSOR;

class UnavailableKeyboard final {
 public:
  void setLEDs(bool num_lock, bool caps_lock, bool scroll_lock) noexcept {
    num_lock_ = num_lock;
    caps_lock_ = caps_lock;
    scroll_lock_ = scroll_lock;
  }
  void getLEDs(bool *num_lock, bool *caps_lock,
               bool *scroll_lock) const noexcept {
    *num_lock = num_lock_;
    *caps_lock = caps_lock_;
    *scroll_lock = scroll_lock_;
  }
  bool isVKDown(fabgl::VirtualKey) const noexcept { return false; }
  void injectVirtualKey(fabgl::VirtualKey, bool, bool) noexcept {}

 private:
  bool num_lock_{};
  bool caps_lock_{};
  bool scroll_lock_{};
};

class UnavailableMouse final {
 public:
  std::uint32_t &wheelAcceleration() noexcept { return mWheelAcc; }
};

inline UnavailableKeyboard *getKeyboard() noexcept {
  static UnavailableKeyboard keyboard;
  return &keyboard;
}

inline UnavailableMouse *getMouse() noexcept {
  static UnavailableMouse mouse;
  return &mouse;
}

inline void setupKeyboardAndMouse() noexcept {}
inline void setKeyboardLayout(std::uint8_t) noexcept {}
inline bool getKeyboardKey(fabgl::VirtualKeyItem *) noexcept { return false; }

inline std::uint8_t packKeyboardModifiers(
    fabgl::VirtualKeyItem *item) noexcept {
  return item->CTRL << 0 | item->SHIFT << 1 | item->LALT << 2 |
         item->RALT << 3 | item->CAPSLOCK << 4 | item->NUMLOCK << 5 |
         item->SCROLLLOCK << 6 | item->GUI << 7;
}

inline bool shiftKeyPressed() noexcept { return false; }
inline bool ctrlKeyPressed() noexcept { return false; }

inline void getKeyboardState(std::uint16_t *repeat_delay,
                             std::uint16_t *repeat_rate,
                             std::uint8_t *led_state) noexcept {
  bool num_lock = false;
  bool caps_lock = false;
  bool scroll_lock = false;
  getKeyboard()->getLEDs(&num_lock, &caps_lock, &scroll_lock);
  *repeat_delay = kbRepeatDelay;
  *repeat_rate = kbRepeatRate;
  *led_state = scroll_lock | (caps_lock << 1) | (num_lock << 2);
}

inline void setKeyboardState(std::uint16_t, std::uint16_t,
                             std::uint8_t) noexcept {}

inline void hideMouseCursor() noexcept { mouseVisible = false; }
inline void showMouseCursor() noexcept { mouseVisible = false; }
inline bool enableMouse() noexcept { return false; }
inline bool disableMouse() noexcept {
  mouseEnabled = false;
  mouseVisible = false;
  return true;
}
inline bool setMouseSampleRate(std::uint8_t) noexcept { return false; }
inline bool setMouseResolution(std::int8_t) noexcept { return false; }
inline bool setMouseScaling(std::uint8_t) noexcept { return false; }
inline bool setMouseAcceleration(std::uint16_t) noexcept { return false; }
inline bool setMouseWheelAcceleration(std::uint32_t) noexcept { return false; }

inline fabgl::MouseStatus *setMousePos(std::uint16_t x,
                                      std::uint16_t y) noexcept {
  static fabgl::MouseStatus status{};
  auto &adapter = agon::extender::display::cursorPositionAdapter();
  auto const width = adapter.width();
  auto const height = adapter.height();
  status.X = width == 0 ? x : std::min<std::uint16_t>(x, width - 1);
  status.Y = height == 0 ? y : std::min<std::uint16_t>(y, height - 1);
  adapter.set(status.X, status.Y);
  return &status;
}

inline bool resetMouse() noexcept { return false; }
inline bool mouseMoved(fabgl::MouseDelta *) noexcept { return false; }
inline void makeMouseCursor(std::uint16_t, std::shared_ptr<fabgl::Bitmap>,
                            std::uint16_t, std::uint16_t) noexcept {}
inline bool setMouseCursor(std::uint16_t cursor = mCursor) noexcept {
  mCursor = cursor;
  mouseVisible = false;
  return false;
}
inline void clearMouseCursor(std::uint16_t) noexcept {}
inline void resetMouseCursors() noexcept { mCursor = MOUSE_DEFAULT_CURSOR; }
