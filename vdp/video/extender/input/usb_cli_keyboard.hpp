// PORT-015 first ordinary-CLI mapping. UK/US and explicit editing keys only;
// retain W2's report decoder and the existing browser map unchanged. Stock
// VDP v2.16.0 agon_ps2.h uses DEL for Backspace, 8/21/10/11 for arrows.
#pragma once
#include "usb_boot_keyboard.hpp"
namespace agon::extender::input {
inline ProcessedKey mapUsbCliKey(uint8_t usage,uint8_t mods,uint8_t locale) {
  if (!hidKeySupported(usage) && !(locale==0 && (usage==50 || usage==100)) &&
      !(usage>=58 && usage<=69) && !(usage>=73 && usage<=82))
    return {0,mods,0,1,0}; // Do not interpret an unsupported table placeholder.
  auto key=mapHidKey(usage,mods);
  uint8_t c=key.ascii,vk=key.virtual_key;
  if (locale==0) {
    if (usage==31 && (mods&2)) c='"';
    if (usage==32 && (mods&2)) { c=163; vk=99; }
    if (usage==52 && (mods&2)) c='@';
    if (usage==49 || usage==50) c=(mods&2)?'~':'#';
    if (usage==100) c=(mods&2)?'|':'\\';
    if (c!=163 && (usage==31 || usage==52 || usage==49 || usage==50 || usage==100)) vk=hidAsciiVirtual(c);
  }
  if (usage==42) { c=8; key.keycode=127; }
  else if (usage>=58 && usage<=69) { c=0; vk=159+usage-58; key.keycode=0; }
  else if (usage>=73 && usage<=82) {
    constexpr uint8_t codes[]={0,0,0,127,0,0,21,8,10,11};
    constexpr uint8_t vkeys[]={128,133,146,130,135,148,156,154,152,150};
    c=0; vk=vkeys[usage-73]; key.keycode=codes[usage-73];
  } else { key.keycode=c; if ((mods&1) && ((c>='a'&&c<='z')||(c>='A'&&c<='Z'))) key.keycode=c&31; }
  key.ascii=c; key.virtual_key=vk; return key;
}
class UsbCliKeyboard {
 public:
  uint8_t locale{};
  uint16_t repeat_delay{500},repeat_rate{100};
  template<class Emit> void report(const uint8_t *data,size_t size,uint32_t now,Emit emit) {
    decoder_.report(data,size,[&](const UsbBootKeyboard::Key &raw) {
      const auto usage=raw.usage;
      if (raw.processed.down) {
        const auto key=mapUsbCliKey(usage,raw.processed.modifiers,locale);
        if (!key.virtual_key || locale>1) return;
        held_[usage]=key;
        if (admitted_ && !wait_neutral_) emit(key);
        if (repeatable(usage)) { repeat_usage_=usage; repeat_at_=now+repeat_delay; }
      } else {
        auto up=held_[usage]; held_[usage]={};
        up.down=0; up.modifiers=raw.processed.modifiers;
        if (repeat_usage_==usage) repeat_usage_=0;
        if (up.virtual_key && admitted_ && !wait_neutral_) emit(up);
      }
    });
    if (decoder_.neutral()) wait_neutral_=false;
  }
  template<class Emit> void tick(uint32_t now,Emit emit) {
    if (!admitted_ || wait_neutral_ || !repeat_usage_ || int32_t(now-repeat_at_)<0) return;
    // At most one repeat per owner iteration: a stalled UART never creates a
    // catch-up burst. Held identity survives modifier/layout changes.
    emit(held_[repeat_usage_]); repeat_at_=now+repeat_rate;
  }
  void admit() { admitted_=true; wait_neutral_=wait_neutral_ || !decoder_.neutral(); repeat_usage_=0; }
  void pause() { admitted_=false; repeat_usage_=0; }
  void admissionBoundary() {
    // Caller drains its accepted old events and releases before the poll reply.
    // A key already held across admission must be released before new input.
    if (!decoder_.neutral()) lost([](ProcessedKey){});
    pause();
  }
  template<class Emit> void lost(Emit emit) {
    decoder_.lostReport([&](const UsbBootKeyboard::Key &raw) { release(raw,emit); });
    wait_neutral_=true; repeat_usage_=0;
  }
  template<class Emit> void disconnect(Emit emit) {
    decoder_.disconnect([&](const UsbBootKeyboard::Key &raw) { release(raw,emit); });
    wait_neutral_=false; repeat_usage_=0;
  }
 private:
  static bool repeatable(uint8_t u) { return (u>=4 && u<=56) || (u>=73 && u<=82) || u==100; }
  template<class Emit> void release(const UsbBootKeyboard::Key &raw,Emit emit) {
    auto up=held_[raw.usage]; held_[raw.usage]={}; up.down=0; up.modifiers=raw.processed.modifiers;
    if (up.virtual_key && admitted_ && !wait_neutral_) emit(up);
  }
  UsbBootKeyboard decoder_;
  std::array<ProcessedKey,232> held_{};
  bool admitted_{},wait_neutral_{};
  uint8_t repeat_usage_{};
  uint32_t repeat_at_{};
};
}
