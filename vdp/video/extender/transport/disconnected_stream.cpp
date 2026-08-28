#include "extender/transport/disconnected_stream.hpp"

namespace agon::extender::transport {

int DisconnectedStream::available() { return 0; }

int DisconnectedStream::read() { return -1; }

int DisconnectedStream::peek() { return -1; }

void DisconnectedStream::flush() {}

std::size_t DisconnectedStream::write(std::uint8_t) {
  discarded_bytes_.fetch_add(1, std::memory_order_relaxed);
  return 1;
}

std::size_t DisconnectedStream::write(std::uint8_t const *,
                                      std::size_t size) {
  discarded_bytes_.fetch_add(size, std::memory_order_relaxed);
  return size;
}

std::uint64_t DisconnectedStream::discardedBytes() const noexcept {
  return discarded_bytes_.load(std::memory_order_relaxed);
}

}  // namespace agon::extender::transport
