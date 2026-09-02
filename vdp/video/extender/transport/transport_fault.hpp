// Shared fail-closed status for Extender VDP transport components.
//
// The retained VDU parser does not propagate every Stream write result.  The
// transport therefore publishes the first failure independently of the byte
// API.  All producers use release/acquire synchronization; a target binding
// must not replace this contract with a volatile callback field.
#pragma once

#include <atomic>
#include <cstdint>

namespace agon::extender::transport {

enum class TransportFault : std::uint16_t {
  kNone = 0,
  kInvalidConfiguration,
  kEpochNotAuthorized,
  kEpochLeaseLost,
  kStaleBufferedInput,
  kReadyRelease,
  kForwardBanksRelease,
  kReturnBankRelease,
  kSharedUartDisable,
  kParallelPadsConfigure,
  kIngressAcquire,
  kIngressEnable,
  kParallelForwardEnable,
  kReceiveArm,
  kReadyAssert,
  kReceiveTimeout,
  kReceiveOverflow,
  kReceiveBackend,
  kInvalidRecordLength,
  kQueueInvariant,
  kReceiveCancel,
  kIngressDisable,
  kIngressRelease,
  kParallelPadsRelease,
  kOutputShortWrite,
  kOutputFlush,
  kOutputDuplexControl,
};

class TransportFaultLatch final {
 public:
  bool latch(TransportFault fault) noexcept {
    if (fault == TransportFault::kNone) return false;
    std::uint32_t expected = static_cast<std::uint32_t>(TransportFault::kNone);
    return value_.compare_exchange_strong(
        expected, static_cast<std::uint32_t>(fault),
        std::memory_order_release, std::memory_order_relaxed);
  }

  TransportFault fault() const noexcept {
    return static_cast<TransportFault>(value_.load(std::memory_order_acquire));
  }

  bool healthy() const noexcept { return fault() == TransportFault::kNone; }

  // The lifecycle owner may clear the latch only after every transport actor
  // is stopped.  The latch intentionally cannot infer that quiescent state.
  void clear() noexcept {
    value_.store(static_cast<std::uint32_t>(TransportFault::kNone),
                 std::memory_order_release);
  }

 private:
  std::atomic<std::uint32_t> value_{
      static_cast<std::uint32_t>(TransportFault::kNone)};
};

// Cross-context cancellation edge used by independently executing transport
// actors.  In particular, the retained parser can discover an output failure
// while the ingress owner is blocked in a receive wait.  Publishing the fault
// latch alone is insufficient: the parser must also wake/cancel that receive
// through the data-plane owner so READY_N is released promptly.
class TransportCancellation {
 public:
  virtual ~TransportCancellation() = default;
  virtual void requestCancel() noexcept = 0;
};

}  // namespace agon::extender::transport
