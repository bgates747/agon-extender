// PORT-003 Phase D compile/link diagnostic only.
//
// This file exists to retain the complete sink-free Phase C/Phase D closure in
// a P4 ELF. It is not production firmware, defines no frame-consumer contract,
// drives no physical output, and must not be used as hardware qualification.
#include <Arduino.h>

#include <array>
#include <cstdint>

#include "canvas.h"
#include "esp_log.h"
#include "extender/display/p4_display_controller.hpp"
#include "extender/display/p4_frame_service.hpp"

namespace display = agon::extender::display;
namespace {

display::P4DisplayController controller(display::defaultDisplayAllocator());
display::P4FrameService frame_service(controller, 64);

}  // namespace

void setup() {
  ESP_LOGI("presentation", "PORT-003 Phase D compile/link diagnostic");
  auto configured = controller.configure(
      {64, 48, display::NativePixelFormat::PALETTE4, false, 0});
  if (configured != display::ConfigureResult::Ok) {
    ESP_LOGE("presentation", "configuration failed: %u",
             static_cast<unsigned>(configured));
    return;
  }

  controller.createPalette(10);
  controller.setItemInPalette(10, 1, 255, 255, 0);
  std::uint16_t signals[] = {24, 0, 24, 10};
  controller.updateSignalList(signals, 2);
  controller.updateRGB2PaletteLUT();
  fabgl::Canvas canvas(&controller);
  canvas.setPixel(0, 0);
  canvas.noOp();

  std::array<display::PresentationRGB888, 8> row{};
  auto composed = controller.composeVisibleRegionQuiescent(
      {0, 0, row.size(), 1}, row.data(), row.size());
  ESP_LOGI("presentation", "composition_result=%u frame_service=%p",
           static_cast<unsigned>(composed), static_cast<void *>(&frame_service));
  auto started = frame_service.start();
  if (started == display::P4FrameServiceStartResult::Ok) frame_service.stop();
  ESP_LOGI("presentation", "frame_service_result=%u",
           static_cast<unsigned>(started));
}

void loop() { delay(1000); }
