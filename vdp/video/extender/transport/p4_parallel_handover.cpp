#include "p4_parallel_handover.hpp"
#include "control_crc.h"
#include "parallel_wire.h"

namespace agon::extender::transport {
bool P4ParallelHandover::admit(std::uint8_t mode, std::uint8_t *session,
                              const std::uint8_t *offer, std::uint8_t *ack) noexcept {
  if (mode != PARALLEL_EXEXT || phase_ != uart ||
      !parallel_offer_valid(session, offer)) return false;
  if (!begin()) return false;
  session[4]=offer[8]; session[5]=offer[9];
  memcpy(ack,offer,16); ack[3]=PARALLEL_ACK;
  const auto crc=console_crc(ack);
  ack[14]=static_cast<std::uint8_t>(crc);
  ack[15]=static_cast<std::uint8_t>(crc>>8);
  return true;
}
bool P4ParallelHandover::begin() noexcept {
  if (phase_ != uart) return false;
  failed_=false; phase_=drain; return true;
}
void P4ParallelHandover::cancel() noexcept {
  failed_=true; phase_=recoveryRelease;
  // Do not change READY until release really completes.
}
P4ParallelHandover::Action P4ParallelHandover::step(std::uint8_t c) noexcept {
  const bool v=c&validHigh, clock=c&clockHigh;
  switch (phase_) {
    case recoveryRelease:
      if (!(c&released)) return release;
      ready_=false; phase_=recoveryAnnounce; break;
    case recoveryAnnounce:
      // READY low also alerts an otherwise idle EMOS to a P4 reset. Do not
      // release that indication until EMOS reports its pads released.
      if (!v || clock) break;
      ready_=true; phase_=recoveryClear; break;
    case recoveryClear:
      if (v || clock) break;
      ready_=false; phase_=recoveryAck; break;
    case recoveryAck:
      if (!v || clock) break;
      phase_=recoveryUart; return restore;
    case recoveryUart:
      if (!(c&uartUp)) return restore;
      ready_=true; phase_=uart; return live;
    case uart:
      if (v && !clock) return live;
      cancel(); return release;
    case drain:
      if (!(c&quiet)) return fence;
      phase_=entryRelease; return release;
    case entryRelease:
      if (!(c&released)) return release;
      phase_=entryRequest; break;
    case entryRequest:
      if (v || clock) break;
      ready_=false; phase_=entryAck; break;
    case entryAck:
      if (!v || clock) break;
      ready_=true; phase_=entryClock; break;
    case entryClock:
      if (!v || !clock) break;
      phase_=localArm; return arm;
    case localArm:
      // EMOS may reset while asynchronous arming is still in progress. Do
      // not publish READY low from that old operation after its grant vanished:
      // a rebooting EMOS could interpret it as a fresh release acknowledgement.
      if (!v || !clock) { cancel(); return release; }
      if (!(c&armed)) return arm;
      ready_=false; phase_=block; return run;
    case block:
      if (v && !clock) { cancel(); return release; }
      // Includes DMA stop AND pad release; raw DMA completion is insufficient.
      if (!(c&done)) break;
      ready_=true; phase_=blockReturn; break;
    case blockReturn:
      if (clock) break;
      // Our pads are already released. EMOS can see that READY high and
      // request acknowledgement before this task sees its intermediate V=1.
      // C=0,V=0 also proves EMOS's release in this post-block phase.
      if (v) phase_=recoveryClear;
      else { ready_=false; phase_=recoveryAck; }
      break;
    default:
      cancel(); return release;
  }
  return wait;
}
} // namespace agon::extender::transport
