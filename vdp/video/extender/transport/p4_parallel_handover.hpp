// PORT-008 F02c1: private ownership sequencer; physical boot/GPIO still unbound.
// One task owns this object and its adapter. Completed bits describe actual
// completed operations; clear stale bits before each new operation. No waits,
// wire decoder, autonomous request or operating-mode authority here.
#pragma once
#include <cstdint>
#include "control_crc.h"
#include "parallel_wire.h"
#include "parallel_session.h"

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
  // Private candidate only. Trusted session[4]+last sequence[2] belongs to
  // the coordinator; no offer may establish it. Caller fences the serializer
  // before this call and drains the complete ACK before claiming quiet.
  bool admit(std::uint8_t mode, std::uint8_t *session,
             const std::uint8_t *offer, std::uint8_t *ack) noexcept;
  // Control-owner binding: release recovery must already have reached UART.
  // This mode argument names the requested capability, before formal mode
  // commitment. sessionAdmit below still requires committed ExExt.
  bool sessionRequest(std::uint8_t mode, t_parallelSession &session,
                      const std::uint8_t *request, const std::uint8_t *nonce,
                      std::uint8_t *reply) noexcept;
  bool sessionAdmit(std::uint8_t mode, t_parallelSession &session,
                    const std::uint8_t *offer, std::uint8_t *ack) noexcept;
  void sessionCancel(t_parallelSession &session) noexcept;
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
