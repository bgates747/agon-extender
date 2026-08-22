// PORT-003 host-only synchronous primitive FIFO; see ../README.md.
#pragma once

#include "FreeRTOS.h"

#include <cstring>
#include <deque>
#include <vector>

struct PhaseBHostQueue {
  std::size_t capacity;
  std::size_t item_size;
  std::deque<std::vector<std::uint8_t>> items;
};

inline QueueHandle_t xQueueCreate(UBaseType_t length, UBaseType_t item_size) {
  return new PhaseBHostQueue{length, item_size, {}};
}

inline void vQueueDelete(QueueHandle_t queue) { delete queue; }

inline BaseType_t xQueueSendToBack(QueueHandle_t queue, void const *item,
                                   TickType_t) {
  if (queue == nullptr || item == nullptr || queue->items.size() >= queue->capacity)
    return pdFALSE;
  std::vector<std::uint8_t> copy(queue->item_size);
  std::memcpy(copy.data(), item, queue->item_size);
  queue->items.push_back(std::move(copy));
  return pdTRUE;
}

inline BaseType_t xQueueReceive(QueueHandle_t queue, void *item, TickType_t) {
  if (queue == nullptr || item == nullptr || queue->items.empty()) return pdFALSE;
  std::memcpy(item, queue->items.front().data(), queue->item_size);
  queue->items.pop_front();
  return pdTRUE;
}

inline BaseType_t xQueueReceiveFromISR(QueueHandle_t queue, void *item,
                                       BaseType_t *) {
  return xQueueReceive(queue, item, 0);
}

inline BaseType_t xQueuePeek(QueueHandle_t queue, void *item, TickType_t) {
  if (queue == nullptr || item == nullptr || queue->items.empty()) return pdFALSE;
  std::memcpy(item, queue->items.front().data(), queue->item_size);
  return pdTRUE;
}

inline UBaseType_t uxQueueMessagesWaiting(QueueHandle_t queue) {
  return queue == nullptr ? 0 : static_cast<UBaseType_t>(queue->items.size());
}
