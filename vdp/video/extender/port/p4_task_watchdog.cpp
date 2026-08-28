// ESP32-P4 correction for the retained VDP watchdog binding.
//
// Provenance and removal condition are documented in p4_task_watchdog.hpp.
// Keep this target-specific adapter until the pinned Arduino helper removes
// both ESP-IDF IDLE subscriptions and their registered hooks itself.

#include "extender/port/p4_task_watchdog.hpp"

#include <esp_log.h>
#include <esp_task_wdt.h>

#ifndef CONFIG_ESP_TASK_WDT_TIMEOUT_S
#error "The P4 retained-VDP watchdog adapter requires an ESP-IDF timeout"
#endif

namespace agon::extender::port {
namespace {

constexpr char kTag[] = "extender_watchdog";

}  // namespace

bool disableRetainedVdpIdleWatchdogs() {
  esp_task_wdt_config_t config{};
  config.timeout_ms = CONFIG_ESP_TASK_WDT_TIMEOUT_S * 1000U;
  config.idle_core_mask = 0;
#if defined(CONFIG_ESP_TASK_WDT_PANIC) && CONFIG_ESP_TASK_WDT_PANIC
  config.trigger_panic = true;
#else
  config.trigger_panic = false;
#endif

  auto const result = esp_task_wdt_reconfigure(&config);
  if (result != ESP_OK) {
    ESP_LOGE(kTag, "failed to disable retained VDP IDLE watchdogs: error=%d",
             static_cast<int>(result));
    return false;
  }

  ESP_LOGI(kTag, "%s", "retained VDP IDLE watchdog subscriptions disabled");
  return true;
}

}  // namespace agon::extender::port
