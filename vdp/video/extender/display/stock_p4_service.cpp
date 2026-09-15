#include "extender/display/stock_p4_service.hpp"
#include "extender/diagnostics/video_timing.hpp"
#include <cassert>

namespace agon::extender::display {
namespace {
#if defined(AGON_EXTENDER_SNAPSHOT_LOOKAHEAD)
constexpr bool kSnapshotLookahead = true;
#else
constexpr bool kSnapshotLookahead = false;
#endif
// QUAL-003 N04n: isolate CPU snapshot interference with parser/drawing.
// Default preserves the retained binding. This flag changes scheduling only;
// original native operations and row locking remain unchanged.
#if defined(AGON_EXTENDER_OUTPUT_BELOW_PARSER)
constexpr unsigned kOutputTaskPriority = 2;
#else
constexpr unsigned kOutputTaskPriority = 6;
#endif
// N04r: keep drawing/parser priorities and all row locks; isolate CPU affinity.
#if defined(AGON_EXTENDER_OUTPUT_DRAW_CORE)
constexpr unsigned kOutputTaskCore = 0;
#else
constexpr unsigned kOutputTaskCore = 1;
#endif
} // namespace
StockP4Service::StockP4Service(Allocator allocator)
    : snapshots_(allocator, SnapshotPixelFormat::RGB222, 0, true, true, kSnapshotLookahead) {
  barrier_done_ = xSemaphoreCreateBinary();
  draw_done_ = xSemaphoreCreateBinary();
  output_done_ = xSemaphoreCreateBinary();
  if (barrier_done_) {
    esp_timer_create_args_t args{};
    args.callback = barrierEntry;
    args.arg = barrier_done_;
    args.dispatch_method = ESP_TIMER_TASK;
    args.name = "stock-clock-join";
    if (esp_timer_create(&args, &barrier_) != ESP_OK) barrier_ = nullptr;
  }
}

StockP4Service::~StockP4Service() {
  detach();
  stopClock();
  if (barrier_) esp_timer_delete(barrier_);
  if (barrier_done_) vSemaphoreDelete(barrier_done_);
  if (draw_done_) vSemaphoreDelete(draw_done_);
  if (output_done_) vSemaphoreDelete(output_done_);
}

bool StockP4Service::startClock(std::uint32_t period_us) {
  if (!period_us || !barrier_ || !draw_done_ || !output_done_) return false;
  if (timer_ && period_us == period_us_) return true;
  if (controller_) return false; // change cadence only at a detached mode boundary
  stopClock();
  period_us_ = period_us;
  clock_.start(esp_timer_get_time(), period_us);
  esp_timer_create_args_t args{};
  args.callback = timerEntry;
  args.arg = this;
  args.dispatch_method = ESP_TIMER_TASK;
  args.name = "stock-clock";
  args.skip_unhandled_events = true; // elapsed time is accounted from esp_timer_get_time
  if (esp_timer_create(&args, &timer_) != ESP_OK) { timer_ = nullptr; return false; }
  if (esp_timer_start_periodic(timer_, period_us) == ESP_OK) return true;
  esp_timer_delete(timer_);
  timer_ = nullptr;
  return false;
}

void StockP4Service::stopClock() {
  if (!timer_) return;
  esp_timer_stop(timer_);
  // esp_timer_delete is deferred and is not a callback join. The pinned IDF
  // serializes ESP_TIMER_TASK callbacks. A subsequent sentinel callback proves
  // any previously dispatched clock callback has returned before state changes.
  timerBarrier();
  esp_timer_delete(timer_);
  timer_ = nullptr;
}

void StockP4Service::timerBarrier() {
  assert(barrier_ && barrier_done_);
  ESP_ERROR_CHECK(esp_timer_start_once(barrier_, 1));
  xSemaphoreTake(barrier_done_, portMAX_DELAY);
}

void StockP4Service::barrierEntry(void *semaphore) { xSemaphoreGive(static_cast<SemaphoreHandle_t>(semaphore)); }

void StockP4Service::timerEntry(void *context) {
  auto &self = *static_cast<StockP4Service *>(context);
  if (!self.clock_.observe(esp_timer_get_time())) return;
  // Coalesced task notifications carry opportunities, not a backlog of frames.
  auto drawing = self.draw_task_.load(std::memory_order_acquire);
  auto output = self.output_task_.load(std::memory_order_acquire);
  if (drawing) xTaskNotifyGive(drawing);
  if (output) xTaskNotifyGive(output);
}

bool StockP4Service::attach(StockRuntimeController &controller) {
  if (!timer_ || controller_ || !draw_done_ || !output_done_ || !snapshots_.enabled()) return false;
  controller_ = &controller;
  controller_->display().enableBackgroundPrimitiveExecution(true);
  stopping_.store(false, std::memory_order_release);
  TaskHandle_t drawing{}, output{};
  // Retain the stock parser/drawing relationship: parser core 0 priority 3;
  // drawing core 0 priority 5. CPU output normally runs core 1 priority 6 so a
  // row waiter has precedence over the next primitive after mutex release.
  // The bounded N04n test selects priority 2 to measure output interference. Pinned
  // IDF esp_timer task runs priority 22/core 0 and never waits for that mutex.
  if (xTaskCreatePinnedToCore(drawEntry, "stock-draw", 8192, this, 5, &drawing, 0) != pdPASS) {
    controller_->display().enableBackgroundPrimitiveExecution(false);
    controller_ = nullptr; stopping_.store(true); return false;
  }
  draw_task_.store(drawing, std::memory_order_release);
  if (xTaskCreatePinnedToCore(outputEntry, "stock-output", 8192, this, kOutputTaskPriority, &output, kOutputTaskCore) != pdPASS) {
    detach(); return false;
  }
  output_task_.store(output, std::memory_order_release);
  return true;
}

void StockP4Service::detach() {
  if (!controller_) return;
  stopping_.store(true, std::memory_order_release);
  auto drawing = draw_task_.load(std::memory_order_acquire);
  auto output = output_task_.load(std::memory_order_acquire);
  if (drawing) xTaskNotifyGive(drawing);
  if (output) xTaskNotifyGive(output);
  // Suspension asks the native worker to stop after its current primitive.
  // No native lock is held while waiting for it or for the output row to finish.
  controller_->display().suspendBackgroundPrimitiveExecution();
  if (drawing) xSemaphoreTake(draw_done_, portMAX_DELAY);
  if (output) xSemaphoreTake(output_done_, portMAX_DELAY);
  draw_task_.store(nullptr, std::memory_order_release);
  output_task_.store(nullptr, std::memory_order_release);
  // Retain task handles until any clock callback which loaded them has left.
  timerBarrier();
  if (drawing) vTaskDelete(drawing);
  if (output) vTaskDelete(output);
  // With both native readers joined, retain stock's disable/flush path so
  // queued dynamic payloads finish against their still-live native mode.
  controller_->display().enableBackgroundPrimitiveExecution(false);
  controller_->display().resumeBackgroundPrimitiveExecution();
  controller_ = nullptr;
}

void StockP4Service::drawEntry(void *p) { static_cast<StockP4Service *>(p)->drawLoop(); }
void StockP4Service::outputEntry(void *p) { static_cast<StockP4Service *>(p)->outputLoop(); }

void StockP4Service::drawLoop() {
  for (;;) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    if (stopping_.load(std::memory_order_acquire)) break;
    controller_->drain();
  }
  xSemaphoreGive(draw_done_);
  // The lifecycle owner deletes this task only after the clock callback join.
  vTaskSuspend(nullptr);
}

