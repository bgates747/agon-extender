#include "extender/display/stock_native_access.hpp"

#if defined(AGON_EXTENDER_STOCK_RUNTIME)
#include <algorithm>
#include <cassert>
#include <limits>

namespace agon::extender::display {
namespace {
std::atomic<std::uint32_t> frame_count{};
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
