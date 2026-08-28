// PORT-003 Phase F host checks for the immutable snapshot pool. Expected state
// transitions come from fixtures/snapshot-pool-model.yaml, not production
// internals.
#include <cstdint>
#include <cstdlib>
#include <iostream>

#include "extender/display/presentation_snapshot_pool.hpp"

namespace display = agon::extender::display;

namespace {

struct Tracking {
  int calls{};
  int live{};
  int fail_on{};
};

void *allocate(void *context, std::size_t size) {
  auto &tracking = *static_cast<Tracking *>(context);
  ++tracking.calls;
  if (tracking.fail_on != 0 && tracking.calls == tracking.fail_on) return nullptr;
  if (size != display::kPresentationSnapshotBytesPerSlot) return nullptr;
  void *result = std::malloc(size);
  if (result != nullptr) ++tracking.live;
  return result;
}

void deallocate(void *context, void *allocation) {
  auto &tracking = *static_cast<Tracking *>(context);
  if (allocation != nullptr) {
    --tracking.live;
    std::free(allocation);
  }
}

display::Allocator allocator(Tracking &tracking) {
  return {&tracking, allocate, deallocate};
}

void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

void checkAllocationFailures() {
  for (int failure = 1; failure <= 3; ++failure) {
    Tracking tracking{};
    tracking.fail_on = failure;
    {
      display::PresentationSnapshotPool pool(allocator(tracking));
      require(!pool.enabled(), "failed allocation disables pool");
      require(pool.metrics().allocation_failures == 1,
              "failed allocation is counted once");
      require(tracking.live == 0, "partial allocation is released");
    }
    require(tracking.live == 0, "failed pool teardown is empty");
  }
}

void checkPublicationAndLease() {
  Tracking tracking{};
  {
    display::PresentationSnapshotPool pool(allocator(tracking));
    require(pool.enabled(), "three-slot pool enabled");
    require(tracking.calls == 3 && tracking.live == 3,
            "exactly three fixed slots allocated");

    display::MutableSnapshotView write{};
    require(pool.tryBegin(320, 240, 100, write) ==
                display::SnapshotBeginResult::Ok,
            "first production begins immediately");
    require(write.pixel_capacity == 1024 * 768,
            "producer receives maximum slot capacity");
    write.pixels[0] = {1, 2, 3};
    require(pool.tryBegin(320, 240, 100, write) ==
                display::SnapshotBeginResult::ProducerBusy,
            "second producer is refused");
    require(pool.finish(display::CompositionResult::Ok, 16667) ==
                display::SnapshotFinishResult::Published,
            "first production publishes");

    display::PresentationSnapshotLease first{};
    require(pool.tryAcquireLatest(0, first), "first generation leases");
    require(first.valid() && first.view().generation == 1,
            "first lease generation");
    require(first.view().width == 320 && first.view().height == 240 &&
                first.view().stride_bytes == 960 &&
                first.view().payload_bytes == 230400,
            "first lease metadata");
    require(first.view().data[0] == 1 && first.view().data[1] == 2 &&
                first.view().data[2] == 3,
            "lease bytes are the completed producer bytes");

    require(pool.tryBegin(320, 240, 200099, write) ==
                display::SnapshotBeginResult::CadenceLimited,
            "199999 microseconds is cadence limited");
    require(pool.tryBegin(1024, 768, 200100, write) ==
                display::SnapshotBeginResult::Ok,
            "maximum surface begins at cadence boundary");
    write.pixels[0] = {4, 5, 6};
    require(pool.finish(display::CompositionResult::Ok, 14286) ==
                display::SnapshotFinishResult::Published,
            "new latest publishes while old lease is held");

    display::PresentationSnapshotLease blocked{};
    require(!pool.tryAcquireLatest(1, blocked),
            "only one network lease exists");
    first.release();
    require(pool.tryAcquireLatest(1, blocked),
            "new latest leases after old release");
    require(blocked.view().generation == 2 &&
                blocked.view().width == 1024 &&
                blocked.view().height == 768 &&
                blocked.view().payload_bytes ==
                    display::kPresentationSnapshotBytesPerSlot,
            "maximum lease metadata");
    blocked.release();

    display::PresentationSnapshotLease no_repeat{};
    require(!pool.tryAcquireLatest(2, no_repeat),
            "connection generation prevents reacquisition");
    display::PresentationSnapshotLease reconnect{};
    require(pool.tryAcquireLatest(0, reconnect),
            "reconnecting connection can lease retained latest");
    require(reconnect.view().generation == 2,
            "reconnect receives retained generation");
    reconnect.release();

    auto metrics = pool.metrics();
    require(metrics.publications == 2, "two publications counted");
    require(metrics.cadence_skips == 1, "cadence skip counted");
    require(metrics.producer_busy == 1, "producer busy counted");
  }
  require(tracking.live == 0, "successful pool teardown releases slots");
}

void checkCancellationAndBounds() {
  Tracking tracking{};
  {
    display::PresentationSnapshotPool pool(allocator(tracking));
    display::MutableSnapshotView write{};
    require(pool.tryBegin(0, 1, 0, write) ==
                display::SnapshotBeginResult::InvalidDimensions,
            "zero width rejected");
    require(pool.tryBegin(1025, 1, 0, write) ==
                display::SnapshotBeginResult::InvalidDimensions,
            "width bound rejected");
    require(pool.tryBegin(1, 769, 0, write) ==
                display::SnapshotBeginResult::InvalidDimensions,
            "height bound rejected");
    require(pool.tryBegin(1, 1, 0, write) ==
                display::SnapshotBeginResult::Ok,
            "valid producer begins");
    require(pool.finish(display::CompositionResult::InvalidPalette, 16667) ==
                display::SnapshotFinishResult::Cancelled,
            "failed composition cancels slot");
    display::PresentationSnapshotLease lease{};
    require(!pool.tryAcquireLatest(0, lease),
            "cancelled composition is never visible");
    require(pool.metrics().composition_failures == 1,
            "composition failure counted");
  }
  require(tracking.live == 0, "cancellation pool teardown releases slots");
}

void checkSustainedBoundedConsumers() {
  Tracking tracking{};
  {
    display::PresentationSnapshotPool pool(allocator(tracking));
    display::MutableSnapshotView write{};

    // A disconnected/null consumer leaves only one replaceable latest frame.
    for (std::uint64_t generation = 1; generation <= 256; ++generation) {
      auto const time = (generation - 1) *
                        display::kPresentationSnapshotMinimumIntervalUs;
      require(pool.tryBegin(320, 240, time, write) ==
                  display::SnapshotBeginResult::Ok,
              "null-consumer production remains available");
      write.pixels[0] = {static_cast<std::uint8_t>(generation), 0, 0};
      require(pool.finish(display::CompositionResult::Ok, 16667) ==
                  display::SnapshotFinishResult::Published,
              "null-consumer publication remains bounded");
    }

    display::PresentationSnapshotLease slow{};
    require(pool.tryAcquireLatest(0, slow), "slow consumer leases latest");
    require(slow.view().generation == 256, "slow lease starts at generation 256");
    auto const *immutable = slow.view().data;
    auto const immutable_byte = immutable[0];

    // One held lease plus a replaceable latest still leaves one producer slot.
    // Beginning that producer occupies all three slots; another begin is
    // refused immediately instead of allocating or waiting.
    auto time = 256 * display::kPresentationSnapshotMinimumIntervalUs;
    require(pool.tryBegin(640, 480, time, write) ==
                display::SnapshotBeginResult::Ok,
            "producer starts while slow lease is held");
    auto *const producer_pixels = write.pixels;
    require(pool.tryBegin(640, 480, time, write) ==
                display::SnapshotBeginResult::ProducerBusy,
            "full three-slot state refuses a second producer");
    require(write.pixels == nullptr,
            "refused begin clears the caller's mutable view");
    producer_pixels[0] = {1, 2, 3};
    require(pool.finish(display::CompositionResult::Ok, 16667) ==
                display::SnapshotFinishResult::Published,
            "producer replaces latest while old lease remains held");

    for (std::uint64_t generation = 258; generation <= 4096; ++generation) {
      time += display::kPresentationSnapshotMinimumIntervalUs;
      require(pool.tryBegin((generation & 1U) == 0 ? 320 : 1024,
                            (generation & 1U) == 0 ? 240 : 768,
                            time, write) == display::SnapshotBeginResult::Ok,
              "sustained producer remains bounded behind slow consumer");
      write.pixels[0] = {static_cast<std::uint8_t>(generation), 4, 5};
      require(pool.finish(display::CompositionResult::Ok, 16667) ==
                  display::SnapshotFinishResult::Published,
              "sustained publication succeeds");
      require(slow.view().data == immutable && immutable[0] == immutable_byte,
              "held slow-consumer bytes remain immutable");
    }

    require(tracking.calls == 3 && tracking.live == 3,
            "sustained operation retains exactly three allocations");
    require(pool.metrics().publications == 4096,
            "sustained generation count is exact");
    require(pool.metrics().producer_busy == 1,
            "slot-pressure producer refusal is counted");
    slow.release();

    display::PresentationSnapshotLease latest{};
    require(pool.tryAcquireLatest(0, latest),
            "latest survives slow-consumer release");
    require(latest.view().generation == 4096,
            "slow consumer collapses intermediate generations to latest");
  }
  require(tracking.live == 0,
          "sustained pool teardown releases exactly three slots");
}

}  // namespace

int main() {
  checkAllocationFailures();
  checkPublicationAndLease();
  checkCancellationAndBounds();
  checkSustainedBoundedConsumers();
  std::cout << "snapshot-pool=pass\n";
  return 0;
}
