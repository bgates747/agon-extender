// PORT-003 Phase F no-device input adapter.
//
// Physical PS/2 acquisition and input routing belong to PORT-005. The retained
// parser still names the official input helpers throughout header-defined VDU
// code, so this bounded adapter supplies the same call surface without
// constructing a PS2Controller or reading GPIO. PORT-005's explicit processed
// binding enables only the key FIFO below; physical mouse and PS/2 stay absent.
// It does not establish browser layout/repeat/query or physical qualification.
#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>

#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
#include "processed_keyboard.hpp"
#endif

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
  bool isVKDown(fabgl::VirtualKey key) const noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
    return agon::extender::input::processedKeyboard().isDown(unsigned(key));
#else
    return false;
#endif
  }
  void injectVirtualKey(fabgl::VirtualKey key, bool down, bool insert) noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
    // Stock &99 uses append only. No reverse HID map or physical PS/2 device.
    // Mirror Keyboard::injectVirtualKey's default-codepage ASCII conversion;
    // retain key-up keycode handling in getKeyboardKey below (agon_ps2.h).
    // EMOS keyboard ingress currently admits byte virtual keys through 248.
    // Later upstream enum additions require a separate EMOS contract change.
    if (unsigned(key) > 248 || insert) return;
    auto &keyboard = agon::extender::input::processedKeyboard();
    const auto modifiers = keyboard.modifiers();
    fabgl::VirtualKeyItem item{};
    item.vk=key; item.down=true;
    item.CTRL=modifiers&1; item.SHIFT=(modifiers>>1)&1;
    item.LALT=(modifiers>>2)&1; item.RALT=(modifiers>>3)&1;
    item.CAPSLOCK=(modifiers>>4)&1; item.NUMLOCK=(modifiers>>5)&1;
    item.SCROLLLOCK=(modifiers>>6)&1; item.GUI=(modifiers>>7)&1;
    const auto ascii=std::uint8_t(fabgl::virtualKeyToASCII(item,nullptr));
    keyboard.pushQuery({0,modifiers,std::uint8_t(key),std::uint8_t(down),ascii,true});
#else
    (void)key; (void)down; (void)insert;
#endif
  }

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
inline void setKeyboardLayout(std::uint8_t region) noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
  // Match stock accepted locale numbers; actual browser mapping is PORT-005's
  // next integration boundary. These already processed events need no remap.
  kbRegion = region <= 17 ? region : 0;
#else
  (void)region;
#endif
}
inline bool getKeyboardKey(fabgl::VirtualKeyItem *item) noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
  agon::extender::input::ProcessedKey event;
  if (!agon::extender::input::processedKeyboard().pop(event)) return false;
  *item = {}; // Processed input has no physical PS/2 scan codes.
  if (!event.query) _keycode = event.keycode;
  else if (event.down) {
    // Retained stock agon_ps2.h getKeyboardKey translation. On query key-up,
    // stock deliberately leaves the preceding global keycode unchanged.
    switch (fabgl::VirtualKey(event.virtual_key)) {
      case fabgl::VK_LEFT: _keycode=0x08; break;
      case fabgl::VK_TAB: _keycode=0x09; break;
      case fabgl::VK_RIGHT: _keycode=0x15; break;
      case fabgl::VK_DOWN: _keycode=0x0A; break;
      case fabgl::VK_UP: _keycode=0x0B; break;
      case fabgl::VK_BACKSPACE: _keycode=0x7F; break;
      default: _keycode=event.ascii; break;
    }
  }
  item->ASCII = event.ascii; item->vk = fabgl::VirtualKey(event.virtual_key);
  item->down = event.down;
  item->CTRL = event.modifiers & 1; item->SHIFT = (event.modifiers >> 1) & 1;
  item->LALT = (event.modifiers >> 2) & 1; item->RALT = (event.modifiers >> 3) & 1;
  item->CAPSLOCK = (event.modifiers >> 4) & 1; item->NUMLOCK = (event.modifiers >> 5) & 1;
  item->SCROLLLOCK = (event.modifiers >> 6) & 1; item->GUI = (event.modifiers >> 7) & 1;
  return true;
#else
  (void)item; return false;
#endif
}

inline std::uint8_t packKeyboardModifiers(
    fabgl::VirtualKeyItem *item) noexcept {
  return item->CTRL << 0 | item->SHIFT << 1 | item->LALT << 2 |
         item->RALT << 3 | item->CAPSLOCK << 4 | item->NUMLOCK << 5 |
         item->SCROLLLOCK << 6 | item->GUI << 7;
}

inline bool shiftKeyPressed() noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
  return (agon::extender::input::processedKeyboard().modifiers() & 2) != 0;
#else
  return false;
#endif
}
inline bool ctrlKeyPressed() noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
  return (agon::extender::input::processedKeyboard().modifiers() & 1) != 0;
#else
  return false;
#endif
}

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

inline void setKeyboardState(std::uint16_t delay, std::uint16_t rate,
                             std::uint8_t leds) noexcept {
#ifdef AGON_EXTENDER_PROCESSED_KEYBOARD
  // Stock v2.16.0 retention/ranges; no physical LED or repeat generation claim.
  if (delay >= 250 && delay <= 1000) kbRepeatDelay = (delay / 250) * 250;
  if (rate >= 33 && rate <= 500) kbRepeatRate = rate;
  if (leds != 255) getKeyboard()->setLEDs(leds & 4, leds & 2, leds & 1);
#else
  (void)delay; (void)rate; (void)leds;
#endif
}

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
