#include <cstdint>
#include <cstdlib>
#include <iostream>

#include "extender/display/cursor_position_adapter.hpp"
#include "extender/display/screen_facade_adapter.hpp"

using namespace agon::extender::display;

namespace {

void check(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

struct TrackingAllocator {
  std::size_t attempts{};
  std::size_t live{};
  std::size_t fail_on{};

  static void *allocate(void *context, std::size_t size) {
    auto &self = *static_cast<TrackingAllocator *>(context);
    ++self.attempts;
    if (self.fail_on != 0 && self.attempts == self.fail_on) return nullptr;
    void *result = std::malloc(size);
    if (result != nullptr) ++self.live;
    return result;
  }
  static void release(void *context, void *allocation) {
    if (allocation == nullptr) return;
    auto &self = *static_cast<TrackingAllocator *>(context);
    std::free(allocation);
    --self.live;
  }
  Allocator binding() { return {this, allocate, release}; }
};

struct FakeFrameService {
  bool is_running{};
  bool fail_next_start{};
  std::uint64_t period{};
  std::size_t starts{};
  std::size_t stops{};

  FrameServiceBinding binding() {
    return {
        this,
        [](void *context) noexcept {
          return static_cast<FakeFrameService *>(context)->is_running;
        },
        [](void *context) noexcept {
          auto &self = *static_cast<FakeFrameService *>(context);
          self.is_running = false;
          ++self.stops;
        },
        [](void *context, std::uint64_t value) noexcept {
          auto &self = *static_cast<FakeFrameService *>(context);
          ++self.starts;
          if (self.fail_next_start) {
            self.fail_next_start = false;
            return false;
          }
          self.period = value;
          self.is_running = true;
          return true;
        },
    };
  }
};

void testParsingAndDepths() {
  OfficialModeLine timing{};
  check(parseOfficialModeline(
            "\"640x480@60Hz\" 25.175 640 656 752 800 480 490 492 525 -HSync -VSync",
            timing),
        "parse official modeline");
  check(timing.width == 640 && timing.height == 480 && timing.refresh_hz == 60,
        "parsed timing");
  check(!parseOfficialModeline("640x480", timing), "reject malformed modeline");
  check(periodForRefresh(60) == 16667 && periodForRefresh(70) == 14286 &&
            periodForRefresh(75) == 13333 && periodForRefresh(0) == 0,
        "rounded periods");
  for (std::uint8_t depth : {2, 4, 8, 16, 64}) {
    NativePixelFormat format{};
    check(nativeFormatForColourDepth(depth, format), "accepted depth");
  }
  NativePixelFormat format{};
  check(!nativeFormatForColourDepth(32, format), "rejected depth");
  std::cout << "modeline-depth-pass\n";
}

void testTransactionalFacade() {
  TrackingAllocator allocations;
  FakeFrameService service;
  {
    P4DisplayController controller(allocations.binding());
    ScreenFacadeAdapter adapter(controller, service.binding());
    constexpr char mode1[] =
        "\"640x480@60Hz\" 25.175 640 656 752 800 480 490 492 525 -HSync -VSync";
    constexpr char mode12[] =
        "\"320x200@70Hz\" 25.175 320 328 376 400 200 245 246 262 -HSync -VSync";
    check(adapter.configure(4, mode1, false) == FacadeConfigureResult::Ok,
          "initial configure");
    check(controller.logicalWidth() == 640 && controller.logicalHeight() == 480 &&
              controller.logicalFormat() == NativePixelFormat::PALETTE4 &&
              service.is_running && service.period == 16667,
          "initial state");

    std::size_t fail_attempt = allocations.attempts + 1;
    allocations.fail_on = fail_attempt;
    check(adapter.configure(64, mode12, false) ==
              FacadeConfigureResult::StorageUnavailable,
          "allocation failure");
    allocations.fail_on = 0;
    check(controller.logicalWidth() == 640 && controller.logicalHeight() == 480 &&
              controller.logicalFormat() == NativePixelFormat::PALETTE4 &&
              service.is_running && service.period == 16667,
          "allocation rollback");

    service.fail_next_start = true;
    check(adapter.configure(64, mode12, false) ==
              FacadeConfigureResult::FrameServiceUnavailable,
          "service failure");
    check(controller.logicalWidth() == 640 && controller.logicalHeight() == 480 &&
              controller.logicalFormat() == NativePixelFormat::PALETTE4 &&
              service.is_running && service.period == 16667,
          "service rollback");

    check(adapter.configure(64, mode12, true) == FacadeConfigureResult::Ok,
          "replacement configure");
    check(controller.logicalWidth() == 320 && controller.logicalHeight() == 200 &&
              controller.logicalFormat() == NativePixelFormat::SBGR2222 &&
              controller.logicalDoubleBuffered() && service.period == 14286,
          "replacement state");
    service.is_running = false;
  }
  check(allocations.live == 0, "allocation teardown");
  std::cout << "transactional-facade-pass\n";
}

void testOfficialFrameCounterExpression() {
  TrackingAllocator allocations;
  {
    P4DisplayController controller(allocations.binding());
    controller.frameCounter = 0xFFFF'FFFEu;
    check(static_cast<std::uint32_t>(controller.frameCounter) == 0xFFFF'FFFEu,
          "official frame counter assignment/read");
    check(controller.advanceFrameCounter(1) == 0xFFFF'FFFFu,
          "frame counter advance");
    check(controller.advanceFrameCounter(1) == 0u &&
              controller.readFrameCounter() == 0u,
          "frame counter rollover");
    std::uint32_t low = 0x1234;
    std::uint32_t last = controller.frameCounter;
    last = (last & 0xFFFF'0000u) | low;
    controller.frameCounter = last;
    check(controller.readFrameCounter() == 0x0000'1234u,
          "official low-word write expression");
  }
  check(allocations.live == 0, "frame counter teardown");
  std::cout << "official-frame-counter-pass\n";
}

void testCursorPositionEndpoint() {
  TrackingAllocator allocations;
  {
    P4DisplayController controller(allocations.binding());
    CursorPositionAdapter adapter;
    check(adapter.set(1, 1) == CursorPositionResult::Unbound,
          "cursor initially unbound");
    check(adapter.bind(320, 200, &controller), "cursor bind");
    check(adapter.set(999, 888) == CursorPositionResult::Ok,
          "cursor position");
    check(adapter.x() == 319 && adapter.y() == 199,
          "cursor clamp");
    check(adapter.bind(100, 50, &controller) && adapter.x() == 99 &&
              adapter.y() == 49,
          "cursor mode-bound clamp");
    check(!adapter.bind(0, 50, &controller) &&
              adapter.set(1, 1) == CursorPositionResult::Unbound,
          "cursor invalid bounds");
  }
  check(allocations.live == 0, "cursor teardown");
  std::cout << "cursor-position-endpoint-pass\n";
}

}  // namespace

int main() {
  testParsingAndDepths();
  testTransactionalFacade();
  testOfficialFrameCounterExpression();
  testCursorPositionEndpoint();
}
