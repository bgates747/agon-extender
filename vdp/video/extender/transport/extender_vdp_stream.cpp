#include "extender/transport/extender_vdp_stream.hpp"

#include <algorithm>
#include <limits>

namespace agon::extender::transport {

ExtenderVdpStream::ExtenderVdpStream(
    SpscByteQueue &input, VdpReturnChannel &output,
    TransportFaultLatch &fault_latch,
    TransportCancellation &cancellation) noexcept
    : input_(input),
      output_(output),
      fault_latch_(fault_latch),
      cancellation_(cancellation) {}

void ExtenderVdpStream::latchOutputFault(TransportFault fault) noexcept {
  // Close record admission before publishing the fault.  A record which
  // already won the single-atomic admission order is quarantined by the fault;
  // requestCancel() itself never waits for the producer.  The service task may
  // also already be waiting with READY_N asserted.
  cancellation_.requestCancel();
  fault_latch_.latch(fault);
}

int ExtenderVdpStream::available() {
  if (!fault_latch_.healthy()) return 0;
  constexpr std::size_t kMaximum =
      static_cast<std::size_t>(std::numeric_limits<int>::max());
  int const available = static_cast<int>(std::min(input_.size(), kMaximum));
  if (available > 0) read_permitted_ = true;
  return available;
}

int ExtenderVdpStream::read() {
  if (!fault_latch_.healthy() && !read_permitted_) return -1;
  // A permit covers exactly the byte which a successful available()/peek()
  // already advertised.  It does not allow a faulted parser to drain the rest
  // of the queue.
  read_permitted_ = false;
  return input_.read();
}

int ExtenderVdpStream::peek() {
  if (!fault_latch_.healthy() && !read_permitted_) return -1;
  int const value = input_.peek();
  if (value >= 0) read_permitted_ = true;
  return value;
}

void ExtenderVdpStream::flush() {
  if (fault_latch_.healthy() && !output_.flush()) {
    latchOutputFault(TransportFault::kOutputFlush);
  }
}

std::size_t ExtenderVdpStream::write(std::uint8_t byte) {
  return write(&byte, 1);
}

std::size_t ExtenderVdpStream::write(std::uint8_t const *bytes,
                                     std::size_t length) {
  if (!fault_latch_.healthy() || length == 0) return 0;
  if (bytes == nullptr) {
    latchOutputFault(TransportFault::kOutputShortWrite);
    return 0;
  }
  std::size_t const accepted = output_.write(bytes, length);
  if (accepted != length) {
    latchOutputFault(TransportFault::kOutputShortWrite);
  }
  return std::min(accepted, length);
}

bool ExtenderVdpStream::setProtocolDuplex(bool full_duplex) noexcept {
  if (!fault_latch_.healthy()) return false;
  if (output_.setProtocolDuplex(full_duplex)) return true;
  latchOutputFault(TransportFault::kOutputDuplexControl);
  return false;
}

}  // namespace agon::extender::transport
