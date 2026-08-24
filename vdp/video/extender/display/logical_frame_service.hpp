// PORT-003 Phase C sink-independent logical frame state machine.
//
// This code deliberately has no ESP timer, FreeRTOS task, network, panel, or
// presentation dependency. A deterministic host driver and the P4 adapter feed
// the same tick/service boundary; physical sinks never own logical VDP time.
#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

#include "extender/display/native_pixel_codec.hpp"

namespace agon::extender::display {

struct FrameNotice {
  std::uint64_t generation;
  std::uint32_t frame_counter;
  std::size_t width;
  std::size_t height;
  NativePixelFormat format;
  bool double_buffered;
  std::uint8_t visible_plane;
};

class FrameWorkExecutor {
 public:
  virtual ~FrameWorkExecutor() = default;
  virtual void setFrameServiceRunning(bool running) noexcept = 0;
  virtual std::size_t executeFrameWork(std::size_t maximum_primitives) = 0;
  virtual std::uint32_t advanceFrameCounter(
      std::uint32_t elapsed_ticks) noexcept = 0;
  virtual std::uint32_t readFrameCounter() const noexcept = 0;
  virtual std::size_t logicalWidth() const noexcept = 0;
  virtual std::size_t logicalHeight() const noexcept = 0;
  virtual NativePixelFormat logicalFormat() const noexcept = 0;
  virtual bool logicalDoubleBuffered() const noexcept = 0;
  virtual std::uint8_t visiblePlaneIdentity() const noexcept = 0;
};

struct FrameServiceMetrics {
  std::uint64_t elapsed_ticks{};
  std::uint64_t serviced_edges{};
  std::uint64_t published_generations{};
  std::uint64_t executed_primitives{};
  std::uint64_t saturated_tick_notifications{};
};

enum class FrameServiceResult : std::uint8_t {
  Serviced,
  Idle,
  Stopped,
};

class LogicalFrameService final {
 public:
  static constexpr std::size_t kMaximumConsumers = 8;

  explicit LogicalFrameService(FrameWorkExecutor &executor,
                               std::size_t work_budget = 64) noexcept;

  bool start() noexcept;
  void stop() noexcept;
  bool running() const noexcept;

  // Timer/host notification boundary. This is allocation-free and lock-free
  // when the target's 32-bit atomic implementation is lock-free. Each pending
  // tick is serviced as its own logical edge to preserve the upstream
  // one-VSYNC-event/one-frame-edge model.
  bool recordTicks(std::uint32_t elapsed_ticks = 1) noexcept;
  FrameServiceResult servicePending();

  // Consumers own no callback on the frame-service task. Each registration is
  // a fixed-capacity latest-notice mailbox which a sink polls independently.
  int registerConsumer() noexcept;
  bool unregisterConsumer(int slot) noexcept;
  bool setConsumerConnected(int slot, bool connected) noexcept;
  bool tryPeekLatest(int slot, FrameNotice &notice) noexcept;
  bool tryConsumeLatest(int slot, FrameNotice &notice) noexcept;
  std::uint32_t consumerDrops(int slot) const noexcept;

  std::uint32_t pendingTicks() const noexcept;
  std::uint64_t generation() const noexcept;
  FrameServiceMetrics metrics() const noexcept;

 private:
  struct ConsumerSlot {
    // PORT-003 Phase C: the producer only tries this lock once. A preempted or
    // slow reader therefore costs one reported drop, never logical frame time.
    std::atomic_flag notice_lock = ATOMIC_FLAG_INIT;
    std::atomic<bool> registered{};
    std::atomic<bool> connected{};
    std::atomic<std::uint32_t> drops{};
    FrameNotice notice{};
    bool has_notice{};
  };

  bool readLatest(int slot, FrameNotice &notice, bool consume) noexcept;
  static void recordDrop(ConsumerSlot &slot) noexcept;

  FrameWorkExecutor &executor_;
  std::size_t work_budget_;
  std::atomic<std::uint32_t> pending_ticks_{};
  std::atomic<std::uint32_t> saturated_tick_notifications_{};
  std::atomic<bool> running_{};
  std::array<ConsumerSlot, kMaximumConsumers> consumers_{};
  std::uint64_t generation_{};
  FrameServiceMetrics metrics_{};
};

}  // namespace agon::extender::display
