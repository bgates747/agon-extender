// PORT-003 Phase E narrow binding for the retained official screen facade.
//
// This file translates only official modeline metadata into the project-owned
// logical controller and frame clock. It does not interpret VGA electrical
// timing, own VDU fallback, or define any physical output sink.
#pragma once

#include <cstdint>

#include "extender/display/p4_display_controller.hpp"

namespace agon::extender::display {

struct OfficialModeLine {
  std::uint16_t width;
  std::uint16_t height;
  std::uint16_t refresh_hz;
};

struct FrameServiceBinding {
  void *context;
  bool (*running)(void *context) noexcept;
  void (*stop)(void *context) noexcept;
  bool (*start)(void *context, std::uint64_t period_microseconds) noexcept;
};

enum class FacadeConfigureResult : std::uint8_t {
  Ok,
  InvalidColourDepth,
  InvalidModeline,
  StorageUnavailable,
  FrameServiceUnavailable,
  RollbackFailed,
};

bool parseOfficialModeline(char const *modeline,
                           OfficialModeLine &result) noexcept;
bool nativeFormatForColourDepth(std::uint8_t colours,
                                NativePixelFormat &result) noexcept;
std::uint64_t periodForRefresh(std::uint16_t refresh_hz) noexcept;

class ScreenFacadeAdapter final {
 public:
  ScreenFacadeAdapter(P4DisplayController &controller,
                      FrameServiceBinding frame_service) noexcept;

  FacadeConfigureResult configure(std::uint8_t colours, char const *modeline,
                                  bool double_buffered) noexcept;
  bool configured() const noexcept;
  ModeDescriptor const &mode() const noexcept;
  OfficialModeLine const &timing() const noexcept;
  ConfigureResult lastControllerResult() const noexcept;

 private:
  bool validBinding() const noexcept;
  bool start(std::uint64_t period_microseconds) noexcept;

  P4DisplayController &controller_;
  FrameServiceBinding frame_service_;
  ModeDescriptor mode_{};
  OfficialModeLine timing_{};
  ConfigureResult last_controller_result_{ConfigureResult::Ok};
  bool configured_{};
};

class P4FrameService;
FrameServiceBinding bindFrameService(P4FrameService &service) noexcept;

}  // namespace agon::extender::display
