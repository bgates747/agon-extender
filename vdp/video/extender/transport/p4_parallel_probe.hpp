// PORT-008 LC03-A fixed private storage/receipt diagnostic. Sole UART task only.
// Neither this caller nor its USB log grants mode, pin or transfer authority.
#pragma once
#include <array>
#include <cstring>
#include "parallel_control.hpp"
#include "parallel_probe_pattern.h"
namespace agon::extender::transport {
class P4ParallelProbe final {
 public:
  struct Receipt {
    std::array<uint8_t,16> descriptor{};
    size_t length{};
    uint8_t direction{},first{},last{};
    uint32_t crc{},elapsedUs{};
    bool guards{},pattern{};
  };
  explicit P4ParallelProbe(ParallelControl &owner):owner_(owner) {}
  bool begin() {
    storage_.fill(0xA5);
    return owner_.provide(storage_.data()+1,4096);
  }
  bool acceptedOffer(uint32_t nowUs) {
    const auto *d=owner_.descriptor();
    uint8_t *buffer{};size_t capacity{};
    if(waiting_ || !d || !owner_.payloadBuffer(buffer,capacity) ||
        buffer!=storage_.data()+1 || capacity!=4096)return false;
    const size_t n=d[10]|(size_t(d[11])<<8);
    if(!n || n>4096 || d[12]>1)return false;
    std::memcpy(offer_.data(),d,16);
    storage_[0]=0xA5;storage_[n+1]=0x5A;
    for(size_t i=0;i<n;++i)buffer[i]=d[12]?
        parallel_probe_pattern(i,parallel_probe_seed(d)):0xCC;
    began_=nowUs;waiting_=true;return true;
  }
  bool take(uint32_t nowUs,Receipt &result) {
    if(!waiting_)return false;
    uint8_t *buffer{},direction{};size_t n{};
    if(!owner_.takeCompleted(buffer,n,direction))return false;
    waiting_=false;
    result={};result.descriptor=offer_;result.length=n;result.direction=direction;
    result.elapsedUs=nowUs-began_;
    result.guards=n>0 && n<=4096 && buffer==storage_.data()+1 &&
        n==size_t(offer_[10]|(size_t(offer_[11])<<8)) && direction==offer_[12] &&
        storage_[0]==0xA5 && storage_[n+1]==0x5A;
    if(!result.guards)return true;
    result.first=buffer[0];result.last=buffer[n-1];result.crc=parallel_probe_crc(buffer,n);
    result.pattern=true;
    if(direction)for(size_t i=0;i<n;++i)
        if(buffer[i]!=parallel_probe_pattern(i,parallel_probe_seed(offer_.data())))
            result.pattern=false;
    // Forward expected CRC is computed independently by the MOSlet and
    // compared with this USB record by the host collector, never inferred here.
    return true;
  }
  void cancel() { waiting_=false; }
 private:
  ParallelControl &owner_;
  std::array<uint8_t,4098> storage_{};
  std::array<uint8_t,16> offer_{};
  uint32_t began_{};
  bool waiting_{};
};
}
