// Keep the established queue behavior; expose completed enqueues so the
// scheduling fixture never guesses whether its swap request reached the FIFO.
#pragma once
#include "../../../../docs/tasks/PORT-003/phase-c/tests/compat/freertos/queue.h"
#include <atomic>

inline std::atomic<unsigned> hdmi_test_enqueued{};
inline BaseType_t hdmiTestQueueSendToBack(QueueHandle_t queue, void const *item,
                                         TickType_t timeout) {
  auto const result = xQueueSendToBack(queue, item, timeout);
  if (result == pdTRUE) ++hdmi_test_enqueued;
  return result;
}
#define xQueueSendToBack hdmiTestQueueSendToBack
