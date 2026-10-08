// HDMI02-M02c, P4 rolling output only: preserve FabGL's primitive queue while
// moving its payload out of scarce internal RAM. The P4 drawing task consumes
// it through getPrimitive(), never the classic VGA getPrimitiveISR() path.
// Three scanout DMA slots and all RTOS control structures remain internal.
// This is processor-specific allocation placement, not a queue-size/scheduling
// change or an upstream allocation-failure workaround. See HDMI-002/MEMORY-RESULTS.
#pragma once
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/idf_additions.h"

namespace agon::extender::display {
inline QueueHandle_t createPrimitiveQueue(UBaseType_t count, UBaseType_t itemSize) {
  auto *control = static_cast<StaticQueue_t *>(heap_caps_malloc(
      sizeof(StaticQueue_t), MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
  auto *payload = static_cast<uint8_t *>(heap_caps_malloc(
      size_t(count) * itemSize, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  if (!control || !payload) {
    heap_caps_free(payload); heap_caps_free(control); return nullptr;
  }
  auto queue = xQueueCreateStatic(count, itemSize, payload, control);
  if (!queue) { heap_caps_free(payload); heap_caps_free(control); }
  return queue;
}
inline void deletePrimitiveQueue(QueueHandle_t queue) {
  // IDF obtains both static buffers before deleting the queue, then frees each
  // through heap_caps_free; their different placement capabilities are retained.
  vQueueDeleteWithCaps(queue);
}
}
