#include "extender/transport/p4_parallel_data_plane.hpp"

namespace agon::extender::transport {

bool TransportAdmissionBarrier::tryAdmitRecordPublication() const noexcept {
  // This single sequentially consistent atomic provides the total order: a
  // false load admits the already-copied record before any later cancellation;
  // a cancellation which ordered first prevents the queue-head store.
  return !cancel_requested_.load(std::memory_order_seq_cst);
}

void TransportAdmissionBarrier::requestCancel() noexcept {
  cancel_requested_.store(true, std::memory_order_seq_cst);
}

void TransportAdmissionBarrier::reset() noexcept {
  cancel_requested_.store(false, std::memory_order_release);
}

bool TransportAdmissionBarrier::cancelRequested() const noexcept {
  return cancel_requested_.load(std::memory_order_acquire);
}

std::atomic<bool> const &TransportAdmissionBarrier::cancellationFlag()
    const noexcept {
  return cancel_requested_;
}

SpscByteQueue::SpscByteQueue(std::uint8_t *storage,
                             std::size_t capacity) noexcept
    : storage_(storage), capacity_(capacity) {}

bool SpscByteQueue::valid() const noexcept {
  return storage_ != nullptr && capacity_ != 0 &&
         (capacity_ & (capacity_ - 1)) == 0;
}

std::size_t SpscByteQueue::capacity() const noexcept { return capacity_; }

std::size_t SpscByteQueue::size() const noexcept {
  if (!valid()) return 0;
  std::size_t const written = write_count_.load(std::memory_order_acquire);
  std::size_t const read = read_count_.load(std::memory_order_acquire);
  std::size_t const used = written - read;
  return used <= capacity_ ? used : capacity_;
}

std::size_t SpscByteQueue::freeSpace() const noexcept {
  return valid() ? capacity_ - size() : 0;
}

bool SpscByteQueue::prepareRecord(std::uint8_t const *bytes,
                                  std::size_t length,
                                  std::size_t &next_write_count) noexcept {
  if (!valid() || (length != 0 && bytes == nullptr)) return false;
  std::size_t const written = write_count_.load(std::memory_order_relaxed);
  std::size_t const read = read_count_.load(std::memory_order_acquire);
  std::size_t const used = written - read;
  if (used > capacity_ || length > capacity_ - used) return false;

  for (std::size_t offset = 0; offset < length; ++offset) {
    storage_[(written + offset) & (capacity_ - 1)] = bytes[offset];
  }
  next_write_count = written + length;
  return true;
}

bool SpscByteQueue::pushRecord(std::uint8_t const *bytes,
                               std::size_t length) noexcept {
  std::size_t next_write_count{};
  if (!prepareRecord(bytes, length, next_write_count)) return false;
  write_count_.store(next_write_count, std::memory_order_release);
  return true;
}

RecordPushResult SpscByteQueue::pushRecord(
    std::uint8_t const *bytes, std::size_t length,
    TransportAdmissionBarrier &admission_barrier) noexcept {
  std::size_t next_write_count{};
  if (!prepareRecord(bytes, length, next_write_count)) {
    return RecordPushResult::kFailed;
  }
  if (!admission_barrier.tryAdmitRecordPublication()) {
    return RecordPushResult::kCancelled;
  }
  write_count_.store(next_write_count, std::memory_order_release);
  return RecordPushResult::kQueued;
}

int SpscByteQueue::read() noexcept {
  if (!valid()) return -1;
  std::size_t const read = read_count_.load(std::memory_order_relaxed);
  std::size_t const written = write_count_.load(std::memory_order_acquire);
  if (read == written) return -1;
  int const value = storage_[read & (capacity_ - 1)];
  read_count_.store(read + 1, std::memory_order_release);
  return value;
}

int SpscByteQueue::peek() const noexcept {
  if (!valid()) return -1;
  std::size_t const read = read_count_.load(std::memory_order_relaxed);
  std::size_t const written = write_count_.load(std::memory_order_acquire);
  return read == written ? -1 : storage_[read & (capacity_ - 1)];
}

void SpscByteQueue::clear() noexcept {
  std::size_t const written = write_count_.load(std::memory_order_acquire);
  read_count_.store(written, std::memory_order_release);
}

P4ParlioIngress::P4ParlioIngress(
    ParlioReceiveBackend &backend, SpscByteQueue &queue,
    TransportFaultLatch &fault_latch, std::uint8_t *record_storage,
    std::size_t record_storage_capacity,
    std::size_t maximum_record_bytes) noexcept
    : backend_(backend),
      queue_(queue),
      fault_latch_(fault_latch),
      record_storage_(record_storage),
      record_storage_capacity_(record_storage_capacity),
      maximum_record_bytes_(maximum_record_bytes) {}

void P4ParlioIngress::markFault(TransportFault fault) noexcept {
  fault_latch_.latch(fault);
  active_ = false;
}

bool P4ParlioIngress::start() noexcept {
  if (active_) return fault_latch_.healthy();
  if (!fault_latch_.healthy() || acquired_ || enabled_ || armed_) return false;
  if (!queue_.valid() || record_storage_ == nullptr ||
      maximum_record_bytes_ == 0 ||
      maximum_record_bytes_ > record_storage_capacity_ ||
      maximum_record_bytes_ > queue_.capacity()) {
    markFault(TransportFault::kInvalidConfiguration);
    return false;
  }

  if (!backend_.acquire(record_storage_, maximum_record_bytes_)) {
    markFault(TransportFault::kIngressAcquire);
    acquired_ = !backend_.release();
    return false;
  }
  acquired_ = true;

  if (!backend_.enable()) {
    markFault(TransportFault::kIngressEnable);
    enabled_ = !backend_.disable();
    bool const released = backend_.release();
    if (!released) {
      fault_latch_.latch(TransportFault::kIngressRelease);
    }
    acquired_ = !released;
    if (released) enabled_ = false;
    return false;
  }
  enabled_ = true;
  active_ = true;
  return true;
}

bool P4ParlioIngress::stop() noexcept {
  bool ok = true;
  if (armed_) {
    bool const cancelled = backend_.cancel();
    if (!cancelled) fault_latch_.latch(TransportFault::kReceiveCancel);
    ok = cancelled && ok;
    if (cancelled) armed_ = false;
  }
  if (enabled_) {
    bool const disabled = backend_.disable();
    if (!disabled) fault_latch_.latch(TransportFault::kIngressDisable);
    ok = disabled && ok;
    if (disabled) enabled_ = false;
  }
  if (acquired_) {
    bool const released = backend_.release();
    if (!released) fault_latch_.latch(TransportFault::kIngressRelease);
    ok = released && ok;
    if (released) {
      acquired_ = false;
      enabled_ = false;
      armed_ = false;
    }
  }
  active_ = false;
  return ok;
}

P4ParlioIngress::ArmResult P4ParlioIngress::arm(
    std::atomic<bool> const &cancel_requested) noexcept {
  if (!active_) return ArmResult::kNotActive;
  if (!fault_latch_.healthy()) {
    active_ = false;
    return ArmResult::kFaulted;
  }
  if (cancel_requested.load(std::memory_order_acquire)) {
    return ArmResult::kCancelled;
  }
  if (queue_.freeSpace() < maximum_record_bytes_) {
    return ArmResult::kBackpressured;
  }
  if (!backend_.arm()) {
    markFault(TransportFault::kReceiveArm);
    // arm() may have failed after programming part of the target peripheral.
    // Treat it as tentatively armed.  The data-plane owner releases the
    // external direction before invoking abortArmed(), and stop() can retry a
    // failed cancellation.
    armed_ = true;
    return ArmResult::kFaulted;
  }
  armed_ = true;
  return ArmResult::kArmed;
}

ReceiveCompletion P4ParlioIngress::wait(
    ReceiveWaitPolicy policy,
    std::atomic<bool> const &cancel_requested) noexcept {
  if (!active_ || !armed_) return {ReceiveStatus::kError, 0};
  return backend_.wait(policy, cancel_requested);
}

P4ParlioIngress::CommitResult P4ParlioIngress::commit(
    std::size_t bytes_received,
    TransportAdmissionBarrier &admission_barrier) noexcept {
  if (!armed_) return CommitResult::kFaulted;
  armed_ = false;
  if (bytes_received == 0 || bytes_received > maximum_record_bytes_) {
    markFault(TransportFault::kInvalidRecordLength);
    return CommitResult::kFaulted;
  }
  switch (queue_.pushRecord(record_storage_, bytes_received,
                            admission_barrier)) {
    case RecordPushResult::kQueued:
      return CommitResult::kQueued;
    case RecordPushResult::kCancelled:
      return CommitResult::kCancelled;
    case RecordPushResult::kFailed:
      markFault(TransportFault::kQueueInvariant);
      return CommitResult::kFaulted;
  }
  markFault(TransportFault::kQueueInvariant);
  return CommitResult::kFaulted;
}

bool P4ParlioIngress::abortArmed() noexcept {
  if (!armed_) return true;
  bool const cancelled = backend_.cancel();
  if (cancelled) {
    armed_ = false;
  } else {
    markFault(TransportFault::kReceiveCancel);
  }
  return cancelled;
}

bool P4ParlioIngress::active() const noexcept { return active_; }

bool P4ParlioIngress::armed() const noexcept { return armed_; }

std::size_t P4ParlioIngress::maximumRecordBytes() const noexcept {
  return maximum_record_bytes_;
}

P4ParallelDataPlane::P4ParallelDataPlane(
    P4EpochHardware &hardware, ParallelEpochAuthority &authority,
    P4ParlioIngress &ingress, SpscByteQueue &input_queue,
    TransportFaultLatch &fault_latch) noexcept
    : hardware_(hardware),
      authority_(authority),
      ingress_(ingress),
      input_queue_(input_queue),
      fault_latch_(fault_latch) {}

bool P4ParallelDataPlane::leaseIsLive() const noexcept {
  return lease_.generation != 0 && authority_.isLive(lease_);
}

void P4ParallelDataPlane::latchCleanupFailure(
    bool operation_ok, TransportFault fault) noexcept {
  if (!operation_ok) fault_latch_.latch(fault);
}

bool P4ParallelDataPlane::failStart(TransportFault fault) noexcept {
  fault_latch_.latch(fault);
  bool ok = true;
  bool const ready_released = hardware_.releaseReady();
  latchCleanupFailure(ready_released, TransportFault::kReadyRelease);
  ok = ready_released && ok;
  bool const forward_released = hardware_.releaseParallelForwardBanks();
  latchCleanupFailure(forward_released,
                      TransportFault::kForwardBanksRelease);
  ok = forward_released && ok;
  ok = ingress_.stop() && ok;
  bool const pads_released = hardware_.releaseParallelInputPads();
  latchCleanupFailure(pads_released, TransportFault::kParallelPadsRelease);
  ok = pads_released && ok;
  bool const return_released = hardware_.releaseReturnBank();
  latchCleanupFailure(return_released, TransportFault::kReturnBankRelease);
  ok = return_released && ok;
  if (ok) lease_ = {};
  state_ = ok ? DataPlaneState::kStopped : DataPlaneState::kFaulted;
  return false;
}

bool P4ParallelDataPlane::enterAuthorizedEpoch(
    ParallelEpochLease lease) noexcept {
  if (state_ != DataPlaneState::kStopped || !fault_latch_.healthy()) {
    return false;
  }
  if (lease.generation == 0 || !authority_.isLive(lease)) {
    fault_latch_.latch(TransportFault::kEpochNotAuthorized);
    return false;
  }
  // Bytes admitted under one authorization generation may never be parsed
  // under another.  Discarding them is a coordinator decision because only it
  // can establish that the consumer is quiescent; entry therefore fails
  // closed instead of silently clearing them.
  if (input_queue_.size() != 0) {
    fault_latch_.latch(TransportFault::kStaleBufferedInput);
    return false;
  }

  state_ = DataPlaneState::kStarting;
  lease_ = lease;
  admission_barrier_.reset();

  if (!hardware_.releaseReady()) {
    return failStart(TransportFault::kReadyRelease);
  }
  if (!hardware_.releaseParallelForwardBanks()) {
    return failStart(TransportFault::kForwardBanksRelease);
  }
  if (!hardware_.releaseReturnBank()) {
    return failStart(TransportFault::kReturnBankRelease);
  }
  if (!hardware_.disableSharedUartOutputs()) {
    return failStart(TransportFault::kSharedUartDisable);
  }
  if (!hardware_.configureParallelInputPads()) {
    return failStart(TransportFault::kParallelPadsConfigure);
  }
  if (!ingress_.start()) {
    TransportFault const ingress_fault = fault_latch_.fault();
    return failStart(
        ingress_fault == TransportFault::kNone
            ? TransportFault::kIngressAcquire
            : ingress_fault);
  }
  if (!leaseIsLive()) {
    return failStart(TransportFault::kEpochLeaseLost);
  }
  if (!hardware_.enableParallelForwardBanks()) {
    return failStart(TransportFault::kParallelForwardEnable);
  }

  state_ = DataPlaneState::kActive;
  return true;
}

ServiceResult P4ParallelDataPlane::failActive(
    TransportFault fault, bool abort_receive) noexcept {
  if (fault == TransportFault::kNone) {
    fault = TransportFault::kReceiveBackend;
  }
  fault_latch_.latch(fault);
  latchCleanupFailure(hardware_.releaseReady(),
                      TransportFault::kReadyRelease);
  latchCleanupFailure(hardware_.releaseParallelForwardBanks(),
                      TransportFault::kForwardBanksRelease);
  if (abort_receive) (void)ingress_.abortArmed();
  state_ = DataPlaneState::kFaulted;
  return ServiceResult::kFaulted;
}

ServiceResult P4ParallelDataPlane::serviceOnce(
    ReceiveWaitPolicy wait_policy) noexcept {
  if (state_ != DataPlaneState::kActive) return ServiceResult::kNotActive;
  if (!wait_policy.valid()) {
    return failActive(TransportFault::kInvalidConfiguration,
                      ingress_.armed());
  }
  if (!fault_latch_.healthy()) {
    return failActive(fault_latch_.fault(), ingress_.armed());
  }
  if (!leaseIsLive()) {
    return failActive(TransportFault::kEpochLeaseLost, ingress_.armed());
  }

  P4ParlioIngress::ArmResult const arm_result =
      ingress_.arm(admission_barrier_.cancellationFlag());
  switch (arm_result) {
    case P4ParlioIngress::ArmResult::kBackpressured:
      return ServiceResult::kBackpressured;
    case P4ParlioIngress::ArmResult::kCancelled:
      return ServiceResult::kCancelled;
    case P4ParlioIngress::ArmResult::kFaulted:
      return failActive(fault_latch_.fault(), ingress_.armed());
    case P4ParlioIngress::ArmResult::kNotActive:
      return failActive(TransportFault::kReceiveBackend, ingress_.armed());
    case P4ParlioIngress::ArmResult::kArmed:
      break;
  }

  // Close the admission window between the backend's pre-arm cancellation
  // check and READY_N assertion.  A request arriving after this acquire load
  // can still race the GPIO operation, but no already-published request may
  // cause an avoidable READY pulse.
  if (admission_barrier_.cancelRequested()) {
    if (!ingress_.abortArmed()) {
      return failActive(fault_latch_.fault(), false);
    }
    return fault_latch_.healthy() ? ServiceResult::kCancelled
                                  : failActive(fault_latch_.fault(), false);
  }
  if (!leaseIsLive()) {
    return failActive(TransportFault::kEpochLeaseLost, true);
  }
  if (!fault_latch_.healthy()) {
    return failActive(fault_latch_.fault(), true);
  }
  if (!hardware_.assertReady()) {
    return failActive(TransportFault::kReadyAssert, true);
  }
  if (!fault_latch_.healthy()) {
    return failActive(fault_latch_.fault(), true);
  }

  ReceiveCompletion const completion =
      ingress_.wait(wait_policy, admission_barrier_.cancellationFlag());
  if (!hardware_.releaseReady()) {
    return failActive(TransportFault::kReadyRelease, true);
  }
  if (!fault_latch_.healthy()) {
    return failActive(fault_latch_.fault(), true);
  }
  if (!leaseIsLive()) {
    return failActive(TransportFault::kEpochLeaseLost, true);
  }
  if (admission_barrier_.cancelRequested()) {
    if (!ingress_.abortArmed()) {
      return failActive(fault_latch_.fault(), false);
    }
    return fault_latch_.healthy() ? ServiceResult::kCancelled
                                  : failActive(fault_latch_.fault(), false);
  }

  switch (completion.status) {
    case ReceiveStatus::kComplete:
      switch (ingress_.commit(completion.bytes_received,
                              admission_barrier_)) {
        case P4ParlioIngress::CommitResult::kFaulted:
          return failActive(fault_latch_.fault(), ingress_.armed());
        case P4ParlioIngress::CommitResult::kCancelled:
          return fault_latch_.healthy()
                     ? ServiceResult::kCancelled
                     : failActive(fault_latch_.fault(), false);
        case P4ParlioIngress::CommitResult::kQueued:
          break;
      }
      // The barrier check before queue-head publication is the admission
      // linearization point.  A fault, lease revocation, or cancellation which
      // wins immediately afterwards
      // quarantines the complete record behind ExtenderVdpStream's fault gate
      // and must never be reported as a post-fault kRecordQueued.
      if (!fault_latch_.healthy()) {
        return failActive(fault_latch_.fault(), false);
      }
      if (!leaseIsLive()) {
        return failActive(TransportFault::kEpochLeaseLost, false);
      }
      if (admission_barrier_.cancelRequested()) {
        return fault_latch_.healthy()
                   ? ServiceResult::kCancelled
                   : failActive(fault_latch_.fault(), false);
      }
      return ServiceResult::kRecordQueued;
    case ReceiveStatus::kIdle:
      // No record began.  READY_N is already released; reset the still-armed
      // peripheral transaction before the owner retries this active epoch.
      if (!ingress_.abortArmed()) {
        return failActive(fault_latch_.fault(), false);
      }
      return ServiceResult::kBackpressured;
    case ReceiveStatus::kCancelled:
      (void)ingress_.abortArmed();
      return fault_latch_.healthy() ? ServiceResult::kCancelled
                                    : failActive(fault_latch_.fault(), false);
    case ReceiveStatus::kTimeout:
      return failActive(TransportFault::kReceiveTimeout, true);
    case ReceiveStatus::kOverflow:
      return failActive(TransportFault::kReceiveOverflow, true);
    case ReceiveStatus::kError:
      return failActive(TransportFault::kReceiveBackend, true);
  }
  return failActive(TransportFault::kReceiveBackend, true);
}

void P4ParallelDataPlane::requestCancel() noexcept {
  admission_barrier_.requestCancel();
}

bool P4ParallelDataPlane::stop() noexcept {
  if (state_ == DataPlaneState::kStopped) return true;
  state_ = DataPlaneState::kStopping;
  requestCancel();

  bool ok = true;
  bool const ready_released = hardware_.releaseReady();
  latchCleanupFailure(ready_released, TransportFault::kReadyRelease);
  ok = ready_released && ok;
  bool const forward_released = hardware_.releaseParallelForwardBanks();
  latchCleanupFailure(forward_released,
                      TransportFault::kForwardBanksRelease);
  ok = forward_released && ok;
  ok = ingress_.stop() && ok;
  bool const pads_released = hardware_.releaseParallelInputPads();
  latchCleanupFailure(pads_released, TransportFault::kParallelPadsRelease);
  ok = pads_released && ok;
  bool const return_released = hardware_.releaseReturnBank();
  latchCleanupFailure(return_released, TransportFault::kReturnBankRelease);
  ok = return_released && ok;

  if (ok) lease_ = {};
  state_ = ok ? DataPlaneState::kStopped : DataPlaneState::kFaulted;
  return ok;
}

bool P4ParallelDataPlane::resetFault() noexcept {
  if (state_ != DataPlaneState::kStopped || ingress_.active() ||
      ingress_.armed()) {
    return false;
  }
  fault_latch_.clear();
  admission_barrier_.reset();
  return true;
}

bool P4ParallelDataPlane::discardBufferedInput() noexcept {
  if (state_ != DataPlaneState::kStopped || ingress_.active() ||
      ingress_.armed()) {
    return false;
  }
  input_queue_.clear();
  return true;
}

DataPlaneState P4ParallelDataPlane::state() const noexcept { return state_; }

ParallelEpochLease P4ParallelDataPlane::lease() const noexcept {
  return lease_;
}

}  // namespace agon::extender::transport
