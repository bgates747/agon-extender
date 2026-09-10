// PORT-003 Phase C ESP32-P4 clock/task adapter.
//
// This is intentionally the only production file that binds logical frame
// service to esp_timer and FreeRTOS. The timer callback records one elapsed
// tick and wakes the owner task; it never executes renderer or consumer code.
#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include "extender/display/logical_frame_service.hpp"

namespace agon::extender::display {

struct P4FrameServiceConfig {
  std::uint64_t period_microseconds{16667};
  std::uint32_t task_stack_bytes{8192};
  UBaseType_t task_priority{configMAX_PRIORITIES - 2};
};

enum class P4FrameServiceStartResult : std::uint8_t {
  Ok,
  AlreadyRunning,
  InvalidConfiguration,
  SemaphoreAllocationFailed,
  TaskCreationFailed,
  TimerCreationFailed,
  TimerStartFailed,
};

class P4FrameService final {
 public:
  explicit P4FrameService(FrameWorkExecutor &executor) noexcept;
  ~P4FrameService();

  P4FrameService(P4FrameService const &) = delete;
  P4FrameService &operator=(P4FrameService const &) = delete;

  P4FrameServiceStartResult start(P4FrameServiceConfig config = {}) noexcept;
  void stop() noexcept;
  bool running() const noexcept;

  // Registration/configuration occurs while stopped. Runtime mailbox notices
  // are polled by consumers independently; metrics may be read after stop.
  LogicalFrameService &logicalService() noexcept;
  LogicalFrameService const &logicalService() const noexcept;

 private:
  static void timerEntry(void *context) noexcept;
  static void taskEntry(void *context) noexcept;
  void taskLoop() noexcept;
  void stopTaskAfterStartFailure() noexcept;

  LogicalFrameService logical_service_;
  esp_timer_handle_t timer_{};
  SemaphoreHandle_t task_stopped_{};
  std::atomic<TaskHandle_t> task_{};
  std::atomic<bool> stopping_{};
};

}  // namespace agon::extender::display
