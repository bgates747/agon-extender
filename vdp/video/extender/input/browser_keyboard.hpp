// Browser session handoff. HTTP producers never call VDP or touch its UART.
// All methods synchronize; pop belongs to the sole VDP process task. Revocation
// discards queued events and releases already-consumed keys BEFORE new events.
#pragma once
#include <array>
#include <mutex>
#include "processed_keyboard.hpp"
namespace agon::extender::input {
class BrowserKeyboard final {
 public:
  struct Event { uint8_t physical, modifiers, down; };
  void ready(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!enabled) revoke();
    ready_=enabled;
  }
  bool take(int owner, uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!ready_) return false;
    revoke(); owner_=owner; seen_=now; return true;
  }
  bool heartbeat(int owner,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke();
    if (owner_!=owner || owner<0) return false;
    seen_=now; return true;
  }
  void close(int owner) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_==owner) revoke();
  }
  bool push(int owner,Event event,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke();
    if (owner<0 || owner!=owner_ || !ready_) return false;
    if (event.down>1 || event.physical>=held_.size() || !supported(event.physical) || count_==queue_.size()) {
      revoke(); return false;
    }
    queue_[(head_+count_)%queue_.size()]=event; ++count_; seen_=now; return true;
  }
  void expire(uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke();
  }
  bool pop(ProcessedKey &out,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke();
    if (releasing_) {
      // Modifier releases first, with physical modifier flags cleared.
      for (unsigned pass=0;pass<2;++pass) for (unsigned i=pass?1:224;i<(pass?224:232);++i)
        if (held_[i].down) { out=held_[i]; held_[i]={}; out.down=0; out.modifiers &= 0x70; return true; }
      releasing_=false;
    }
    while (count_) {
      auto event=queue_[head_]; head_=(head_+1)%queue_.size(); --count_;
      auto &held=held_[event.physical];
      if (!event.down) {
        if (!held.down) continue;
        out=held; held={}; out.down=0; out.modifiers=event.modifiers; return true;
      }
      if (held.down) { out=held; out.modifiers=event.modifiers; return true; }
      out=map(event); held=out; return true;
    }
    return false;
  }
  static bool supported(uint8_t p) { return (p>=4 && p<=56 && p!=50) || p==57 || (p>=224&&p<=231); }
  static ProcessedKey map(Event e) {
    uint8_t c=0,vk=0; const auto p=e.physical;
    const bool shift=e.modifiers&2, caps=e.modifiers&16;
    if (p>=4 && p<=29) c=(shift!=caps?'A':'a')+p-4;
    else if (p>=30 && p<=39) c=shift ? "!@#$%^&*()"[p-30] : "1234567890"[p-30];
    else if (p==40) { c=13; vk=143; }
    else if (p==41) { c=27; vk=125; }
    else if (p==42) { c=8; vk=132; }
    else if (p==43) { c=9; vk=142; }
    else if (p==44) c=' ';
    else if (p>=45&&p<=56) c=(shift ? "_+{}| :\"~<>?" : "-=[]\\ ;'`,./")[p-45];
    else if (p==57) vk=141;
    else if (p>=224&&p<=231) { constexpr uint8_t modifiers[]={121,117,119,123,122,118,120,124}; vk=modifiers[p-224]; }
    if (!vk) vk=asciiVirtual(c);
    auto keycode=c;
    if ((e.modifiers&1) && ((c>='a'&&c<='z')||(c>='A'&&c<='Z'))) keycode=c&31;
    return {keycode,e.modifiers,vk,1,keycode};
  }
 private:
  static uint8_t asciiVirtual(uint8_t c) {
    if (c>='a'&&c<='z') return 22+c-'a';
    if (c>='A'&&c<='Z') return 48+c-'A';
    if (c>='0'&&c<='9') return 2+c-'0';
    if (c==' ') return 1;
    constexpr char chars[]="`'\"=-+*\\/.:,;&|#@^$%! ?{}[]()<>_~";
    constexpr uint8_t codes[]={74,76,77,78,79,81,84,85,87,89,90,91,92,93,94,95,96,97,98,101,102,1,103,104,105,106,107,108,109,110,111,112,115};
    for (unsigned i=0;i<sizeof(chars)-1;++i) if (chars[i]==c) return codes[i];
    return 0;
  }
  void revoke() { owner_=-1; head_=count_=0; releasing_=true; }
  std::mutex mutex_;
  std::array<Event,64> queue_{};
  std::array<ProcessedKey,232> held_{};
  size_t head_{}, count_{};
  int owner_=-1;
  uint32_t seen_{};
  bool ready_{}, releasing_{};
};
inline BrowserKeyboard &browserKeyboard() { static BrowserKeyboard keyboard; return keyboard; }
}
