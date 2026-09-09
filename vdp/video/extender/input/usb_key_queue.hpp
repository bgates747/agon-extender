// One owner; reserve space for all held-key releases on loss/admission.
#pragma once
#include <array>
#include "processed_keyboard.hpp"
namespace agon::extender::input {
class UsbKeyQueue {
 public:
  bool push(ProcessedKey key) {
    if (size_>=48 || key.virtual_key>=held_.size() || !key.virtual_key) return false;
    append(key); held_[key.virtual_key]=key; return true;
  }
  bool pop(ProcessedKey &key) {
    if (!size_) return false;
    key=queue_[head_]; head_=(head_+1)%queue_.size(); --size_; return true;
  }
  bool releaseAll() {
    // Boot reports have at most six ordinary and eight modifier usages.
    // Preserve queued order; do not discard an unsent release of an older key.
    for(unsigned i=117;i<=124;++i) if (!release(i)) return false;
    for(unsigned i=1;i<held_.size();++i) if ((i<117 || i>124) && !release(i)) return false;
    return true;
  }
  void reset() { head_=size_=0; held_={}; }
  bool empty() const { return size_==0; }
 private:
  void append(ProcessedKey key) { queue_[(head_+size_)%queue_.size()]=key; ++size_; }
  bool release(unsigned i) {
    if (!held_[i].down) return true;
    if(size_==queue_.size()) return false;
    auto key=held_[i]; key.down=0; key.modifiers=0; held_[i]={};append(key);return true;
  }
  std::array<ProcessedKey,64> queue_{};
  std::array<ProcessedKey,249> held_{};
  unsigned head_{},size_{};
};
}
