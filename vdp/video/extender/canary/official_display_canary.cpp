// PORT-003 Phase E compile/link diagnostic only.
//
// This translation unit deliberately includes the adapted official screen
// facade, which in turn carries the retained official Teletext implementation.
// It proves a P4 build closure but defines no VDU transport, physical input,
// frame consumer, output sink, deployment image, or hardware qualification.
#include <Arduino.h>

#include <cstdarg>

#include "esp_log.h"

void debug_log(char const *, ...) {}

#include "agon_screen.h"

void setup() {
  ESP_LOGI("official-display", "PORT-003 Phase E compile/link diagnostic");
  auto teletext = changeMode(7);
  if (teletext == 0) {
    ttxtMode = false;  // Exact vdu_mode() owns this transition in production.
    auto bitmap = changeMode(8);
    setMouseCursorPos(1, 1);
    _VGAController->frameCounter = 0xFFFF'FFFEu;
    _VGAController->advanceFrameCounter(2);
    ESP_LOGI("official-display", "teletext=%d bitmap=%d mode=%u frame=%lu",
             teletext, bitmap, videoMode,
             static_cast<unsigned long>(
                 static_cast<std::uint32_t>(_VGAController->frameCounter)));
  } else {
    ESP_LOGE("official-display", "Teletext initialization failed: %d", teletext);
  }
}

void loop() { delay(1000); }
