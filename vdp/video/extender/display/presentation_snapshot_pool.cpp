// See presentation_snapshot_pool.hpp. The atomic guard protects only bounded
// state transitions; the producer never spins and the network owner never
// retains the guard while handling or transmitting pixel bytes.
#include "extender/display/presentation_snapshot_pool.hpp"

#include <limits>

namespace agon::extender::display {

PresentationSnapshotLease::PresentationSnapshotLease(
    PresentationSnapshotPool *owner, std::size_t slot,
    ImmutableSnapshotView view) noexcept
    : owner_(owner), slot_(slot), view_(view) {}

PresentationSnapshotLease::~PresentationSnapshotLease() { release(); }

PresentationSnapshotLease::PresentationSnapshotLease(
    PresentationSnapshotLease &&other) noexcept
    : owner_(other.owner_), slot_(other.slot_), view_(other.view_) {
  other.owner_ = nullptr;
  other.view_ = {};
}

PresentationSnapshotLease &PresentationSnapshotLease::operator=(
    PresentationSnapshotLease &&other) noexcept {
  if (this == &other) return *this;
  release();
  owner_ = other.owner_;
  slot_ = other.slot_;
  view_ = other.view_;
  other.owner_ = nullptr;
  other.view_ = {};
  return *this;
}

bool PresentationSnapshotLease::valid() const noexcept {
  return owner_ != nullptr;
}

ImmutableSnapshotView const &PresentationSnapshotLease::view() const noexcept {
  return view_;
}

void PresentationSnapshotLease::release() noexcept {
  if (owner_ == nullptr) return;
  auto *owner = owner_;
  owner_ = nullptr;
  owner->releaseLease(slot_, view_.generation);
  view_ = {};
}

PresentationSnapshotPool::PresentationSnapshotPool(
    Allocator allocator, SnapshotPixelFormat format,
    std::uint64_t minimum_interval_us, bool on_demand, bool direct_rgb222,
    bool lookahead) noexcept
    : allocator_(allocator), format_(format), minimum_interval_us_(minimum_interval_us),
      on_demand_(on_demand), direct_rgb222_(direct_rgb222),
      lookahead_(on_demand && lookahead) {
#if !defined(AGON_EXTENDER_SNAPSHOT_MUTEX)
  transition_lock_.clear(std::memory_order_release);
#endif
  if (allocator_.allocate == nullptr || allocator_.deallocate == nullptr ||
      (direct_rgb222_ && format_ != SnapshotPixelFormat::RGB222)) {
    increment(allocation_failures_);
    return;
  }
  for (auto &slot : slots_) {
    slot.pixels = static_cast<PresentationRGB888 *>(
        allocator_.allocate(allocator_.context,
                            direct_rgb222_ ? kPresentationSnapshotMaximumWidth *
                                kPresentationSnapshotMaximumHeight : kPresentationSnapshotBytesPerSlot));
    if (slot.pixels == nullptr) {
      increment(allocation_failures_);
      releaseAllocations();
      return;
    }
  }
  enabled_ = true;
}

PresentationSnapshotPool::~PresentationSnapshotPool() { releaseAllocations(); }

bool PresentationSnapshotPool::enabled() const noexcept { return enabled_; }

void PresentationSnapshotPool::increment(
    std::atomic<std::uint32_t> &counter) noexcept {
  std::uint32_t value = counter.load(std::memory_order_relaxed);
  while (value != std::numeric_limits<std::uint32_t>::max() &&
         !counter.compare_exchange_weak(value, value + 1,
                                        std::memory_order_relaxed,
                                        std::memory_order_relaxed)) {
  }
}

bool PresentationSnapshotPool::tryLockProducer() noexcept {
#if defined(AGON_EXTENDER_SNAPSHOT_MUTEX)
  return transition_lock_.try_lock();
#else
  return !transition_lock_.test_and_set(std::memory_order_acquire);
#endif
}

void PresentationSnapshotPool::lockConsumer() noexcept {
#if defined(AGON_EXTENDER_SNAPSHOT_MUTEX)
  // N04s: a spinning higher-priority consumer can preempt the task holding
  // this lock and starve it forever. IDF's task mutex blocks and inherits
  // priority; producer admission above still tries only once. No ISR caller.
  transition_lock_.lock();
#else
  // Historical binding requires producer scheduling above its consumers.
  while (transition_lock_.test_and_set(std::memory_order_acquire)) {
  }
#endif
}

void PresentationSnapshotPool::unlock() noexcept {
#if defined(AGON_EXTENDER_SNAPSHOT_MUTEX)
  transition_lock_.unlock();
#else
  transition_lock_.clear(std::memory_order_release);
#endif
}

int PresentationSnapshotPool::findLocked(SlotState state) const noexcept {
  for (std::size_t index = 0; index < slots_.size(); ++index) {
    if (slots_[index].state == state) return static_cast<int>(index);
  }
  return -1;
}

bool PresentationSnapshotPool::tryFinalizePending() noexcept {
  if (pending_action_ == PendingAction::None) return true;
  if (!tryLockProducer()) {
    increment(transition_busy_);
    return false;
  }
  finalizePendingLocked();
  unlock();
  return true;
}

void PresentationSnapshotPool::finalizePendingLocked() noexcept {
  if (producer_slot_ < 0 ||
      static_cast<std::size_t>(producer_slot_) >= slots_.size()) {
    pending_action_ = PendingAction::None;
    producer_slot_ = -1;
    return;
  }
  auto &producer = slots_[static_cast<std::size_t>(producer_slot_)];
  if (producer.state != SlotState::Producer) {
    pending_action_ = PendingAction::None;
    producer_slot_ = -1;
    return;
  }
  if (pending_action_ == PendingAction::Cancel) {
    producer.state = SlotState::Free;
    producer.width = 0;
    producer.height = 0;
    producer.payload_bytes = 0;
    producer.generation = 0;
    producer.present_period_us = 0;
  } else if (pending_action_ == PendingAction::Publish) {
    int previous_latest = findLocked(SlotState::Latest);
    if (previous_latest >= 0) {
      auto &old = slots_[static_cast<std::size_t>(previous_latest)];
      old.state = SlotState::Free;
      old.width = 0;
      old.height = 0;
      old.payload_bytes = 0;
      old.generation = 0;
      old.present_period_us = 0;
    }
    ++generation_;
    producer.generation = generation_;
    producer.present_period_us = pending_present_period_us_;
    producer.state = SlotState::Latest;
    last_publication_time_us_ = pending_boundary_time_us_;
    has_publication_time_ = true;
    increment(publications_);
  }
  pending_action_ = PendingAction::None;
  producer_slot_ = -1;
}

SnapshotBeginResult PresentationSnapshotPool::tryBegin(
    std::size_t width, std::size_t height,
    std::uint64_t boundary_time_us, MutableSnapshotView &view) noexcept {
  view = {};
  if (!enabled_) return SnapshotBeginResult::Disabled;
  if (pending_action_ != PendingAction::None && !tryFinalizePending())
    return SnapshotBeginResult::TransitionBusy;
  if (producer_slot_ >= 0) {
    increment(producer_busy_);
    return SnapshotBeginResult::ProducerBusy;
  }
  if (width == 0 || height == 0 ||
      width > kPresentationSnapshotMaximumWidth ||
      height > kPresentationSnapshotMaximumHeight ||
      width > std::numeric_limits<std::size_t>::max() / height ||
      width * height >
          std::numeric_limits<std::size_t>::max() /
              kPresentationSnapshotBytesPerPixel) {
    return SnapshotBeginResult::InvalidDimensions;
  }
  // An unthrottled high-priority frame task must not continuously compose
  // full surfaces with no browser demand. That starved HTTP startup in r05.
  // Consumer demand admits one snapshot at a logical boundary; no fixed fps
  // cap or network wait is introduced into logical VDP work.
  if (on_demand_ && !requested_.load(std::memory_order_acquire))
    return SnapshotBeginResult::NotRequested;
  if (has_publication_time_ &&
      boundary_time_us - last_publication_time_us_ <
          minimum_interval_us_) {
    increment(cadence_skips_);
    return SnapshotBeginResult::CadenceLimited;
  }
  if (!tryLockProducer()) {
    increment(transition_busy_);
    return SnapshotBeginResult::TransitionBusy;
  }
  int free_slot = findLocked(SlotState::Free);
  if (free_slot < 0) {
    unlock();
    increment(producer_no_slot_);
    return SnapshotBeginResult::NoFreeSlot;
  }
  requested_.store(false, std::memory_order_release);
  auto &slot = slots_[static_cast<std::size_t>(free_slot)];
  slot.state = SlotState::Producer;
  slot.width = width;
  slot.height = height;
  slot.payload_bytes = width * height * (direct_rgb222_ ? 1 : kPresentationSnapshotBytesPerPixel);
  slot.generation = 0;
  slot.present_period_us = 0;
  producer_slot_ = free_slot;
  pending_boundary_time_us_ = boundary_time_us;
  unlock();

  view = {direct_rgb222_ ? nullptr : slot.pixels,
          kPresentationSnapshotBytesPerSlot /
              kPresentationSnapshotBytesPerPixel,
          width,
          height,
          direct_rgb222_ ? reinterpret_cast<std::uint8_t *>(slot.pixels) : nullptr};
  return SnapshotBeginResult::Ok;
}

SnapshotFinishResult PresentationSnapshotPool::finish(
    CompositionResult composition,
    std::uint64_t present_period_us) noexcept {
  if (producer_slot_ < 0) return SnapshotFinishResult::NoProducer;
  if (composition == CompositionResult::Ok) {
    if (pending_action_ == PendingAction::None &&
        format_ == SnapshotPixelFormat::RGB222 && !direct_rgb222_) {
      // P4 already quantizes the composed palette/overlay image to RGB222.
      // Pack forward in the exclusive producer slot BEFORE immutable publication.
      // Reading each RGB888 value before overwriting its earlier output byte
      // permits in-place compaction without another frame allocation or a lock
      // over the pixel loop. A deferred publication must never pack twice.
      auto &slot = slots_[static_cast<std::size_t>(producer_slot_)];
      auto *packed = reinterpret_cast<std::uint8_t *>(slot.pixels);
      const auto count = slot.width * slot.height;
      for (std::size_t i = 0; i < count; ++i) {
        const auto pixel = slot.pixels[i];
        packed[i] = (pixel.red >> 6) | ((pixel.green >> 6) << 2) |
                    ((pixel.blue >> 6) << 4);
      }
      slot.payload_bytes = count;
    }
    pending_action_ = PendingAction::Publish;
    pending_present_period_us_ = present_period_us;
  } else {
    increment(composition_failures_);
    pending_action_ = PendingAction::Cancel;
    pending_present_period_us_ = 0;
  }
  if (!tryFinalizePending()) return SnapshotFinishResult::Deferred;
  return composition == CompositionResult::Ok
             ? SnapshotFinishResult::Published
             : SnapshotFinishResult::Cancelled;
}

bool PresentationSnapshotPool::tryAcquireLatest(
    std::uint64_t last_generation,
    PresentationSnapshotLease &lease) noexcept {
  if (!enabled_ || lease.valid()) return false;
  lockConsumer();
  if (findLocked(SlotState::Leased) >= 0) {
    unlock();
    increment(consumer_no_new_);
    return false;
  }
  int latest = findLocked(SlotState::Latest);
  if (latest < 0 ||
      slots_[static_cast<std::size_t>(latest)].generation <= last_generation) {
    // A network retry while a producer is composing waits for that same
    // frame. Re-arming demand here queued another full composition on every
    // catch-up tick, starving console work with continuous browser credit
    // (PORT-003 RGB-4, console r06). The Producer state remains set through
    // deferred publication, so it also covers retries during that interval.
    // After failure/cancellation, the next consumer poll may request a retry.
    if (findLocked(SlotState::Producer) < 0)
      requested_.store(true, std::memory_order_release);
    unlock();
    increment(consumer_no_new_);
    return false;
  }
  auto &slot = slots_[static_cast<std::size_t>(latest)];
  slot.state = SlotState::Leased;
  // Optional one-frame lookahead overlaps capture with this lease's send.
  // Only a successful acquisition arms it: retries/held leases cannot create
  // continuous no-demand composition (the historical RGB-4 starvation bug).
  // An already active producer supplies the next frame and must not be rearmed.
  if (lookahead_ && findLocked(SlotState::Producer) < 0)
    requested_.store(true, std::memory_order_release);
  ImmutableSnapshotView view{
      reinterpret_cast<std::uint8_t const *>(slot.pixels),
      slot.payload_bytes,
      slot.width,
      slot.height,
      slot.width * (format_ == SnapshotPixelFormat::RGB222 ? 1 : 3),
      slot.generation,
      slot.present_period_us,
      format_,
  };
  unlock();
  lease = PresentationSnapshotLease(this, static_cast<std::size_t>(latest),
                                    view);
  return true;
}

void PresentationSnapshotPool::releaseLease(
    std::size_t slot_index, std::uint64_t generation) noexcept {
  if (!enabled_ || slot_index >= slots_.size()) return;
  lockConsumer();
  auto &slot = slots_[slot_index];
  if (slot.state == SlotState::Leased && slot.generation == generation) {
    int latest = findLocked(SlotState::Latest);
    if (latest < 0 || generation >
                          slots_[static_cast<std::size_t>(latest)].generation) {
      slot.state = SlotState::Latest;
    } else {
      slot.state = SlotState::Free;
      slot.width = 0;
      slot.height = 0;
      slot.payload_bytes = 0;
      slot.generation = 0;
      slot.present_period_us = 0;
    }
  }
  unlock();
}

SnapshotPoolMetrics PresentationSnapshotPool::metrics() const noexcept {
  return {
      enabled_,
      allocation_failures_.load(std::memory_order_relaxed),
      cadence_skips_.load(std::memory_order_relaxed),
      transition_busy_.load(std::memory_order_relaxed),
      producer_busy_.load(std::memory_order_relaxed),
      producer_no_slot_.load(std::memory_order_relaxed),
      composition_failures_.load(std::memory_order_relaxed),
      publications_.load(std::memory_order_relaxed),
      consumer_no_new_.load(std::memory_order_relaxed),
  };
}

void PresentationSnapshotPool::releaseAllocations() noexcept {
  enabled_ = false;
  if (allocator_.deallocate == nullptr) return;
  for (auto &slot : slots_) {
    if (slot.pixels != nullptr) {
      allocator_.deallocate(allocator_.context, slot.pixels);
      slot.pixels = nullptr;
    }
    slot.state = SlotState::Free;
  }
}

}  // namespace agon::extender::display
