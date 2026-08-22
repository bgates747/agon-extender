// PORT-003 Phase C host-only task notifications with counted wake semantics.
#pragma once

#include "FreeRTOS.h"

#include <condition_variable>
#include <mutex>
#include <thread>

struct PhaseCHostTask {
  std::mutex mutex;
  std::condition_variable condition;
  std::uint32_t notifications{};
};

inline thread_local PhaseCHostTask phase_c_current_task;

inline TaskHandle_t xTaskGetCurrentTaskHandle() { return &phase_c_current_task; }

inline std::uint32_t ulTaskNotifyTake(BaseType_t clear, TickType_t timeout) {
  auto &task = phase_c_current_task;
  std::unique_lock lock(task.mutex);
  if (timeout == portMAX_DELAY) {
    task.condition.wait(lock, [&] { return task.notifications != 0; });
  } else if (task.notifications == 0) {
    return 0;
  }
  std::uint32_t result = task.notifications;
  if (clear) task.notifications = 0;
  else --task.notifications;
  return result;
}

inline BaseType_t xTaskNotifyGive(TaskHandle_t handle) {
  if (handle == nullptr) return pdFALSE;
  {
    std::lock_guard lock(handle->mutex);
    ++handle->notifications;
  }
  handle->condition.notify_one();
  return pdTRUE;
}

inline void vTaskNotifyGiveFromISR(TaskHandle_t handle, BaseType_t *) {
  xTaskNotifyGive(handle);
}

inline void vTaskDelete(TaskHandle_t) {}
inline void taskYIELD() { std::this_thread::yield(); }
