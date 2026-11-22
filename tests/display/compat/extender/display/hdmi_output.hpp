// Host-only substitution for the physical DSI/bridge sink. StockP4Service,
// native controllers, queues, swaps and synchronization compile unchanged.
#pragma once
#include <atomic>
#include <functional>
#include <mutex>
#ifdef AGON_TEST_PALETTE_DMA
#include "native_scanout_palette_dma.h"
#endif

constexpr int ESP_ERR_INVALID_STATE = 0x103;

namespace agon::extender::display {
class StockRuntimeController;
class HdmiOutput {
 public:
  using FrameCallback = bool (*)(void *);
  std::function<bool(StockRuntimeController &, std::atomic<bool> &)> observer;
  std::atomic<unsigned> publications{};

#ifdef AGON_EXTENDER_NATIVE_SCANOUT
  using NativeRender = bool (*)(void *,uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,uint32_t,bool *);
  bool bindNativeRows(void *context, NativeRender render, void (*wake)(void *)) {
    std::lock_guard lock(row_mutex_);
    if (row_context_ || fail_row_bind) return false;
#ifdef AGON_TEST_PALETTE_DMA
    if (!palette_dma_bind(context, render, wake)) return false;
#endif
    row_context_ = context; render_=render; wake_=wake; return true;
  }
  unsigned outputSize() const {
#ifdef AGON_TEST_PALETTE_DMA
    return (848u << 16) | 480;
#else
    return (320u << 16) | 32;
#endif
  }
  void joinNativeRows() {
    std::lock_guard lock(row_mutex_);
#ifdef AGON_TEST_PALETTE_DMA
    palette_dma_unbind();
#endif
    row_context_=nullptr;
  }
  bool emitRows(uint8_t *pixels, uint32_t frame, bool release_drawing) {
    std::lock_guard lock(row_mutex_);
    if (!row_context_) return false;
    if (release_drawing) wake_(row_context_);
    return render_(row_context_,pixels,0,32,320,32,0,frame,&slot_black_);
  }
  bool fail_row_bind{};
 private:
  bool slot_black_{};  // fixture starts with deliberately dirty pixels
  std::mutex row_mutex_;
  void *row_context_{};
  NativeRender render_{};
  void (*wake_)(void *){};
 public:
#endif
  bool ready() const noexcept { return true; }
  void allowDirectSwaps() {}
  bool bindFrameCallback(FrameCallback callback, void *context) {
    std::lock_guard lock(callback_mutex_);
    if (callback_) return false;
    callback_ = callback;
    context_ = context;
    return true;
  }
  void unbindFrameCallback(void *expected_context) {
    // Holding this mutex across emitFrame joins an in-progress callback.
    std::lock_guard lock(callback_mutex_);
    if (context_ != expected_context) return;
    callback_ = nullptr;
    context_ = nullptr;
  }
  bool publish(StockRuntimeController &controller, std::atomic<bool> &stopping) {
    ++publications;
    return observer ? observer(controller, stopping) : true;
  }

  // These two methods are test instrumentation, absent from the physical sink.
  bool emitFrame() {
    std::lock_guard lock(callback_mutex_);
    if (!callback_) return false;
    callback_(context_);
    return true;
  }
  bool callbackBound() {
    std::lock_guard lock(callback_mutex_);
    return callback_ != nullptr;
  }

 private:
  std::mutex callback_mutex_;
  FrameCallback callback_{};
  void *context_{};
};

inline HdmiOutput &hdmiOutput() {
  static HdmiOutput output;
  return output;
}
} // namespace agon::extender::display
