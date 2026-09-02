// Production forward-parallel data-plane core for the ESP32-P4 VDP port.
//
// This file contains no ESP-IDF calls, circuit-revision branches, activation
// grammar, or return-UART binding.  A target adapter supplies PARLIO and pad
// operations.  The same core can therefore be driven by a production epoch
// coordinator or by a non-release fixed-backend qualification composition.
#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include "extender/transport/transport_fault.hpp"

namespace agon::extender::transport {

// Arbitrates the single producer's queue-head publication with cross-context
// cancellation.  A successful admission check is the record's linearization
// point.  Cancellation never waits for the producer: a record which won first
// may finish its head store, but subsequent fault checks quarantine it.
class TransportAdmissionBarrier final {
 public:
  bool tryAdmitRecordPublication() const noexcept;
  void requestCancel() noexcept;
  void reset() noexcept;
  bool cancelRequested() const noexcept;
  std::atomic<bool> const &cancellationFlag() const noexcept;

 private:
  std::atomic<bool> cancel_requested_{};
};

enum class RecordPushResult : std::uint8_t {
  kQueued,
  kCancelled,
  kFailed,
};

// A fixed-capacity, allocation-free single-producer/single-consumer byte
// queue.  Capacity must be a power of two: that makes ring positions invariant
// when the monotonic unsigned counters wrap.  pushRecord publishes its head
// only after copying the complete physical record, so the parser can never
// observe a truncated record.  The queue deliberately does not preserve
// record boundaries.
class SpscByteQueue final {
 public:
  SpscByteQueue(std::uint8_t *storage, std::size_t capacity) noexcept;

  bool valid() const noexcept;
  std::size_t capacity() const noexcept;
  std::size_t size() const noexcept;
  std::size_t freeSpace() const noexcept;
  bool pushRecord(std::uint8_t const *bytes, std::size_t length) noexcept;
  int read() noexcept;
  int peek() const noexcept;

  // The lifecycle owner may discard buffered input only while producer and
  // consumer are quiescent.
  void clear() noexcept;

 private:
  friend class P4ParlioIngress;

  bool prepareRecord(std::uint8_t const *bytes, std::size_t length,
                     std::size_t &next_write_count) noexcept;
  RecordPushResult pushRecord(
      std::uint8_t const *bytes, std::size_t length,
      TransportAdmissionBarrier &admission_barrier) noexcept;

  std::uint8_t *storage_{};
  std::size_t capacity_{};
  alignas(64) std::atomic<std::size_t> write_count_{};
  alignas(64) std::atomic<std::size_t> read_count_{};
};

struct ParallelEpochLease {
  std::uint64_t generation{};
};

class ParallelEpochAuthority {
 public:
  virtual ~ParallelEpochAuthority() = default;
  virtual bool isLive(ParallelEpochLease const &lease) const noexcept = 0;
};

// P4EpochHardware is the sole owner of READY_N, the parallel-forward enables,
// the return-bank enable, and the shared UART/parallel pad mux.  Every release
// method must be idempotent and must implement open-drain release rather than
// a push-pull high at an active-low circuit control.
class P4EpochHardware {
 public:
  virtual ~P4EpochHardware() = default;
  virtual bool releaseReady() noexcept = 0;
  virtual bool releaseParallelForwardBanks() noexcept = 0;
  virtual bool releaseReturnBank() noexcept = 0;
  virtual bool disableSharedUartOutputs() noexcept = 0;
  virtual bool configureParallelInputPads() noexcept = 0;
  virtual bool releaseParallelInputPads() noexcept = 0;
  virtual bool enableParallelForwardBanks() noexcept = 0;
  virtual bool assertReady() noexcept = 0;
};

enum class ReceiveStatus : std::uint8_t {
  kComplete,
  // No VALID-active record was observed during one bounded idle poll.  The
  // owner may reset/re-arm the transaction without faulting the epoch.
  kIdle,
  // A VALID-active record failed to complete within its bounded window.
  kTimeout,
  kCancelled,
  kOverflow,
  kError,
};

struct ReceiveCompletion {
  ReceiveStatus status{ReceiveStatus::kError};
  std::size_t bytes_received{};
};

struct ReceiveWaitPolicy {
  // ESP-IDF's PARLIO completion API expresses this bound in milliseconds.  A
  // backend may return kIdle after this long without observing record activity;
  // once activity begins, it must grant a fresh full completion window before
  // returning kTimeout.  Keep milliseconds at this portable boundary; the
  // target adapter performs any checked scheduler conversion.
  std::uint32_t completion_timeout_ms{};
  // A target wait must observe requestCancel() within this many milliseconds,
  // either through an ISR/task notification or bounded wait slices.  Waiting
  // for the full completion timeout before checking cancellation is invalid.
  std::uint32_t cancellation_poll_ms{};

