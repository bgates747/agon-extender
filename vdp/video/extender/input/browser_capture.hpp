// Browser transitions join the existing processed-key serializer. No I/O here;
// the shared input lock covers browser admission, USB takeover and UART take.
#pragma once
#include "remote_keyboard.hpp"
namespace agon::extender::input {
class BrowserCapture {
 public:
  bool active() const { return owner_!=0; }
  uint32_t generation() const { return generation_; }
  void capture(uint32_t owner,uint32_t now,unsigned locale) {
    cancel(); owner_=owner; if(++generation_==0)++generation_;
    sequence_=1; renewed_=now; locale_=locale; known_=locks_=0;
  }
  void cancel() { owner_=0; count_=head_=0; preview_={}; repeat_=0; }
  void disconnect(uint32_t owner) { if(owner_==owner)cancel(); }
  void tick(uint32_t now) {
    // Console can sample time just before HTTP renews under the same lock.
    if(active() && int32_t(now-renewed_)>=5000)cancel();
  }
  // BK v1: op, generation32, sequence32, usage, down, known-locks, locks.
  // Locks use stock modifier bits (Caps 16, Num 32, Scroll 64).
  bool request(uint32_t owner,const uint8_t *p,uint32_t now) {
    tick(now);
    if(owner!=owner_ || !active() || remote32(p+4)!=generation_ ||
       sequence_==0xffffffffU || remote32(p+8)!=sequence_+1 ||
       (p[14]&~0x70) || (p[15]&~p[14]))return false;
    if(p[3]==2) {
      auto u=p[12],down=p[13];
      if(u>=preview_.size() || down>1 || preview_[u]==bool(down) || count_==queue_.size())return false;
      if(!mapUsbCliKey(u,p[15],locale_).virtual_key)return false;
      // Translation cannot guess an unknown lock. Releases retain down identity.
      if(down && ((u>=4 && u<=29 && !(p[14]&16)) ||
                  (u>=89 && u<=99 && !(p[14]&32))))return false;
      unsigned held=down; for(unsigned k=0;k<224;++k)if(k!=u)held+=preview_[k];
      if(u<224 && held>6)return false;
      preview_[u]=down;queue_[(head_+count_)%queue_.size()]={u,down,p[15]};++count_;
    } else if(p[3]==4)cancel();
    else if(p[3]!=3 && p[3]!=5)return false;
    locks_=p[15];known_=p[14];++sequence_;renewed_=now;return true;
  }
  bool release(ProcessedKey &key) {
    // Called after cancellation and before any new provider emits a down.
    for(unsigned u=0;u<held_.size();++u)if(held_[u].down) {
      key=held_[u];held_[u]={};key.down=0;key.modifiers=modifiers(key.modifiers&0x70);return true;
    }
    return false;
  }
  bool take(ProcessedKey &key,uint32_t now) {
    tick(now);
    if(!active())return release(key);
    if(count_) {
      const auto e=queue_[head_];head_=(head_+1)%queue_.size();--count_;
      if(e.down) {
        held_[e.usage].down=1;key=mapUsbCliKey(e.usage,modifiers(e.locks),locale_);held_[e.usage]=key;
        if(repeatable(e.usage)){repeat_=e.usage;due_=now+delay;}
      } else {
        key=held_[e.usage];held_[e.usage]={};key.down=0;key.modifiers=modifiers(e.locks);
        if(repeat_==e.usage)repeat_=0;
      }
      return true;
    }
    if(repeat_ && int32_t(now-due_)>=0) {
      key=held_[repeat_];due_=now+rate;return true; // no catch-up burst
    }
    return false;
  }
  uint16_t delay{500},rate{100};
 private:
  static bool repeatable(uint8_t u) {
    return (u>=4 && u<=56)||(u>=73 && u<=82)||(u>=84 && u<=99)||u==100;
  }
  uint8_t modifiers(uint8_t locks) const {
    uint8_t raw=0;for(unsigned i=0;i<8;++i)if(held_[224+i].down)raw|=1<<i;
    return ((raw&0x11)?1:0)|((raw&0x22)?2:0)|((raw&4)?4:0)|
      ((raw&0x40)?8:0)|((raw&0x88)?128:0)|locks;
  }
  struct Event { uint8_t usage,down,locks; };
  std::array<Event,64> queue_{};
  std::array<bool,232> preview_{};
  std::array<ProcessedKey,232> held_{};
  unsigned head_{},count_{},locale_{};
  uint32_t owner_{},generation_{},sequence_{},renewed_{},due_{};
  uint8_t locks_{},known_{},repeat_{};
};

class InputOwner : public RemoteKeyboard {
 public:
  void begin(uint32_t boot) { RemoteKeyboard::begin(boot);browser_=BrowserCapture{};browser_cleanup_=false; }
  void boundary(Reason reason=admission) { browser_.cancel();RemoteKeyboard::boundary(reason); }
  void cancel(Reason reason) { browser_.cancel();RemoteKeyboard::cancel(reason); }
  void physicalKey(ProcessedKey key) {
    if(key.down)browser_.cancel();
    RemoteKeyboard::physicalKey(key);
  }
  void physicalNeutral(bool value) {
    if(!value) { browser_.cancel();RemoteKeyboard::cancel(physical); }
    RemoteKeyboard::physicalNeutral(value);
  }
  void physicalLost() { browser_.cancel();RemoteKeyboard::physicalLost(); }
  void tick(uint32_t now) { browser_.tick(now);RemoteKeyboard::tick(now); }
  bool release(ProcessedKey &key) { return RemoteKeyboard::release(key)||browser_.release(key); }
  bool take(ProcessedKey &key,uint32_t now) {
    tick(now);
    if(RemoteKeyboard::release(key))return true;
    if(browser_cleanup_) { if(browser_.release(key))return true;browser_cleanup_=false; }
    if(browser_.take(key,now))return true;
    return !browser_.active() && RemoteKeyboard::take(key,now);
  }
  unsigned post(const uint8_t *p,unsigned n,uint32_t now) {
    tick(now);return browser_.active()?503:RemoteKeyboard::post(p,n,now);
  }
  void browserDisconnect(uint32_t owner) { browser_.disconnect(owner); }
  void repeat(uint16_t delay,uint16_t rate) { browser_.delay=delay;browser_.rate=rate; }
  unsigned browserRequest(uint32_t owner,const uint8_t *p,unsigned n,uint32_t now,uint32_t &generation) {
    tick(now);generation=browser_.generation();
    if(n!=16 || p[0]!='B' || p[1]!='K' || p[2]!=1 || !owner)return 400;
    if(p[3]==1) {
      auto s=status(now);
      if(remote32(p+4) || remote32(p+8)!=1 || p[12] || p[13] || p[14] || p[15])return 400;
      if(!s.ready || !s.physical_neutral)return 503;
      RemoteKeyboard::cancel(cancelled);browser_.capture(owner,now,s.locale);browser_cleanup_=true;
      generation=browser_.generation();return 200;
    }
    return browser_.request(owner,p,now)?200:409;
  }
 private:
  BrowserCapture browser_;
  bool browser_cleanup_{};
};
}
