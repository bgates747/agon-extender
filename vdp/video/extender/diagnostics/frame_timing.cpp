// AUDIT-006: only the selected diagnostic console links this translation unit.
#include "frame_timing.hpp"
#include <esp_timer.h>
#include <cstdio>
#include <memory>
#include <new>

namespace agon::extender::diagnostics {
namespace { FrameRecorder recorder; }
FrameRecorder &frameRecorder() noexcept { return recorder; }
std::uint32_t timingNow() noexcept { return static_cast<std::uint32_t>(esp_timer_get_time()); }
std::string timingJson() {
  // HTTP's stack is small. Allocation/formatting is confined to this reader;
  // frame/parse writers only try the fixed recorder lock and never wait for it.
  std::unique_ptr<Snapshot> s(new (std::nothrow) Snapshot{});
  if (!s) return "";
  frameRecorder().read(*s, timingNow());
  std::string result; result.reserve(12000);
  auto add = [&](const char *fmt, auto... args) {
    char b[512]; const int n = std::snprintf(b, sizeof(b), fmt, args...);
    if (n > 0 && static_cast<std::size_t>(n) < sizeof(b)) result.append(b, n);
  };
  add("{\"schema\":1,\"now_us\":%u,\"totals_valid\":%s,\"lost_completions\":%u,"
      "\"overlapping_calls\":%u,\"busy_reads\":%u,\"slow_threshold_us\":%u,\"phases\":[",
      s->now_us, s->totals_valid ? "true" : "false", s->lost_completions,
      s->overlapping_calls, s->busy_reads, slowMicroseconds);
  for (std::size_t i = 0; i < phaseCount; ++i) {
    auto &t = s->totals[i]; auto &a = s->active[i];
    add("%s{\"name\":\"%s\",\"count\":%llu,\"total_us\":%llu,\"units\":%llu,"
        "\"max_us\":%u,\"max_at_us\":%u,\"max_context\":%u,\"last_us\":%u,\"last_at_us\":%u,",
        i ? "," : "", phaseNames[i], static_cast<unsigned long long>(t.count),
        static_cast<unsigned long long>(t.total_us), static_cast<unsigned long long>(t.units),
        t.max_us, t.max_at_us, t.max_context, t.last_us, t.last_at_us);
    add("\"active\":{\"state\":%u,\"generation\":%u,\"start_us\":%u,\"context\":%u,"
        "\"age_us\":%u,\"consistent\":%s}}", a.state, a.generation, a.start_us,
        a.context, a.age_us, a.consistent ? "true" : "false");
  }
  add("],\"history_overwritten\":%llu,\"history\":[", static_cast<unsigned long long>(s->history_overwritten));
  for (unsigned i = 0; i < s->history_count; ++i) {
    auto &e = s->history[(s->history_next + historySize - s->history_count + i) % historySize];
    add("%s{\"phase\":\"%s\",\"start_us\":%u,\"duration_us\":%u,\"context\":%u,\"units\":%u}",
        i ? "," : "", phaseNames[e.phase], e.start_us, e.duration_us, e.context, e.units);
  }
  result += "]}";
  return result;
}
} // namespace agon::extender::diagnostics
