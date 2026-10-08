// PORT-008 F02 reverse-block core. No pad binding or runtime activation yet.
// The EMOS-owned coordinator must first establish UART quiescence and eZ80
// input ownership; this object alone cannot grant permission to drive Port C.
#pragma once

#include <cstddef>
#include <cstdint>

namespace agon::extender::transport {

enum class ParallelTxStatus { pending, complete, failed };
struct ParallelTxProgress {
  ParallelTxStatus status;
  std::size_t bytes;
  // Per-admission latched VALID edges, not a task's sample of the current
  // level. A complete short block may occur between two task polls.
  bool started;
  bool ended;
};

class ParallelTxBackend {
 public:
  virtual ~ParallelTxBackend() = default;
  // start may partially acquire hardware even when returning false. Data must
  // stay immutable/alive until stop succeeds. Hold the final byte after DMA
  // completion: EMOS may not yet have sampled it or released VALID_N.
  virtual bool start(std::uint8_t const *data, std::size_t length) noexcept = 0;
  virtual ParallelTxProgress progress() noexcept = 0;
  // Cleanup is idempotent, including after a partially failed start. Only
  // resources belonging to this admission may be stopped/released.
  virtual bool stop() noexcept = 0;
  // Explicitly detach/disable outputs; a PARLIO idle value is not tri-state.
  virtual bool releaseDataPins() noexcept = 0;
  virtual bool setReadyN(bool high) noexcept = 0;
};

enum class ParallelTxResult {
  idle, pending, complete, invalid, busy, backendFault, timeout, shortBlock,
  cleanupFault
};

// Single-owner task context. ISR callbacks belong inside the backend and must
// publish completion safely; no ISR may mutate this core concurrently.
class P4ParallelEgress final {
 public:
  static constexpr std::size_t maximumBlockBytes = 4096;
  explicit P4ParallelEgress(ParallelTxBackend &backend) noexcept : backend_(backend) {}
  P4ParallelEgress(P4ParallelEgress const &) = delete;
  P4ParallelEgress &operator=(P4ParallelEgress const &) = delete;

  ParallelTxResult begin(std::uint8_t const *data, std::size_t length,
                         std::uint32_t now, std::uint32_t timeoutTicks) noexcept;
  ParallelTxResult poll(std::uint32_t now) noexcept;
  // Abort never restores the UART or opens another block. The coordinator
  // still needs fresh peer admission after either endpoint faults/resets.
  ParallelTxResult abort() noexcept;
  ParallelTxResult result() const noexcept { return result_; }

 private:
  ParallelTxResult finish(ParallelTxResult result) noexcept;
  ParallelTxBackend &backend_;
  ParallelTxResult result_{ParallelTxResult::idle};
  std::size_t length_{};
  std::uint32_t started_{};
  std::uint32_t timeout_{};
};

}  // namespace agon::extender::transport
