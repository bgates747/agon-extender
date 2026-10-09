// PORT-008 boot-only pad adapter. No live startup caller yet.
// Caller has fenced all UART/PARLIO users and uses the installing UART core.
// Normal suspension must use P4UartParking after packet/shift-register drain.
#pragma once
#include <array>
#include "p4_parallel_handover.hpp"

namespace agon::extender::transport {
class P4BootRelease final {
 public:
  enum Result { waiting, restore, live, fault };
  P4BootRelease(const std::array<int,8> &data, int ready, int clock,
                int valid, int ownerCore) noexcept
      : data_(data), ready_(ready), clock_(clock), valid_(valid), core_(ownerCore) {}
  bool begin(P4ParallelHandover &handover) noexcept;
  // uartRestored is completion of the coordinator's real, authorized restore,
  // not a timeout or a sampled high READY. No UART writer is called here.
  Result poll(P4ParallelHandover &handover, bool uartRestored) noexcept;
 private:
  std::array<int,8> data_;
  int ready_,clock_,valid_,core_;
  bool released_{},failed_{true},initial_{};
  bool releasePads() noexcept;
};
} // namespace agon::extender::transport
