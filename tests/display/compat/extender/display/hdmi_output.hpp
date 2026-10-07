// Host-only substitution for the physical DSI/bridge sink. StockP4Service,
// native controllers, queues, swaps and synchronization compile unchanged.
#pragma once
#include <atomic>
#include <functional>
#include <mutex>

constexpr int ESP_ERR_INVALID_STATE = 0x103;

namespace agon::extender::display {
class StockRuntimeController;
class HdmiOutput {
 public:
  using FrameCallback = bool (*)(void *);
  std::function<bool(StockRuntimeController &, std::atomic<bool> &)> observer;
  std::atomic<unsigned> publications{};

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
