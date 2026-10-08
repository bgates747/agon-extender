// PORT-008 F02c2a: private native UART boundary; no live console caller yet.
#pragma once
#include <driver/uart.h>
#include <freertos/FreeRTOS.h>

namespace agon::extender::transport {
class P4UartParking final {
 public:
  enum class Result { ready, busy, fault };
  // irqCore is the core on which uart_driver_install ran. The same single
  // owner must call these leaves on that core, with a zero-sized TX ring.
  P4UartParking(int tx, int rx, int rts, int cts, int irqCore) noexcept
      : tx_(tx), rx_(rx), rts_(rts), cts_(cts), irqCore_(irqCore) {}

  // Caller has fenced every software TX producer, drained UART events, and
  // obtained EMOS's packet-boundary quiet acknowledgement. This is NOT an
  // admission mechanism or permission to interrupt arbitrary UART traffic.
  Result park(bool packetBoundary, bool peerQuiet) noexcept;
  // Caller stopped parallel DMA, released ALL eight data pads, and received
  // EMOS's pad-release acknowledgement. Never infer this from UART timeout.
  Result restore(bool dataReleased, bool peerReleased) noexcept;

 private:
  enum class State { uart, parked, failed } state_{State::uart};
  int tx_, rx_, rts_, cts_, irqCore_;
  portMUX_TYPE mux_ = portMUX_INITIALIZER_UNLOCKED;
  bool releaseOutputs() noexcept;
  void isolateInputs() noexcept;
};
} // namespace agon::extender::transport
