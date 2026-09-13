// PORT-003 optional output-boundary diagnosis, independent of VDP primitive timing.
// Writers never allocate, log, block for the recorder, or perform network I/O.
#pragma once
#include <cstdint>

#if defined(AGON_EXTENDER_VIDEO_TIMING)
#include "frame_recorder.hpp"
#include <esp_timer.h>
#include <cstdio>
#include <memory>
#include <new>
#include <string>
#endif

namespace agon::extender::diagnostics {
enum class VideoPhase { Snapshot, SocketSend };

#if defined(AGON_EXTENDER_VIDEO_TIMING)
inline FrameRecorder videoRecorder;
inline std::uint32_t videoTimingNow() noexcept {
  return static_cast<std::uint32_t>(esp_timer_get_time());
}
inline Phase videoRecorderPhase(VideoPhase phase) noexcept {
  return phase == VideoPhase::Snapshot ? Phase::Snapshot : Phase::TxComplete;
}

class VideoTimingScope {
 public:
  explicit VideoTimingScope(VideoPhase phase, std::uint32_t context) noexcept
      : token_(videoRecorder.begin(videoRecorderPhase(phase), videoTimingNow(), context)) {}
  ~VideoTimingScope() { finish(0); }
  // Positive units identify a successful complete operation. An early exit or
  // explicit failure records zero units; consumers reject mixed/failed windows.
  void finish(std::uint32_t units) noexcept {
    if (!token_.valid) return;
    videoRecorder.end(token_, videoTimingNow(), units);
    token_.valid = false;
  }
  VideoTimingScope(VideoTimingScope const &) = delete;
  VideoTimingScope &operator=(VideoTimingScope const &) = delete;
 private:
  Token token_;
};

// HTTP task only. A separate instance avoids enabling old parser/primitive
// probes merely to measure two output boundaries. No runtime reset endpoint.
inline std::string videoTimingJson() {
  std::unique_ptr<Snapshot> s(new (std::nothrow) Snapshot{});
  if (!s) return "";
  videoRecorder.read(*s, videoTimingNow());
  std::string out;
  out.reserve(2048);
  auto add = [&](char const *format, auto... args) {
    char text[512];
    const int n = std::snprintf(text, sizeof(text), format, args...);
    if (n > 0 && static_cast<std::size_t>(n) < sizeof(text)) out.append(text, n);
  };
  add("{\"schema\":1,\"clock_bits\":32,\"now_us\":%u,\"totals_valid\":%s,"
      "\"lost_completions\":%u,\"overlapping_calls\":%u,\"busy_reads\":%u,\"phases\":[",
      s->now_us, s->totals_valid ? "true" : "false", s->lost_completions,
      s->overlapping_calls, s->busy_reads);
  const Phase phases[] = {Phase::Snapshot, Phase::TxComplete};
  const char *names[] = {"snapshot", "socket_send"};
  for (unsigned i = 0; i < 2; ++i) {
    const auto index = static_cast<unsigned>(phases[i]);
    const auto &t = s->totals[index];
    const auto &a = s->active[index];
    add("%s{\"name\":\"%s\",\"count\":%llu,\"total_us\":%llu,\"units\":%llu,"
        "\"max_us\":%u,\"last_us\":%u,\"last_at_us\":%u,\"max_context\":%u,",
        i ? "," : "", names[i], static_cast<unsigned long long>(t.count),
        static_cast<unsigned long long>(t.total_us), static_cast<unsigned long long>(t.units),
        t.max_us, t.last_us, t.last_at_us, t.max_context);
    add("\"active\":{\"state\":%u,\"generation\":%u,\"context\":%u,"
        "\"age_us\":%u,\"consistent\":%s}}", a.state, a.generation,
        a.context, a.age_us, a.consistent ? "true" : "false");
  }
  out += "]}";
  return out;
}
#else
class VideoTimingScope {
 public:
  explicit VideoTimingScope(VideoPhase, std::uint32_t) noexcept {}
  void finish(std::uint32_t) noexcept {}
};
#endif
} // namespace agon::extender::diagnostics
