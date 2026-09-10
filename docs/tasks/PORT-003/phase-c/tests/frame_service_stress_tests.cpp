// PORT-003 Phase C adversarial logical-service stress qualification.
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <thread>

#include "extender/display/logical_frame_service.hpp"

using namespace agon::extender::display;

namespace {

void check(bool condition) {
  if (!condition) std::abort();
}

struct Executor final : FrameWorkExecutor {
  bool running{};
  std::uint32_t frame{};
  std::uint64_t executions{};

  void setFrameServiceRunning(bool value) noexcept override { running = value; }
  std::size_t executeFrameWork() override {
    ++executions;
    return 0;
  }
  std::uint32_t advanceFrameCounter(std::uint32_t elapsed) noexcept override {
    frame += elapsed;
    return frame;
  }
  std::uint32_t readFrameCounter() const noexcept override { return frame; }
  std::size_t logicalWidth() const noexcept override { return 320; }
  std::size_t logicalHeight() const noexcept override { return 240; }
  NativePixelFormat logicalFormat() const noexcept override {
    return NativePixelFormat::SBGR2222;
  }
  bool logicalDoubleBuffered() const noexcept override { return false; }
  std::uint8_t visiblePlaneIdentity() const noexcept override { return 0; }
};

void concurrentTickBurst() {
  constexpr std::uint32_t kTicks = 200000;
  Executor executor;
  LogicalFrameService service(executor);
  int slot = service.registerConsumer();
  check(slot >= 0 && service.start());
  std::atomic<bool> done{};
  std::thread producer([&] {
    for (std::uint32_t tick = 0; tick < kTicks; ++tick)
      check(service.recordTicks());
    done.store(true, std::memory_order_release);
  });
  do {
    service.servicePending();
    std::this_thread::yield();
  } while (!done.load(std::memory_order_acquire) || service.pendingTicks() != 0);
  producer.join();
  auto metrics = service.metrics();
  check(metrics.elapsed_ticks == kTicks);
  check(executor.frame == kTicks);
  check(metrics.serviced_edges == service.generation());
  check(metrics.serviced_edges == kTicks);
  check(static_cast<std::uint64_t>(service.consumerDrops(slot)) + 1 ==
        service.generation());
  service.stop();
  std::cout << "concurrent-tick-burst-pass\n";
}

void saturationAndLifecycle() {
  Executor executor;
  LogicalFrameService service(executor);
  check(service.start());
  check(service.recordTicks(std::numeric_limits<std::uint32_t>::max()));
  check(service.recordTicks(42));
  check(service.pendingTicks() == std::numeric_limits<std::uint32_t>::max());
  service.stop();
  auto metrics = service.metrics();
  check(metrics.saturated_tick_notifications == 1);
  for (int cycle = 0; cycle < 1000; ++cycle) {
    check(service.start());
    check(executor.running);
    check(service.recordTicks());
    check(service.servicePending() == FrameServiceResult::Serviced);
    service.stop();
    check(!executor.running);
  }
  std::cout << "saturation-lifecycle-pass\n";
}

void boundedConsumerRegistry() {
  Executor executor;
  LogicalFrameService service(executor);
  for (std::size_t index = 0; index < LogicalFrameService::kMaximumConsumers;
       ++index) {
    check(service.registerConsumer() == static_cast<int>(index));
  }
  check(service.registerConsumer() == -1);
  check(service.start());
  check(service.registerConsumer() == -1);
  check(service.recordTicks(100));
  while (service.servicePending() == FrameServiceResult::Serviced) {
  }
  service.stop();
  for (std::size_t index = 0; index < LogicalFrameService::kMaximumConsumers;
       ++index) {
    check(service.unregisterConsumer(static_cast<int>(index)));
  }
  std::cout << "bounded-consumer-registry-pass\n";
}

}  // namespace

int main() {
  concurrentTickBurst();
  saturationAndLifecycle();
  boundedConsumerRegistry();
  return 0;
}
