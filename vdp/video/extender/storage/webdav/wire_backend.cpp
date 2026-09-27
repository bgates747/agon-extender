#include "wire_backend.hpp"
namespace agon::extender::webdav {
namespace {
unsigned operationClass(const std::string &m) {
  if (m == "HEAD")
    return 1;
  if (m == "PROPFIND")
    return 2;
  if (m == "PUT")
    return 3;
  if (m == "GET")
    return 4;
  if (m == "MKCOL")
    return 5;
  if (m == "MOVE")
    return 6;
  if (m == "COPY")
    return 7;
  if (m == "DELETE")
    return 8;
  return 0;
}
void add32(std::vector<std::uint8_t> &v, std::uint32_t n) {
  size_t a = v.size();
  v.resize(a + 4);
  sd_put32(v.data() + a, n);
}
} // namespace
WireBackend::Bytes WireBackend::pathBytes(const std::string &s) {
  Bytes b{std::uint8_t(s.size())};
  b.insert(b.end(), s.begin(), s.end());
  return b;
}
int WireBackend::rpc(unsigned op, const Bytes &payload) {
  if (!active_ || poisoned_ || seq_ == 0xffffffffU ||
      payload.size() > SD_MAX_PAYLOAD)
    return 503;
  std::array<std::uint8_t, SD_MAX_RECORD> request{}, response{};
  unsigned n = 0;
  sd_header(request.data(), SD_REQUEST, session_, ++seq_, op, 0,
            payload.size());
  std::copy(payload.begin(), payload.end(), request.data() + 20);
  sd_seal(request.data());
  int s = channel_.exchange(binding_, request.data(), 20 + payload.size(),
                            response.data(), n);
  if (s != 200) {
    poisoned_ = true;
    return s;
  }
  if (!sd_valid(response.data(), n) || response[3] != SD_RESPONSE ||
      std::memcmp(request.data() + 4, response.data() + 4, 9)) {
    poisoned_ = true;
    return 500;
  }
  reply_.assign(response.data() + 20, response.data() + n);
  switch (response[13]) {
  case SD_OK:
    return 200;
  case SD_BAD_REQUEST:
    return 400;
  case SD_UNSUPPORTED:
    return 501;
  case SD_BUSY:
  case SD_STALE:
  case SD_SEQUENCE:
    poisoned_ = true;
    return 503;
  case SD_FILE_ERROR:
    if (reply_.size() != 1)
      return 500;
    switch (reply_[0]) {
    case 4:
    case 5:
      return 404;
    case 7:
      return 403;
    case 8:
      return 412;
    default:
      return 500;
    }
  default:
    return 500;
  }
}
int WireBackend::begin(const Operation &op) {
  if (active_ || snapshot_)
    return 503;
  operation_ = op;
  seq_ = tid_ = 0;
  poisoned_ = false;
  binding_ = {};
  session_ = 0;
  int s = channel_.enter(op, binding_, session_);
  if (s != 200)
    return s;
  active_ = true;
  const auto *b = binding_.data();
  auto nz = [](const std::uint8_t *p, unsigned n) {
    unsigned v = 0;
    while (n--)
      v |= *p++;
    return v;
  };
  if (!session_ || !nz(b, 8) || !nz(b + 8, 4) || !nz(b + 12, 4) ||
      !nz(b + 16, 8) || b[24] != 1 || b[25] != operationClass(op.method) ||
      b[26] || b[27]) {
    cancel();
    return 503;
  }
  s = rpc(SD_HELLO);
  if (s == 200 && (reply_.size() != 8 || sd_u16(reply_.data() + 4) != 212 ||
                   (sd_u16(reply_.data() + 6) & 63) != 47))
    s = 501; // checked, directory-capable only
  if (s != 200)
    cancel();
  return s;
}
int WireBackend::finish() {
  if (!active_)
    return 503;
  int s = poisoned_ ? 503 : channel_.leave(binding_);
  if (s != 200)
    channel_.cancel(binding_);
  active_ = false;
  return s;
}
void WireBackend::cancel() {
  if (active_)
    channel_.cancel(binding_);
  active_ = false;
  store_.invalidate();
  snapshot_ = false;
}
int WireBackend::stat(const std::string &p, Entry &e) {
  int s = rpc(SD_STAT, pathBytes(p));
  if (s != 200)
    return s;
  if (reply_.size() != 5)
    return 500;
  e = {p, sd_u32(reply_.data()), bool(reply_[4] & 16)};
  return 200;
}
int WireBackend::list(const std::string &p,
                      const std::function<bool(const Entry &)> &emit) {
  for (unsigned cursor = 0; cursor <= 65535; ++cursor) {
    Bytes args;
    add32(args, cursor);
    auto name = pathBytes(p);
    args.insert(args.end(), name.begin(), name.end());
    int s = rpc(SD_LIST, args);
    if (s != 200)
      return s;
    if (reply_.size() < 5 || reply_[4] > 1)
      return 500;
    if (reply_[4])
      return reply_.size() == 5 && sd_u32(reply_.data()) == cursor ? 200 : 500;
    if (reply_.size() < 11 || reply_.size() != 11U + reply_[10] ||
        sd_u32(reply_.data()) != cursor + 1)
      return 500;
    std::string leaf(reply_.begin() + 11, reply_.end()),
        child = (p == "/" ? "" : p) + "/" + leaf, checked;
    if (leaf.find('/') != leaf.npos || !path(encode(child), checked) ||
        checked != child)
      return 500;
    Entry e{child, sd_u32(reply_.data() + 6), bool(reply_[5] & 16)};
    if (!emit(e))
      return 200; // bounded caller explicitly stops enumeration
  }
  return 507;
}
int WireBackend::remoteRead(const std::string &p, std::uint32_t at, void *out,
                            unsigned want, unsigned &n, std::uint32_t &size) {
  Bytes args;
  add32(args, at);
  args.push_back(want);
  args.push_back(want >> 8);
  auto name = pathBytes(p);
  args.insert(args.end(), name.begin(), name.end());
  int s = rpc(SD_READ, args);
  if (s != 200)
    return s;
  if (reply_.size() < 4)
    return 500;
  size = sd_u32(reply_.data());
  n = reply_.size() - 4;
  if (at > size || n != std::min<std::uint32_t>(want, size - at))
    return 500;
  std::memcpy(out, reply_.data() + 4, n);
  return 200;
}
spool::Job WireBackend::job(const std::string &src, const std::string &dst,
                            std::uint32_t n, bool replace) {
  spool::Job j;
  j.binding = binding_;
  j.size = n;
  auto *d = j.descriptor.data();
  d[0] = binding_[25];
  d[1] = replace;
  sd_put16(d + 2, src.size());
  sd_put16(d + 4, dst.size());
  if (src.size() > 120 || dst.size() > 120)
    return j;
  std::memcpy(d + 8, src.data(), src.size());
  std::memcpy(d + 8 + src.size(), dst.data(), dst.size());
  j.descriptorSize = 8 + src.size() + dst.size();
  return j;
}
int WireBackend::stageDownload(const std::string &src, const std::string &dst,
                               std::uint32_t size) {
  int s = spoolStatus(store_.begin(job(src, dst, size, false)));
  if (s != 200)
    return s;
  std::array<std::uint8_t, 216> buf{};
  std::uint32_t at = 0;
  do {
    unsigned n = 0;
    std::uint32_t actual = 0;
    s = remoteRead(src, at, buf.data(), buf.size(), n, actual);
    if (s != 200 || actual != size) {
      store_.invalidate();
      return s == 200 ? 409 : s;
    }
    if (n &&
        (s = spoolStatus(store_.append(binding_, at, buf.data(), n))) != 200) {
      store_.invalidate();
      return s;
    }
    at += n;
  } while (at < size);
  s = spoolStatus(store_.seal(binding_));
  if (s != 200)
    store_.invalidate();
  return s;
}
int WireBackend::snapshot(const std::string &p, std::uint32_t &size) {
  Entry e;
  int s = stat(p, e);
  if (s != 200)
    return s;
  if (e.directory)
    return 405;
  size = e.size;
  s = stageDownload(p, "/snapshot", size);
  snapshot_ = s == 200;
  return s;
}
int WireBackend::readSnapshot(std::uint32_t at, void *p, size_t n,
                              size_t &got) {
  if (!snapshot_)
    return 503;
  return spoolStatus(store_.read(binding_, at, p, n, got));
}
void WireBackend::releaseSnapshot() {
  if (snapshot_)
    store_.discard(binding_);
  store_.invalidate();
  snapshot_ = false;
}
int WireBackend::transfer(const std::string &destination, bool replace) {
  if (destination.size() > 112)
    return 400; // sibling readback must fit wire path
  Entry old;
  int s = stat(destination, old);
  if (s != 200 && s != 404)
    return s;
  if (s == 200 && (!replace || old.directory))
    return 412;
  // Store inspection is deliberately unavailable while owned; compute identity
  // by streaming the already sealed local payload, with bounded reads.
  std::array<std::uint8_t, 216> buf{};
  std::uint32_t size = 0, sum = 0xffffffffU;
  for (;;) {
    size_t got = 0;
    s = spoolStatus(store_.read(binding_, size, buf.data(), buf.size(), got));
    if (s != 200)
      return s;
    if (!got)
      break;
    sum = sd_crc_update(sum, buf.data(), got);
    size += got;
  }
  sum ^= 0xffffffffU;
  transferSize_ = size;
  transferCrc_ = sum;
  if (++tid_ == 0)
    return 503;
  Bytes args;
  add32(args, tid_);
  add32(args, size);
  add32(args, sum);
  auto name = pathBytes(destination);
  args.insert(args.end(), name.begin(), name.end());
  s = rpc(SD_BEGIN, args);
  if (s != 200)
    return s;
  if (reply_.size() != 8 || sd_u32(reply_.data()) != tid_ ||
      sd_u32(reply_.data() + 4))
    return 500;
  for (std::uint32_t at = 0; at < size;) {
    size_t got = 0;
    s = spoolStatus(store_.read(binding_, at, buf.data(), 212, got));
    if (s != 200 || !got)
      return s == 200 ? 500 : s;
    args.clear();
    add32(args, tid_);
    add32(args, at);
    args.insert(args.end(), buf.begin(), buf.begin() + got);
    s = rpc(SD_WRITE, args);
    if (s != 200)
      return s;
    at += got;
    if (reply_.size() != 8 || sd_u32(reply_.data()) != tid_ ||
        sd_u32(reply_.data() + 4) != at)
      return 500;
  }
  args.clear();
  add32(args, tid_);
  s = rpc(SD_FINISH, args);
  if (s != 200)
    return s;
  if (reply_.size() != 8 || sd_u32(reply_.data()) != size ||
      sd_u32(reply_.data() + 4) != sum)
    return 500;
  // Independent remote stage byte comparison, matching normal host put
  // behavior.
  for (std::uint32_t at = 0; at < size;) {
    size_t got = 0;
    s = spoolStatus(store_.read(binding_, at, buf.data(), buf.size(), got));
    if (s != 200 || !got)
      return s == 200 ? 500 : s;
    std::array<std::uint8_t, 216> remote{};
    unsigned n = 0;
    std::uint32_t actual = 0;
    s = remoteRead(destination + ".p17part", at, remote.data(), got, n, actual);
    if (s != 200 || actual != size || n != got ||
        std::memcmp(buf.data(), remote.data(), n))
      return s == 200 ? 500 : s;
    at += got;
  }
  return 200;
}
int WireBackend::activate(const std::string &destination) {
  Bytes args;
  add32(args, tid_);
  int s = rpc(SD_ACTIVATE, args);
  if (s != 200 || !reply_.empty())
    return s == 200 ? 500 : s;
  std::array<std::uint8_t, 216> buffer{};
  std::uint32_t at = 0, crc = 0xffffffffU;
  do {
    unsigned got = 0;
    std::uint32_t size = 0;
    s = remoteRead(destination, at, buffer.data(), buffer.size(), got, size);
    if (s != 200 || size != transferSize_)
      return s == 200 ? 500 : s;
    crc = sd_crc_update(crc, buffer.data(), got);
    at += got;
  } while (at < transferSize_);
  return (crc ^ 0xffffffffU) == transferCrc_ ? 200 : 500;
}
Outcome WireBackend::put(const std::string &p, std::uint32_t n, bool replace,
                         Body &body) {
  if (p.size() > 112)
    return {400, 0, p};
  auto j = job("/incoming", p, n, replace);
  return stagedPut(
      store_, j, body,
      [&](auto &, const auto &) { return transfer(p, replace); },
      [&](const auto &) { return activate(p); });
}
Outcome WireBackend::mkdir(const std::string &p) {
  return {rpc(SD_MKDIR, pathBytes(p)), 0, p};
}
Outcome WireBackend::move(const std::string &a, const std::string &b,
                          bool replace) {
  if (replace)
    return {501, 0, b};
  Bytes descriptor(8, 0);
  descriptor[0] = 6;
  sd_put16(descriptor.data() + 2, a.size());
  sd_put16(descriptor.data() + 4, b.size());
  descriptor.insert(descriptor.end(), a.begin(), a.end());
  descriptor.insert(descriptor.end(), b.begin(), b.end());
  auto crc = sd_crc(descriptor.data(), descriptor.size());
  for (unsigned at = 0; at < descriptor.size();) {
    unsigned n = std::min<unsigned>(184, descriptor.size() - at);
    Bytes args(8);
    sd_put16(args.data(), descriptor.size());
    sd_put16(args.data() + 2, at);
    sd_put32(args.data() + 4, crc);
    args.insert(args.end(), descriptor.begin() + at,
                descriptor.begin() + at + n);
    int s = rpc(SD_MOVE, args);
    if (s != 200)
      return {s, 0, b};
    at += n;
    if (reply_.size() != 3 || sd_u16(reply_.data()) != at ||
        reply_[2] != (at == descriptor.size()))
      return {500, 0, b};
  }
  return {200, 1, {}};
}
Outcome WireBackend::removeTree(const std::string &p, unsigned depth,
                                unsigned &completed) {
  if (depth > 16)
    return {507, completed, p};
  auto args = pathBytes(p);
  args.insert(args.begin(), 1);
  int s = rpc(SD_REMOVE, args);
  if (s != 200)
    return {s, completed, p};
  Entry e;
  s = stat(p, e);
  if (s != 200)
    return {s, completed, p};
  if (e.directory) {
    for (;;) {
      std::string child;
      s = list(p, [&](const Entry &next) {
        child = next.path;
        return false;
      });
      if (s != 200)
        return {s, completed, p};
      if (child.empty())
        break;
      auto r = removeTree(child, depth + 1, completed);
      if (r.status != 200)
        return r;
    }
  }
  args[0] = 0;
  s = rpc(SD_REMOVE, args);
  if (s == 200)
    ++completed;
  return {s, completed, s == 200 ? "" : p};
}
Outcome WireBackend::remove(const std::string &p) {
  unsigned n = 0;
  return removeTree(p, 0, n);
}
Outcome WireBackend::copyTree(const std::string &src, const std::string &dst,
                              bool replace, bool recursive, unsigned depth,
                              unsigned &completed) {
  if (depth > 16)
    return {507, completed, dst};
  Entry e;
  int s = stat(src, e);
  if (s != 200)
    return {s, completed, src};
  if (e.directory) {
    s = rpc(SD_MKDIR, pathBytes(dst));
    if (s != 200)
      return {s, completed, dst};
    ++completed;
    if (!recursive)
      return {200, completed, {}};
    Outcome failure;
    s = list(src, [&](const Entry &child) {
      std::string target = dst + child.path.substr(src.size());
      std::string checked;
      if (!path(encode(target), checked)) {
        failure = {400, completed, target};
        return false;
      }
      failure =
          copyTree(child.path, target, replace, true, depth + 1, completed);
      return failure.status == 200;
    });
    if (s != 200)
      return {s, completed, src};
    return failure.status == 200 ? Outcome{200, completed, {}} : failure;
  }
  if (dst.size() > 112)
    return {400, completed, dst};
  s = stageDownload(src, dst, e.size);
  if (s == 200)
    s = transfer(dst, replace);
  if (s == 200)
    s = spoolStatus(store_.activationStarted(binding_));
  if (s == 200)
    s = activate(dst);
  if (s == 200)
    s = spoolStatus(store_.confirmed(binding_));
  if (s == 200)
    s = spoolStatus(store_.discard(binding_));
  store_.invalidate();
  if (s == 200)
    ++completed;
  return {s, completed, s == 200 ? "" : dst};
}
Outcome WireBackend::copy(const std::string &a, const std::string &b,
                          bool replace, bool recursive) {
  if (overlap(a, b))
    return {403, 0, b};
  unsigned completed = 0;
  return copyTree(a, b, replace, recursive, 0, completed);
}
} // namespace agon::extender::webdav
