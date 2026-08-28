#pragma once

#include <cstdint>

using esp_err_t = int;

constexpr esp_err_t ESP_OK = 0;
constexpr esp_err_t ESP_FAIL = -1;

struct esp_task_wdt_config_t {
  std::uint32_t timeout_ms;
  std::uint32_t idle_core_mask;
  bool trigger_panic;
};

extern "C" esp_err_t esp_task_wdt_reconfigure(
    esp_task_wdt_config_t const *config);