void StockP4Service::outputLoop() {
  for (;;) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    if (stopping_.load(std::memory_order_acquire)) break;
    publish();
  }
  xSemaphoreGive(output_done_);
  vTaskSuspend(nullptr);
}

void StockP4Service::publish() {
  auto &display = controller_->display();
  MutableSnapshotView view{};
  if (snapshots_.tryBegin(display.getViewPortWidth(), display.getViewPortHeight(),
                          esp_timer_get_time(), view) != SnapshotBeginResult::Ok) return;
  assert(view.packed_pixels && !view.pixels);
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
  controller_->outputRowTiming().reset();
#endif
  diagnostics::VideoTimingScope timing(diagnostics::VideoPhase::Snapshot,
      (static_cast<std::uint32_t>(view.width) << 16) | view.height);
  alignas(8) std::uint8_t signal[kPresentationSnapshotMaximumWidth];
  bool complete = true;
  for (std::size_t y = 0; y < view.height; ++y) {
    if (stopping_.load(std::memory_order_acquire)) { complete = false; break; }
    controller_->prepareRow(y, signal); // native lock covers only this row
    StockScanlineController<fabgl::VGA2Controller>::normalizeRow(
        signal, view.packed_pixels + y * view.width, view.width);
  }
  snapshots_.finish(complete ? CompositionResult::Ok : CompositionResult::InvalidRegion, period_us_);
  timing.finish(complete ? view.width * view.height : 0);
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
  if (complete) controller_->outputRowTiming().publish(
      (static_cast<std::uint32_t>(view.width) << 16) | view.height);
#endif
}
} // namespace agon::extender::display
