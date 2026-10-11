// Author-requested data-only comparison endpoint, never a production service.
// No PCNT, phase logging or timing instrumentation. Ordinary mode retains
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
  // PORT-008 DIRECTION-ISOLATION-R01 only: a private build selects this mode.
  // Generate TX independently of RX, and compare retained bytes after completed
  // UART restoration. This must not change native DMA/handshake behavior.
  enum class Mode { echo, independentDirections };
  static std::uint8_t pattern(std::size_t i) {
    return std::uint8_t((i*73u)^((i>>3)*29u)^(i>>8)^0x69u);
  }
  struct Snapshot {
    std::size_t length{};
    std::uint8_t direction{},count{};
    std::uint32_t fnv{2166136261u},preparedFnv{};
    std::size_t mismatches{},firstMismatch{};
    std::uint8_t actual{},expected{};
    bool independent{};
    std::array<std::uint8_t,16> first{},last{};
  };
  explicit P4ParallelDataCheck(ParallelControl &owner,Mode mode=Mode::echo):owner_(owner),mode_(mode) {}
  bool begin() { return owner_.provide(bytes_.data()+1,4096); }
  bool acceptedOffer() {
    const auto *d=owner_.descriptor();
    if(waiting_ || !d)return false;
    const size_t n=d[10]|(size_t(d[11])<<8);
    if(!n || n>4096 || d[12]>1 || (d[12] && mode_==Mode::echo && retained_!=n))return false;
    if(!d[12])retained_=0;
    bytes_[0]=0xA5;bytes_[n+1]=0x5A;
    preparedFnv_=0;
    if(d[12] && mode_==Mode::independentDirections) {
      preparedFnv_=2166136261u;
      for(size_t i=0;i<n;++i) {
        bytes_[i+1]=pattern(i);
        preparedFnv_=(preparedFnv_^bytes_[i+1])*16777619u;
      }
    }
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
    snapshot_.independent=mode_==Mode::independentDirections;
    snapshot_.preparedFnv=preparedFnv_;snapshot_.firstMismatch=n;
    for(size_t i=0;i<n;++i) {
      snapshot_.fnv=(snapshot_.fnv^p[i])*16777619u;
      if(snapshot_.independent && p[i]!=pattern(i)) {
        if(!snapshot_.mismatches) {
          snapshot_.firstMismatch=i;snapshot_.actual=p[i];snapshot_.expected=pattern(i);
        }
        ++snapshot_.mismatches;
      }
    }
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
  const Mode mode_;
  std::uint32_t preparedFnv_{};
  std::array<uint8_t,4098> bytes_{};
  size_t retained_{};
  bool waiting_{};
  Snapshot snapshot_{};
  bool snapshotReady_{};
};
}