  bool valid() const noexcept {
    return completion_timeout_ms != 0 && cancellation_poll_ms != 0 &&
           cancellation_poll_ms <= completion_timeout_ms;
  }
};

// The target backend owns the concrete PARLIO unit, delimiter, DMA resources,
// and ISR/task notification.  wait() must return a completion copied through
// an ISR-safe primitive with release/acquire semantics.  A volatile byte count
// does not satisfy this interface.  All cleanup methods are idempotent so the
// core can unwind a partially successful operation.
class ParlioReceiveBackend {
 public:
  virtual ~ParlioReceiveBackend() = default;
  virtual bool acquire(std::uint8_t *record_storage,
                       std::size_t capacity) noexcept = 0;
  virtual bool enable() noexcept = 0;
  virtual bool arm() noexcept = 0;
  virtual ReceiveCompletion wait(
      ReceiveWaitPolicy policy,
      std::atomic<bool> const &cancel_requested) noexcept = 0;
  virtual bool cancel() noexcept = 0;
  virtual bool disable() noexcept = 0;
  virtual bool release() noexcept = 0;
};

class P4ParlioIngress final {
 public:
  enum class ArmResult : std::uint8_t {
    kArmed,
    kBackpressured,
    kCancelled,
    kFaulted,
    kNotActive,
  };

  enum class CommitResult : std::uint8_t {
    kQueued,
    kCancelled,
    kFaulted,
  };

  P4ParlioIngress(ParlioReceiveBackend &backend, SpscByteQueue &queue,
                  TransportFaultLatch &fault_latch,
                  std::uint8_t *record_storage,
                  std::size_t record_storage_capacity,
                  std::size_t maximum_record_bytes) noexcept;

  bool start() noexcept;
  bool stop() noexcept;
  ArmResult arm(std::atomic<bool> const &cancel_requested) noexcept;
  ReceiveCompletion wait(
      ReceiveWaitPolicy policy,
      std::atomic<bool> const &cancel_requested) noexcept;
  CommitResult commit(
      std::size_t bytes_received,
      TransportAdmissionBarrier &admission_barrier) noexcept;
  bool abortArmed() noexcept;

  bool active() const noexcept;
  bool armed() const noexcept;
  std::size_t maximumRecordBytes() const noexcept;

 private:
  void markFault(TransportFault fault) noexcept;

  ParlioReceiveBackend &backend_;
  SpscByteQueue &queue_;
  TransportFaultLatch &fault_latch_;
  std::uint8_t *record_storage_{};
  std::size_t record_storage_capacity_{};
  std::size_t maximum_record_bytes_{};
  bool acquired_{};
  bool enabled_{};
  bool armed_{};
  bool active_{};
};

enum class DataPlaneState : std::uint8_t {
  kStopped,
  kStarting,
  kActive,
  kFaulted,
  kStopping,
};

enum class ServiceResult : std::uint8_t {
  kRecordQueued,
  kBackpressured,
  kCancelled,
  kFaulted,
  kNotActive,
};

// P4ParallelDataPlane is the already-authorized epoch boundary.  Activation
// remains outside this class: enterAuthorizedEpoch() accepts only a live lease
// from the injected authority.  All lifecycle calls except requestCancel()
// belong to one owner task.  requestCancel() is the sole cross-context method.
class P4ParallelDataPlane final : public TransportCancellation {
 public:
  P4ParallelDataPlane(P4EpochHardware &hardware,
                      ParallelEpochAuthority &authority,
                      P4ParlioIngress &ingress,
                      SpscByteQueue &input_queue,
                      TransportFaultLatch &fault_latch) noexcept;

  bool enterAuthorizedEpoch(ParallelEpochLease lease) noexcept;
  ServiceResult serviceOnce(ReceiveWaitPolicy wait_policy) noexcept;
  void requestCancel() noexcept override;
  bool stop() noexcept;

  // resetFault() and discardBufferedInput() are permitted only in Stopped.
  // The coordinator must separately ensure the parser consumer is quiescent.
  bool resetFault() noexcept;
  bool discardBufferedInput() noexcept;

  DataPlaneState state() const noexcept;
  ParallelEpochLease lease() const noexcept;

 private:
  bool leaseIsLive() const noexcept;
  bool failStart(TransportFault fault) noexcept;
  ServiceResult failActive(TransportFault fault,
                           bool abort_receive) noexcept;
  void latchCleanupFailure(bool operation_ok,
                           TransportFault fault) noexcept;

  P4EpochHardware &hardware_;
  ParallelEpochAuthority &authority_;
  P4ParlioIngress &ingress_;
  SpscByteQueue &input_queue_;
  TransportFaultLatch &fault_latch_;
  TransportAdmissionBarrier admission_barrier_;
  ParallelEpochLease lease_{};
  DataPlaneState state_{DataPlaneState::kStopped};
};

}  // namespace agon::extender::transport
