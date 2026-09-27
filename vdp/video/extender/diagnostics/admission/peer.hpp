// REMOTE-005 A04 controlled hardware peer, NOT the production file service.
// All calls use sd_mutex. HTTP only arms a short-lived synthetic intent;
// the existing console owner alone consumes controls and transmits UART bytes.
#pragma once
#include <cstdint>
#include <cstring>
#include "../../storage/sd_wire.h"
namespace agon::extender::storage {
struct AdmissionProbe {
  std::uint8_t reply[48]{}, nonce[8]{}, grant[8]{};
  unsigned length=0, armed=0, race=0, hellos=0,polls=0,decides=0,closes=0,last=0;
  std::uint32_t poll_at=0, armed_at=0, job=0,generation=0;
  bool valid_poll=false,offered=false;
  bool arm(unsigned which,std::uint32_t now) {
    if(which>3)return false;
    if(which && (!valid_poll || now-poll_at>150 || armed || offered || length))return false;
    armed=which;armed_at=now;return true;
  }
  bool receive(const std::uint8_t *p,unsigned n,std::uint32_t now,std::uint32_t a,std::uint32_t b) {
    if(n!=48 || p[0]!='S'||p[1]!='D'||p[2]!=1||p[3]!=4||sd_u16(p+14)!=28)return false;
    auto c=sd_crc_update(0xffffffffU,p,16);c=sd_crc_update(c,p+20,28)^0xffffffffU;
    if(c!=sd_u32(p+16))return true;
    if(length)return true; // One request/reply at a time, never overwrite.
    std::memcpy(reply,p,48);reply[3]=5;reply[13]=0;
    if(p[12]==1) {
      ++hellos;sd_put32(nonce,a?a:1);sd_put32(nonce+4,b?b:1);
      std::memset(reply+20,0,28);std::memcpy(reply+20,nonce,8);reply[46]=5;
      valid_poll=offered=false;armed=0;
    } else {
      if(std::memcmp(p+20,nonce,8))return true;
      if(p[12]==2) {
        ++polls;valid_poll=true;poll_at=now;
        if(offered && sd_u32(p+28)!=generation)offered=false;
        if(armed && now-armed_at>1000)armed=0;
        if(armed && !offered) {
          ++job;if(!job)++job;generation=sd_u32(p+28);
          sd_put32(reply+32,job);reply[44]=1;reply[45]=3;offered=true;
        } else reply[13]=1;
      } else if(p[12]==3 && offered && sd_u32(p+32)==job && sd_u32(p+28)==generation) {
        ++decides;std::memcpy(grant,p+36,8);race=armed==3;armed=0;
      } else if(p[12]==10 && offered && sd_u32(p+32)==job && sd_u32(p+28)==generation) {
        ++closes;last=p[13];offered=false;armed=0;
      } else return true;
    }
    sd_seal(reply);length=48;
    if(p[12]==2 && offered && armed==2) {reply[16]^=1;armed=0;offered=false;}
    return true;
  }
  unsigned take(std::uint8_t *p) {auto n=length;std::memcpy(p,reply,n);length=0;return n;}
};
inline AdmissionProbe admission_probe;
}
