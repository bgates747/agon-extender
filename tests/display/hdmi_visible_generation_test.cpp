// Exercise the actual retained controller's swap and native exclusion. No ESP32
// hardware is contacted; the existing stock host substrate supplies allocation.
#include <cassert>
#include <chrono>
#include <future>
#include "dispdrivers/vga64controller.h"
#include "extender/display/stock_native_access.hpp"

using namespace agon::extender::display;
using namespace std::chrono_literals;

struct Controller : fabgl::VGA64Controller {
  void const volatile *visible() const noexcept { return m_viewPortVisible[0]; }
  void const volatile *drawing() const noexcept { return m_viewPort[0]; }
  void swap() { swapBuffers(); }
};

int main() {
  Controller controller;
  controller.begin();
  controller.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",
                           64, 16, true);
  assert(controller.isViewPortAllocated() && controller.isDoubleBuffered());
  auto const before = stockVisibleGeneration();
  auto const front = controller.visible();
  auto const back = controller.drawing();
  assert(front != back);

  std::future<void> swap;
  {
    StockNativeGuard row_copy(stockNativeMutex());
    std::promise<void> started;
    auto entered = started.get_future();
    swap = std::async(std::launch::async, [&] {
      started.set_value();
      controller.swap();
    });
    entered.get();
    // A reader's copied row and its generation cannot race the alias update.
    assert(swap.wait_for(30ms) == std::future_status::timeout);
    assert(stockVisibleGeneration() == before);
    assert(controller.visible() == front && controller.drawing() == back);
  }
  swap.get();
  {
    StockNativeGuard row_copy(stockNativeMutex());
    assert(stockVisibleGeneration() == before + 1);
    assert(controller.visible() == back && controller.drawing() == front);
  }

  // A converter which started before the swap must reject this candidate even
  // though every individual copied row was protected against source mutation.
  assert(stockVisibleGeneration() != before);
  controller.swap();
  assert(stockVisibleGeneration() == before + 2);
  assert(controller.visible() == front && controller.drawing() == back);
  controller.end();
}
