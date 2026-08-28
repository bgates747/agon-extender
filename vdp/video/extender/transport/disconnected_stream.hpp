// PORT-003 Phase F disconnected Arduino Stream binding.
//
// Gate F needs the retained VDUStreamProcessor and startup lifecycle in the
// bootable image before PORT-008 supplies physical parallel ingress. This
// Stream therefore never fabricates input. Return traffic is deliberately
// discarded and counted so its absence remains inspectable and cannot be
// mistaken for a qualified reverse transport.
#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include <Stream.h>

namespace agon::extender::transport {

class DisconnectedStream final : public Stream {
 public:
  int available() override;
  int read() override;
  int peek() override;
  void flush() override;
  std::size_t write(std::uint8_t byte) override;
  std::size_t write(std::uint8_t const *buffer, std::size_t size) override;

  std::uint64_t discardedBytes() const noexcept;

 private:
  std::atomic<std::uint64_t> discarded_bytes_{};
};

}  // namespace agon::extender::transport

// The official VDP variable surface can request UART duplex changes. Gate F
// has no physical transport, so the disconnected binding owns an explicit
// no-device implementation rather than linking stock UART GPIO code.
inline void setVDPProtocolDuplex(bool) noexcept {}
