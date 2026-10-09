// Private F7 version-2 owner binding. No GPIO, UART writer or mode authority.
// The physical adapter must complete handover recovery before any request can
// succeed. Ordinary UART-only startup deliberately never supplies that proof.
#pragma once
#include "p4_parallel_handover.hpp"

namespace agon::extender::transport {
class ParallelControl final {
 public:
  P4ParallelHandover handover;
  t_parallelSession session{};

  bool request(const uint8_t *p, uint32_t now, uint32_t challenge, uint8_t *reply) {
    expire(now);
    uint8_t nonce[4];
    for (unsigned i=0;i<4;++i) nonce[i]=uint8_t(challenge>>(8*i));
    if (!handover.sessionRequest(PARALLEL_EXEXT,session,p,nonce,reply)) return false;
    if (session.phase==PARALLEL_SESSION_STAGED) prepared_at_=now;
    return true;
  }
  void expire(uint32_t now) {
    if (session.phase==PARALLEL_SESSION_STAGED && uint32_t(now-prepared_at_)>=2000)
      cancel();
  }
  void cancel() { handover.sessionCancel(session); }
 private:
  uint32_t prepared_at_{};
};
} // namespace agon::extender::transport
