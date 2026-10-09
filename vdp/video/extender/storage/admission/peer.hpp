#pragma once
// Fixed-size P4 control/file queues. Console owner alone calls
// take()/receive(). Runtime wrapper serializes all calls; no filesystem,
// sockets or allocation here.
#include "../sd_wire.h"
#include <array>
#include <cstdint>
#include <cstring>
namespace agon::extender::storage::admission {
using Binding = std::array<std::uint8_t, 28>;
class Peer {
  // UART and HTTP callers can sample time before competing for the lock.
  // A slightly older sample is not a 49-day timeout. Deadlines are all well
  // below half the uint32 clock period, so signed ordering also handles wrap.
  static std::uint32_t age(std::uint32_t now, std::uint32_t then) {
    const auto delta = now - then;
    return delta < 0x80000000U ? delta : 0;
  }
public:
  enum Phase {
    offline,
    idle,
    armed,
    offered,
    claimed,
    active,
    closing,
    finished,
    closed,
    failed
  };
  Phase phase = offline;
  Binding binding{};
  bool success = false;
  void transportLost() {
    // Keep an already-confirmed CLOSE receipt for its HTTP worker. Other jobs
    // fail with their binding intact; no old record or capability may be sent.
    if(phase!=closed)fail();
    pollValid_=false;controlSize_=cachedSize_=lastSize_=fileSize_=answerSize_=0;
    controlSession_=lastSequence_=0;std::memset(nonce_,0,sizeof(nonce_));
  }
  std::uint32_t fileSession() const {
    auto n = sd_crc(binding.data(), binding.size());
    return n ? n : 1;
  }
  static bool validDescriptor(const std::uint8_t *p, unsigned n) {
    if (n < 9 || n > 248 || p[0] < 1 || p[0] > 8 || p[1] > 3 || sd_u16(p + 6))
      return false;
    unsigned a = sd_u16(p + 2), b = sd_u16(p + 4);
    if (a > 120 || b > 120 || 8 + a + b != n)
      return false;
    if (p[0] == 6 || p[0] == 7) {
      if (!a || !b)
        return false;
    } else if (p[0] == 3 || p[0] == 5) {
      if (a || !b)
        return false;
    } else if (!a || b)
      return false;
    unsigned start = 8;
    for (unsigned len : {a, b}) {
      if (len) {
        if (p[start] != '/')
          return false;
        for (unsigned i = start; i < start + len; ++i)
          if (p[i] < 32 || p[i] > 126 || p[i] == '\\')
            return false;
      }
      start += len;
    }
    return true;
  }
  std::uint32_t pollAge(std::uint32_t now) const {
    return pollValid_ ? age(now, pollAt_) : 0xffffffffU;
  }
  bool idleReady(std::uint32_t now) const {
    return phase == idle && pollValid_ && age(now, pollAt_) <= 150;
  }
  bool owned() const { return phase >= armed && phase <= finished; }
  bool reserve(const std::uint8_t *descriptor, unsigned n, std::uint32_t now) {
    expire(now);
    if (phase != idle || !pollValid_ || age(now, pollAt_) > 150 ||
        !validDescriptor(descriptor, n) || nextJob_ == 0xffffffffU)
      return false;
    std::memcpy(descriptor_, descriptor, n);
    descriptorSize_ = n;
    descriptorCrc_ = sd_crc(descriptor, n);
    binding = {};
    std::memcpy(binding.data(), nonce_, 8);
    sd_put32(binding.data() + 8, generation_);
    sd_put32(binding.data() + 12, ++nextJob_);
    binding[24] = 1;
    binding[25] = descriptor[0];
    phase = armed;
    since_ = now;
    success = false;
    fileSize_ = answerSize_ = 0;
    poisoned_ = cancelled_ = false;
    return true;
  }
  bool submit(const Binding &b, const std::uint8_t *p, unsigned n,
              std::uint32_t now) {
    expire(now);
    if (phase != active || poisoned_ || b != binding || fileSize_ ||
        !sd_valid(p, n) || p[3] != SD_REQUEST || p[13] || !sd_u32(p + 8) ||
        sd_u32(p + 4) != fileSession())
      return false;
    fileSize_ = n;
    std::memcpy(file_, p, n);
    answerSize_ = 0;
    fileSent_ = false;
    return true;
  }
  unsigned answer(const Binding &b, std::uint8_t *p) {
    if (b != binding || !answerSize_)
      return 0;
    unsigned n = answerSize_;
    std::memcpy(p, answer_, n);
    answerSize_ = 0;
    fileSize_ = 0;
    return n;
  }
  bool finish(const Binding &b, std::uint32_t now) {
    if (phase != active || b != binding || fileSize_)
      return false;
    phase = closing;
    since_ = now;
    return true;
  }
  void cancel(const Binding &b, bool orderly = false) {
    if (b == binding && owned()) {
      // A client EOF is not a UART fault. Only a healthy quiet boundary may
      // request normal FINISH; the utility still rejects open write stages.
      // Preserve poison across repeated requests and never call a cancelled
      // operation successful merely because terminal cleanup succeeded.
      const bool quiet = (phase == active || (phase == closing && cancelled_)) &&
                         !fileSize_ && !answerSize_;
      poisoned_ = poisoned_ || !orderly || !quiet;
      cancelled_ = true;
      phase = closing;
      fileSize_ = answerSize_ = 0;
    }
  }
  void retire() {
    if (phase == closed || phase == failed) {
      phase = idle;
      pollValid_ = false;
      fileSize_ = answerSize_ = 0;
    }
  }
  void expire(std::uint32_t now) {
    if ((phase == armed || phase == offered) && age(now, since_) > 200)
      fail();
    if (phase == claimed && age(now, since_) > 1000)
      fail();
    if ((phase == active || phase == closing || phase == finished) &&
        age(now, seen_) > 5000)
      fail();
    if (phase == idle && pollValid_ && age(now, pollAt_) > 150)
      pollValid_ = false;
  }
  unsigned take(std::uint8_t *out, std::uint32_t now) {
    expire(now);
    if (controlSize_) {
      unsigned n = controlSize_;
      std::memcpy(out, control_, n);
      controlSize_ = 0;
      return n;
    }
    if (phase == active && fileSize_ && !fileSent_) {
      std::memcpy(out, file_, fileSize_);
      fileSent_ = true;
      return fileSize_;
    }
    return 0;
  }
  bool receive(const std::uint8_t *p, unsigned n, std::uint32_t now,
               std::uint32_t randomA, std::uint32_t randomB) {
    expire(now);
    if (n >= 20 && p[3] == SD_RESPONSE) {
      if (phase == active && fileSize_ && fileSent_ && sd_valid(p, n) &&
          !std::memcmp(p + 4, file_ + 4, 9)) {
        std::memcpy(answer_, p, n);
        answerSize_ = n;
        seen_ = now;
      }
      return owned();
    }
    if (n < 48 || n > 240 || p[0] != 'S' || p[1] != 'D' || p[2] != 1 ||
        p[3] != 4 || sd_u16(p + 14) != n - 20 || !sd_u32(p + 4) ||
        !sd_u32(p + 8))
      return false;
    auto crc = sd_crc_update(0xffffffffU, p, 16);
    crc = sd_crc_update(crc, p + 20, n - 20) ^ 0xffffffffU;
    if (crc != sd_u32(p + 16))
      return true;
    if (controlSize_)
      return true;
    if (lastSize_ && sd_u32(p + 4) == sd_u32(last_ + 4) &&
        sd_u32(p + 8) == sd_u32(last_ + 8)) {
      if (n == lastSize_ && !std::memcmp(p, last_, n)) {
        std::memcpy(control_, cached_, cachedSize_);
        controlSize_ = cachedSize_;
      } else
        fail();
      return true;
    }
    auto op = p[12];
    unsigned body = 28;
    std::uint8_t result = 0;
    std::memcpy(control_, p, 48);
    control_[3] = 5;
    if (op == 1) {
      if (n != 48 || p[13] || p[46] != 1 || p[47])
        return true;
      for (unsigned i = 20; i < 46; ++i)
        if (p[i])
          return true;
      bool interrupted = owned();
      sd_put32(nonce_, randomA ? randomA : 1);
      sd_put32(nonce_ + 4, randomB ? randomB : 1);
      std::memset(control_ + 20, 0, 28);
      std::memcpy(control_ + 20, nonce_, 8);
      control_[46] = 15; // External/application jobs and negotiated ExCom framing
      // EMOS renegotiates immediately after CLOSE. Retain the terminal
      // receipt until the HTTP worker observes it; scheduling must not turn
      // an already completed mutation into an uncertain failure.
      if (phase != closed)
        phase = interrupted ? failed : idle;
      pollValid_ = false;
      fileSize_ = answerSize_ = 0;
      nextJob_ = 0;
      lastSequence_ = 0;
      controlSession_ = sd_u32(p + 4);
    } else {
      if (sd_u32(p + 4) != controlSession_ || sd_u32(p + 8) <= lastSequence_ ||
          std::memcmp(p + 20, nonce_, 8))
        return true;
      if (p[13] && op != 3 && op != 9 && op != 10)
        return true;
      if (p[13] > 10)
        return true;
      if (op == 2) {
        if (n != 48 || p[13] || sd_u32(p + 32) || nonzero(p + 36, 12))
          return true;
        auto gen = sd_u32(p + 28);
        if (!gen)
          return true;
        if ((phase == armed || phase == offered) && gen != generation_)
          fail();
        generation_ = gen;
        pollValid_ = true;
        pollAt_ = now;
        if (phase == armed || phase == offered) {
          std::memcpy(control_ + 20, binding.data(), 28);
          phase = offered;
        } else
          result = 1;
      } else if (op == 3) {
        if (n != 48 || phase != offered || !matches(p, false) ||
            !nonzero(p + 36, 8))
          return true;
        if (p[13]) {
          fail();
          result = 9;
        } else {
          std::memcpy(binding.data() + 16, p + 36, 8);
          phase = claimed;
          since_ = now;
        }
      } else {
        if (!matches(p, true))
          return true;
        if (op == 6 && phase == claimed && n == 50) {
          unsigned at = sd_u16(p + 48);
          if (at >= descriptorSize_) {
            result = 6;
          } else {
            unsigned count = descriptorSize_ - at;
            if (count > 184)
              count = 184;
            sd_put16(control_ + 48, descriptorSize_);
            sd_put16(control_ + 50, at);
            sd_put32(control_ + 52, descriptorCrc_);
            std::memcpy(control_ + 56, descriptor_ + at, count);
            body += 8 + count;
          }
        } else if (op == 4 && phase == claimed && n == 48) {
          phase = active;
          seen_ = now;
        } else if (op == 7 && (phase == active || phase == closing) &&
                   n == 48) {
          body = 29;
          control_[48] = phase == closing ? 1 : 0;
          result = poisoned_ ? 8 : 0;
          seen_ = now;
        } else if (op == 9 && (phase == active || phase == closing) &&
                   n == 49 && p[48] <= 3) {
          success = !p[13] && !poisoned_ && !cancelled_;
          phase = finished;
          seen_ = now;
        } else if (op == 10 && n == 48) {
          success = phase == finished && success && !p[13];
          phase = closed;
          fileSize_ = answerSize_ = 0;
          pollValid_ = false;
        } else
          result = 6;
      }
    }
    control_[13] = result;
    sd_put16(control_ + 14, body);
    sd_seal(control_);
    controlSize_ = 20 + body;
    std::memcpy(last_, p, n);
    lastSize_ = n;
    std::memcpy(cached_, control_, controlSize_);
    cachedSize_ = controlSize_;
    lastSequence_ = sd_u32(p + 8);
    return true;
  }

private:
  std::uint8_t nonce_[8]{}, descriptor_[248]{}, control_[240]{}, cached_[240]{},
      last_[240]{}, file_[240]{}, answer_[240]{};
  unsigned descriptorSize_ = 0, controlSize_ = 0, lastSize_ = 0,
           cachedSize_ = 0, fileSize_ = 0, answerSize_ = 0;
  std::uint32_t descriptorCrc_ = 0, nextJob_ = 0, generation_ = 0, pollAt_ = 0,
                since_ = 0, seen_ = 0, lastSequence_ = 0, controlSession_ = 0;
  bool pollValid_ = false, fileSent_ = false, poisoned_ = false, cancelled_ = false;
  static bool nonzero(const std::uint8_t *p, unsigned n) {
    unsigned a = 0;
    while (n--)
      a |= *p++;
    return a != 0;
  }
  bool matches(const std::uint8_t *p, bool grant) const {
    return !std::memcmp(p + 20, binding.data(), 16) &&
           (!grant || !std::memcmp(p + 36, binding.data() + 16, 8)) &&
           !std::memcmp(p + 44, binding.data() + 24, 4);
  }
  void fail() {
    phase = failed;
    success = false;
    pollValid_ = false;
    fileSize_ = answerSize_ = 0;
  }
};
} // namespace agon::extender::storage::admission
