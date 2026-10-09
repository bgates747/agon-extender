// PORT-008 F02c3 private, one-admission native leaf. No console/mode/API caller.
// Keep this owner alive until cleanup succeeds: an unsuccessful driver stop
// retains DMA storage and callback context. The real coordinator must park UART,
// retain its descriptor, and complete matched UART status before publishing data.
#pragma once
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <driver/parlio_rx.h>
#include <driver/parlio_tx.h>
#include <esp_attr.h>
#include "p4_parallel_egress.hpp"
#include "p4_parallel_handover.hpp"
namespace agon::extender::transport {
class P4NativePayload final : private ParallelTxBackend {
 public:
  enum class Result { idle, pending, complete, rejected, wrongOwner, fault, timeout, cleanupFault };
  P4NativePayload(std::array<int,8> data,int clock,int valid,int ready,int core) noexcept
      : pins_(data),clock_(clock),valid_(valid),ready_(ready),core_(core),egress_(*this) {}
  P4NativePayload(P4NativePayload const&)=delete;
  P4NativePayload& operator=(P4NativePayload const&)=delete;
  // parked is completion of the coordinator's real P4UartParking::park,
  // never an ACK, deadline, or merely a requested operation. This leaf does
  // not consume/establish admission or change the committed EMOS mode.
  // The coordinator must retain handover, this object and buffer through
  // cleanup, bind direction/length to its retained admitted offer, and withhold
  // received data until matched UART status. A failed cancel is not retirement.
  Result arm(P4ParallelHandover const& handover,bool parked,bool transmit,
      std::uint8_t* buffer,std::size_t capacity,std::size_t length,
      std::uint32_t now,std::uint32_t timeout) noexcept;
  Result poll(std::uint32_t now) noexcept;
  Result cancel() noexcept;
  Result result() const noexcept { return result_; }
 private:
  bool start(std::uint8_t const*,std::size_t) noexcept override;
  ParallelTxProgress progress() noexcept override;
  bool stop() noexcept override;
  bool releaseDataPins() noexcept override;
  bool setReadyN(bool) noexcept override;
  bool startReceive() noexcept;
  bool watchValid() noexcept;
  void discardBuffer() noexcept;
  Result finish(Result) noexcept;
  static void IRAM_ATTR validEdge(void*) noexcept;
  static bool IRAM_ATTR receiveDone(parlio_rx_unit_handle_t,parlio_rx_event_data_t const*,void*) noexcept;
  static bool IRAM_ATTR transmitDone(parlio_tx_unit_handle_t,parlio_tx_done_event_data_t const*,void*) noexcept;
  std::array<int,8> pins_;
  int clock_,valid_,ready_,core_;
  P4ParallelEgress egress_;
  P4ParallelHandover const* handover_{};
  parlio_rx_unit_handle_t rx_{};
  parlio_rx_delimiter_handle_t delimiter_{};
  parlio_tx_unit_handle_t tx_{};
  std::uint8_t *dma_{},*buffer_{};
  std::size_t length_{};
  std::uint32_t began_{},timeout_{};
  std::atomic<std::size_t> completed_{};
  std::atomic<unsigned> edges_{};
  std::atomic<bool> done_{};
  std::atomic<bool> accepting_{};
  bool enabled_{},watching_{},transmit_{};
  Result result_{Result::idle};
};
}
