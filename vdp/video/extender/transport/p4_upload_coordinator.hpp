// Private file-worker/console handoff for the PORT-008 upload candidate.
// The persistent mailbox retains source lifetime even if a worker times out.
#pragma once
#include <atomic>
#include <optional>
#include "p4_parallel_upload.hpp"
#include "p4_parallel_handover.hpp"
#include "p4_uart_parking.hpp"

namespace agon::extender::transport {
class P4UploadMailbox final {
 public:
  enum State : unsigned { free, loading, queued, prepared, offered, active,
                          returned, refused, cleanupFault };
  // Worker calls load/offer/retire; console calls every driver/pin operation.
  bool load(FILE *file,std::size_t length,std::uint32_t id) noexcept {
    unsigned expected=free;
    if(!state.compare_exchange_strong(expected,loading))return false;
    job=id;cancel.store(false);outcome.store(unsigned(P4ParallelUpload::Result::idle));
    if(!source.load(file,length)){state.store(free,std::memory_order_release);return false;}
    state.store(queued,std::memory_order_release);return true;
  }
  bool offer() noexcept {
    unsigned expected=prepared;
    return state.compare_exchange_strong(expected,offered);
  }
  void retire() noexcept { cancel.store(true,std::memory_order_release); }
  unsigned status() const noexcept { return state.load(std::memory_order_acquire); }
  std::atomic<unsigned> state{free},outcome{unsigned(P4ParallelUpload::Result::idle)};
  std::atomic<bool> cancel{false};
  P4UploadSource source;
  std::uint32_t job{};
};
inline P4UploadMailbox uploadMailbox;

class P4UploadCoordinator final {
 public:
  enum class Result { uart, drain, exclusive, recovery, cleanupFault };
  using Admission=bool(*)(std::uint32_t,std::uint32_t,std::uint32_t);
  P4UploadCoordinator(P4ParallelHandover &handover,std::array<int,8> data,
      int clock,int valid,int ready,int tx,int rx,int rts,int cts,int core,Admission admission)
      : handover_(handover),data_(data),clock_(clock),valid_(valid),ready_(ready),
        tx_(tx),rx_(rx),rts_(rts),cts_(cts),core_(core),admit_(admission) {}
  Result poll(std::uint32_t now,bool boundary,bool empty) noexcept;
  bool ownsPhysical() const noexcept { return physical_; }
 private:
  Result fence() noexcept;
  bool releasePads() noexcept;
  P4ParallelHandover &handover_;
  std::array<int,8> data_;
  int clock_,valid_,ready_,tx_,rx_,rts_,cts_,core_;
  Admission admit_;
  std::optional<P4ParallelUpload> payload_;
  std::optional<P4UartParking> parking_;
  std::uint32_t phaseAt_{};
  P4ParallelHandover::Phase phase_{P4ParallelHandover::uart};
  bool physical_{},parked_{},released_{},restored_{},fenced_{};
};
}
