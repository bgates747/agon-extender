// PORT-003 Phase F fixed-capacity immutable presentation snapshots.
//
// The frame-task producer receives one mutable slot only for synchronous
// composition at a controller-owned quiescent boundary. Publication removes
// mutable access. Network consumers receive move-only immutable leases and
// never receive a logical-plane pointer. The producer tries every transition
// lock once and therefore never waits for a consumer.
#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

#include "extender/display/plane_storage.hpp"
#include "extender/display/presentation_compositor.hpp"

namespace agon::extender::display {

inline constexpr std::size_t kPresentationSnapshotSlotCount = 3;
inline constexpr std::size_t kPresentationSnapshotMaximumWidth = 1024;
inline constexpr std::size_t kPresentationSnapshotMaximumHeight = 768;
inline constexpr std::size_t kPresentationSnapshotBytesPerPixel = 3;
inline constexpr std::size_t kPresentationSnapshotBytesPerSlot =
    kPresentationSnapshotMaximumWidth * kPresentationSnapshotMaximumHeight *
    kPresentationSnapshotBytesPerPixel;
inline constexpr std::uint64_t kPresentationSnapshotMinimumIntervalUs =
    200'000;

static_assert(sizeof(PresentationRGB888) == kPresentationSnapshotBytesPerPixel,
              "PresentationRGB888 must remain tightly packed");

enum class SnapshotBeginResult : std::uint8_t {
  Ok,
  Disabled,
  InvalidDimensions,
  CadenceLimited,
  TransitionBusy,
  ProducerBusy,
  NoFreeSlot,
};

enum class SnapshotFinishResult : std::uint8_t {
  Published,
  Cancelled,
  Deferred,
  NoProducer,
};

struct MutableSnapshotView {
  PresentationRGB888 *pixels;
  std::size_t pixel_capacity;
  std::size_t width;
  std::size_t height;
};

struct ImmutableSnapshotView {
  std::uint8_t const *data;
  std::size_t payload_bytes;
  std::size_t width;
  std::size_t height;
  std::size_t stride_bytes;
  std::uint64_t generation;
  std::uint64_t present_period_us;
};

struct SnapshotPoolMetrics {
  bool enabled;
  std::uint32_t allocation_failures;
  std::uint32_t cadence_skips;
  std::uint32_t transition_busy;
  std::uint32_t producer_busy;
  std::uint32_t producer_no_slot;
  std::uint32_t composition_failures;
  std::uint32_t publications;
  std::uint32_t consumer_no_new;
};

class PresentationSnapshotPool;

class PresentationSnapshotLease final {
 public:
  PresentationSnapshotLease() noexcept = default;
  ~PresentationSnapshotLease();

  PresentationSnapshotLease(PresentationSnapshotLease const &) = delete;
  PresentationSnapshotLease &operator=(PresentationSnapshotLease const &) =
      delete;
  PresentationSnapshotLease(PresentationSnapshotLease &&other) noexcept;
  PresentationSnapshotLease &operator=(
      PresentationSnapshotLease &&other) noexcept;

  bool valid() const noexcept;
  ImmutableSnapshotView const &view() const noexcept;
  void release() noexcept;

 private:
  friend class PresentationSnapshotPool;
  PresentationSnapshotLease(PresentationSnapshotPool *owner,
                            std::size_t slot,
                            ImmutableSnapshotView view) noexcept;

  PresentationSnapshotPool *owner_{};
  std::size_t slot_{};
  ImmutableSnapshotView view_{};
};

class PresentationSnapshotPool final {
 public:
  explicit PresentationSnapshotPool(Allocator allocator) noexcept;
  ~PresentationSnapshotPool();

  PresentationSnapshotPool(PresentationSnapshotPool const &) = delete;
  PresentationSnapshotPool &operator=(PresentationSnapshotPool const &) =
      delete;

  bool enabled() const noexcept;

  // Called only by the controller's frame-task owner. These methods never
  // wait for the transition guard. A deferred finish remains bounded to the
  // one producer slot and is retried at the next frame boundary.
  SnapshotBeginResult tryBegin(std::size_t width, std::size_t height,
                               std::uint64_t boundary_time_us,
                               MutableSnapshotView &view) noexcept;
  SnapshotFinishResult finish(CompositionResult composition,
                              std::uint64_t present_period_us) noexcept;

  // Called by the network owner. The guard is held only for the state change;
  // it is released before callers inspect or send immutable bytes.
  bool tryAcquireLatest(std::uint64_t last_generation,
                        PresentationSnapshotLease &lease) noexcept;

  SnapshotPoolMetrics metrics() const noexcept;

 private:
  friend class PresentationSnapshotLease;

  enum class SlotState : std::uint8_t { Free, Producer, Latest, Leased };
  enum class PendingAction : std::uint8_t { None, Publish, Cancel };

  struct Slot {
    PresentationRGB888 *pixels{};
    SlotState state{SlotState::Free};
    std::size_t width{};
    std::size_t height{};
    std::size_t payload_bytes{};
    std::uint64_t generation{};
    std::uint64_t present_period_us{};
  };

  static void increment(std::atomic<std::uint32_t> &counter) noexcept;
  bool tryLockProducer() noexcept;
  void lockConsumer() noexcept;
  void unlock() noexcept;
  bool tryFinalizePending() noexcept;
  void finalizePendingLocked() noexcept;
  void releaseLease(std::size_t slot, std::uint64_t generation) noexcept;
  int findLocked(SlotState state) const noexcept;
  void releaseAllocations() noexcept;

  Allocator allocator_{};
  std::array<Slot, kPresentationSnapshotSlotCount> slots_{};
  mutable std::atomic_flag transition_lock_ = ATOMIC_FLAG_INIT;
  bool enabled_{};
  int producer_slot_{-1};
  PendingAction pending_action_{PendingAction::None};
  std::uint64_t pending_boundary_time_us_{};
  std::uint64_t pending_present_period_us_{};
  std::uint64_t generation_{};
  std::uint64_t last_publication_time_us_{};
  bool has_publication_time_{};

  std::atomic<std::uint32_t> allocation_failures_{};
  std::atomic<std::uint32_t> cadence_skips_{};
  std::atomic<std::uint32_t> transition_busy_{};
  std::atomic<std::uint32_t> producer_busy_{};
  std::atomic<std::uint32_t> producer_no_slot_{};
  std::atomic<std::uint32_t> composition_failures_{};
  std::atomic<std::uint32_t> publications_{};
  std::atomic<std::uint32_t> consumer_no_new_{};
};

}  // namespace agon::extender::display
