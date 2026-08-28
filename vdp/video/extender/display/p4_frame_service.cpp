// See p4_frame_service.hpp. No renderer, swap, publication, or completion
// operation is permitted in timerEntry(); all such work belongs to taskLoop().
#include "extender/display/p4_frame_service.hpp"

#include "esp_err.h"

namespace agon::extender::display {

P4FrameService::P4FrameService(FrameWorkExecutor &executor,
                               std::size_t work_budget) noexcept
    : logical_service_(executor, work_budget) {}

P4FrameService::~P4FrameService() { stop(); }

P4FrameServiceStartResult P4FrameService::start(
    P4FrameServiceConfig config) noexcept {
  if (running()) return P4FrameServiceStartResult::AlreadyRunning;
  if (config.period_microseconds == 0 || config.task_stack_bytes == 0 ||
      config.task_priority >= configMAX_PRIORITIES) {
    return P4FrameServiceStartResult::InvalidConfiguration;
  }

  logical_service_.setFramePeriodMicroseconds(config.period_microseconds);

  task_stopped_ = xSemaphoreCreateBinary();
  if (task_stopped_ == nullptr) {
    return P4FrameServiceStartResult::SemaphoreAllocationFailed;
  }
  stopping_.store(false, std::memory_order_release);
  if (!logical_service_.start()) {
    vSemaphoreDelete(task_stopped_);
    task_stopped_ = nullptr;
    return P4FrameServiceStartResult::AlreadyRunning;
  }

  TaskHandle_t created_task = nullptr;
  BaseType_t task_result = xTaskCreate(
      taskEntry, "extender-frame", config.task_stack_bytes, this,
      config.task_priority, &created_task);
  if (task_result != pdPASS || created_task == nullptr) {
    logical_service_.stop();
    vSemaphoreDelete(task_stopped_);
    task_stopped_ = nullptr;
    return P4FrameServiceStartResult::TaskCreationFailed;
  }
  task_.store(created_task, std::memory_order_release);

  esp_timer_create_args_t timer_args{};
  timer_args.callback = timerEntry;
  timer_args.arg = this;
  timer_args.dispatch_method = ESP_TIMER_TASK;
  timer_args.name = "extender-frame";
  timer_args.skip_unhandled_events = false;
  if (esp_timer_create(&timer_args, &timer_) != ESP_OK) {
    stopTaskAfterStartFailure();
    return P4FrameServiceStartResult::TimerCreationFailed;
  }
  if (esp_timer_start_periodic(timer_, config.period_microseconds) != ESP_OK) {
    esp_timer_delete(timer_);
    timer_ = nullptr;
    stopTaskAfterStartFailure();
    return P4FrameServiceStartResult::TimerStartFailed;
  }
  return P4FrameServiceStartResult::Ok;
}

void P4FrameService::stop() noexcept {
  if (!running()) return;
  if (timer_ != nullptr) {
    esp_timer_stop(timer_);
    esp_timer_delete(timer_);
    timer_ = nullptr;
  }
  stopping_.store(true, std::memory_order_release);
  TaskHandle_t task = task_.load(std::memory_order_acquire);
  if (task != nullptr) xTaskNotifyGive(task);
  if (task_stopped_ != nullptr) {
    xSemaphoreTake(task_stopped_, portMAX_DELAY);
    // Only after the sole owner task has exited may logical stop invoke the
    // unchanged upstream background-disable path. That path drains queued
    // work and owns its normal dynamic-payload lifetime without racing this
    // task's bounded executor.
    logical_service_.stop();
    vSemaphoreDelete(task_stopped_);
    task_stopped_ = nullptr;
  }
}

bool P4FrameService::running() const noexcept {
  return logical_service_.running();
}

LogicalFrameService &P4FrameService::logicalService() noexcept {
  return logical_service_;
}

LogicalFrameService const &P4FrameService::logicalService() const noexcept {
  return logical_service_;
}

void P4FrameService::timerEntry(void *context) noexcept {
  auto &self = *static_cast<P4FrameService *>(context);
  if (!self.logical_service_.recordTicks()) return;
  TaskHandle_t task = self.task_.load(std::memory_order_acquire);
  if (task != nullptr) xTaskNotifyGive(task);
}

void P4FrameService::taskEntry(void *context) noexcept {
  static_cast<P4FrameService *>(context)->taskLoop();
}

void P4FrameService::taskLoop() noexcept {
  for (;;) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    if (stopping_.load(std::memory_order_acquire)) break;
    while (logical_service_.servicePending() == FrameServiceResult::Serviced) {
      if (stopping_.load(std::memory_order_acquire)) break;
    }
  }
  task_.store(nullptr, std::memory_order_release);
  xSemaphoreGive(task_stopped_);
  vTaskDelete(nullptr);
}

void P4FrameService::stopTaskAfterStartFailure() noexcept {
  stopping_.store(true, std::memory_order_release);
  TaskHandle_t task = task_.load(std::memory_order_acquire);
  if (task != nullptr) xTaskNotifyGive(task);
  xSemaphoreTake(task_stopped_, portMAX_DELAY);
  logical_service_.stop();
  vSemaphoreDelete(task_stopped_);
  task_stopped_ = nullptr;
}

}  // namespace agon::extender::display
