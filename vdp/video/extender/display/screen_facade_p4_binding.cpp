// PORT-003 Phase E platform binding for ScreenFacadeAdapter. Keeping this
// target-only dependency separate makes the modeline/configuration state
// machine directly host-qualifiable without mocking ESP-IDF headers.
#include "extender/display/screen_facade_adapter.hpp"

#include "extender/display/p4_frame_service.hpp"

namespace agon::extender::display {

FrameServiceBinding bindFrameService(P4FrameService &service) noexcept {
  return {
      &service,
      [](void *context) noexcept {
        return static_cast<P4FrameService *>(context)->running();
      },
      [](void *context) noexcept {
        static_cast<P4FrameService *>(context)->stop();
      },
      [](void *context, std::uint64_t period) noexcept {
        P4FrameServiceConfig config{};
        config.period_microseconds = period;
        return static_cast<P4FrameService *>(context)->start(config) ==
               P4FrameServiceStartResult::Ok;
      },
  };
}

}  // namespace agon::extender::display
