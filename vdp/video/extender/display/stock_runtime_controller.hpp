// Original depth controllers with the accepted P4 execution/output binding.
// No rendering algorithm is implemented here. The original class owns rows,
// painting, readback, palettes, primitives and sprites. A service must join its
// worker and output calls before reconfiguring or destroying this object.
#pragma once
#include <climits>
#include <memory>
#include "extender/display/stock_scanline.hpp"
#include "extender/display/stock_native_access.hpp"

namespace agon::extender::display {
class StockRuntimeController {
 public:
  virtual ~StockRuntimeController() = default;
  virtual fabgl::VGABaseController &display() noexcept = 0;
  virtual fabgl::VGAPalettedController &paletted() noexcept = 0;
  virtual std::size_t drain() = 0;
  virtual void prepareRow(int y, std::uint8_t *signal) = 0;
};

template<class Depth>
class StockBoundController : public StockScanlineController<Depth>, public StockRuntimeController {
 public:
  ~StockBoundController() override { end(); }
  fabgl::VGABaseController &display() noexcept override { return *this; }
  fabgl::VGAPalettedController &paletted() noexcept override { return *this; }

  void suspendBackgroundPrimitiveExecution() override { execution_.suspend(); }
  void resumeBackgroundPrimitiveExecution() override { execution_.resume(); }

  void end() override {
    // Lifecycle caller has already joined both tasks. Balance the suspension
    // acquired by stock's native teardown before the gate itself is destroyed.
    bool allocated = this->m_viewPort != nullptr;
    Depth::end();
    if (allocated) execution_.resume();
  }

  void readScreen(fabgl::Rect const &rect, fabgl::RGB888 *dest) override {
    AGON_STOCK_NATIVE_GUARD;
    Depth::readScreen(rect, dest);
  }

  std::size_t drain() override {
    if (!execution_.beginWorker()) return 0;
    struct Leave { StockExecutionGate &gate; ~Leave() { gate.endWorker(); } } leave{execution_};
    std::size_t count = 0;
    // Stock VGABaseController::primitiveExecTask inner drain, with its optional
    // timeout disabled. Only admission/suspension are bound to the P4 gate;
    // execPrimitive and showSprites retain their original bodies. The native
    // guard is inside each operation, never around this complete drain.
    fabgl::Rect updateRect(SHRT_MAX, SHRT_MAX, SHRT_MIN, SHRT_MIN);
    do {
      fabgl::Primitive prim;
      if (this->getPrimitive(&prim, 0) == false)
        break;
      this->execPrimitive(prim, updateRect, false);
      ++count;
      if (execution_.suspended())
        break;
    } while (true);
    this->showSprites(updateRect);
    return count;
  }

  void prepareRow(int y, std::uint8_t *signal) override {
    AGON_STOCK_NATIVE_GUARD;
    // A task can be descheduled between rows, unlike the physical rolling
    // scanout deadline. Palette/list mutation may retire its saved Copper
    // node. Rebind only after such a mutation; ordinary rows keep the exact
    // stock sequential cursor and lookup. No raw pointer survives this guard
    // except that revision-checked cursor.
    if (palette_revision_ != stockPaletteRevision()) {
      this->m_currentSignalItem = this->m_signalList;
      palette_revision_ = stockPaletteRevision();
    }
    this->prepareStockRowQuiescent(y, signal);
  }
 private:
  StockExecutionGate execution_;
  std::uint32_t palette_revision_{UINT32_MAX};
};

std::unique_ptr<StockRuntimeController> makeStockRuntimeController(int colours);
} // namespace agon::extender::display
