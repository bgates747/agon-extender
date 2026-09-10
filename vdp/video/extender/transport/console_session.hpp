// EMOS owns formal mode; this class owns only the P4 console transport lease.
// No VDU parser, GPIO access or keyboard policy belongs in this state machine.
#pragma once
#include <cstdint>
#include <cstring>
#include "console_wire.h"
namespace agon::extender::transport {
class ConsoleSession {
 public:
  bool active() const { return active_; }
  void expire(uint32_t now) { if (prepared_ && uint32_t(now-prepared_at_)>=2000) prepared_=false; }
  bool request(const uint8_t *p, uint32_t now, uint32_t challenge, uint8_t *reply) {
    expire(now);
    if (!console_valid(p) || p[13] || p[3]<CONSOLE_PREPARE || p[3]>CONSOLE_ABORT ||
        !(p[4]|p[5]|p[6]|p[7])) return false;
    if (p[3]==CONSOLE_PREPARE) {
      if (p[8]|p[9]|p[10]|p[11]) return false;
      // An explicit fresh prepare invalidates an older lease, including after
      // an Agon-only reset. Stale commits cannot reuse its random challenge.
      std::memcpy(transaction_,p+4,4);
      if (!challenge) challenge=1;
      for (unsigned i=0;i<4;++i) nonce_[i]=uint8_t(challenge>>(i*8));
      active_=false;prepared_=true;prepared_at_=now;
    } else {
      if (std::memcmp(p+4,transaction_,4) || std::memcmp(p+8,nonce_,4)) return false;
      if (p[3]==CONSOLE_COMMIT) {
        if (!prepared_) return false;
        prepared_=false;active_=true;
      } else { prepared_=false;active_=false; }
    }
    std::memcpy(reply,p,CONSOLE_SIZE);
    std::memcpy(reply+8,nonce_,4);reply[3]|=0x80;console_seal(reply);
    return true;
  }
  void cancel() { prepared_=active_=false; std::memset(nonce_,0,4); }
 private:
  uint8_t transaction_[4]{},nonce_[4]{};
  uint32_t prepared_at_{};
  bool prepared_{},active_{};
};
}
