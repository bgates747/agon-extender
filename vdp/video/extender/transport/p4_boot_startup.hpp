// PORT-008 private startup composition, not a qualified ExExt transport.
// Sole installing UART task; no concurrent serializer or PARLIO owner.
// A deadline repeats physical release. It never authorizes UART restoration.
#pragma once
#include "p4_boot_release.hpp"
namespace agon::extender::transport {
class P4BootStartup final {
 public:
  P4BootStartup(const std::array<int,8> &data,int ready,int clock,int valid,int core)
      : pads_(data,ready,clock,valid,core) {}
  bool begin(std::uint32_t now) noexcept {
    restored_=live_=false;phaseAt_=now;
    started_=pads_.begin(handover_);return started_;
  }
  template<class Restore> bool poll(std::uint32_t now,Restore restoreUart) noexcept {
    if(live_)return true;
    if(!started_){begin(now);return false;}
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
  P4ParallelHandover handover_;
  std::uint32_t phaseAt_{};
  bool started_{},restored_{},live_{};
};
}
