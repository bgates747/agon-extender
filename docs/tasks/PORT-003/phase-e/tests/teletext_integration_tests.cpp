// PORT-003 Phase E host execution of retained official Teletext and Canvas.
//
// `agon_screen.h` includes the real vendored Teletext implementation. Only the
// ESP timer/task owner is replaced here with a synchronous host service; the
// target adapter is compiled separately by the P4 diagnostic environment.
#include <cstdarg>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <unordered_set>

namespace {

bool fail_first_psram_allocation = false;
std::size_t psram_attempts = 0;
std::size_t heap_live = 0;
std::unordered_set<void *> heap_allocations;

}  // namespace

bool phase_e_psram_init() noexcept { return true; }

void *phase_e_ps_malloc(std::size_t size) noexcept {
  ++psram_attempts;
  if (fail_first_psram_allocation && psram_attempts == 1) return nullptr;
  return std::malloc(size);
}

void *phase_e_heap_caps_malloc(std::size_t size) noexcept {
  void *allocation = std::malloc(size);
  if (allocation != nullptr) {
    heap_allocations.insert(allocation);
    ++heap_live;
  }
  return allocation;
}

void phase_e_heap_caps_free(void *allocation) noexcept {
  if (allocation != nullptr && heap_allocations.erase(allocation) != 0) {
    --heap_live;
  }
  std::free(allocation);
}

void debug_log(char const *, ...) {}

#include "agon_screen.h"

namespace agon::extender::display {

P4FrameService::P4FrameService(FrameWorkExecutor &executor) noexcept
    : logical_service_(executor) {}

P4FrameService::~P4FrameService() { stop(); }

P4FrameServiceStartResult P4FrameService::start(
    P4FrameServiceConfig config) noexcept {
  if (config.period_microseconds == 0 || config.task_stack_bytes == 0 ||
      config.task_priority >= configMAX_PRIORITIES) {
    return P4FrameServiceStartResult::InvalidConfiguration;
  }
  return logical_service_.start() ? P4FrameServiceStartResult::Ok
                                  : P4FrameServiceStartResult::AlreadyRunning;
}

void P4FrameService::stop() noexcept { logical_service_.stop(); }
bool P4FrameService::running() const noexcept {
  return logical_service_.running();
}
LogicalFrameService &P4FrameService::logicalService() noexcept {
  return logical_service_;
}
LogicalFrameService const &P4FrameService::logicalService() const noexcept {
  return logical_service_;
}

}  // namespace agon::extender::display

namespace {

[[noreturn]] void finish(int status) {
  canvas.reset();
  _screenFacadeAdapter.reset();
  _P4FrameService.reset();
  _VGAController.reset();
  std::cout.flush();
  std::cerr.flush();
  std::_Exit(status);
}

void check(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    finish(1);
  }
}

void successAndExit() {
  check(changeMode(7) == 0, "Teletext mode 7 failed");
  check(ttxtMode && videoMode == 7 && canvasW == 640 && canvasH == 480 &&
            getVGAColourDepth() == 16 && canvas != nullptr &&
            _VGAController != nullptr && _VGAController->logicalWidth() == 640 &&
            _VGAController->logicalHeight() == 480 &&
            _VGAController->logicalFormat() ==
                agon::extender::display::NativePixelFormat::PALETTE16,
        "Teletext mode metadata differs");
  check(psram_attempts == 4, "Teletext allocation sequence differs");
  std::cout << "teletext-init-pass\n";

  // The exact vdu_mode() lifecycle clears this flag before calling changeMode;
  // item 8 separately executes that exact body. This call then proves the
  // retained facade and Canvas can leave mode 7 without a text controller.
  ttxtMode = false;
  check(changeMode(8) == 0, "transition out of Teletext failed");
  check(!ttxtMode && videoMode == 8 && canvasW == 320 && canvasH == 240 &&
            getVGAColourDepth() == 64 && canvas != nullptr &&
            _VGAController->logicalWidth() == 320 &&
            _VGAController->logicalHeight() == 240 &&
            _VGAController->logicalFormat() ==
                agon::extender::display::NativePixelFormat::SBGR2222,
        "post-Teletext mode metadata differs");
  std::cout << "teletext-exit-pass\n";
  finish(0);
}

void failureAndExit() {
  fail_first_psram_allocation = true;
  check(changeMode(7) == -1, "injected Teletext failure was not reported");
  check(!ttxtMode && videoMode != 7 && canvasW == 640 && canvasH == 480 &&
            getVGAColourDepth() == 16 && canvas != nullptr &&
            psram_attempts == 1,
        "injected Teletext failure state differs");
  std::cout << "teletext-allocation-failure-pass\n";
  finish(0);
}

}  // namespace

int main(int argc, char **argv) {
  if (argc != 2) return 2;
  std::string scenario = argv[1];
  if (scenario == "success") successAndExit();
  if (scenario == "failure") failureAndExit();
  return 3;
}
