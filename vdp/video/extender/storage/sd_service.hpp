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
  unsigned protocol() const { return protocol_; }
  // REMOTE-009: the P4 worker owns requests independently of HTTP progress.
  // A generation token fences stale workers after transport/boot loss.
  unsigned claim(std::uint32_t now) {
    if(owner_ || pending_ || !online(now) || protocol_!=SD_FAST_VERSION || next_owner_==UINT32_MAX)return 0;
    return owner_=++next_owner_;
  }
  bool owns(unsigned token) const { return token && token==owner_; }
  void release(unsigned token) {
    if(owns(token)) {
      owner_=0;bulkHeld_=false;
      // Stop queued transmission/retries when the worker leaves. Bytes already
      // handed to UART may still complete; the job must retain uncertainty.
      if(pending_){pending_=sent_=false;request_length_=response_length_=0;}
    }
  }
  unsigned postOwned(unsigned token,const std::uint8_t *data,unsigned n,
                     std::uint8_t *out,unsigned &out_length,std::uint32_t now) {
    if(!owns(token)){out_length=0;return 503;}
    return postRecord(data,n,out,out_length,now);
  }
  void transportLost() {
    owner_=0;bulkHeld_=false;admitted_=pending_=sent_=false;request_length_=response_length_=0;
    boot_=seen_=sent_at_=0;
    protocol_=0;
  }
  unsigned post(const std::uint8_t *data,unsigned n,std::uint8_t *out,
                unsigned &out_length,std::uint32_t now) {
    if(owner_){out_length=0;return 409;}
    return postRecord(data,n,out,out_length,now);
  }
 private:
  unsigned postRecord(const std::uint8_t *data,unsigned n,std::uint8_t *out,
                      unsigned &out_length,std::uint32_t now) {
    out_length=0;
    if(n>=SD_HEADER && online(now) && data[2]!=protocol_)return 400;
    if(!sd_valid(data,n) || data[3]!=SD_REQUEST || data[13] || !sd_u32(data+8))return 400;
    if(request_length_ && sd_u32(data+4)==sd_u32(request_+4) &&
       sd_u32(data+8)==sd_u32(request_+8)) {
      if(n!=request_length_ || std::memcmp(data,request_,n))return 409;
      if(response_length_) {
        std::memcpy(out,response_,response_length_);out_length=response_length_;return 200;
      }
      return online(now) || (bulkHeld_ && now-bulkAt_<600000U)?202:503;
    }
    if(!online(now))return 503;
    if(pending_)return 409;
    std::memcpy(request_,data,n);request_length_=n;response_length_=0;
    pending_=true;sent_=false;bulkHeld_=false;return 202;
  }
 public:
  // The parser/keyboard owner polls this only at packet boundaries and after keys.
  unsigned take(std::uint8_t *out,std::uint32_t now) {
    if(!pending_ || !online(now) || (sent_ &&
        (request_[12]==SD_PARALLEL_WRITE || now-sent_at_<400)))return 0;
    std::memcpy(out,request_,request_length_);sent_=true;sent_at_=now;
    return request_length_;
  }
  // Sole console owner, only after actual EMOS release/admission. Presence
  // cannot travel on parked UART. Bind the exception to this exact sent request;
  // never manufacture a heartbeat or let ordinary requests inherit this grace.
  bool admitBulk(std::uint32_t now,std::uint32_t job,std::uint32_t length) {
    if(bulkHeld_ || !online(now) || !owner_ || !pending_ || !sent_ || request_length_!=SD_HEADER+8 ||
        request_[2]!=SD_FAST_VERSION || request_[12]!=SD_PARALLEL_WRITE ||
        sd_u32(request_+20)!=job || sd_u32(request_+24)!=length)return false;
    bulkHeld_=true;bulkAt_=now;return true;
  }
  bool receive(const std::uint8_t *data,unsigned n,std::uint32_t now) {
    if(n>=SD_HEADER && data[3]!=SD_PRESENCE && admitted_ && data[2]!=protocol_)return false;
    if(!sd_valid(data,n))return false;
    if(data[3]==SD_PRESENCE) {
      if(sd_u16(data+14) || data[13] || data[12]>1)return false;
      auto id=sd_u32(data+4);
      if(id!=boot_ || data[2]!=protocol_) {
        owner_=0;bulkHeld_=false;boot_=id;request_length_=response_length_=0;pending_=sent_=false;
      }
      // Retain a completed EXIT reply for the original HTTP client to collect.
      if(data[12]){owner_=0;bulkHeld_=false;pending_=sent_=false;}
      protocol_=data[2];
      seen_=now;admitted_=data[12]==0;return true;
    }
    if(data[3]!=SD_RESPONSE || !pending_ || data[2]!=request_[2] ||
       sd_u32(data+4)!=sd_u32(request_+4) ||
       sd_u32(data+8)!=sd_u32(request_+8) || data[12]!=request_[12])return false;
    std::memcpy(response_,data,n);response_length_=n;pending_=false;bulkHeld_=false;seen_=now;
    return true;
  }
 private:
  std::uint8_t request_[SD_MAX_RECORD]{},response_[SD_MAX_RECORD]{};
  unsigned request_length_{},response_length_{};
  std::uint32_t boot_{},seen_{},sent_at_{};
  bool admitted_{},pending_{},sent_{},bulkHeld_{};
  std::uint32_t bulkAt_{};
  unsigned protocol_{};
  unsigned owner_{},next_owner_{};
};
}
