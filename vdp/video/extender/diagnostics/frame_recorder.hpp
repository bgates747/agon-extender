// AUDIT-006 observation only. No blocking locks, allocation, logging or I/O.
// Intervals are wall time (including preemption). Nested phases overlap.
#pragma once
#include <array>
#include <atomic>
#include <cstdint>
#include <cstddef>

namespace agon::extender::diagnostics {
enum class Phase : unsigned { Frame, Queue, Sprites, Snapshot, Suspend, Parser,
                              TxEnqueue, TxComplete, Count };
constexpr std::size_t phaseCount = static_cast<unsigned>(Phase::Count);
constexpr std::size_t historySize = 32;
constexpr std::uint32_t slowMicroseconds = 20000;
inline constexpr const char *phaseNames[phaseCount] = {
    "frame", "queue", "sprites", "snapshot", "suspend", "parser",
    "tx_enqueue", "tx_complete"};
struct Totals {
  std::uint64_t count{}, total_us{}, units{};
  std::uint32_t max_us{}, max_at_us{}, last_us{}, last_at_us{}, max_context{};
};
struct Event {
  std::uint32_t phase{}, start_us{}, duration_us{}, context{}, units{};
};
struct Active {
  std::uint32_t state{}, generation{}, start_us{}, context{}, age_us{};
  bool consistent{};
};
struct Snapshot {
  std::uint32_t now_us{}, lost_completions{}, overlapping_calls{}, busy_reads{};
  bool totals_valid{};
  std::array<Totals, phaseCount> totals{};
  std::array<Active, phaseCount> active{};
  std::array<Event, historySize> history{};
  std::uint32_t history_next{}, history_count{};
  std::uint64_t history_overwritten{};
};
struct Token {
  Phase phase{};
  std::uint32_t start_us{}, context{};
  bool valid{};
};

class FrameRecorder {
 public:
  Token begin(Phase phase, std::uint32_t now, std::uint32_t context = 0) noexcept {
    auto &live = live_[static_cast<unsigned>(phase)];
    std::uint32_t idle = 0;
    if (!live.state.compare_exchange_strong(idle, 1)) {
      overlapping_.fetch_add(1);
      return {phase, now, context, false};
    }
    live.start.store(now);
    live.context.store(context);
    live.generation.fetch_add(1);
    live.state.store(2);
    return {phase, now, context, true};
  }
  void end(Token token, std::uint32_t now, std::uint32_t units = 0) noexcept {
    if (!token.valid) return;
    const auto index = static_cast<unsigned>(token.phase);
    // Unsigned subtraction supports one 32-bit microsecond wrap. The bounded
    // reproduction is shorter than 71 minutes; longer intervals are ambiguous.
    const std::uint32_t elapsed = now - token.start_us;
    if (lock_.test_and_set(std::memory_order_acquire)) {
      lost_.fetch_add(1);
    } else {
      auto &t = totals_[index];
      ++t.count; t.total_us += elapsed; t.units += units;
      t.last_us = elapsed; t.last_at_us = token.start_us;
      if (elapsed > t.max_us) {
        t.max_us = elapsed; t.max_at_us = token.start_us;
        t.max_context = token.context;
      }
      if (elapsed >= slowMicroseconds) {
        history_[history_next_] = {index, token.start_us, elapsed, token.context, units};
        history_next_ = (history_next_ + 1) % historySize;
        if (history_count_ < historySize) ++history_count_;
        else ++history_overwritten_;
      }
      lock_.clear(std::memory_order_release);
    }
    // Even a lost aggregate update MUST clear the live phase. Otherwise a
    // busy HTTP copy could create a false indefinitely stalled operation.
    live_[index].state.store(0);
  }
  void read(Snapshot &out, std::uint32_t now) noexcept {
    out.now_us = now;
    out.totals_valid = !lock_.test_and_set(std::memory_order_acquire);
    if (out.totals_valid) {
      out.totals = totals_; out.history = history_;
      out.history_next = history_next_; out.history_count = history_count_;
      out.history_overwritten = history_overwritten_;
      lock_.clear(std::memory_order_release);
    } else {
      busy_reads_.fetch_add(1);
    }
    for (std::size_t i = 0; i < phaseCount; ++i) {
      auto &a = out.active[i]; auto &live = live_[i];
      a.generation = live.generation.load(); a.state = live.state.load();
      a.start_us = live.start.load(); a.context = live.context.load();
      a.consistent = a.state != 1 && a.state == live.state.load() &&
                     a.generation == live.generation.load();
      a.age_us = a.consistent && a.state == 2 ? now - a.start_us : 0;
      // now is sampled before this copy; a newly begun phase can be newer.
      // Reject that observation rather than reporting a wrapped multi-hour age.
      if (a.age_us > 0x7fffffffU) { a.consistent = false; a.age_us = 0; }
    }
    out.lost_completions = lost_.load();
    out.overlapping_calls = overlapping_.load(); out.busy_reads = busy_reads_.load();
  }
 private:
  friend struct RecorderTestAccess;
  struct Live {
    // 0 idle, 1 publishing metadata, 2 active. All fields atomic: concurrent
    // HTTP observations cannot race on a non-atomic seqlock payload.
    std::atomic<std::uint32_t> state{}, generation{}, start{}, context{};
  };
  static_assert(std::atomic<std::uint32_t>::is_always_lock_free);
  std::array<Live, phaseCount> live_{};
  std::atomic_flag lock_ = ATOMIC_FLAG_INIT;
  std::array<Totals, phaseCount> totals_{};
  std::array<Event, historySize> history_{};
  std::uint32_t history_next_{}, history_count_{};
  std::uint64_t history_overwritten_{};
  std::atomic<std::uint32_t> lost_{}, overlapping_{}, busy_reads_{};
};
} // namespace agon::extender::diagnostics
