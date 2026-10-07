#include "extender/display/hdmi_geometry.hpp"
#include "extender/display/hdmi_buffer_ownership.hpp"
#include <array>
#include <cassert>
#include <cstdint>

using namespace agon::extender::display;

int main() {
  HdmiBufferOwnership buffers;
  assert(!buffers.pending() && buffers.writable(false) == 0 && buffers.writable(true) == 1);
  // Ordinary path: selection and task metadata precede the DMA completion.
  buffers.submitted(1);
  assert(buffers.pending());
  buffers.frameComplete();
  assert(!buffers.pending() && buffers.writable(false) == 1 && buffers.writable(true) == 0);
  // ISR occurs after driver selection but before task metadata publication.
  // The old software front is retained until the following completion; the
  // output task remains in its publication call and cannot begin another write.
  buffers.frameComplete();
  assert(buffers.writable(false) == 1);
  buffers.submitted(0);
  assert(buffers.pending());
  buffers.frameComplete();
  assert(!buffers.pending() && buffers.writable(false) == 0 && buffers.writable(true) == 1);
  // Unrelated repeated scanout never swaps software ownership. A mode change
  // can wait for pending completion then use the confirmed single-buffer front.
  buffers.frameComplete();
  assert(buffers.writable(false) == 0);
  buffers.submitted(1);
  buffers.frameComplete();
  assert(buffers.writable(false) == 1);

  const auto small = centeredHdmiGeometry(640, 480);
  assert(small.valid() && small.source_x == 0 && small.source_y == 0);
  assert(small.destination_x == 320 && small.destination_y == 120);
  assert(small.width == 640 && small.height == 480);
  const auto tall = centeredHdmiGeometry(1024, 768);
  assert(tall.source_y == 24 && tall.height == 720 && tall.destination_y == 0);
  assert(tall.destination_x == 128 && tall.source_x == 0);
  const auto oversized = centeredHdmiGeometry(1401, 801);
  assert(oversized.source_x == 60 && oversized.source_y == 40);
  assert(oversized.width == 1280 && oversized.height == 720);
  const auto odd = centeredHdmiGeometry(639, 479);
  assert(odd.destination_x == 320 && odd.destination_y == 120);
  assert(kHdmiWidth - odd.destination_x - odd.width == 321);
  assert(kHdmiHeight - odd.destination_y - odd.height == 121);
  assert(!centeredHdmiGeometry(0, 480).valid());
  assert(!centeredHdmiGeometry(640, -1).valid());

  // Check every RGB222 value and both nonzero sync bits independently of the
  // conversion loop. Exercise x^2 lane order and BGR hardware byte ordering.
  alignas(8) std::array<std::uint8_t, 64> signal{};
  for (unsigned x = 0; x < signal.size(); ++x) signal[x ^ 2] = x | 0xc0;
  std::array<std::uint8_t, 64 * 3 + 2> output{};
  output.front() = output.back() = 0xa5;
  expandSignalRowToHdmi(signal.data(), output.data() + 1, 0, 64);
  for (unsigned x = 0; x < 64; ++x) {
    assert(output[1 + x * 3] == ((x >> 4) & 3) * 85);
    assert(output[2 + x * 3] == ((x >> 2) & 3) * 85);
    assert(output[3 + x * 3] == (x & 3) * 85);
  }
  assert(output.front() == 0xa5 && output.back() == 0xa5);
  std::array<std::uint8_t, 7 * 3> cropped{};
  expandSignalRowToHdmi(signal.data(), cropped.data(), 5, 7);
  for (unsigned x = 0; x < 7; ++x)
    assert(cropped[x * 3 + 2] == ((x + 5) & 3) * 85);
}
