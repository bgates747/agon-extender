// P4 clock/worker/output binding for the original depth controllers.
// Timer callbacks never acquire native state or execute drawing/output work.
#pragma once
#include <atomic>
#include <memory>
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
  // Compatibility owner for isolated tests. Product mode replacement keeps
  // one external snapshot pool alive across every candidate service.
  explicit StockP4Service(Allocator snapshot_allocator);
  explicit StockP4Service(PresentationSnapshotPool &snapshots);
  ~StockP4Service();
  StockP4Service(StockP4Service const &) = delete;
  StockP4Service &operator=(StockP4Service const &) = delete;
  // startClock + prepare allocate every fallible runtime resource while the
  // current service remains active. activate performs no allocation.
  bool startClock(std::uint32_t period_us = 16667);
  bool prepare(StockRuntimeController &controller);
  void activate();
  bool attach(StockRuntimeController &controller);
  void detach();
  PresentationSnapshotPool &snapshotPool() noexcept { return *snapshots_; }
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
  void initializeSynchronization();

  std::unique_ptr<PresentationSnapshotPool> owned_snapshots_;
  PresentationSnapshotPool *snapshots_{}; // external in product; survives modes
  StockClock clock_;
  StockRuntimeController *controller_{}; // stable until both tasks have joined
  esp_timer_handle_t timer_{};
  esp_timer_handle_t barrier_{};
  SemaphoreHandle_t barrier_done_{};
  SemaphoreHandle_t draw_done_{};
  SemaphoreHandle_t output_done_{};
  std::atomic<TaskHandle_t> draw_task_{};
  std::atomic<TaskHandle_t> output_task_{};
  std::atomic<bool> active_{};
  std::atomic<bool> stopping_{true};
  std::uint32_t period_us_{};
};
} // namespace agon::extender::display
