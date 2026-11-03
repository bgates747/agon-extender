#pragma once
// P4-owned fast file loop. The network is deliberately absent from this API.
// Reuses the installed bounded UART records; it is NOT a bulk UART carrier.
#include "../sd_wire.h"
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

namespace agon::extender::storage::fast {
constexpr std::uint32_t Quota = 32U * 1024U * 1024U;
struct Plan {
  std::string path;
  std::uint32_t id = 0, size = 0, boot = 0;
  bool upload = false, activate = false;
};
enum Error : unsigned { Ok, Invalid, Transport, Protocol, Remote, Local, TooLarge };
struct Progress {
  std::uint32_t bytes = 0, size = 0, records = 0;
  unsigned error = Ok, remoteStatus = 0, filesystem = 0;
};
struct Link {
  virtual ~Link() = default;
  // One exclusive, boot-bound queue owner. False means uncertain completion;
  // caller must not submit a replacement operation to another session.
  virtual bool exchange(const std::uint8_t *, unsigned, std::uint8_t *, unsigned &) = 0;
  virtual void progress(const Progress &) {}
  // Candidate selection occurs before payload admission; failure never retries
  // a partly executed parallel upload through UART.
  virtual bool parallelUploads() const { return false; }
  virtual bool prepareUpload(FILE *,std::uint32_t,std::uint32_t) { return false; }
  virtual bool uploadReturned() const { return false; }
};
inline bool valid(const Plan &p) {
  if (!p.id || !p.boot || p.size > Quota || p.path.empty() || p.path[0] != '/' ||
      p.path.size() > (p.upload ? 112U : 120U) || (p.activate && !p.upload)) return false;
  if (p.path == "/") return false;
  size_t start = 1;
  for (size_t i = 1; i <= p.path.size(); ++i) {
    auto c = static_cast<unsigned char>(i == p.path.size() ? 0 : p.path[i]);
    if (c && (c < 32 || c > 126 || c == ':' || c == '\\' || c == '*' || c == '?')) return false;
    if (!c || c == '/') {
      auto part = p.path.substr(start, i-start);
      if (part.empty() || part == "." || part == ".." || part.back() == '.' || part.back() == ' ') return false;
      start = i+1;
    }
  }
  return true;
}
class Engine {
  Link &link_;
  std::uint32_t session_, sequence_ = 0;
  std::array<std::uint8_t, SD_MAX_RECORD> request_{}, reply_{};
  unsigned replySize_ = 0;
  Progress p_{};
  bool fail(unsigned e) { p_.error = e; link_.progress(p_); return false; }
  bool rpc(unsigned op, const std::uint8_t *data = nullptr, unsigned size = 0) {
    if (size > SD_MAX_PAYLOAD || sequence_ == UINT32_MAX) return fail(Protocol);
    sd_header_mode(request_.data(), SD_REQUEST, session_, ++sequence_, op, 0, size, 1);
    if (size) std::memcpy(request_.data()+SD_HEADER, data, size);
    sd_seal(request_.data()); // major2 zeros reserved fields; no CRC work
    unsigned n = 0;
    if (!link_.exchange(request_.data(), SD_HEADER+size, reply_.data(), n)) return fail(Transport);
    // Reject a checked-mode peer BEFORE the shared decoder can calculate CRC.
    if (n < SD_HEADER || n > SD_MAX_RECORD || reply_[2] != SD_FAST_VERSION ||
        !sd_valid(reply_.data(), n) || reply_[3] != SD_RESPONSE ||
        std::memcmp(reply_.data()+4, request_.data()+4, 9)) return fail(Protocol);
    ++p_.records;
    p_.remoteStatus = reply_[13];
    if (reply_[13]) {
      if (reply_[13] == SD_FILE_ERROR && n == SD_HEADER+1) p_.filesystem = reply_[SD_HEADER];
      return fail(Remote);
    }
    replySize_ = n-SD_HEADER;
    return true;
  }
  bool identity(std::uint32_t a, std::uint32_t b) {
    return replySize_ == 8 && sd_u32(reply_.data()+20) == a && sd_u32(reply_.data()+24) == b;
  }
public:
  Engine(Link &link, std::uint32_t session) : link_(link), session_(session) {}
  Progress run(const Plan &plan, FILE *spool) {
    if (!valid(plan) || !session_ || !spool) { fail(Invalid); return p_; }
    p_.size = plan.size;
    if (!rpc(SD_HELLO)) return p_;
    if (replySize_ != 8 || sd_u32(reply_.data()+20) != plan.boot ||
        sd_u16(reply_.data()+24) != 212 || (sd_u16(reply_.data()+26)&95) != 95) {
      fail(Protocol); return p_;
    }
    std::array<std::uint8_t, SD_MAX_PAYLOAD> args{};
    auto path = [&](unsigned at) {
      args[at] = plan.path.size();
      std::memcpy(args.data()+at+1, plan.path.data(), plan.path.size());
      return unsigned(at+1+plan.path.size());
    };
    if (plan.upload) {
      const bool parallel=plan.size && (sd_u16(reply_.data()+26)&128) && link_.parallelUploads();
      if(parallel && !link_.prepareUpload(spool,plan.size,plan.id)){fail(Local);return p_;}
      sd_put32(args.data(), plan.id); sd_put32(args.data()+4, plan.size);
      // bytes8..11 reserved zero; no digest on either processor.
      if (!rpc(SD_BEGIN, args.data(), path(12))) return p_;
      if (!identity(plan.id, 0)) { fail(Protocol); return p_; }
      if(parallel) {
        sd_put32(args.data(),plan.id);sd_put32(args.data()+4,plan.size);
        if(!rpc(SD_PARALLEL_WRITE,args.data(),8))return p_;
        if(!identity(plan.id,plan.size) || !link_.uploadReturned()){fail(Protocol);return p_;}
        p_.bytes=plan.size;link_.progress(p_);
      }
      while (!parallel && p_.bytes < p_.size) {
        auto n = std::min<std::uint32_t>(212, p_.size-p_.bytes);
        sd_put32(args.data(), plan.id); sd_put32(args.data()+4, p_.bytes);
        if (std::fread(args.data()+8, 1, n, spool) != n) { fail(Local); return p_; }
        if (!rpc(SD_WRITE, args.data(), n+8)) return p_;
        if (!identity(plan.id, p_.bytes+n)) { fail(Protocol); return p_; }
        p_.bytes += n; link_.progress(p_);
      }
      if (!parallel && (std::fgetc(spool) != EOF || std::ferror(spool))) { fail(Local); return p_; }
      sd_put32(args.data(), plan.id);
      if (!rpc(SD_FINISH, args.data(), 4)) return p_;
      if (!identity(plan.size, 0)) { fail(Protocol); return p_; }
      if (plan.activate && (!rpc(SD_ACTIVATE, args.data(), 4) || replySize_)) {
        if (!p_.error) fail(Protocol);
        return p_;
      }
    } else {
      if (!rpc(SD_STAT, args.data(), path(0))) return p_;
      if (replySize_ != 5 || (reply_[24]&16)) { fail(Protocol); return p_; }
      p_.size = sd_u32(reply_.data()+20);
      if (p_.size > Quota) { fail(TooLarge); return p_; }
      while (p_.bytes < p_.size) {
        auto n = std::min<std::uint32_t>(216, p_.size-p_.bytes);
        sd_put32(args.data(), p_.bytes); sd_put16(args.data()+4, n);
        if (!rpc(SD_READ, args.data(), path(6))) return p_;
        if (replySize_ != n+4 || sd_u32(reply_.data()+20) != p_.size) { fail(Protocol); return p_; }
        if (std::fwrite(reply_.data()+24, 1, n, spool) != n) { fail(Local); return p_; }
        p_.bytes += n; link_.progress(p_);
      }
      if (std::fflush(spool)) { fail(Local); return p_; }
    }
    link_.progress(p_);
    return p_;
  }
};
} // namespace agon::extender::storage::fast
