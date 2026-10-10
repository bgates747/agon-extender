// Author-requested data-only comparison endpoint, never a production service.
// No PCNT, phase logging, timing instrumentation or pattern generation. Retain
// one successfully received block and echo it on the next same-length read.
// EMOS remains sole admission/handshake owner; the MOSlet compares every byte.
// PORT-008 DATA-SNAPSHOT-R01: a bounded post-receipt fingerprint/byte snapshot
// distinguishes retained RX corruption from TX output corruption. Publication
// follows matched completion/UART restore; no logging or inspection in DMA/ISR.
#pragma once
#include <array>
#include "parallel_control.hpp"
namespace agon::extender::transport {
class P4ParallelDataCheck final {
 public:
  struct Snapshot {
    std::size_t length{};
    std::uint8_t direction{},count{};
    std::uint32_t fnv{2166136261u};
    std::array<std::uint8_t,16> first{},last{};
  };
  explicit P4ParallelDataCheck(ParallelControl &owner):owner_(owner) {}
  bool begin() { return owner_.provide(bytes_.data()+1,4096); }
  bool acceptedOffer() {
    const auto *d=owner_.descriptor();
    if(waiting_ || !d)return false;
    const size_t n=d[10]|(size_t(d[11])<<8);
    if(!n || n>4096 || d[12]>1 || (d[12] && retained_!=n))return false;
    if(!d[12])retained_=0;
    bytes_[0]=0xA5;bytes_[n+1]=0x5A;
    waiting_=true;return true;
  }
  bool retire() {
    if(!waiting_)return true;
    uint8_t *p{},direction{};size_t n{};
    if(!owner_.takeCompleted(p,n,direction))return true;
    waiting_=false;
    if(p!=bytes_.data()+1 || !n || n>4096 ||
        bytes_[0]!=0xA5 || bytes_[n+1]!=0x5A)return false;
    snapshot_={};snapshot_.length=n;snapshot_.direction=direction;
    snapshot_.count=std::uint8_t(n<16?n:16);
    for(size_t i=0;i<n;++i)snapshot_.fnv=(snapshot_.fnv^p[i])*16777619u;
    for(size_t i=0;i<snapshot_.count;++i) {
      snapshot_.first[i]=p[i];snapshot_.last[i]=p[n-snapshot_.count+i];
    }
    snapshotReady_=true;
    retained_=direction?0:n;return true;
  }
  bool takeSnapshot(Snapshot &out) {
    if(!snapshotReady_)return false;
    out=snapshot_;snapshotReady_=false;return true;
  }
  void cancel() {waiting_=false;retained_=0;snapshotReady_=false;}
 private:
  ParallelControl &owner_;
  std::array<uint8_t,4098> bytes_{};
  size_t retained_{};
  bool waiting_{};
  Snapshot snapshot_{};
  bool snapshotReady_{};
};
}
