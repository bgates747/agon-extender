#include "extender/display/stock_runtime_controller.hpp"
#include <new>
#if defined(AGON_EXTENDER_DIRECT_RGB888) && !defined(FABGL_EMULATED)
#include "extender/display/hdmi_output.hpp"
#endif

namespace agon::extender::display {
std::unique_ptr<StockRuntimeController> makeStockRuntimeController(int colours, int width, int height) {
#ifdef AGON_EXTENDER_DIRECT_RGB888
  // RGB-001 explicitly bounds the alternative storage to the selected 64-colour
  // geometries. Ordinary startup/indexed modes retain their existing controller.
  if(rgb888ExperimentGeometry(colours, width, height)) {
    auto *controller=new (std::nothrow) StockBoundController<fabgl::P4Rgb888Controller>();
#if !defined(FABGL_EMULATED)
    if(controller) {
      auto storage=hdmiOutput().panelStorage();
      if(!storage.count) {delete controller;return nullptr;}
      controller->bindPanelStorage(storage);
    }
#endif
    return std::unique_ptr<StockRuntimeController>(controller);
  }
#endif
  switch (colours) {
    case 2: return std::unique_ptr<StockRuntimeController>(
        new (std::nothrow) StockBoundController<fabgl::VGA2Controller>());
    case 4: return std::unique_ptr<StockRuntimeController>(
        new (std::nothrow) StockBoundController<fabgl::VGA4Controller>());
    case 8: return std::unique_ptr<StockRuntimeController>(
        new (std::nothrow) StockBoundController<fabgl::VGA8Controller>());
    case 16: return std::unique_ptr<StockRuntimeController>(
        new (std::nothrow) StockBoundController<fabgl::VGA16Controller>());
    case 64: return std::unique_ptr<StockRuntimeController>(
        new (std::nothrow) StockBoundController<fabgl::VGA64Controller>());
    default: return nullptr;
  }
}
} // namespace agon::extender::display
