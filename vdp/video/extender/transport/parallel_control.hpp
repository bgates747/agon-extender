// Experimental F7 CRC-free format4 owner binding. No GPIO, UART writer or mode authority.
// The physical adapter must complete handover recovery before any request can
// succeed. Ordinary UART-only startup deliberately never supplies that proof.
#pragma once
#include <cstddef>
#include "p4_parallel_handover.hpp"

namespace agon::extender::transport {
class ParallelControl final {
 public:
  P4ParallelHandover handover;
  t_parallelSession session{};

  // Caller owns storage through native/DMA cleanup and local consumer handoff.
  // Provisioning storage grants neither mode admission nor physical ownership.
  bool provide(uint8_t *buffer, size_t capacity) {
    if (pending_ || completed_ || handover.phase()!=P4ParallelHandover::uart) return false;
    buffer_=buffer; capacity_=capacity; return true;
  }

  bool request(const uint8_t *p, uint32_t now, uint32_t challenge, uint8_t *reply) {
    expire(now);
    if (p[3]==PARALLEL_OFFER) {
      const size_t length=p[10] | (size_t(p[11])<<8);
      if (pending_ || completed_ || !buffer_ || length>capacity_ ||
          !handover.sessionAdmit(PARALLEL_EXEXT,session,p,reply)) return false;
      memcpy(offer_,p,16); pending_=true;
      phase_=handover.phase(); phase_at_=now; return true;
    }
    if (pending_ || completed_) return false;
    uint8_t nonce[4];
    for (unsigned i=0;i<4;++i) nonce[i]=uint8_t(challenge>>(8*i));
    if (!handover.sessionRequest(PARALLEL_EXEXT,session,p,nonce,reply)) return false;
    if (session.phase==PARALLEL_SESSION_STAGED) prepared_at_=now;
    return true;
  }
  void expire(uint32_t now) {
    if (session.phase==PARALLEL_SESSION_STAGED && uint32_t(now-prepared_at_)>=2000)
      cancel();
    if (pending_) {
      if (handover.failed() || session.phase!=PARALLEL_SESSION_ACTIVE) { cancel(); return; }
      // Check the OLD deadline first: a late phase change cannot resurrect it.
      if (uint32_t(now-phase_at_)>=2000) { cancel(); return; }
      if (phase_!=handover.phase()) { phase_=handover.phase(); phase_at_=now; }
    }
  }
  // Physical coordinator only, after exact native completion, DMA cleanup,
  // reciprocal release and UART restore, BEFORE it advertises final READY-high.
  // This is a local handoff, not a wire receipt. Faults call cancel(), never
  // this method. A failed READY write also cancels before any consumer runs.
  bool payloadReturned(uint32_t now) {
    expire(now);
    if (!pending_ || handover.failed() || session.phase!=PARALLEL_SESSION_ACTIVE ||
        handover.phase()!=P4ParallelHandover::uart) return false;
    pending_=false; completed_=true; return true;
  }
  bool takeCompleted(uint8_t *&buffer,size_t &length,uint8_t &direction) {
    if (!completed_ || handover.failed() || handover.phase()!=P4ParallelHandover::uart ||
        session.phase!=PARALLEL_SESSION_ACTIVE) return false;
    buffer=buffer_; length=offer_[10] | (size_t(offer_[11])<<8);
    direction=offer_[12]; completed_=false; return true;
  }
  bool pending() const { return pending_; }
  // Physical coordinator only: bytes remain provisional until takeCompleted.
  bool payloadBuffer(uint8_t *&buffer,size_t &capacity) const {
    if(!pending_)return false;
    buffer=buffer_;capacity=capacity_;return buffer_!=nullptr;
  }
  const uint8_t *descriptor() const { return pending_ ? offer_ : nullptr; }
  // A normal console lease change revokes the dormant parallel capability,
  // not the already-proven UART pad ownership. Active work must finish or be
  // explicitly cancelled/recovered before a console transition is admitted.
  bool uartTransitionAllowed() const {
    return handover.phase()==P4ParallelHandover::uart && !pending_ && !completed_;
  }
  bool revokeUartCapability() {
    if(!uartTransitionAllowed())return false;
    parallel_session_invalidate(&session);return true;
  }
  void cancel() {
    pending_=completed_=false;
    handover.sessionCancel(session);
  }
 private:
  uint32_t prepared_at_{};
  uint32_t phase_at_{};
  P4ParallelHandover::Phase phase_{P4ParallelHandover::recoveryRelease};
  uint8_t offer_[16]{};
  uint8_t *buffer_{};
  size_t capacity_{};
  bool pending_{},completed_{};
};
} // namespace agon::extender::transport
