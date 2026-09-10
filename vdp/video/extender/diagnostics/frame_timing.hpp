// Diagnostic scopes compile away outside the selected AUDIT-006 console.
#pragma once
#include "frame_recorder.hpp"
#if defined(AGON_EXTENDER_FRAME_TIMING)
#include <string>
#endif
namespace agon::extender::diagnostics {
#if defined(AGON_EXTENDER_FRAME_TIMING)
FrameRecorder &frameRecorder() noexcept;
std::uint32_t timingNow() noexcept;
std::string timingJson(); // HTTP task only; never called from measured paths
class Scope {
 public:
  explicit Scope(Phase phase, std::uint32_t context = 0) noexcept
      : token_(frameRecorder().begin(phase, timingNow(), context)) {}
  ~Scope() { frameRecorder().end(token_, timingNow(), units_); }
  void units(std::uint32_t value) noexcept { units_ = value; }
  Scope(Scope const &) = delete;
  Scope &operator=(Scope const &) = delete;
 private:
  Token token_;
  std::uint32_t units_{};
};
#else
class Scope {
 public:
  explicit Scope(Phase, std::uint32_t = 0) noexcept {}
  void units(std::uint32_t) noexcept {}
};
#endif
} // namespace agon::extender::diagnostics
