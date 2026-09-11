// Host scheduling substrate for the real StockP4Service. No priority/affinity
// or timing-accuracy claim: target execution remains a separate gate.
#pragma once
#include "freertos/FreeRTOS.h"
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>

struct PhaseCHostTask {
  std::mutex mutex;
  std::condition_variable condition;
  std::uint32_t notifications{};
  bool deleted{};
  std::thread thread;
};
inline thread_local PhaseCHostTask host_caller;
inline thread_local TaskHandle_t host_task{};
inline std::atomic<unsigned> host_stale_notifications{};
inline int host_creation_fail_after{-1}; // serialized lifecycle-owner fault injection
inline std::vector<std::unique_ptr<PhaseCHostTask>> host_managed_tasks;
inline thread_local std::function<void()> phase_c_yield_hook;

inline TaskHandle_t xTaskGetCurrentTaskHandle() { return host_task ? host_task : &host_caller; }
inline std::uint32_t ulTaskNotifyTake(BaseType_t clear, TickType_t timeout) {
  auto &t=*xTaskGetCurrentTaskHandle();
  std::unique_lock lock(t.mutex);
  if (timeout == portMAX_DELAY) t.condition.wait(lock,[&]{return t.notifications != 0;});
  else if (timeout) t.condition.wait_for(lock,std::chrono::milliseconds(timeout),[&]{return t.notifications != 0;});
  auto result=t.notifications;
  if (clear) t.notifications=0; else if(t.notifications) --t.notifications;
  return result;
}
inline BaseType_t xTaskNotifyGive(TaskHandle_t handle) {
  if (!handle) return pdFALSE;
  { std::lock_guard lock(handle->mutex);
    if (handle->deleted) { ++host_stale_notifications; return pdFALSE; }
    ++handle->notifications;
  }
  handle->condition.notify_all(); return pdTRUE;
}
inline void vTaskNotifyGiveFromISR(TaskHandle_t h,BaseType_t *) { xTaskNotifyGive(h); }
inline BaseType_t xTaskCreatePinnedToCore(void (*entry)(void *), char const *, unsigned, void *arg,
                                        unsigned, TaskHandle_t *out, int) {
  if (host_creation_fail_after==0) {host_creation_fail_after=-1;return pdFALSE;}
  if (host_creation_fail_after>0) --host_creation_fail_after;
  auto task=std::make_unique<PhaseCHostTask>();
  auto raw=task.get(); *out=raw;
  host_managed_tasks.push_back(std::move(task));
  raw->thread=std::thread([=]{host_task=raw; entry(arg); host_task=nullptr;});
  return pdPASS;
}
inline void vTaskSuspend(TaskHandle_t handle) {
  auto &t=*(handle ? handle : xTaskGetCurrentTaskHandle());
  std::unique_lock lock(t.mutex);
  t.condition.wait(lock,[&]{return t.deleted;});
}
inline void vTaskDelete(TaskHandle_t h) {
  if (!h) return;
  { std::lock_guard lock(h->mutex); h->deleted=true; }
  h->condition.notify_all();
  h->thread.join();
  // Retain retired handles for the fixture so late notifications are detected
  // deterministically instead of relying on a host allocator's use-after-free.
}
inline void taskYIELD() { if(phase_c_yield_hook) phase_c_yield_hook(); std::this_thread::yield(); }
inline void vTaskDelay(TickType_t ticks) { std::this_thread::sleep_for(std::chrono::milliseconds(ticks)); }
