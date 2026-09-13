// REMOTE-002: bounded host requests; caller serializes all access. No I/O here.
// USB HID usage IDs reuse the existing CLI mapping, not the retired browser UI.
#pragma once
#include <array>
#include <cstring>
#include "usb_cli_keyboard.hpp"
namespace agon::extender::input {
constexpr unsigned REMOTE_HEADER=24,REMOTE_EVENTS=96,REMOTE_MAX=REMOTE_HEADER+REMOTE_EVENTS*2;
inline uint32_t remote32(const uint8_t *p) { return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24); }
inline uint32_t remoteCrc(const uint8_t *p,unsigned n) {
  uint32_t c=~0U;
  for(unsigned i=0;i<n;++i) {
    c^=(i>=20 && i<24)?0:p[i];
    for(unsigned b=0;b<8;++b)c=(c>>1)^(0xEDB88320U&uint32_t(-int(c&1)));
  }
  return ~c;
}
class RemoteKeyboard {
 public:
  enum Reason { none, cancelled, physical, expired, admission, disconnected, transport };
  struct Status {
    uint32_t boot{},session{},sequence{},emitted{},accepted{},discarded{};
    unsigned pending{},held{},locale{};
    bool ready{},physical_neutral{},caps{};
    Reason reason{};
  };
  void begin(uint32_t boot) { *this=RemoteKeyboard{};boot_=boot?boot:1; }
  void admit(unsigned locale) { locale_=locale;ready_=locale<=1; }
  void physicalNeutral(bool value) {
    physical_neutral_=value;
    // The USB decoder is authoritative across admission/layout changes, where
    // its suppressed releases need not have reached physicalKey().
    if(value)physical_={};
  }
  // Layout/reboot/admission invalidates old requests; release before next keys.
  void boundary(Reason reason=admission) {
    cancel(reason);ready_=false;if(++boot_==0)++boot_;
  }
  void physicalKey(ProcessedKey key) {
    if(key.virtual_key<physical_.size())physical_[key.virtual_key]=key.down;
    caps_=(key.modifiers&16)!=0;
    if(key.down) {physical_neutral_=false;cancel(physical);}
  }
  void physicalLost() { physical_={};caps_=false;cancel(disconnected); }
  void tick(uint32_t now) {
    // HTTP can renew after the console samples its iteration timestamp but
    // before console takes the shared lock. Unsigned subtraction interpreted
    // that slightly older timestamp as almost a whole 49-day timer period.
    // Signed modular elapsed time tolerates it and still handles timer wrap.
    if(session_ && reason_==none && int32_t(now-last_request_)>=5000)cancel(expired);
  }
  Status status(uint32_t now) {
    tick(now);unsigned held=0;for(auto k:held_)held+=k.down!=0;
    return {boot_,session_,sequence_,emitted_,accepted_,discarded_,count_-index_,held,locale_,ready_,neutral(),caps_,reason_};
  }
  // KY,v1,op, boot32,session32,sequence32, payload16,reserved16, CRC32;
  // op1=open,2=events (usage/down pairs),3=cancel,4=heartbeat. Little endian.
  unsigned post(const uint8_t *p,unsigned n,uint32_t now) {
    tick(now);
    if(n<REMOTE_HEADER || n>REMOTE_MAX || p[0]!='K' || p[1]!='Y' || p[2]!=1 ||
       p[18] || p[19] || unsigned(p[16]|p[17]<<8)!=n-REMOTE_HEADER ||
       remote32(p+20)!=remoteCrc(p,n))return 400;
    const auto op=p[3];const auto boot=remote32(p+4),sid=remote32(p+8),seq=remote32(p+12);
    if(!sid || !seq || boot!=boot_)return 409;
    if(sid==session_ && seq==sequence_)
      return n==cached_size_ && !std::memcmp(p,cached_.data(),n)?200:409;
    if(op==1) {
      if(n!=REMOTE_HEADER || seq!=1)return 400;
      if(!ready_ || !neutral() || releasing_)return 503;
      if(session_ && reason_==none)return 409;
      session_=sid;sequence_=0;reason_=none;emitted_=accepted_=discarded_=0;held_={};count_=index_=0;due_=now;
    } else {
      if(sid!=session_ || seq!=sequence_+1 || sequence_==0xffffffffU)return 409;
      if(op==3) {
        if(n!=REMOTE_HEADER)return 400;
        cancel(cancelled);
      } else {
        if(!ready_ || reason_!=none)return 409;
        if(op==4) { if(n!=REMOTE_HEADER)return 400; }
        else if(op==2) {
          if(n==REMOTE_HEADER || (n-REMOTE_HEADER)%2)return 400;
          if(index_!=count_)return 503;
          auto preview=held_;
          for(unsigned i=REMOTE_HEADER;i<n;i+=2) {
            const auto u=p[i],down=p[i+1];
            if(u>=preview.size() || u==57 || down>1 || bool(preview[u].down)==bool(down))return 400;
            if(!mapUsbCliKey(u,0,locale_).virtual_key)return 400;
            preview[u].down=down;
            unsigned ordinary=0;for(unsigned k=0;k<224;++k)ordinary+=preview[k].down!=0;
            if(ordinary>6)return 400;
          }
          count_=(n-REMOTE_HEADER)/2;index_=0;accepted_+=count_;
          std::memcpy(events_.data(),p+REMOTE_HEADER,n-REMOTE_HEADER);
          // Keep the preceding event's deadline across request boundaries.
          // Resetting it here lets tiny HTTP batches bypass the 20 ms spacing.
        } else return 400;
      }
    }
    sequence_=seq;last_request_=now;cached_size_=n;std::memcpy(cached_.data(),p,n);
    return 200;
  }
  // Called by the UART owner only, after physical input and when output can
  // accept another complete event. One event per call; no catch-up repeat burst.
  bool take(ProcessedKey &key,uint32_t now) {
    tick(now);
    if(release(key))return true;
    if(!ready_ || reason_!=none || index_==count_ || int32_t(now-due_)<0)return false;
    const auto u=events_[index_*2],down=events_[index_*2+1];
    if(down) {
      held_[u].down=1;key=mapUsbCliKey(u,modifiers(),locale_);held_[u]=key;
    } else {
      key=held_[u];held_[u]={};key.down=0;key.modifiers=modifiers();
    }
    ++index_;++emitted_;due_=now+20;return true;
  }
  // Immediate physical takeover drains only remote held-key releases before
  // queuing the new physical press. Unsent remote events are discarded.
  bool release(ProcessedKey &key) {
    if(!releasing_)return false;
    // Release ordinary keys before modifiers, preserving remaining state.
    for(unsigned u=0;u<held_.size();++u)if(held_[u].down) {
      key=held_[u];held_[u]={};key.down=0;key.modifiers=modifiers();return true;
    }
    releasing_=false;return false;
  }
  void cancel(Reason reason) {
    if(session_ && reason_==none)reason_=reason;
    discarded_+=count_-index_;count_=index_=0;releasing_=false;
    for(const auto &key:held_)if(key.down)releasing_=true;
  }
 private:
  bool neutral() const { if(!physical_neutral_)return false;for(bool b:physical_)if(b)return false;return true; }
  uint8_t modifiers() const {
    uint8_t raw=0;for(unsigned i=0;i<8;++i)if(held_[224+i].down)raw|=1<<i;
    return ((raw&0x11)?1:0)|((raw&0x22)?2:0)|((raw&4)?4:0)|
      ((raw&0x40)?8:0)|((raw&0x88)?128:0)|(caps_?16:0);
  }
  uint32_t boot_{1},session_{},sequence_{},emitted_{},accepted_{},discarded_{},last_request_{},due_{};
  unsigned locale_{},count_{},index_{},cached_size_{};
  bool ready_{},caps_{},releasing_{},physical_neutral_{true};
  Reason reason_{none};
  std::array<bool,249> physical_{};
  std::array<ProcessedKey,232> held_{};
  std::array<uint8_t,REMOTE_EVENTS*2> events_{};
  std::array<uint8_t,REMOTE_MAX> cached_{};
};
}
