// Private F7 version-2 owner binding. No GPIO, UART writer or mode authority.
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

  // Caller owns this storage through native DMA cleanup and the final receipt.
  // Provisioning storage grants neither mode admission nor physical ownership.
  bool provide(uint8_t *buffer, size_t capacity) {
    if (pending_ || receipt_ || handover.phase()!=P4ParallelHandover::uart) return false;
    buffer_=buffer; capacity_=capacity; return true;
  }

  bool request(const uint8_t *p, uint32_t now, uint32_t challenge, uint8_t *reply) {
    expire(now);
    if (p[3]==PARALLEL_OFFER) {
      const size_t length=p[10] | (size_t(p[11])<<8);
      if (pending_ || receipt_ || !buffer_ || length>capacity_ ||
          !handover.sessionAdmit(PARALLEL_EXEXT,session,p,reply)) return false;
      memcpy(offer_,p,16); pending_=true; returned_=false;
      phase_=handover.phase(); phase_at_=now; return true;
    }
    if (p[3]==PARALLEL_COMPLETE) {
      if (!pending_ || !returned_ || handover.phase()!=P4ParallelHandover::uart ||
          !parallel_block_matches(offer_,p,PARALLEL_COMPLETE)) return false;
      memcpy(reply,p,16); reply[3]=PARALLEL_COMPLETE_ACK;
      reply[13]=(local_status_ || p[13] || handover.failed()) ? 1 : 0;
      parallel_session_seal(reply);
      if (reply[13]) {
        // UART is already restored. Revoke capability without requesting a
        // new pad fence ahead of the queued failure reply. Physical faults
        // use cancel() instead and can never manufacture this return proof.
        pending_=returned_=false; parallel_session_invalidate(&session);
      }
      else { pending_=false; receipt_=true; }
      return true;
    }
    if (pending_ || receipt_) return false;
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
  // The physical owner must complete reciprocal UART restore first. Calling
  // this method is not a substitute for stop/release/restore adapter proofs.
  bool payloadReturned(uint8_t status,uint32_t now) {
    expire(now);
    if (!pending_ || returned_ || status>1 ||
        handover.phase()!=P4ParallelHandover::uart) return false;
    returned_=true; local_status_=status; phase_at_=now; return true;
  }
  bool takeCompleted(uint8_t *&buffer,size_t &length,uint8_t &direction) {
    if (!receipt_ || handover.failed() || handover.phase()!=P4ParallelHandover::uart ||
        session.phase!=PARALLEL_SESSION_ACTIVE) return false;
    buffer=buffer_; length=offer_[10] | (size_t(offer_[11])<<8);
    direction=offer_[12]; receipt_=false; return true;
  }
  bool pending() const { return pending_; }
  // Physical coordinator only: bytes remain provisional until takeCompleted.
  bool payloadBuffer(uint8_t *&buffer,size_t &capacity) const {
    if(!pending_ || returned_)return false;
    buffer=buffer_;capacity=capacity_;return buffer_!=nullptr;
  }
  const uint8_t *descriptor() const { return pending_ ? offer_ : nullptr; }
  // A normal console lease change revokes the dormant parallel capability,
  // not the already-proven UART pad ownership. Active work must finish or be
  // explicitly cancelled/recovered before a console transition is admitted.
  bool uartTransitionAllowed() const {
    return handover.phase()==P4ParallelHandover::uart && !pending_ && !receipt_;
  }
  bool revokeUartCapability() {
    if(!uartTransitionAllowed())return false;
    parallel_session_invalidate(&session);return true;
  }
  void cancel() {
    pending_=returned_=receipt_=false;
    handover.sessionCancel(session);
  }
 private:
  uint32_t prepared_at_{};
  uint32_t phase_at_{};
  P4ParallelHandover::Phase phase_{P4ParallelHandover::recoveryRelease};
  uint8_t offer_[16]{};
  uint8_t *buffer_{};
  size_t capacity_{};
  uint8_t local_status_{};
  bool pending_{},returned_{},receipt_{};
};
} // namespace agon::extender::transport
