#include "extender/display/stock_runtime_controller.hpp"

namespace agon::extender::display {
std::unique_ptr<StockRuntimeController> makeStockRuntimeController(int colours) {
  switch (colours) {
    case 2: return std::make_unique<StockBoundController<fabgl::VGA2Controller>>();
    case 4: return std::make_unique<StockBoundController<fabgl::VGA4Controller>>();
    case 8: return std::make_unique<StockBoundController<fabgl::VGA8Controller>>();
    case 16: return std::make_unique<StockBoundController<fabgl::VGA16Controller>>();
    case 64: return std::make_unique<StockBoundController<fabgl::VGA64Controller>>();
    default: return nullptr;
  }
}
} // namespace agon::extender::display
