// USB HID 1.11 Appendix B boot-keyboard report acquisition. This class has one
// process owner; the USB callback copies bytes to that owner, never edits keys.
// No report-descriptor parser, software repeat or LED writes in this increment.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include "hid_key_mapping.hpp"

namespace agon::extender::input {
class UsbBootKeyboard final {
 public:
  enum class Result { accepted, invalid, waiting_neutral, rearmed };
  struct Key { uint8_t usage; ProcessedKey processed; bool mapped; };

  bool neutral() const {
    for (const auto &key:held_) if (key.processed.down) return false;
    return true;
  }

  template<class Emit> void releaseAll(Emit emit) {
    // Preserve the pressed key's identity; physical modifier flags are cleared.
    for (unsigned i=224;i<232;++i) release(i,0,emit);
    for (unsigned i=4;i<224;++i) release(i,0,emit);
  }
  template<class Emit> void disconnect(Emit emit) {
    releaseAll(emit); caps_=false; waiting_neutral_=false;
  }
  template<class Emit> void lostReport(Emit emit) {
    releaseAll(emit); waiting_neutral_=true;
  }
  template<class Emit> Result report(const uint8_t *data,size_t size,Emit emit) {
    if (size!=8 || !data || data[1]!=0) {
      lostReport(emit); return Result::invalid;
    }
    std::array<bool,232> pressed{};
    for (unsigned i=0;i<8;++i) pressed[224+i]=(data[0]>>i)&1;
    for (unsigned i=2;i<8;++i) {
      const auto key=data[i];
      if ((key>0 && key<4) || key>=224) {
        // ErrorRollOver, POSTFail and ErrorUndefined do not describe held keys.
        lostReport(emit); return Result::invalid;
      }
      if (key) pressed[key]=true; // Duplicate or reordered slots are one key.
    }
    if (waiting_neutral_) {
      for (bool down:pressed) if (down) return Result::waiting_neutral;
      waiting_neutral_=false; return Result::rearmed;
    }
    if (pressed[57] && !held_[57].processed.down) caps_=!caps_;
    const uint8_t modifiers=mosModifiers(data[0]) | (caps_?16:0);
    // Emit modifier transitions first, then all releases before new presses.
    for (unsigned i=224;i<232;++i) transition(i,pressed[i],modifiers,emit);
    for (unsigned i=4;i<224;++i) if (!pressed[i]) release(i,modifiers,emit);
    for (unsigned i=4;i<224;++i) if (pressed[i]) transition(i,true,modifiers,emit);
    return Result::accepted;
  }

 private:
  static uint8_t mosModifiers(uint8_t raw) {
    return ((raw&0x11)?1:0) | ((raw&0x22)?2:0) | ((raw&4)?4:0) |
           ((raw&0x40)?8:0) | ((raw&0x88)?128:0);
  }
  template<class Emit> void release(unsigned usage,uint8_t modifiers,Emit emit) {
    auto &held=held_[usage];
    if (!held.processed.down) return;
    auto up=held; held={}; up.processed.down=0;
    up.processed.modifiers=modifiers; emit(up);
  }
  template<class Emit> void transition(unsigned usage,bool down,uint8_t modifiers,Emit emit) {
    if (!down) { release(usage,modifiers,emit); return; }
    auto &held=held_[usage];
    if (held.processed.down) return; // USB idle reports are not typematic.
    const auto key=static_cast<uint8_t>(usage);
    held={key,hidKeySupported(key)?mapHidKey(key,modifiers):
          ProcessedKey{0,modifiers,0,1,0},hidKeySupported(key)};
    emit(held);
  }
  std::array<Key,232> held_{};
  bool caps_{},waiting_neutral_{};
};
}
