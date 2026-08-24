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

std::uint8_t drawingPixel(P4DisplayController const &controller, int x, int y) {
  ConstPlaneView plane = controller.drawingPlane();
  std::uint8_t value = 0;
  check(NativePixelCodec::read(
            plane.data + static_cast<std::size_t>(y) * plane.stride,
            controller.logicalWidth(), controller.logicalFormat(),
            static_cast<std::size_t>(x), value) ==
        CodecResult::Ok);
  return value;
}

void drainInitialRefresh(LogicalFrameService &service) {
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
}

void testUpstreamQueueWait(Allocator allocator) {
  std::cerr << "running upstream queue wait\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::SBGR2222, false, 0xC0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 1);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  drainInitialRefresh(service);
  fabgl::Canvas canvas(&controller);
  canvas.setPixel(1, 1);

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
  check(drawingPixel(controller, 1, 1) != 0);
  service.stop();
  std::cout << "upstream-queue-wait-pass\n";
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
  std::this_thread::sleep_for(2ms);
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
  drainInitialRefresh(service);
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

  // Stop uses the unchanged upstream background-disable path. It drains
  // queued work instead of cancelling it and retains upstream's trailing
  // single-buffer Refresh behavior.
  canvas.noOp();
  service.stop();
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
  drainInitialRefresh(service);
  fabgl::Canvas canvas(&controller);
  canvas.beginUpdate();
  canvas.setPixel(0, 0);
  check(service.recordTicks(3));
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(drawingPixel(controller, 0, 0) == 0);
  check(controller.readFrameCounter() == 2);
  check(service.pendingTicks() == 2);
  canvas.endUpdate();
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(drawingPixel(controller, 0, 0) != 0);
  while (service.servicePending() == FrameServiceResult::Serviced) {
  }
  controller.writeFrameCounter(UINT32_MAX);
  check(service.recordTicks(2));
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.readFrameCounter() == 0);
  check(service.pendingTicks() == 1);
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.readFrameCounter() == 1);
  service.stop();
  std::cout << "suspension-counter-pass\n";
}

void testDrainRestartAndReconfigure(Allocator allocator) {
  std::cerr << "running drain/restart/reconfigure\n";
  P4DisplayController controller(allocator);
  check(controller.configure({8, 6, NativePixelFormat::SBGR2222, false, 0xC0}) ==
        ConfigureResult::Ok);
  LogicalFrameService service(controller, 8);
  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  drainInitialRefresh(service);
  fabgl::Canvas canvas(&controller);
  fabgl::Point path[]{{0, 0}, {3, 2}, {7, 5}};
  canvas.drawPath(path, 3);
  service.stop();  // Upstream disable executes and releases the path normally.

  check(service.start());
  controller.enableBackgroundPrimitiveExecution(true);
  drainInitialRefresh(service);
  canvas.noOp();
  check(service.recordTicks());
  check(service.servicePending() == FrameServiceResult::Serviced);
  check(controller.configure({4, 4, NativePixelFormat::PALETTE4, true, 0}) ==
        ConfigureResult::ServiceRunning);
  service.stop();
  check(controller.configure({4, 4, NativePixelFormat::PALETTE4, true, 0}) ==
        ConfigureResult::Ok);
  check(controller.visiblePlaneIdentity() == 0);
  check(controller.drawingPlaneIdentity() == 1);
  std::cout << "drain-restart-reconfigure-pass\n";
}

}  // namespace

int main() {
  Allocator allocator = defaultDisplayAllocator();
  testUpstreamQueueWait(allocator);
  testDoubleBufferSwap(allocator);
  testSingleBufferNextEdgeAndStop(allocator);
  testSuspensionAndCounter(allocator);
  testDrainRestartAndReconfigure(allocator);
  return 0;
}
