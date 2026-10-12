#include "extender/diagnostics/render_benchmark.hpp"
// Original depth controllers with the accepted P4 execution/output binding.
// No rendering algorithm is implemented here. The original class owns rows,
// painting, readback, palettes, primitives and sprites. A service must join its
// worker and output calls before reconfiguring or destroying this object.
#pragma once
#include <climits>
#include <memory>
#include <type_traits>
#include "extender/display/stock_scanline.hpp"
#include "extender/display/stock_native_access.hpp"
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
#include "extender/diagnostics/video_timing.hpp"
#endif

namespace agon::extender::display {
class StockRuntimeController {
 public:
  virtual ~StockRuntimeController() = default;
  virtual fabgl::VGABaseController &display() noexcept = 0;
  virtual fabgl::VGAPalettedController &paletted() noexcept = 0;
  virtual void bindNativeAliases() noexcept = 0;
  virtual std::size_t drain() = 0;
  virtual void prepareRow(int y, std::uint8_t *signal) = 0;
  virtual bool linearStorage() const noexcept { return false; }
  virtual void prepareLinearRow(int, std::uint8_t *, bool) {}
#ifdef AGON_EXTENDER_INDEXED_FRAME_SNAPSHOT
  // The HDMI output caller holds native exclusion for this complete copy AND
  // the matching immutable overlay scene. No lock or DMA wait occurs here.
  virtual bool copyLinearFrameUnderNativeGuard(std::uint8_t *, bool,
                                              std::atomic<bool> &) { return false; }
#endif
  virtual bool rgb888Storage() const noexcept { return false; }
  virtual bool panelStorage() const noexcept { return false; }
  // Called with native exclusion held through cache submission.
  virtual unsigned preparePanelFrame(int &) { return 0; }
  virtual void bindDrawingTask(TaskHandle_t) {}
  virtual void prepareRgb888Row(int, std::uint8_t *, std::uint8_t *) {}
#if defined(AGON_EXTENDER_OUTPUT_ROW_PAIR)
  virtual void prepareRows(int y, unsigned count, std::uint8_t *signal, unsigned stride) {
    for (unsigned i=0;i<count;++i) prepareRow(y+i, signal+i*stride);
  }
#endif
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
  virtual diagnostics::VideoRowTotals &outputRowTiming() noexcept = 0;
#endif
};

template<class Depth>
class StockBoundController : public StockScanlineController<Depth>, public StockRuntimeController {
 public:
  ~StockBoundController() override { end(); }
  fabgl::VGABaseController &display() noexcept override { return *this; }
  fabgl::VGAPalettedController &paletted() noexcept override { return *this; }
  bool linearStorage() const noexcept override {
#ifdef AGON_EXTENDER_INDEXED_PPA
    return std::is_same_v<Depth, fabgl::P4Color64Controller>;
#else
    return false;
#endif
  }
  void prepareLinearRow(int y, std::uint8_t *destination, bool decorate) override {
#ifdef AGON_EXTENDER_INDEXED_PPA
    if constexpr (std::is_same_v<Depth, fabgl::P4Color64Controller>) {
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      agon_bench::Scope wait(agon_bench::RowWait);
#endif
      AGON_STOCK_NATIVE_GUARD;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      wait.finish();agon_bench::Scope compose(agon_bench::RowCompose);
#endif
      this->copyLinearRow(y,destination,decorate);
    }
#endif
  }
#ifdef AGON_EXTENDER_INDEXED_FRAME_SNAPSHOT
  bool copyLinearFrameUnderNativeGuard(std::uint8_t *destination, bool decorate,
                                      std::atomic<bool> &stopping) override {
#ifdef AGON_EXTENDER_INDEXED_PPA
    if constexpr (std::is_same_v<Depth, fabgl::P4Color64Controller>) {
#if defined(AGON_EXTENDER_SW_VISIBLE_SNAPSHOT) && AGON_EXTENDER_SW_VISIBLE_SNAPSHOT
      // Refuse before touching private snapshot bytes. Prior HDMI frame keeps
      // scanning; caller releases native before PPA or any panel-buffer wait.
      if (!this->softwareSpritesVisibleForSnapshot()) {
        stockRequestSoftwareSnapshotWake();
        return false;
      }
#endif
      const int width = this->getViewPortWidth();
      const int height = this->getViewPortHeight();
      // Retain row descriptors: stock full-width scrolling may rotate them,
      // and the allocator does not promise one contiguous visible plane.
      for (int y = 0; y < height; ++y) {
        if (stopping.load(std::memory_order_acquire)) return false;
        this->copyLinearRow(y, destination + std::size_t(y) * width, decorate);
      }
      return true;
    }
#endif
    return false;
  }
#endif
  bool rgb888Storage() const noexcept override {
#ifdef AGON_EXTENDER_DIRECT_RGB888
    return !linearStorage() && std::is_same_v<Depth, fabgl::P4Rgb888Controller>;
#else
    return false;
#endif
  }
  void prepareRgb888Row(int y, std::uint8_t *destination, std::uint8_t *signal) override {
#ifdef AGON_EXTENDER_DIRECT_RGB888
    if constexpr (std::is_same_v<Depth, fabgl::P4Rgb888Controller>) {
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      agon_bench::Scope wait(agon_bench::RowWait);
#endif
      AGON_STOCK_NATIVE_GUARD;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      wait.finish(); agon_bench::Scope compose(agon_bench::RowCompose);
#endif
      this->copyRgb888Row(y, destination, signal);
    }
#endif
  }
  bool panelStorage() const noexcept override {
#ifdef AGON_EXTENDER_DIRECT_RGB888
    if constexpr (std::is_same_v<Depth, fabgl::P4Rgb888Controller>) return Depth::panelStorage();
#endif
    return false;
  }
  unsigned preparePanelFrame(int &marker) override {
#ifdef AGON_EXTENDER_DIRECT_RGB888
    if constexpr (std::is_same_v<Depth, fabgl::P4Rgb888Controller>) return Depth::preparePanelFrame(marker);
#endif
    return 0;
  }
  void bindDrawingTask(TaskHandle_t task) override { drawing_task_.store(task,std::memory_order_release); }
  void queuedSwapReady() override {
    if(panelStorage() && this->isDoubleBuffered()) {
      auto task=drawing_task_.load(std::memory_order_acquire);
      if(task)xTaskNotifyGive(task);
    }
  }

