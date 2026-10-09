// PORT-008 private startup composition, not a qualified ExExt transport.
// Sole installing UART task; no concurrent serializer or PARLIO owner.
// A deadline repeats physical release. It never authorizes UART restoration.
#pragma once
#include "p4_boot_release.hpp"
#include <freertos/FreeRTOS.h>
namespace agon::extender::transport {
class P4BootStartup final {
 public:
  P4BootStartup(P4ParallelHandover &handover,const std::array<int,8> &data,
                int ready,int clock,int valid,int core)
      : pads_(data,ready,clock,valid,core),handover_(handover),core_(core) {}
  bool begin(std::uint32_t now) noexcept {
    if(xPortGetCoreID()!=core_)return false;
    restored_=live_=blockOwned_=false;phaseAt_=now;
    started_=pads_.begin(handover_);return started_;
  }
  template<class Restore> bool poll(std::uint32_t now,Restore restoreUart) noexcept {
    return poll(now,restoreUart,[](){return true;});
  }
  template<class Restore,class Cancel>
  bool poll(std::uint32_t now,Restore restoreUart,Cancel cancelTransport) noexcept {
    if(xPortGetCoreID()!=core_ || cleanupFailed_)return false;
    // PORT-008 LC01: entry/payload/return belongs to the shared block owner.
    // Its CLOCK/VALID transitions are not reset indications. Yield without
    // touching pads or applying the boot deadline. LC02 must poll the native
    // owner and its own deadlines; yielding is never permission to run UART.
    if(handover_.phase()>P4ParallelHandover::uart) {
      blockOwned_=true;return false;
    }
    if(blockOwned_) {
      // Normal block return traverses recovery phases too. Keep yielding
      // until the block owner proves UART restored. Explicit cancellation
      // marks failed(), so it instead starts a NEW reset fence below.
      if(!handover_.failed() && handover_.phase()!=P4ParallelHandover::uart)
        return false;
      blockOwned_=false;
    }
    if(live_) {
      if(handover_.phase()==P4ParallelHandover::uart && pads_.uartLive())return true;
      // Stop this owner's parser/serializer immediately. Only a completed
      // physical fence permits queue cancellation; SDK failures retry release.
      pendingLoss_=true;begin(now);return false;
    }
    if(!started_){begin(now);return false;}
    if(pendingLoss_) {
      pendingLoss_=false;
      if(!cancelTransport())cleanupFailed_=true;
      return false;
    }
    if(std::uint32_t(now-phaseAt_)>=2000){begin(now);return false;}
    const auto before=handover_.phase();
    const auto result=pads_.poll(handover_,restored_);
    if(result==P4BootRelease::fault){begin(now);return false;}
    if(result==P4BootRelease::restore && !restored_){
      if(!restoreUart()){begin(now);return false;}
      restored_=true;
    }
    if(before!=handover_.phase())phaseAt_=now;
    if(result==P4BootRelease::live)live_=true;
    return live_;
  }
 private:
  P4BootRelease pads_;
  P4ParallelHandover &handover_; // same lifetime/owner as ParallelControl
  int core_;
  std::uint32_t phaseAt_{};
  bool started_{},restored_{},live_{};
  bool pendingLoss_{},cleanupFailed_{},blockOwned_{};
};
}
