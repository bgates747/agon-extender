// PORT-003 Phase C compile/link and physical-qualification diagnostic.
// This is not production firmware and implements no physical output sink.
#include <Arduino.h>

#include <algorithm>
#include <cinttypes>
#include <cstdint>
#include <limits>
#include <memory>

#include "canvas.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "extender/display/p4_display_controller.hpp"
#include "extender/display/p4_frame_service.hpp"

#ifndef AGON_EXTENDER_SOURCE_IDENTITY
#define AGON_EXTENDER_SOURCE_IDENTITY "UNVERSIONED-DO-NOT-DEPLOY"
#endif
#ifndef AGON_EXTENDER_BUILD_ID
#define AGON_EXTENDER_BUILD_ID "UNVERSIONED-DO-NOT-DEPLOY"
#endif
#ifndef AGON_EXTENDER_ARTIFACT_STATUS
#define AGON_EXTENDER_ARTIFACT_STATUS "UNVERSIONED-DO-NOT-DEPLOY"
#endif

namespace display = agon::extender::display;
namespace {

class TimingConsumer final {
 public:
  void record() noexcept {
    std::int64_t now = esp_timer_get_time();
    if (previous_ != 0) {
      std::uint64_t interval = static_cast<std::uint64_t>(now - previous_);
      minimum_ = std::min(minimum_, interval);
      maximum_ = std::max(maximum_, interval);
      sum_ += interval;
      ++samples_;
    }
    previous_ = now;
  }

  void reset() noexcept {
    previous_ = 0;
    minimum_ = std::numeric_limits<std::uint64_t>::max();
    maximum_ = 0;
    sum_ = 0;
    samples_ = 0;
  }
  std::uint64_t minimum() const noexcept { return samples_ == 0 ? 0 : minimum_; }
  std::uint64_t maximum() const noexcept { return maximum_; }
  std::uint64_t average() const noexcept {
    return samples_ == 0 ? 0 : sum_ / samples_;
  }
  std::uint64_t samples() const noexcept { return samples_; }

 private:
  std::int64_t previous_{};
  std::uint64_t minimum_{std::numeric_limits<std::uint64_t>::max()};
  std::uint64_t maximum_{};
  std::uint64_t sum_{};
  std::uint64_t samples_{};
};

enum class QualificationPhase { NormalCadence, RolloverAndCoalescing, Finished };

display::P4DisplayController controller(display::defaultDisplayAllocator());
display::P4FrameService frame_service(controller, 64);
TimingConsumer timing_consumer;
std::unique_ptr<fabgl::Canvas> canvas;
QualificationPhase phase{QualificationPhase::NormalCadence};
std::uint32_t phase_started_ms{};
std::size_t initial_free_heap{};
int unconsumed_slot{-1};
int timing_slot{-1};
display::FrameServiceMetrics normal_metrics{};
std::uint64_t normal_timing_samples{};
std::uint64_t normal_timing_maximum{};
bool injected_ticks_accepted{};

void pollTimingNotice() {
  display::FrameNotice notice{};
  if (frame_service.logicalService().tryConsumeLatest(timing_slot, notice)) {
    timing_consumer.record();
  }
}

bool startService() {
  auto result = frame_service.start();
  if (result != display::P4FrameServiceStartResult::Ok) {
    ESP_LOGE("frame-service", "start_result=%u", static_cast<unsigned>(result));
    return false;
  }
  controller.enableBackgroundPrimitiveExecution(true);
  return true;
}

void reportTiming(char const *phase_name) {
  ESP_LOGI("frame-service",
           "phase=%s samples=%" PRIu64 " min_us=%" PRIu64
           " avg_us=%" PRIu64 " max_us=%" PRIu64,
           phase_name, timing_consumer.samples(), timing_consumer.minimum(),
           timing_consumer.average(), timing_consumer.maximum());
}

}  // namespace

