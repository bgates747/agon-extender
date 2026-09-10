// RGB222 publication/EVF1 regression. No device access; exact all-colour
// expectations are independent of the production packer and browser shader.
#include <array>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include "extender/web/browser_video_provider.hpp"

namespace d = agon::extender::display;
namespace n = agon::extender::network;
namespace w = agon::extender::web;
void *allocate(void *, std::size_t n) { return std::malloc(n); }
void deallocate(void *, void *p) { std::free(p); }

int main() {
  d::PresentationSnapshotPool pool({nullptr, allocate, deallocate},
                                  d::SnapshotPixelFormat::RGB222);
  w::BrowserVideoProvider provider(pool);
  n::OpaqueMessageLease held;
  std::array<std::uint8_t, 64> original{};
  // Publish at every 60 Hz boundary while one old network frame is leased.
  // Fixed storage must collapse intermediate frames without mutating the lease.
  for (unsigned generation = 1; generation <= 120; ++generation) {
    d::MutableSnapshotView write{};
    assert(pool.tryBegin(8, 8, generation * 16667ULL, write) ==
           d::SnapshotBeginResult::Ok);
    for (unsigned i = 0; i < 64; ++i) {
      unsigned colour = (i + generation - 1) % 64;
      write.pixels[i] = {std::uint8_t((colour % 4) * 85),
                        std::uint8_t(((colour / 4) % 4) * 85),
                        std::uint8_t((colour / 16) * 85)};
    }
    assert(pool.finish(d::CompositionResult::Ok, 16667) ==
           d::SnapshotFinishResult::Published);
    if (generation == 1) {
      assert(provider.tryAcquireAfter(0, held) == n::OpaqueAcquireResult::Acquired);
      auto message = held.view();
      assert(message.total_bytes == 96 && message.segment_count == 2);
      const std::array<std::uint8_t, 32> header = {
          'E','V','F','1',1,32,2,3,1,0,0,0,8,0,8,0,8,0,0,0,
          64,0,0,0,0x1b,0x41,0,0,0,0,0,0};
      for (unsigned i = 0; i < header.size(); ++i)
        assert(message.segments[0].data[i] == header[i]);
      for (unsigned i = 0; i < 64; ++i) {
        original[i] = message.segments[1].data[i];
        assert(original[i] == i);
      }
    } else {
      for (unsigned i = 0; i < 64; ++i)
        assert(held.view().segments[1].data[i] == original[i]);
    }
  }
  assert(pool.metrics().cadence_skips == 0 && pool.metrics().publications == 120);
  held.release(n::OpaqueReleaseDisposition::Sent);
  n::OpaqueMessageLease latest;
  assert(provider.tryAcquireAfter(1, latest) == n::OpaqueAcquireResult::Acquired);
  assert(latest.view().token == 120);
  for (unsigned i = 0; i < 64; ++i)
    assert(latest.view().segments[1].data[i] == (i + 119) % 64);
  latest.release(n::OpaqueReleaseDisposition::Sent);
  assert(provider.tryAcquireAfter(120, latest) == n::OpaqueAcquireResult::NoNewMessage);
  // Production demand path: idle startup does no expensive composition.
  d::PresentationSnapshotPool demand({nullptr, allocate, deallocate},
                                    d::SnapshotPixelFormat::RGB222, 0, true);
  w::BrowserVideoProvider requested(demand);
  d::MutableSnapshotView destination{};
  for (unsigned tick = 1; tick <= 120; ++tick)
    assert(demand.tryBegin(8, 8, tick * 16667ULL, destination) ==
           d::SnapshotBeginResult::NotRequested);
  for (unsigned tick = 121; tick <= 240; ++tick) {
    n::OpaqueMessageLease frame;
    const auto previous = tick - 121;
    assert(requested.tryAcquireAfter(previous, frame) == n::OpaqueAcquireResult::NoNewMessage);
    assert(demand.tryBegin(8, 8, tick * 16667ULL, destination) == d::SnapshotBeginResult::Ok);
    for (unsigned i = 0; i < 64; ++i) destination.pixels[i] = {255, 0, 0};
    assert(demand.finish(d::CompositionResult::Ok, 16667) == d::SnapshotFinishResult::Published);
    assert(requested.tryAcquireAfter(previous, frame) == n::OpaqueAcquireResult::Acquired);
    assert(frame.view().token == previous + 1);
    assert(demand.tryBegin(8, 8, tick * 16667ULL + 1, destination) ==
           d::SnapshotBeginResult::NotRequested);
    frame.release(n::OpaqueReleaseDisposition::Sent);
  }
  assert(demand.metrics().publications == 120 && demand.metrics().cadence_skips == 0);
  std::cout << "PASS: RGB222 all colours, exact EVF1 bytes, 60 Hz publication with bounded demand, immutable slow-client lease and latest selection\n";
}
