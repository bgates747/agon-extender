// Host scheduling substrate exercises the allocator-specific worker lifecycle.
#pragma once
#include "freertos/task.h"
#include <mutex>
using portMUX_TYPE = std::mutex;
#define portMUX_INITIALIZER_UNLOCKED {}
#define portENTER_CRITICAL(mux) (mux)->lock()
#define portEXIT_CRITICAL(mux) (mux)->unlock()
inline BaseType_t xTaskCreatePinnedToCoreWithCaps(TaskFunction_t fn, const char *name,
    uint32_t stack, void *ctx, UBaseType_t priority, TaskHandle_t *out, BaseType_t core,
    unsigned) {
  return xTaskCreatePinnedToCore(fn,name,stack,ctx,priority,out,core);
}
inline void vTaskDeleteWithCaps(TaskHandle_t task) { vTaskDelete(task); }
