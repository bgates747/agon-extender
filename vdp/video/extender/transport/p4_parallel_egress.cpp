#include "p4_parallel_egress.hpp"

namespace agon::extender::transport {

ParallelTxResult P4ParallelEgress::finish(ParallelTxResult outcome) noexcept {
  // Always attempt pad release even if peripheral stop fails. Never advertise
  // reusable shared pins unless both operations succeeded. The caller must
  // retain the DMA source on cleanupFault until hardware recovery establishes
  // that DMA really stopped.
  bool stopped = backend_.stop();
  bool released = backend_.releaseDataPins();
  if (!stopped || !released) return result_ = ParallelTxResult::cleanupFault;
  if (!backend_.setReadyN(true)) return result_ = ParallelTxResult::cleanupFault;
  return result_ = outcome;
}

ParallelTxResult P4ParallelEgress::begin(
    std::uint8_t const *data, std::size_t length,
    std::uint32_t now, std::uint32_t timeoutTicks) noexcept {
  if (result_ == ParallelTxResult::pending) return ParallelTxResult::busy;
  if (result_ != ParallelTxResult::idle && result_ != ParallelTxResult::complete)
    return result_;  // sticky fault; coordinator must recover explicitly
  if (!data || !length || length > maximumBlockBytes || !timeoutTicks ||
      timeoutTicks > 0x7fffffffU) return ParallelTxResult::invalid;
  length_ = length;
  started_ = now;
  timeout_ = timeoutTicks;
  // No pin/buffer operation is allowed before validating all bounds.
  result_ = ParallelTxResult::pending;
  if (!backend_.setReadyN(true) || !backend_.start(data, length) ||
      !backend_.setReadyN(false)) return finish(ParallelTxResult::backendFault);
  return result_;
}

ParallelTxResult P4ParallelEgress::poll(std::uint32_t now) noexcept {
  if (result_ != ParallelTxResult::pending) return result_;
  if (static_cast<std::uint32_t>(now - started_) >= timeout_)
    return finish(ParallelTxResult::timeout);
  auto progress = backend_.progress();
  if (progress.status == ParallelTxStatus::failed || progress.bytes > length_ ||
      (progress.ended && !progress.started))
    return finish(ParallelTxResult::backendFault);
  // DMA completion can precede the eZ80's last read. Leave pads and READY
  // untouched until VALID deasserts; initial inactive VALID is not completion.
  if (!progress.started || !progress.ended) return result_;
  // An ISR/completion publication may lag the final VALID edge. Do not turn
  // scheduler latency into a false short-block diagnosis; the deadline bounds it.
  if (progress.status == ParallelTxStatus::pending) return result_;
  if (progress.bytes != length_)
    return finish(ParallelTxResult::shortBlock);
  return finish(ParallelTxResult::complete);
}

ParallelTxResult P4ParallelEgress::abort() noexcept {
  // Idempotent cleanup is also the recovery route after a failed stop/release.
  return finish(ParallelTxResult::backendFault);
}

}  // namespace agon::extender::transport
