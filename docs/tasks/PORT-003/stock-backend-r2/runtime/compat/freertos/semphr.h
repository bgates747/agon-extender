#pragma once
#include "freertos/FreeRTOS.h"
#include <condition_variable>
#include <mutex>
#include <chrono>
struct StockHostSemaphore { std::mutex mutex; std::condition_variable condition; bool available{}; };
inline SemaphoreHandle_t xSemaphoreCreateBinary() { return new StockHostSemaphore; }
inline SemaphoreHandle_t xSemaphoreCreateMutex() { auto s=new StockHostSemaphore; s->available=true; return s; }
inline BaseType_t xSemaphoreTake(SemaphoreHandle_t handle,TickType_t timeout) {
  auto &s=*static_cast<StockHostSemaphore *>(handle);
  std::unique_lock lock(s.mutex);
  if (timeout==portMAX_DELAY) s.condition.wait(lock,[&]{return s.available;});
  else if(timeout) s.condition.wait_for(lock,std::chrono::milliseconds(timeout),[&]{return s.available;});
  if (!s.available) return pdFALSE;
  s.available=false; return pdTRUE;
}
inline BaseType_t xSemaphoreGive(SemaphoreHandle_t handle) {
  auto &s=*static_cast<StockHostSemaphore *>(handle);
  std::lock_guard lock(s.mutex); s.available=true;
  s.condition.notify_all(); return pdTRUE;
}
inline void vSemaphoreDelete(SemaphoreHandle_t handle) { delete static_cast<StockHostSemaphore *>(handle); }
