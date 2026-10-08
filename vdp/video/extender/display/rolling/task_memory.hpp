// HDMI02-F: internal SRAM belongs to the three scanout DMA slots. These
// task-only workers do not perform flash/NVS/cache-disabled operations. Keep
// their existing stack sizes, priorities and affinities; IDF keeps task control
// blocks and interrupt stacks internal. Re-review before adding cache-off work.
// The capability-created tasks MUST use the matching deletion function.
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "freertos/idf_additions.h"
#include "esp_heap_caps.h"
#endif
namespace agon::extender {
inline BaseType_t createVideoWorker(TaskFunction_t entry,const char *name,
    uint32_t bytes,void *context,UBaseType_t priority,TaskHandle_t *handle,BaseType_t core) {
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  return xTaskCreatePinnedToCoreWithCaps(entry,name,bytes,context,priority,handle,
      core,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
#else
  return xTaskCreatePinnedToCore(entry,name,bytes,context,priority,handle,core);
#endif
}
inline void deleteVideoWorker(TaskHandle_t handle) {
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  vTaskDeleteWithCaps(handle);
#else
  vTaskDelete(handle);
#endif
}
}
