// P4 CPU-output binding, PORT-003-R2-D001. This is synchronization around
// retained upstream operations, not a replacement renderer or an upstream fix.
// The independent clock must never enter these guards.
#pragma once

#if defined(AGON_EXTENDER_STOCK_RUNTIME)
#include <atomic>
#include <condition_variable>
#include <cstdint>
#include <mutex>

namespace agon::extender::display {

// One active stock display; the original native row aliases are static too.
// ESP-IDF implements std::recursive_mutex through its recursive FreeRTOS mutex
// (components/pthread/pthread.c), including priority inheritance. Recursion is
// needed when one original primitive invokes sprite/native helper operations.
std::recursive_mutex &stockNativeMutex();
std::recursive_mutex &stockForegroundMutex();
std::uint32_t &stockPaletteRevision();  // accessed only under the native mutex
using StockNativeGuard = std::lock_guard<std::recursive_mutex>;

struct StockPaletteGuard {
  StockNativeGuard guard{stockNativeMutex()};
  ~StockPaletteGuard() { ++stockPaletteRevision(); }
};

// Serialize worker admission with suspension. Foreground API entry has its own
// recursive mutex, so concurrent immediate flushes cannot dequeue/reorder work.
// Suspension itself can persist while background execution is disabled; it
// must not retain a thread-owned mutex across that state or mode lifetime.
class StockExecutionGate {
 public:
  void suspend();
  void resume();
  bool beginWorker();
  void endWorker();
  bool suspended() const noexcept { return depth_.load(std::memory_order_acquire) != 0; }
 private:
  std::mutex state_;
  std::condition_variable idle_;
  std::atomic<unsigned> depth_{1};  // stock setup begins suspended
  bool worker_active_{};
};

// Original context code reads/assigns frameCounter. In the runtime binding it
// addresses a sink-independent register, whose lifetime exceeds native modes.
class StockFrameCounter {
 public:
  operator std::uint32_t() const noexcept;
  StockFrameCounter &operator=(std::uint32_t value) noexcept;
  static void advance(std::uint32_t count) noexcept;
};

// Single clock-owner accounting, callable without a native lock or renderer.
// start() precedes timer startup; observe() runs only on that timer owner.
// A late callback advances elapsed time once, not one render pass per old tick.
class StockClock {
 public:
  void start(std::uint64_t now_us, std::uint32_t period_us) noexcept;
  std::uint32_t observe(std::uint64_t now_us) noexcept;
  std::uint32_t maximumLatenessUs() const noexcept { return max_lateness_.load(); }
  std::uint32_t delayedTicks() const noexcept { return delayed_ticks_.load(); }
 private:
  std::uint64_t next_edge_us_{};
  std::uint32_t period_us_{};
  std::atomic<std::uint32_t> max_lateness_{};
  std::atomic<std::uint32_t> delayed_ticks_{};
};

} // namespace agon::extender::display

#define AGON_STOCK_NATIVE_GUARD \
  ::agon::extender::display::StockNativeGuard agon_stock_native_guard( \
      ::agon::extender::display::stockNativeMutex())
#define AGON_STOCK_PALETTE_GUARD \
  ::agon::extender::display::StockPaletteGuard agon_stock_palette_guard
#define AGON_STOCK_FOREGROUND_GUARD \
  ::agon::extender::display::StockNativeGuard agon_stock_foreground_guard( \
      ::agon::extender::display::stockForegroundMutex())
#else
#define AGON_STOCK_NATIVE_GUARD
#define AGON_STOCK_PALETTE_GUARD
#define AGON_STOCK_FOREGROUND_GUARD
#endif
