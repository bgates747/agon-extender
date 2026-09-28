#pragma once
#include "../sd_wire.h"
#include <cstring>
namespace agon::extender::storage::application {
// All methods called with sd_mutex. No filesystem, allocation or wait here.
struct Mailbox {
  std::uint8_t request[240]{},response[240]{};
  unsigned requestSize=0,responseSize=0,generation=0;
  std::uint32_t touched=0;
  bool owned=false,working=false,closing=false;
  static bool hello(const std::uint8_t *p,unsigned n) {
    return n==48&&p[3]==4&&p[12]==1&&p[44]==2;
  }
  bool receive(const std::uint8_t *p,unsigned n,std::uint32_t now,bool other) {
    if(!owned&&!hello(p,n))return false;
    if(other)return true; // competing owner: no execution or deferred queue
    if(n<20||n>240||p[0]!='S'||p[1]!='D'||p[2]!=1||sd_u16(p+14)!=n-20)return true;
    auto c=sd_crc_update(0xffffffffU,p,16);
    if((sd_crc_update(c,p+20,n-20)^0xffffffffU)!=sd_u32(p+16))return true;
    if(requestSize||responseSize||working)return true;
    if(!owned){owned=true;closing=false;++generation;}
    std::memcpy(request,p,n);requestSize=n;touched=now;return true;
  }
  unsigned take(std::uint8_t *p) {
    auto n=responseSize;if(n){std::memcpy(p,response,n);responseSize=0;if(closing)owned=closing=false;}return n;
  }
};
}
