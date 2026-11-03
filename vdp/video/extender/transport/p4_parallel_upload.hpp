// PORT-008 reverse-upload prototype. Private console-owner leaf, not an API
// for applications or network workers to park UART or acquire shared pins.
// Source staging may run on a file worker. All driver operations run on the
// console/ISR core. The coordinator retains BOTH objects until cleanup succeeds.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <driver/parlio_tx.h>
#include <driver/gpio_filter.h>
#include "p4_valid_counter.hpp"

namespace agon::extender::transport {
class P4ParallelUpload;
class P4UploadSource final {
 public:
  static constexpr std::size_t maximumBytes=32U*1024U*1024U;
  P4UploadSource()=default;
  P4UploadSource(P4UploadSource const&)=delete;
  P4UploadSource& operator=(P4UploadSource const&)=delete;
  // A caller abandoning a live DMA owner must leak rather than free its source.
  // This is an error containment rule, not successful cleanup; retain the owner.
  ~P4UploadSource() { (void)release(); }
  bool load(FILE *spool,std::size_t length) noexcept;
  bool release() noexcept;
  std::size_t size() const noexcept { return length_; }
  std::size_t allocated() const noexcept { return allocated_; }
  bool borrowed() const noexcept { return borrowed_; }
 private:
  friend class P4ParallelUpload;
  std::uint8_t *data_{};
  std::size_t length_{},allocated_{};
  bool borrowed_{};
};

class P4ParallelUpload final {
 public:
  enum class Result { idle, prepared, pending, complete, rejected, wrongOwner,
                      fault, shortPayload, timeout, cleanupFault };
  P4ParallelUpload(std::array<int,8> data,int clock,int valid,int ready,int core)
      noexcept: pins_(data),clock_(clock),valid_(valid),ready_(ready),core_(core) {}
  P4ParallelUpload(P4ParallelUpload const&)=delete;
  P4ParallelUpload& operator=(P4ParallelUpload const&)=delete;
  // Reserve DMA descriptors/source before offering capacity. This observes
  // CLOCK as an input but connects NO shared data output and asserts no READY.
  Result prepare(P4UploadSource &source) noexcept;
  // Real coordinator supplies completed UART parking + admission bound to the
  // same source length. No DMA/pad output is enabled before these checks.
  Result arm(bool parked,std::size_t admittedLength,std::uint32_t now,
             std::uint32_t timeoutMs) noexcept;
  Result poll(std::uint32_t now) noexcept;
  Result cancel() noexcept;
  Result result() const noexcept { return result_; }
  int observedClocks() const noexcept { return observedClocks_; }
  int observedValid() const noexcept { return observedValid_; }
 private:
  Result finish(Result outcome) noexcept;
  bool stop() noexcept;
  bool releasePads() noexcept;
  std::array<int,8> pins_;
  int clock_,valid_,ready_,core_;
  P4UploadSource *source_{};
  parlio_tx_unit_handle_t tx_{};
  gpio_glitch_filter_handle_t filter_{};
  std::optional<P4ValidCounter> clocks_,validEdges_;
  std::uint32_t began_{},timeout_{};
  bool enabled_{},filterEnabled_{},padsTouched_{},admitted_{},deleteFailed_{};
  Result result_{Result::idle};
  int observedClocks_{-1},observedValid_{-1};
};
}
