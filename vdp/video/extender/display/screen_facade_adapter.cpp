// See screen_facade_adapter.hpp. The rollback below is intentionally local to
// the P4 replacement seam: official vdu_mode() still owns requested/old/mode-1
// fallback and remains byte-identical to agon-vdp v2.16.0.
#include "extender/display/screen_facade_adapter.hpp"

#include <cstdio>
#include <limits>

namespace agon::extender::display {

bool parseOfficialModeline(char const *modeline,
                           OfficialModeLine &result) noexcept {
  if (modeline == nullptr) return false;
  unsigned int width = 0, height = 0, refresh = 0;
  char trailing = '\0';
  if (std::sscanf(modeline, "\"%ux%u@%uHz\"%c", &width, &height, &refresh,
                  &trailing) != 4 || trailing != ' ') {
    return false;
  }
  if (width == 0 || height == 0 || refresh == 0 ||
      width > std::numeric_limits<std::uint16_t>::max() ||
      height > std::numeric_limits<std::uint16_t>::max() ||
      refresh > std::numeric_limits<std::uint16_t>::max()) {
    return false;
  }
  result = {static_cast<std::uint16_t>(width),
            static_cast<std::uint16_t>(height),
            static_cast<std::uint16_t>(refresh)};
  return true;
}

bool nativeFormatForColourDepth(std::uint8_t colours,
                                NativePixelFormat &result) noexcept {
  switch (colours) {
    case 2: result = NativePixelFormat::PALETTE2; return true;
    case 4: result = NativePixelFormat::PALETTE4; return true;
    case 8: result = NativePixelFormat::PALETTE8; return true;
    case 16: result = NativePixelFormat::PALETTE16; return true;
    case 64: result = NativePixelFormat::SBGR2222; return true;
    default: return false;
  }
}

std::uint64_t periodForRefresh(std::uint16_t refresh_hz) noexcept {
  return refresh_hz == 0 ? 0 : (1'000'000ULL + refresh_hz / 2) / refresh_hz;
}

ScreenFacadeAdapter::ScreenFacadeAdapter(
    P4DisplayController &controller,
    FrameServiceBinding frame_service) noexcept
    : controller_(controller), frame_service_(frame_service) {}

bool ScreenFacadeAdapter::validBinding() const noexcept {
  return frame_service_.context != nullptr && frame_service_.running != nullptr &&
         frame_service_.stop != nullptr && frame_service_.start != nullptr;
}

bool ScreenFacadeAdapter::start(std::uint64_t period_microseconds) noexcept {
  return validBinding() && frame_service_.start(frame_service_.context,
                                                period_microseconds);
}

FacadeConfigureResult ScreenFacadeAdapter::configure(
    std::uint8_t colours, char const *modeline,
    bool double_buffered) noexcept {
  NativePixelFormat format{};
  if (!nativeFormatForColourDepth(colours, format)) {
    return FacadeConfigureResult::InvalidColourDepth;
  }
  OfficialModeLine requested_timing{};
  if (!parseOfficialModeline(modeline, requested_timing)) {
    return FacadeConfigureResult::InvalidModeline;
  }
  if (!validBinding()) return FacadeConfigureResult::FrameServiceUnavailable;

  ModeDescriptor requested{
      requested_timing.width, requested_timing.height, format,
      double_buffered, 0xC0};
  bool was_running = frame_service_.running(frame_service_.context);
  if (was_running) frame_service_.stop(frame_service_.context);

  last_controller_result_ = controller_.configure(requested);
  if (last_controller_result_ != ConfigureResult::Ok) {
    if (was_running && configured_) start(periodForRefresh(timing_.refresh_hz));
    return FacadeConfigureResult::StorageUnavailable;
  }

  if (!start(periodForRefresh(requested_timing.refresh_hz))) {
    if (configured_) {
      ConfigureResult rollback = controller_.configure(mode_);
      if (rollback != ConfigureResult::Ok ||
          (was_running && !start(periodForRefresh(timing_.refresh_hz)))) {
        last_controller_result_ = rollback;
        return FacadeConfigureResult::RollbackFailed;
      }
    }
    return FacadeConfigureResult::FrameServiceUnavailable;
  }

  mode_ = requested;
  timing_ = requested_timing;
  configured_ = true;
  return FacadeConfigureResult::Ok;
}

bool ScreenFacadeAdapter::configured() const noexcept { return configured_; }
ModeDescriptor const &ScreenFacadeAdapter::mode() const noexcept { return mode_; }
OfficialModeLine const &ScreenFacadeAdapter::timing() const noexcept { return timing_; }
ConfigureResult ScreenFacadeAdapter::lastControllerResult() const noexcept {
  return last_controller_result_;
}

}  // namespace agon::extender::display
