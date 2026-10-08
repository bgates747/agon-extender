// PORT-008 F02c1: private ownership sequencer, not bound to live UART/GPIO.
// One task owns this object and its adapter. Completed bits describe actual
// completed operations; clear stale bits before each new operation. No waits,
// wire decoder, autonomous request or operating-mode authority here.
#pragma once
#include <cstdint>

namespace agon::extender::transport {
class P4ParallelHandover final {
 public:
  enum Completed : std::uint8_t {
    validHigh=1, clockHigh=2, quiet=4, released=8, armed=16, done=32, uartUp=64
  };
  enum Action : std::uint8_t { wait, fence, release, arm, run, restore, live };
  enum Phase : std::uint8_t {
    recoveryRelease, recoveryAnnounce, recoveryClear, recoveryAck,
    recoveryUart, uart, drain, entryRelease, entryRequest, entryAck,
    entryClock, localArm, block, blockReturn
  };

  // Reset adapter FIRST disables all shared output enables. Starting from
  // reset RAM without this physical reset/input fence is not recovery.
  bool begin() noexcept;
  void cancel() noexcept;
  Action step(std::uint8_t completed) noexcept;
  Phase phase() const noexcept { return phase_; }
  bool readyN() const noexcept { return ready_; }
  bool failed() const noexcept { return failed_; }

 private:
  Phase phase_{recoveryRelease};
  bool ready_{true}, failed_{true};
};
} // namespace agon::extender::transport
