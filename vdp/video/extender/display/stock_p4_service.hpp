// P4 clock/worker/output binding for the original depth controllers.
// Timer callbacks never acquire native state or execute drawing/output work.
#pragma once
#include <atomic>
#include "extender/diagnostics/output_isolation.hpp"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "extender/display/stock_runtime_controller.hpp"
#include "extender/display/presentation_snapshot_pool.hpp"

namespace agon::extender::display {
class StockP4Service {
 public:
  explicit StockP4Service(Allocator snapshot_allocator);
  ~StockP4Service();
  StockP4Service(StockP4Service const &) = delete;
  StockP4Service &operator=(StockP4Service const &) = delete;
  // Serialized lifecycle owner. Detach before changing/freeing native modes.
  // Detach leaves the clock running, including while native allocation occurs.
  bool startClock(std::uint32_t period_us = 16667);
  bool attach(StockRuntimeController &controller);
  void detach();
  PresentationSnapshotPool &snapshotPool() noexcept { return snapshots_; }
  StockClock const &clock() const noexcept { return clock_; }
 private:
  static void timerEntry(void *);
  static void barrierEntry(void *);
  static void drawEntry(void *);
  static void outputEntry(void *);
  void drawLoop();
  void outputLoop();
  void publish();
  void timerBarrier();
  void stopClock();

#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
  agon_output_isolation::PrebuiltSlots prebuilt_;
  std::uint64_t discard_generation_{};
#endif
  PresentationSnapshotPool snapshots_; // survives every replaceable native mode
  StockClock clock_;
  StockRuntimeController *controller_{}; // stable until both tasks have joined
  esp_timer_handle_t timer_{};
  esp_timer_handle_t barrier_{};
  SemaphoreHandle_t barrier_done_{};
  SemaphoreHandle_t draw_done_{};
  SemaphoreHandle_t output_done_{};
  std::atomic<TaskHandle_t> draw_task_{};
  std::atomic<TaskHandle_t> output_task_{};
  std::atomic<bool> stopping_{true};
  std::uint32_t period_us_{};
};
} // namespace agon::extender::display
