// See logical_frame_service.hpp. Every state transition follows the order
// frozen in docs/tasks/PORT-003/phase-c/contracts.md.
#include "extender/display/logical_frame_service.hpp"

#include <limits>

namespace agon::extender::display {

static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "timer notification requires lock-free 32-bit atomics");

LogicalFrameService::LogicalFrameService(FrameWorkExecutor &executor,
                                         std::size_t work_budget) noexcept
    : executor_(executor), work_budget_(work_budget == 0 ? 1 : work_budget) {}

bool LogicalFrameService::start() noexcept {
  bool expected = false;
  if (!running_.compare_exchange_strong(expected, true,
                                        std::memory_order_acq_rel,
                                        std::memory_order_acquire)) {
    return false;
  }
  pending_ticks_.store(0, std::memory_order_release);
  executor_.setFrameServiceRunning(true);
  return true;
}

void LogicalFrameService::stop() noexcept {
  if (!running_.exchange(false, std::memory_order_acq_rel)) return;
  pending_ticks_.store(0, std::memory_order_release);
  executor_.setFrameServiceRunning(false);
}

bool LogicalFrameService::running() const noexcept {
  return running_.load(std::memory_order_acquire);
}

void LogicalFrameService::setFramePeriodMicroseconds(
    std::uint64_t period_microseconds) noexcept {
  executor_.setLogicalFramePeriodMicroseconds(period_microseconds);
}

bool LogicalFrameService::recordTicks(std::uint32_t elapsed_ticks) noexcept {
  if (elapsed_ticks == 0 || !running()) return false;
  std::uint32_t pending = pending_ticks_.load(std::memory_order_acquire);
  for (;;) {
    std::uint32_t room = std::numeric_limits<std::uint32_t>::max() - pending;
    std::uint32_t replacement =
        elapsed_ticks > room ? std::numeric_limits<std::uint32_t>::max()
                             : pending + elapsed_ticks;
    if (pending_ticks_.compare_exchange_weak(
            pending, replacement, std::memory_order_acq_rel,
            std::memory_order_acquire)) {
      if (elapsed_ticks > room)
        saturated_tick_notifications_.fetch_add(1, std::memory_order_relaxed);
      return true;
    }
    if (!running()) return false;
  }
}

FrameServiceResult LogicalFrameService::servicePending() {
  if (!running()) return FrameServiceResult::Stopped;
  std::uint32_t pending = pending_ticks_.load(std::memory_order_acquire);
  for (;;) {
    if (pending == 0) return FrameServiceResult::Idle;
    if (pending_ticks_.compare_exchange_weak(
            pending, pending - 1, std::memory_order_acq_rel,
            std::memory_order_acquire)) {
      break;
    }
    if (!running()) return FrameServiceResult::Stopped;
  }

  std::uint32_t frame_counter = executor_.advanceFrameCounter(1);
  ++metrics_.elapsed_ticks;
  ++metrics_.serviced_edges;

  std::size_t executed = executor_.executeFrameWork(work_budget_);
  ++generation_;
  FrameNotice notice{
      generation_,
      frame_counter,
      executor_.logicalWidth(),
      executor_.logicalHeight(),
      executor_.logicalFormat(),
      executor_.logicalDoubleBuffered(),
      executor_.visiblePlaneIdentity(),
  };
  for (auto &slot : consumers_) {
    if (!slot.registered.load(std::memory_order_acquire) ||
        !slot.connected.load(std::memory_order_acquire)) {
      continue;
    }
    if (slot.notice_lock.test_and_set(std::memory_order_acquire)) {
      recordDrop(slot);
      continue;
    }
    if (slot.has_notice) recordDrop(slot);
    slot.notice = notice;
    slot.has_notice = true;
    slot.notice_lock.clear(std::memory_order_release);
  }

  ++metrics_.published_generations;
  metrics_.executed_primitives += executed;
  return FrameServiceResult::Serviced;
}