  void bindNativeAliases() noexcept override {
    fabgl::VGABaseController::s_viewPort = this->m_viewPort;
    fabgl::VGABaseController::s_viewPortVisible = this->m_viewPortVisible;
    fabgl::VGABaseController::s_scanWidth = this->m_viewPortWidth;
    fabgl::VGABaseController::s_viewPortHeight = this->m_viewPortHeight;
  }

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
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    agon_bench::RenderBatch render;
#endif
    if (!execution_.beginWorker()) {
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      render.finish(0,true);
#endif
      return 0;
    }
    struct Leave { StockExecutionGate &gate; ~Leave() { gate.endWorker(); } } leave{execution_};
    std::size_t count = 0;
    // Stock VGABaseController::primitiveExecTask inner drain, with its optional
    // timeout disabled. Only admission/suspension are bound to the P4 gate;
    // execPrimitive and showSprites retain their original bodies. The native
    // guard is inside each operation, never around this complete drain.
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    // RESEARCH-007: separate native-lock wait from queued execution. This
    // default-off probe adds an outer recursive guard only around the single
    // existing operation; the inherited inner guard and queue order are intact.
    // No timing/guard changes occur outside an admitted measured window.
    auto measured=[&](agon_bench::RenderKind kind,auto operation) {
      if(!render.enabled()){operation();return;}
      const auto before=esp_timer_get_time();
      std::int64_t acquired,finished;
      {
        AGON_STOCK_NATIVE_GUARD;
        acquired=esp_timer_get_time();operation();finished=esp_timer_get_time();
      }
      render.operation(kind,before,acquired,finished);
    };
#endif
    fabgl::Rect updateRect(SHRT_MAX, SHRT_MAX, SHRT_MIN, SHRT_MIN);
    do {
      fabgl::Primitive prim;
      if (this->getPrimitive(&prim, 0) == false)
        break;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
      auto kind=agon_bench::RenderKind::Other;
      if(prim.cmd==fabgl::PrimitiveCmd::VScroll || prim.cmd==fabgl::PrimitiveCmd::HScroll)
        kind=agon_bench::RenderKind::Scroll;
      else if(prim.cmd==fabgl::PrimitiveCmd::DrawBitmap)kind=agon_bench::RenderKind::Bitmap;
      else if(prim.cmd==fabgl::PrimitiveCmd::RefreshSprites)kind=agon_bench::RenderKind::RefreshSprites;
      measured(kind,[&]{this->execPrimitive(prim,updateRect,false);});
#else
      this->execPrimitive(prim, updateRect, false);
#endif
      ++count;
      if (execution_.suspended())
        break;
    } while (true);
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    measured(agon_bench::RenderKind::FinalSprites,[&]{this->showSprites(updateRect);});
    render.finish(count);
#else
    this->showSprites(updateRect);
#endif
    return count;
  }

#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
  diagnostics::VideoRowTotals &outputRowTiming() noexcept override { return row_timing_; }
#endif
  void prepareRow(int y, std::uint8_t *signal) override {
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    agon_bench::Scope rowWait(agon_bench::RowWait);
#endif
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
    const auto before = diagnostics::videoTimingNow();
    std::uint32_t acquired{}, finished{};
#endif
    {
    AGON_STOCK_NATIVE_GUARD;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    rowWait.finish();agon_bench::Scope rowCompose(agon_bench::RowCompose);
#endif
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
    acquired = diagnostics::videoTimingNow();
#endif
    prepareRowLocked(y, signal);
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
    finished = diagnostics::videoTimingNow();
#endif
    }
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
    row_timing_.add(acquired - before, finished - acquired);
#endif
  }
#if defined(AGON_EXTENDER_OUTPUT_ROW_PAIR)
  void prepareRows(int y, unsigned count, std::uint8_t *signal, unsigned stride) override {
    // N04u: stock VGA64 ISR composes two rows per interrupt. Only the adapter
    // exclusion granularity changes; each original row body runs in order.
    AGON_STOCK_NATIVE_GUARD;
    for (unsigned i=0;i<count;++i) prepareRowLocked(y+i, signal+i*stride);
  }
#endif
 private:
  void prepareRowLocked(int y, std::uint8_t *signal) {
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
#if defined(AGON_EXTENDER_VIDEO_ROW_TIMING)
  diagnostics::VideoRowTotals row_timing_;
#endif
  StockExecutionGate execution_;
  std::atomic<TaskHandle_t> drawing_task_{};
  std::uint32_t palette_revision_{UINT32_MAX};
};

std::unique_ptr<StockRuntimeController> makeStockRuntimeController(int colours, int width = 0, int height = 0);
} // namespace agon::extender::display
