#include "extender/display/hdmi_geometry.hpp"
#include "extender/display/hdmi_buffer_ownership.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#if defined(AGON_EXTENDER_HDMI_848X480) || defined(AGON_EXTENDER_HDMI_512X384) || defined(AGON_EXTENDER_HDMI_684X384)
#include "extender/display/rolling/strip_config.h"
#endif

using namespace agon::extender::display;

int main() {
  // Repeated mode0 -> title8 -> game20 -> mode0 transitions must select
  // carriers by logical geometry, never by colour depth or buffer flag.
  struct Mode { int w,h,ow,oh,x,y; };
  for(int pass=0;pass<5;++pass) for(const auto mode: {
      Mode{640,480,848,480,104,0}, Mode{320,240,684,384,182,72},
      Mode{512,384,684,384,86,0}, Mode{640,480,848,480,104,0},
      Mode{640,240,684,384,22,72}, Mode{512,192,684,384,86,96}}) {
    const auto carrier=selectHdmiTiming(mode.w,mode.h);
    assert(carrier.width==mode.ow && carrier.height==mode.oh);
    const auto image=centeredHdmiGeometry(mode.w,mode.h,carrier.width,carrier.height);
    assert(image.source_x==0 && image.source_y==0);
    assert(image.width==mode.w && image.height==mode.h);
    assert(image.destination_x==mode.x && image.destination_y==mode.y);
    assert(carrier.hTotal()==1104 && carrier.vTotal()==517);
  }
  assert(selectHdmiTiming(800,600).width==848); // unqualified crop fallback
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
  assert(small.valid());
#if defined(AGON_EXTENDER_HDMI_848X480) || defined(AGON_EXTENDER_HDMI_512X384) || defined(AGON_EXTENDER_HDMI_684X384)
  static_assert(STRIP_WIDTH == kHdmiWidth && STRIP_HEIGHT == kHdmiHeight);
  static_assert(STRIP_ROWS == 32 && STRIP_BLOCKS <= 15 && STRIP_BLOCKS % STRIP_SLOTS == 0);
  static_assert((STRIP_WIDTH * STRIP_ROWS * 3) % 64 == 0);
#endif
#ifdef AGON_EXTENDER_HDMI_512X384
  assert(small.source_x == 64 && small.source_y == 48);
  assert(small.destination_x == 0 && small.destination_y == 0);
  assert(small.width == 512 && small.height == 384);
  const auto game = centeredHdmiGeometry(512,384);
  assert(game.source_x == 0 && game.source_y == 0);
  assert(game.destination_x == 0 && game.destination_y == 0);
  assert(game.width == 512 && game.height == 384 && kHdmiStride == 1536);
  const auto low = centeredHdmiGeometry(320,240);
  assert(low.destination_x == 96 && low.destination_y == 72);
  assert(low.source_x == 0 && low.source_y == 0 && low.width == 320 && low.height == 240);
  assert(kHdmiTiming.hTotal() == 1104 && kHdmiTiming.vTotal() == 517 && kHdmiTiming.vic == 0);
  assert(kHdmiTiming.refreshHz() > 60.06 && kHdmiTiming.refreshHz() < 60.08);
#elif defined(AGON_EXTENDER_HDMI_684X384)
  assert(small.source_x == 0 && small.source_y == 48);
  assert(small.destination_x == 22 && small.destination_y == 0);
  assert(small.width == 640 && small.height == 384);
  const auto game = centeredHdmiGeometry(512,384);
  assert(game.destination_x == 86 && game.destination_y == 0);
  assert(game.source_x == 0 && game.source_y == 0 && kHdmiStride == 2052);
  assert(game.width == 512 && game.height == 384);
  const auto low = centeredHdmiGeometry(320,240);
  assert(low.destination_x == 182 && low.destination_y == 72);
  assert(kHdmiTiming.h_front == 196 && kHdmiTiming.v_front == 102);
  assert(kHdmiTiming.hTotal() == 1104 && kHdmiTiming.vTotal() == 517);
  assert(kHdmiTiming.refreshHz() > 60.06 && kHdmiTiming.refreshHz() < 60.08);
#elif defined(AGON_EXTENDER_HDMI_848X480) || defined(AGON_EXTENDER_HDMI_AUTO)
  assert(small.source_x == 0 && small.source_y == 0);
  assert(small.destination_x == 104 && small.destination_y == 0);
  const auto game = centeredHdmiGeometry(512,384);
  assert(game.destination_x==168 && game.destination_y==48 && game.width==512 && game.height==384);
  assert(game.source_x==0 && game.source_y==0 && kHdmiStride==2544);
  assert(kHdmiTiming.hTotal()==1104 && kHdmiTiming.vTotal()==517 && kHdmiTiming.vic==0);
  assert(kHdmiTiming.refreshHz()>60.06 && kHdmiTiming.refreshHz()<60.08);
  const auto clipped = centeredHdmiGeometry(1024,768);
  assert(clipped.source_x==88 && clipped.source_y==144 && clipped.width==848 && clipped.height==480);
#else
  assert(small.source_x == 0 && small.source_y == 0);
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
#endif
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
