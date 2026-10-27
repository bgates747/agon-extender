// F310 XInput wire facts: Linux xpad.c (v6.12), xpad360_process_packet.
// Own bounded decoder; no Linux driver code or HID boot-keyboard assumptions.
#pragma once
#include "receiver.hpp"
namespace agon::extender::controller {
enum class UsbReport { state, ignored, invalid };
inline bool f310DpadConflict(std::uint8_t value){
  return (value&3)==3||(value&12)==12;
}
inline UsbReport decodeF310(const std::uint8_t*p,std::size_t n,State&out){
  if(!n)return UsbReport::invalid;
  if(p[0]!=0)return UsbReport::ignored; // XInput status, not a controller snapshot.
  if(n!=20||p[1]!=20)return UsbReport::invalid;
  State s{};
  for(unsigned i=0;i<4;++i){
    const int v=int(get16(p+6+i*2));
    // Linux evdev/xpad convention: positive Y is down. Bitwise complement
    // preserves the asymmetric signed16 endpoints without overflowing -32768.
    s.sticks[i]=std::int16_t((i&1)?(v>=32768?65535-v:-1-v):(v>=32768?v-65536:v));
  }
  s.triggers={p[4],p[5]};
  // Existing carrier control order: A B Y X LB RB Back Start Guide L3 R3,
  // then D-pad left/right/up/down. No trigger-to-digital conversion.
  constexpr unsigned byte[]={3,3,3,3,3,3,2,2,3,2,2,2,2,2,2};
  constexpr unsigned mask[]={16,32,128,64,1,2,32,16,4,64,128,4,8,1,2};
  for(unsigned i=0;i<15;++i)if(p[byte[i]]&mask[i])s.held|=1u<<i;
  // Linux v6.12 xpad360_process_packet reports each hat axis as positive
  // contact minus negative contact. Opposite contacts therefore cancel; they
  // are not a malformed USB packet. The old decoder faulted the entire USB
  // client on these transitions (INPUT-003 D-pad review). Keep LAN/carrier
  // validHeld strict by normalizing only this device's raw contacts here.
  if((p[2]&12)==12)s.held&=~std::uint16_t(0x1800);
  if((p[2]&3)==3)s.held&=~std::uint16_t(0x6000);
  out=s;return UsbReport::state;
}

struct F310Interface {unsigned number{},endpoint{},packet{},interval{};};
inline bool f310Interface(const std::uint8_t*p,std::size_t n,F310Interface&out){
  if(n<9||p[0]<9||p[1]!=2||get16(p+2)!=n)return false;
  bool selected=false;unsigned iface=0;
  for(std::size_t at=0;at<n;){
    const auto len=p[at];if(len<2||len>n-at)return false;
    if(p[at+1]==4){
      if(len<9)return false;
      iface=p[at+2];
      selected=p[at+3]==0&&p[at+5]==0xff&&p[at+6]==0x5d&&p[at+7]==1;
    }else if(p[at+1]==5&&selected){
      if(len<7)return false;
      const unsigned ep=p[at+2],packet=get16(p+at+4);
      if((ep&0x80)&&(ep&15)&&(p[at+3]&3)==3&&packet>=20&&packet<=64&&p[at+6]){
        out={iface,ep,packet,p[at+6]};return true;
      }
    }
    at+=len;
  }
  return false;
}

// Caller holds the controller mutex. Local publication reuses the receiver's
// proven bounded edge retention; no packets are encoded, sent, or checksummed.
// A private non-routable endpoint separates local writes from real UDP peers.
class UsbSource {
 public:
  void connect(Receiver&core){disconnect(core);attached_=true;fault_=false;}
  void disconnect(Receiver&core){
    if(owns(core))core.invalidate(Fault::Source);
    attached_=have_=false;token_=0;
  }
  void fail(Receiver&core){if(owns(core))core.invalidate(Fault::Source);fault_=true;have_=false;}
  void report(const State&s){latest_=s;have_=true;}
  bool attached()const{return attached_;}
  bool ready()const{return attached_&&have_&&!fault_;}
  bool owns(const Receiver&core)const{return token_&&coreSession(core)==token_;}
  // An explicit new EMOS application token may rearm queue overflow. Physical
  // USB faults still require reconnect; a healthy running app is never reset.
  void rearm(Receiver&core,std::uint32_t caller,std::uint64_t now){
    if(caller&&caller!=caller_){
      caller_=caller;
      if(owns(core)&&!core.snapshot(now).active)token_=0;
    }
  }
  void tick(Receiver&core,std::uint64_t now,std::uint64_t token){
    if(!ready())return;
    auto s=core.snapshot(now);
    if(token_){
      if(s.session!=token_){token_=0;return;}
      if(!s.active)return; // fault latch: explicit new caller/reconnect only.
    }else{
      if(s.active)return; // Never steal a live LAN source.
      if(!token||token==s.session)return;
      if(core.open(s.instance,token,{0,1},250,token,now)!=200)return;
      token_=token;sequence_=edge_=0;previous_=latest_.held;
    }
    if(sequence_==UINT32_MAX||edge_>UINT32_MAX-15){core.invalidate(Fault::Source);return;}
    Packet p{};p.instance=s.instance;p.session=token_;p.sequence=++sequence_;p.state=latest_;p.profile=Native;
    for(unsigned i=0;i<15;++i)if((previous_^latest_.held)&(1u<<i))
      p.edges[p.count++]={++edge_,std::uint8_t(i),std::uint8_t(bool(latest_.held&(1u<<i)))};
    previous_=latest_.held;
    std::array<std::uint8_t,40>ack{};core.receive(p,{0,1},now,ack);
  }
 private:
  // Receiver exposes only the session for ownership checks; querying here
  // must not advance expiry with a fabricated clock.
  static std::uint64_t coreSession(const Receiver&core){return core.session();}
  State latest_{};bool attached_{},have_{},fault_{};
  std::uint64_t token_{};std::uint32_t sequence_{},edge_{},caller_{};
  std::uint16_t previous_{};
};
}
