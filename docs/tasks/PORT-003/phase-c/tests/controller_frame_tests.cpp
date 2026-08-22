// PORT-003 Phase C retained Canvas/common-queue integration qualification.
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <thread>

#include "canvas.h"
#include "extender/display/logical_frame_service.hpp"
#include "extender/display/p4_display_controller.hpp"

using namespace agon::extender::display;
using namespace std::chrono_literals;

namespace {

void checkAt(bool condition, int line) {
  if (!condition) {
    std::cerr << "check failed at line " << line << '\n';
    std::abort();
  }
}

#define check(condition) checkAt((condition), __LINE__)

template <typename Predicate>
void waitUntil(Predicate predicate) {
  for (int attempt = 0; attempt < 10000 && !predicate(); ++attempt)
    std::this_thread::yield();
  check(predicate());
}

void testDequeuedCompletionRace(Allocator allocator) {
  std::cerr << "running dequeued completion\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::SBGR2222, false, 0xC0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 1);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  fabgl::Canvas canvas(&controller);
  canvas.setPixel(1, 1);
  check(controller.submittedSequence() == 1);
  check(controller.executeFrameWork(1) == 1);
  check(controller.startedSequence() == 1);
  check(controller.completedSequence() == 0);

  std::atomic<bool> returned{};
  std::thread waiter([&] {
    canvas.waitCompletion(true);
    returned.store(true, std::memory_order_release);
  });
  std::this_thread::sleep_for(2ms);
  check(!returned.load(std::memory_order_acquire));
  controller.completeFrameWork(1);
  waiter.join();
  check(returned.load(std::memory_order_acquire));
  check(controller.completedSequence() == 1);
  service.stop();
  std::cout << "dequeued-completion-pass\n";
}

void testDoubleBufferSwap(Allocator allocator) {
  std::cerr << "running double-buffer swap\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::SBGR2222, true, 0xC0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 1);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  fabgl::Canvas canvas(&controller);
  canvas.setPixel(2, 2);  // immediate drawing in double-buffer mode
  auto initial_visible = controller.visiblePlaneIdentity();
  auto initial_drawing = controller.drawingPlaneIdentity();

  std::atomic<bool> returned{};
  std::thread submitter([&] {
    canvas.swapBuffers();
    returned.store(true, std::memory_order_release);
  });
  waitUntil([&] { return controller.submittedSequence() == 1; });
  std::cerr << "double swap submitted\n";
  check(!returned.load(std::memory_order_acquire));
  check(service.recordTicks());
  std::cerr << "double tick recorded\n";
  check(service.servicePending() == FrameServiceResult::Serviced);
  std::cerr << "double edge serviced\n";
  submitter.join();
  std::cerr << "double submitter joined\n";
  check(returned.load(std::memory_order_acquire));
  check(controller.visiblePlaneIdentity() == initial_drawing);
  check(controller.drawingPlaneIdentity() == initial_visible);
  check(controller.completedSequence() == 1);
  check(service.generation() == 1);
  service.stop();
  std::cout << "double-buffer-swap-pass\n";
}

void testSingleBufferNextEdgeAndStop(Allocator allocator) {
  std::cerr << "running single-buffer edge/stop\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::PALETTE4, false, 0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 8);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  fabgl::Canvas canvas(&controller);
  canvas.noOp();
  std::atomic<bool> returned{};
  std::thread waiter([&] {
    canvas.waitCompletion(true);
    returned.store(true, std::memory_order_release);
  });
  std::this_thread::sleep_for(2ms);
  check(!returned.load(std::memory_order_acquire));
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
  waiter.join();
  check(returned.load(std::memory_order_acquire));

  canvas.noOp();
  returned.store(false, std::memory_order_release);
  std::thread cancelled([&] {
    canvas.waitCompletion(true);
    returned.store(true, std::memory_order_release);
  });
  std::this_thread::sleep_for(2ms);
  check(!returned.load(std::memory_order_acquire));
  service.stop();
  cancelled.join();
  check(returned.load(std::memory_order_acquire));
  std::cout << "single-buffer-edge-stop-pass\n";
}

void testSuspensionAndCounter(Allocator allocator) {
  std::cerr << "running suspension/counter\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::PALETTE8, false, 0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 8);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  fabgl::Canvas canvas(&controller);
  canvas.beginUpdate();
  canvas.setPixel(0, 0);
  check(service.recordTicks(3));
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.startedSequence() == 0);
  check(controller.frameCounter() == 3);
  check(service.metrics().coalesced_ticks == 2);
  canvas.endUpdate();
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.completedSequence() == 1);
  controller.writeFrameCounter(UINT32_MAX);
  check(service.recordTicks(2));
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.frameCounter() == 1);
  service.stop();
  std::cout << "suspension-counter-pass\n";
}

void testCancellationRestartAndReconfigure(Allocator allocator) {
  std::cerr << "running cancellation/restart/reconfigure\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::SBGR2222, false, 0xC0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 8);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  fabgl::Canvas canvas(&controller);
  fabgl::Point path[]{{0, 0}, {3, 2}, {7, 5}};
  canvas.drawPath(path, 3);
  check(controller.submittedSequence() == 1);
  service.stop();  // Cancels and releases the retained dynamic path copy.

  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  canvas.noOp();
  check(controller.submittedSequence() == 1);
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.completedSequence() == 1);
  check(controller.configure({4, 4, NativePixelFormat::PALETTE4, true, 0}) ==
        ConfigureResult::ServiceRunning);
  service.stop();
  check(controller.configure({4, 4, NativePixelFormat::PALETTE4, true, 0}) ==
        ConfigureResult::Ok);
  check(controller.visiblePlaneIdentity() == 0);
  check(controller.drawingPlaneIdentity() == 1);
  std::cout << "cancellation-restart-reconfigure-pass\n";
}

}  // namespace

int main() {
  Allocator allocator = defaultDisplayAllocator();
  testDequeuedCompletionRace(allocator);
  testDoubleBufferSwap(allocator);
  testSingleBufferNextEdgeAndStop(allocator);
  testSuspensionAndCounter(allocator);
  testCancellationRestartAndReconfigure(allocator);
  return 0;
}
