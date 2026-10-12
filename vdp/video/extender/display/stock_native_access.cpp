#include "extender/display/stock_native_access.hpp"

#if defined(AGON_EXTENDER_STOCK_RUNTIME)
#include <algorithm>
#include <cassert>
#include <limits>

namespace agon::extender::display {
namespace {
std::atomic<std::uint32_t> frame_count{};
std::atomic<std::uint32_t> visible_generation{};
static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "The frame clock must not acquire a runtime mutex");
}

std::recursive_mutex &stockNativeMutex() {
  static std::recursive_mutex mutex;
  return mutex;
}

std::recursive_mutex &stockForegroundMutex() {
  static std::recursive_mutex mutex;
  return mutex;
}

std::uint32_t &stockPaletteRevision() {
  static std::uint32_t revision{};
  return revision;
}

std::uint32_t stockVisibleGeneration() noexcept {
  return visible_generation.load(std::memory_order_acquire);
}

void stockVisibleBufferSwapped() noexcept {
  visible_generation.fetch_add(1, std::memory_order_release);
}

#if defined(AGON_EXTENDER_SW_VISIBLE_SNAPSHOT) && AGON_EXTENDER_SW_VISIBLE_SNAPSHOT
namespace {
// Native exclusion serializes request/show with bind/cancel. No additional lock
// or callback pointer survives that exclusion. Cancel waits for an already-issued
// notification to return, clears pending state, then lets teardown join/delete
// the old task. Bind of a new mode occurs only after old task teardown joins.
void *software_snapshot_owner{};
StockSoftwareSnapshotWake software_snapshot_wake{};
void *software_snapshot_context{};
bool software_snapshot_pending{};
}
bool stockBindSoftwareSnapshotWake(void *owner, StockSoftwareSnapshotWake wake, void *context) {
  if (!owner || !wake || !context) return false;
  AGON_STOCK_NATIVE_GUARD;
  if (software_snapshot_owner) return false;
  software_snapshot_pending = false;
  software_snapshot_context = context;
  software_snapshot_wake = wake;
  software_snapshot_owner = owner;
  return true;
}
void stockCancelSoftwareSnapshotWake(void *owner) {
  AGON_STOCK_NATIVE_GUARD;
  if (software_snapshot_owner != owner) return;
  software_snapshot_pending = false;
  software_snapshot_owner = nullptr;
  software_snapshot_wake = nullptr;
  software_snapshot_context = nullptr;
}
void stockRequestSoftwareSnapshotWake() noexcept {
  if (software_snapshot_owner) software_snapshot_pending = true;
}
void stockSoftwareSpritesShown() noexcept {
  if (!software_snapshot_pending || !software_snapshot_wake) return;
  software_snapshot_pending = false;
  software_snapshot_wake(software_snapshot_context);
}
#endif

void StockExecutionGate::suspend() {
  std::unique_lock lock(state_);
  depth_.fetch_add(1, std::memory_order_release);
  idle_.wait(lock, [&] { return !worker_active_; });
}

void StockExecutionGate::resume() {
  std::lock_guard lock(state_);
  if (depth_.load(std::memory_order_relaxed)) depth_.fetch_sub(1, std::memory_order_release);
}

bool StockExecutionGate::beginWorker() {
  std::lock_guard lock(state_);
  if (worker_active_ || depth_.load(std::memory_order_relaxed)) return false;
  worker_active_ = true;
  return true;
}

void StockExecutionGate::endWorker() {
  {
    std::lock_guard lock(state_);
    assert(worker_active_);
    worker_active_ = false;
  }
  idle_.notify_all();
}

StockFrameCounter::operator std::uint32_t() const noexcept { return frame_count.load(std::memory_order_relaxed); }
StockFrameCounter &StockFrameCounter::operator=(std::uint32_t value) noexcept {
  frame_count.store(value, std::memory_order_relaxed);
  return *this;
}
void StockFrameCounter::advance(std::uint32_t count) noexcept { frame_count.fetch_add(count, std::memory_order_relaxed); }

void StockClock::start(std::uint64_t now_us, std::uint32_t period_us) noexcept {
  assert(period_us != 0);
  period_us_ = period_us;
  next_edge_us_ = now_us + period_us;
  max_lateness_.store(0);
  delayed_ticks_.store(0);
}

std::uint32_t StockClock::observe(std::uint64_t now_us) noexcept {
  if (!period_us_ || now_us < next_edge_us_) return 0;
  auto late = now_us - next_edge_us_;
  auto elapsed = late / period_us_ + 1;
  auto measured = static_cast<std::uint32_t>(std::min<std::uint64_t>(late, UINT32_MAX));
  if (measured > max_lateness_.load(std::memory_order_relaxed)) max_lateness_.store(measured, std::memory_order_relaxed);
  delayed_ticks_.fetch_add(static_cast<std::uint32_t>(elapsed - 1), std::memory_order_relaxed);
  next_edge_us_ += elapsed * period_us_;
  StockFrameCounter::advance(static_cast<std::uint32_t>(elapsed));
  return static_cast<std::uint32_t>(elapsed);
}
} // namespace agon::extender::display
#endif
