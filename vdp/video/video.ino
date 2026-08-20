// Temporary SETUP-001 hybrid bring-up canary. The official agon-vdp video.ino
// replaces this file unchanged at the source-import gate.
//
// This r02 revision reports through ESP-IDF logging because the first physical
// run proved that the board's USB Serial/JTAG console carries ESP-IDF logs while
// Arduino's global Serial object remains UART0 unless separate Arduino USB CDC
// macros remap it. Qualification should observe the proven console rather than
// change an upstream Arduino API mapping solely for this temporary file.

#include <Arduino.h>

#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_system.h"
#include "extender/version.h"

namespace {

constexpr char kLogTag[] = "setup-001-canary";

void printCanaryIdentity() {
  esp_chip_info_t chip{};
  esp_chip_info(&chip);

  uint32_t flashSize = 0;
  const esp_err_t flashResult = esp_flash_get_size(nullptr, &flashSize);
  const esp_partition_t *running = esp_ota_get_running_partition();

  ESP_LOGI(kLogTag, "source_identity=%s", AGON_EXTENDER_SOURCE_ID);
  ESP_LOGI(kLogTag, "build_id=%s", AGON_EXTENDER_BUILD_ID);
  ESP_LOGI(kLogTag, "chip_model=%d cores=%d revision=%d.%d",
           static_cast<int>(chip.model), chip.cores, chip.revision / 100,
           chip.revision % 100);
  ESP_LOGI(kLogTag, "cpu_mhz=%u", getCpuFrequencyMhz());
  ESP_LOGI(kLogTag, "flash_bytes=%u flash_probe=%s", flashSize,
           esp_err_to_name(flashResult));
  ESP_LOGI(kLogTag, "psram_bytes=%u psram_free=%u caps_total=%u",
           ESP.getPsramSize(), ESP.getFreePsram(),
           heap_caps_get_total_size(MALLOC_CAP_SPIRAM));
  ESP_LOGI(kLogTag, "running_partition=%s offset=0x%08x size=0x%08x",
           running == nullptr ? "none" : running->label,
           running == nullptr ? 0 : running->address,
           running == nullptr ? 0 : running->size);
  ESP_LOGI(kLogTag, "No Extender GPIO is configured");
}

}  // namespace

void setup() {
  printCanaryIdentity();
}

void loop() {
  delay(1000);
}
