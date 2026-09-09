// Browser session handoff. HTTP producers never call VDP or touch its UART.
// All methods synchronize; pop belongs to the sole VDP process task. Revocation
// discards queued events and releases already-consumed keys BEFORE new events.
#pragma once
#include <array>
#include <mutex>
#include "hid_key_mapping.hpp"
#include "../diagnostic/browser_trace.hpp"
namespace agon::extender::input {
class BrowserKeyboard final {
 public:
  struct Event { uint8_t physical, modifiers, down; uint32_t trace_session{},trace_ordinal{}; };
  void ready(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!enabled) revoke(1);
    ready_=enabled;
  }
  bool take(int owner, uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!ready_) return false;
    revoke(2); owner_=owner; seen_=now; return true;
  }
  bool heartbeat(int owner,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke(3);
    if (owner_!=owner || owner<0) return false;
    seen_=now; return true;
  }
  void close(int owner) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_==owner) revoke(4);
  }
  bool push(int owner,Event event,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke(3);
    if (owner<0 || owner!=owner_ || !ready_) return false;
    if (event.down>1 || event.physical>=held_.size() || !supported(event.physical) || count_==queue_.size()) {
      revoke(5); return false;
    }
    queue_[(head_+count_)%queue_.size()]=event; ++count_; seen_=now; return true;
  }
  void expire(uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke(3);
  }
  bool pop(ProcessedKey &out,uint32_t now) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (owner_>=0 && uint32_t(now-seen_)>=2000) revoke(3);
    if (releasing_) {
      // Modifier releases first, with physical modifier flags cleared.
      for (unsigned pass=0;pass<2;++pass) for (unsigned i=pass?1:224;i<(pass?224:232);++i)
        if (held_[i].down) { out=held_[i]; held_[i]={}; out.down=0; out.modifiers &= 0x70; return true; }
      releasing_=false;
    }
    while (count_) {
      auto event=queue_[head_]; head_=(head_+1)%queue_.size(); --count_;
      diagnostic::trace("key_dequeue",event.trace_session,event.trace_ordinal,event.physical,event.down);
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
  static bool supported(uint8_t p) { return hidKeySupported(p); }
  static ProcessedKey map(Event e) { return mapHidKey(e.physical,e.modifiers); }
 private:
  void revoke(int reason) {
    if(owner_>=0) diagnostic::trace("owner_revoke",owner_,reason,count_);
    owner_=-1; head_=count_=0; releasing_=true; }
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
