#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>

#include "extender/display/screen_facade_adapter.hpp"

using namespace agon::extender::display;

namespace {

struct TrackingAllocator {
  std::size_t attempts{};
  std::size_t live{};
  static void *allocate(void *context, std::size_t size) {
    auto &self = *static_cast<TrackingAllocator *>(context);
    ++self.attempts;
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
        [](void *context, std::uint64_t period) noexcept {
          auto &self = *static_cast<FakeFrameService *>(context);
          self.is_running = true;
          self.period = period;
          ++self.starts;
          return true;
        },
    };
  }
};

char const *formatName(NativePixelFormat format) {
  switch (format) {
    case NativePixelFormat::PALETTE2: return "PALETTE2";
    case NativePixelFormat::PALETTE4: return "PALETTE4";
    case NativePixelFormat::PALETTE8: return "PALETTE8";
    case NativePixelFormat::PALETTE16: return "PALETTE16";
    case NativePixelFormat::SBGR2222: return "SBGR2222";
  }
  return "UNKNOWN";
}

}  // namespace

int main() {
  TrackingAllocator allocations;
  FakeFrameService service;
  std::size_t count = 0;
  {
    P4DisplayController controller(allocations.binding());
    ScreenFacadeAdapter adapter(controller, service.binding());
    std::string line;
    while (std::getline(std::cin, line)) {
      if (line == "END") break;
      auto first = line.find('|');
      auto second = line.find('|', first + 1);
      if (first == std::string::npos || second == std::string::npos) return 70;
      unsigned colours = std::stoul(line.substr(0, first));
      bool double_buffered = std::stoul(line.substr(first + 1, second - first - 1)) != 0;
      std::string modeline = line.substr(second + 1);
      auto result = adapter.configure(static_cast<std::uint8_t>(colours),
                                      modeline.c_str(), double_buffered);
      auto const &mode = adapter.mode();
      auto const &timing = adapter.timing();
      std::cout << "O\t" << count++ << '\t' << unsigned(result) << '\t'
                << mode.width << '\t' << mode.height << '\t'
                << formatName(mode.format) << '\t' << unsigned(mode.double_buffered)
                << '\t' << timing.refresh_hz << '\t' << service.period << '\t'
                << controller.getScreenHeight() << '\t'
                << controller.getViewPortHeight() << '\t' << allocations.live
                << '\n';
    }
    service.is_running = false;
  }
  std::cout << "T\t" << allocations.live << '\t' << allocations.attempts
            << '\t' << service.starts << '\t' << service.stops << '\n';
  return 0;
}
