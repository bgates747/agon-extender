// PORT-017 bounded RPC state. Caller owns synchronization and UART transmission.
#pragma once
#include <cstdint>
#include <cstring>
#include "sd_wire.h"

namespace agon::extender::storage {
class SdService {
 public:
  bool online(std::uint32_t now) const { return admitted_ && now-seen_<5000; }
  std::uint32_t boot() const { return boot_; }
  bool pending() const { return pending_; }
  unsigned post(const std::uint8_t *data,unsigned n,std::uint8_t *out,
                unsigned &out_length,std::uint32_t now) {
    out_length=0;
    if(!sd_valid(data,n) || data[3]!=SD_REQUEST || data[13] || !sd_u32(data+8))return 400;
    if(request_length_ && sd_u32(data+4)==sd_u32(request_+4) &&
       sd_u32(data+8)==sd_u32(request_+8)) {
      if(n!=request_length_ || std::memcmp(data,request_,n))return 409;
      if(response_length_) {
        std::memcpy(out,response_,response_length_);out_length=response_length_;return 200;
      }
      return online(now)?202:503;
    }
    if(!online(now))return 503;
    if(pending_)return 409;
    std::memcpy(request_,data,n);request_length_=n;response_length_=0;
    pending_=true;sent_=false;return 202;
  }
  // The parser/keyboard owner polls this only at packet boundaries and after keys.
  unsigned take(std::uint8_t *out,std::uint32_t now) {
    if(!pending_ || !online(now) || (sent_ && now-sent_at_<400))return 0;
    std::memcpy(out,request_,request_length_);sent_=true;sent_at_=now;
    return request_length_;
  }
  bool receive(const std::uint8_t *data,unsigned n,std::uint32_t now) {
    if(!sd_valid(data,n))return false;
    if(data[3]==SD_PRESENCE) {
      if(sd_u16(data+14) || data[13] || data[12]>1)return false;
      auto id=sd_u32(data+4);
      if(id!=boot_) {
        boot_=id;request_length_=response_length_=0;pending_=sent_=false;
      }
      seen_=now;admitted_=data[12]==0;return true;
    }
    if(data[3]!=SD_RESPONSE || !pending_ ||
       sd_u32(data+4)!=sd_u32(request_+4) ||
       sd_u32(data+8)!=sd_u32(request_+8) || data[12]!=request_[12])return false;
    std::memcpy(response_,data,n);response_length_=n;pending_=false;seen_=now;
    return true;
  }
 private:
  std::uint8_t request_[SD_MAX_RECORD]{},response_[SD_MAX_RECORD]{};
  unsigned request_length_{},response_length_{};
  std::uint32_t boot_{},seen_{},sent_at_{};
  bool admitted_{},pending_{},sent_{};
};
}
