// Exercise the network consumer against the HDMI-only pool, and compare the
// former producer's allocation contract under the same snapshot settings.
#include "extender/display/hdmi_timing.hpp"
#include "extender/web/browser_video_provider.hpp"

#include <cassert>
#include <cstdio>
#include <cstdlib>

using namespace agon::extender;

int main() {
  static_assert(display::selectHdmiTiming(320, 240).width == 848);
  static_assert(display::selectHdmiTiming(320, 200).width == 684);
  static_assert(display::selectHdmiTiming(512, 384).width == 684);
  static_assert(display::selectHdmiTiming(640, 240).width == 848);

  std::size_t reserved = 0;
  display::Allocator allocator{
      &reserved,
      [](void *context, std::size_t bytes) -> void * {
        *static_cast<std::size_t *>(context) += bytes;
        return std::malloc(bytes);
      },
      [](void *, void *pixels) { std::free(pixels); }};
  {
    display::PresentationSnapshotPool previous(
        allocator, display::SnapshotPixelFormat::RGB222, 0, true, true);
    assert(previous.enabled() && reserved == 3U * 1024 * 768);
  }

  display::PresentationSnapshotPool hdmiOnly;
  web::BrowserVideoProvider provider(hdmiOnly);
  network::OpaqueMessageLease lease;
  display::MutableSnapshotView view{};
  assert(!hdmiOnly.enabled());
  assert(hdmiOnly.tryBegin(320, 240, 0, view) ==
         display::SnapshotBeginResult::Disabled);
  assert(!view.pixels && !view.packed_pixels);
  assert(provider.tryAcquireAfter(0, lease) ==
         network::OpaqueAcquireResult::Unavailable);
  assert(!lease.valid());
  const auto metrics = hdmiOnly.metrics();
  assert(!metrics.enabled && !metrics.allocation_failures && !metrics.publications);
  assert(!provider.metrics().invalid_snapshot && !provider.metrics().acquired);
  std::printf("PASS: HDMI carrier selection, disabled provider/status; "
              "browser pixel backing %zu -> 0 bytes\n", reserved);
}
