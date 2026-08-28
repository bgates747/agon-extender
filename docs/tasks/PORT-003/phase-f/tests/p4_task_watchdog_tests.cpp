#include <cassert>

#include "esp_task_wdt.h"
#include "extender/port/p4_task_watchdog.hpp"

namespace {

esp_task_wdt_config_t observed{};
esp_err_t nextResult = ESP_OK;
int calls = 0;

}  // namespace

extern "C" esp_err_t esp_task_wdt_reconfigure(
    esp_task_wdt_config_t const *config) {
  assert(config != nullptr);
  observed = *config;
  ++calls;
  return nextResult;
}

int main() {
  using agon::extender::port::disableRetainedVdpIdleWatchdogs;

  assert(disableRetainedVdpIdleWatchdogs());
  assert(calls == 1);
  assert(observed.timeout_ms == 5000U);
  assert(observed.idle_core_mask == 0U);
  assert(!observed.trigger_panic);

  nextResult = ESP_FAIL;
  assert(!disableRetainedVdpIdleWatchdogs());
  assert(calls == 2);
}
