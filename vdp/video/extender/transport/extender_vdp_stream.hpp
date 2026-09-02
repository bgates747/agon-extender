// Composite production Stream presented to the retained VDUStreamProcessor.
//
// Input is the flattened forward-parallel queue.  Output is always delegated
// to an explicit return channel: production will bind the UART return owner,
// while qualification may bind a byte-capturing observer.  There is no
// discard-success implementation in this class.
#pragma once

#include <cstddef>
#include <cstdint>

#include <Stream.h>

#include "extender/transport/p4_parallel_data_plane.hpp"

namespace agon::extender::transport {

class VdpReturnChannel {
 public:
  virtual ~VdpReturnChannel() = default;
  virtual std::size_t write(std::uint8_t const *bytes,
                            std::size_t length) noexcept = 0;
  virtual bool flush() noexcept = 0;
  virtual bool setProtocolDuplex(bool full_duplex) noexcept = 0;
};

class ExtenderVdpStream final : public Stream {
 public:
  ExtenderVdpStream(SpscByteQueue &input, VdpReturnChannel &output,
                    TransportFaultLatch &fault_latch,
                    TransportCancellation &cancellation) noexcept;

  int available() override;
  int read() override;
  int peek() override;
  void flush() override;
  std::size_t write(std::uint8_t byte) override;
  std::size_t write(std::uint8_t const *bytes, std::size_t length) override;

  // The P4 target's retained setVDPProtocolDuplex() hook must forward here.
  // A binding with no UART owner returns false and thereby latches a fault;
  // inheriting the prototype's silent no-op is not permitted.
  bool setProtocolDuplex(bool full_duplex) noexcept;

 private:
  void latchOutputFault(TransportFault fault) noexcept;

  SpscByteQueue &input_;
  VdpReturnChannel &output_;
  TransportFaultLatch &fault_latch_;
  TransportCancellation &cancellation_;
  // The retained parser is the queue's sole consumer.  A successful
  // available()/peek() admits exactly its next read so a later fault cannot
  // turn that already-advertised byte into Stream's -1 sentinel.
  bool read_permitted_{};
};

}  // namespace agon::extender::transport
