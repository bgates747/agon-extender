// PORT-003 Phase C host-only bounded blocking byte-copy queue.
#pragma once

#include "FreeRTOS.h"

#include <condition_variable>
#include <cstring>
#include <deque>
#include <mutex>
#include <vector>

struct PhaseCHostQueue {
  std::size_t capacity;
  std::size_t item_size;
  std::mutex mutex;
  std::condition_variable readable;
  std::condition_variable writable;
  std::deque<std::vector<std::uint8_t>> items;
};

inline QueueHandle_t xQueueCreate(UBaseType_t length, UBaseType_t item_size) {
  return new PhaseCHostQueue{length, item_size, {}, {}, {}, {}};
}

inline void vQueueDelete(QueueHandle_t queue) { delete queue; }

inline BaseType_t xQueueSendToBack(QueueHandle_t queue, void const *item,
                                   TickType_t timeout) {
  if (queue == nullptr || item == nullptr) return pdFALSE;
  std::unique_lock lock(queue->mutex);
  if (timeout == portMAX_DELAY) {
    queue->writable.wait(lock, [&] { return queue->items.size() < queue->capacity; });
  } else if (queue->items.size() >= queue->capacity) {
    return pdFALSE;
  }
  std::vector<std::uint8_t> copy(queue->item_size);
  std::memcpy(copy.data(), item, queue->item_size);
  queue->items.push_back(std::move(copy));
  lock.unlock();
  queue->readable.notify_one();
  return pdTRUE;
}

inline BaseType_t xQueueReceive(QueueHandle_t queue, void *item,
                                TickType_t timeout) {
  if (queue == nullptr || item == nullptr) return pdFALSE;
  std::unique_lock lock(queue->mutex);
  if (timeout == portMAX_DELAY) {
    queue->readable.wait(lock, [&] { return !queue->items.empty(); });
  } else if (queue->items.empty()) {
    return pdFALSE;
  }
  std::memcpy(item, queue->items.front().data(), queue->item_size);
  queue->items.pop_front();
  lock.unlock();
  queue->writable.notify_one();
  return pdTRUE;
}

inline BaseType_t xQueueReceiveFromISR(QueueHandle_t queue, void *item,
                                       BaseType_t *) {
  return xQueueReceive(queue, item, 0);
}

inline BaseType_t xQueuePeek(QueueHandle_t queue, void *item,
                             TickType_t timeout) {
  if (queue == nullptr || item == nullptr) return pdFALSE;
  std::unique_lock lock(queue->mutex);
  if (timeout == portMAX_DELAY) {
    queue->readable.wait(lock, [&] { return !queue->items.empty(); });
  } else if (queue->items.empty()) {
    return pdFALSE;
  }
  std::memcpy(item, queue->items.front().data(), queue->item_size);
  return pdTRUE;
}

inline UBaseType_t uxQueueMessagesWaiting(QueueHandle_t queue) {
  if (queue == nullptr) return 0;
  std::lock_guard lock(queue->mutex);
  return static_cast<UBaseType_t>(queue->items.size());
}