void setup() {
  ESP_LOGI("frame-service", "source_identity=%s", AGON_EXTENDER_SOURCE_IDENTITY);
  ESP_LOGI("frame-service", "build_id=%s", AGON_EXTENDER_BUILD_ID);
  ESP_LOGI("frame-service", "artifact_status=%s", AGON_EXTENDER_ARTIFACT_STATUS);
  ESP_LOGI("frame-service", "PORT-003 Phase C sink-free qualification starting");
  if (controller.configure(
          {64, 48, display::NativePixelFormat::SBGR2222, false, 0xC0}) !=
      display::ConfigureResult::Ok) {
    ESP_LOGE("frame-service", "logical storage configuration failed");
    phase = QualificationPhase::Finished;
    return;
  }
  canvas = std::make_unique<fabgl::Canvas>(&controller);
  timing_slot = frame_service.logicalService().registerConsumer();
  if (timing_slot < 0) {
    ESP_LOGE("frame-service", "timing consumer registration failed");
    phase = QualificationPhase::Finished;
    return;
  }
  // This mailbox is deliberately never consumed. It qualifies latest-only
  // drop accounting while proving no sink callback can stall logical time.
  unconsumed_slot = frame_service.logicalService().registerConsumer();
  if (unconsumed_slot < 0 || !startService()) {
    ESP_LOGE("frame-service", "consumer/service setup failed");
    phase = QualificationPhase::Finished;
    return;
  }
  canvas->noOp();
  // Exercise the unchanged upstream queue-depth completion path in the target
  // closure. The running logical frame task must drain the marker; this is not
  // evidence that already-dequeued work remains outstanding.
  canvas->waitCompletion(true);
  initial_free_heap = heap_caps_get_free_size(MALLOC_CAP_8BIT);
  phase_started_ms = millis();
}

void loop() {
  if (phase == QualificationPhase::Finished) {
    delay(1000);
    return;
  }

  pollTimingNotice();

  if (phase == QualificationPhase::NormalCadence &&
      millis() - phase_started_ms >= 10000) {
    frame_service.stop();
    pollTimingNotice();
    normal_metrics = frame_service.logicalService().metrics();
    normal_timing_samples = timing_consumer.samples();
    normal_timing_maximum = timing_consumer.maximum();
    reportTiming("normal");
    ESP_LOGI("frame-service",
             "phase=normal elapsed=%" PRIu64 " edges=%" PRIu64
             " heap=%u",
             normal_metrics.elapsed_ticks, normal_metrics.serviced_edges,
             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_8BIT)));

    controller.writeFrameCounter(UINT32_MAX - 2);
    timing_consumer.reset();
    if (!startService()) {
      phase = QualificationPhase::Finished;
      return;
    }
    // The next real timer callback wakes the owner task, which must service
    // every injected tick as a distinct logical edge.
    injected_ticks_accepted = frame_service.logicalService().recordTicks(5);
    if (!injected_ticks_accepted) {
      ESP_LOGE("frame-service", "injected tick burst was rejected");
    }
    phase = QualificationPhase::RolloverAndCoalescing;
    phase_started_ms = millis();
    return;
  }

  if (phase == QualificationPhase::RolloverAndCoalescing &&
      millis() - phase_started_ms >= 1000) {
    frame_service.stop();
    pollTimingNotice();
    auto final_metrics = frame_service.logicalService().metrics();
    std::uint64_t injected_edges =
        final_metrics.serviced_edges - normal_metrics.serviced_edges;
    std::uint64_t unconsumed_drops =
        frame_service.logicalService().consumerDrops(unconsumed_slot);
    reportTiming("rollover");
    ESP_LOGI("frame-service",
             "phase=rollover frame=%" PRIu32 " edge_delta=%" PRIu64
             " unconsumed_drops=%" PRIu64,
             controller.frameCounter(), injected_edges, unconsumed_drops);

    bool lifecycle_ok = true;
    for (int cycle = 0; cycle < 20; ++cycle) {
      lifecycle_ok = startService() && lifecycle_ok;
      delay(25);
      frame_service.stop();
    }
    std::size_t final_free_heap = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    bool passed = normal_metrics.elapsed_ticks >= 550 &&
                  normal_metrics.elapsed_ticks <= 650 &&
                  normal_timing_samples >= 500 &&
                  normal_timing_maximum < 100000 &&
                  injected_ticks_accepted && injected_edges >= 5 &&
                  controller.frameCounter() < 1000 &&
                  unconsumed_drops != 0 && lifecycle_ok &&
                  final_free_heap + 4096 >= initial_free_heap;
    ESP_LOGI("frame-service",
             "phase=teardown restart_cycles=20 initial_heap=%u final_heap=%u",
             static_cast<unsigned>(initial_free_heap),
             static_cast<unsigned>(final_free_heap));
    ESP_LOGI("frame-service", "PORT003_PHASE_C_RESULT pass=%u",
             static_cast<unsigned>(passed));
    phase = QualificationPhase::Finished;
  }
  delay(10);
}