int LogicalFrameService::registerConsumer() noexcept {
  if (running()) return -1;
  for (std::size_t index = 0; index < consumers_.size(); ++index) {
    auto &slot = consumers_[index];
    if (!slot.registered.load(std::memory_order_acquire)) {
      slot.notice_lock.clear(std::memory_order_release);
      slot.has_notice = false;
      slot.drops.store(0, std::memory_order_release);
      slot.connected.store(true, std::memory_order_release);
      slot.registered.store(true, std::memory_order_release);
      return static_cast<int>(index);
    }
  }
  return -1;
}

bool LogicalFrameService::unregisterConsumer(int slot) noexcept {
  if (running() || slot < 0 ||
      static_cast<std::size_t>(slot) >= consumers_.size() ||
      !consumers_[slot].registered.load(std::memory_order_acquire)) {
    return false;
  }
  auto &entry = consumers_[slot];
  entry.connected.store(false, std::memory_order_release);
  while (entry.notice_lock.test_and_set(std::memory_order_acquire)) {
  }
  entry.has_notice = false;
  entry.notice_lock.clear(std::memory_order_release);
  entry.registered.store(false, std::memory_order_release);
  return true;
}

bool LogicalFrameService::setConsumerConnected(int slot,
                                               bool connected) noexcept {
  if (slot < 0 || static_cast<std::size_t>(slot) >= consumers_.size())
    return false;
  auto &entry = consumers_[slot];
  if (!entry.registered.load(std::memory_order_acquire)) return false;
  entry.connected.store(connected, std::memory_order_release);
  if (!connected) {
    while (entry.notice_lock.test_and_set(std::memory_order_acquire)) {
    }
    entry.has_notice = false;
    entry.notice_lock.clear(std::memory_order_release);
  }
  return true;
}

bool LogicalFrameService::tryPeekLatest(int slot,
                                        FrameNotice &notice) noexcept {
  return readLatest(slot, notice, false);
}

bool LogicalFrameService::tryConsumeLatest(int slot,
                                           FrameNotice &notice) noexcept {
  return readLatest(slot, notice, true);
}

bool LogicalFrameService::readLatest(int slot, FrameNotice &notice,
                                     bool consume) noexcept {
  if (slot < 0 || static_cast<std::size_t>(slot) >= consumers_.size())
    return false;
  auto &entry = consumers_[slot];
  if (!entry.registered.load(std::memory_order_acquire) ||
      !entry.connected.load(std::memory_order_acquire) ||
      entry.notice_lock.test_and_set(std::memory_order_acquire)) {
    return false;
  }
  bool available = entry.has_notice;
  if (available) {
    notice = entry.notice;
    if (consume) entry.has_notice = false;
  }
  entry.notice_lock.clear(std::memory_order_release);
  return available;
}

void LogicalFrameService::recordDrop(ConsumerSlot &slot) noexcept {
  std::uint32_t value = slot.drops.load(std::memory_order_relaxed);
  while (value != std::numeric_limits<std::uint32_t>::max() &&
         !slot.drops.compare_exchange_weak(value, value + 1,
                                           std::memory_order_relaxed,
                                           std::memory_order_relaxed)) {
  }
}

std::uint32_t LogicalFrameService::consumerDrops(int slot) const noexcept {
  if (slot < 0 || static_cast<std::size_t>(slot) >= consumers_.size()) return 0;
  return consumers_[slot].drops.load(std::memory_order_relaxed);
}

std::uint32_t LogicalFrameService::pendingTicks() const noexcept {
  return pending_ticks_.load(std::memory_order_acquire);
}

std::uint64_t LogicalFrameService::generation() const noexcept {
  return generation_;
}

FrameServiceMetrics LogicalFrameService::metrics() const noexcept {
  FrameServiceMetrics result = metrics_;
  result.saturated_tick_notifications =
      saturated_tick_notifications_.load(std::memory_order_relaxed);
  return result;
}

}  // namespace agon::extender::display
