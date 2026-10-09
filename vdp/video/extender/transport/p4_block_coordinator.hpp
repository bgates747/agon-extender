// PORT-008 LC02 private physical owner. The sole console/ISR core calls poll.
// No mode authority or buffer consumer: ParallelControl retains admission and
// the caller retains its buffer through matched completion and receipt take.
#pragma once
#include <optional>
#include "parallel_control.hpp"
#include "p4_native_payload.hpp"
#include "p4_uart_parking.hpp"
namespace agon::extender::transport {
class P4BlockCoordinator final {
 public:
  enum class Result { uart, drain, exclusive, recovery, cleanupFault };
  P4BlockCoordinator(ParallelControl &control,std::array<int,8> data,
      int clock,int valid,int ready,int tx,int rx,int rts,int cts,int core)
      : control_(control),data_(data),clock_(clock),valid_(valid),ready_(ready),
        tx_(tx),rx_(rx),rts_(rts),cts_(cts),core_(core) {
    parking_.emplace(tx,rx,rts,cts,core);
  }
  // boundary/empty are observations of this SAME owner's parser and complete
  // software serializer, including the offer ACK. Parking independently checks
  // RX ring/FIFO and physical TX shift-register idle on the ISR's core.
  Result poll(std::uint32_t now,bool boundary,bool empty) noexcept;
  // Only after boot recovery actually restored UART. A failed native cleanup
  // never permits boot's pad fence to run over a live DMA/callback owner.
  void recovered() noexcept;
 private:
  ParallelControl &control_;
  std::array<int,8> data_;
  int clock_,valid_,ready_,tx_,rx_,rts_,cts_,core_;
  std::optional<P4UartParking> parking_;
  std::optional<P4NativePayload> payload_;
  bool active_{},parked_{},released_{},restored_{},recovering_{};
  bool releasePads() noexcept;
  Result fail() noexcept;
};
}
