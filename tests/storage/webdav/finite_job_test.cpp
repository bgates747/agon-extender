// Actual EMOS finite utility + checked engine + P4 admission peer. Only the
// gateway/clock and FatFS platform operations are host substitutions.
#include "extender/storage/admission/peer.hpp"
#include <cassert>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <vector>
extern "C" {
int sdjob_run(void);
void fs_root(const char *);
}
using namespace agon::extender::storage::admission;
using Bytes = std::vector<std::uint8_t>;
static Peer peer;
static std::vector<Bytes> requests;
static Binding grant;
static unsigned index_, ticks, lastseq, terminal_, cancel_after, drop_ready,
    records;
static bool closed_, opened_;
static Bytes descriptor(unsigned cls, const char *a, const char *b,
                        unsigned flags = 0) {
  Bytes d(8);
  d[0] = cls;
  d[1] = flags;
  sd_put16(d.data() + 2, strlen(a));
  sd_put16(d.data() + 4, strlen(b));
  d.insert(d.end(), a, a + strlen(a));
  d.insert(d.end(), b, b + strlen(b));
  return d;
}
static void control(unsigned op, Binding b) {
  std::uint8_t p[48], q[240];
  sd_header(p, 4, 1, ++lastseq, op, 0, 28);
  memcpy(p + 20, b.data(), 28);
  sd_seal(p);
  assert(peer.receive(p, sizeof p, ticks * 8, 123, 456));
  assert(peer.take(q, ticks * 8) == 48);
  if (op == 1) {
    memcpy(grant.data(), q + 20, 28);
    grant[26] = 0;
    sd_put32(grant.data() + 8, 1);
  }
}
static void setup(const Bytes &d) {
  peer = Peer{};
  requests.clear();
  ticks = index_ = lastseq = terminal_ = cancel_after = drop_ready = records =
      0;
  closed_ = opened_ = false;
  grant = {};
  grant[26] = 1;
  control(1, grant);
  control(2, grant);
  assert(peer.reserve(d.data(), d.size(), ticks * 8));
  control(2, grant);
  grant = peer.binding;
  sd_put32(grant.data() + 16, 7);
  control(3, grant);
}
static Bytes path(const char *p) {
  Bytes b{static_cast<std::uint8_t>(strlen(p))};
  b.insert(b.end(), p, p + strlen(p));
  return b;
}
static void add(unsigned op, Bytes body = {}) {
  Bytes b(20);
  sd_header(b.data(), SD_REQUEST, peer.fileSession(), requests.size() + 1, op,
            0, body.size());
  b.insert(b.end(), body.begin(), body.end());
  sd_seal(b.data());
  requests.push_back(b);
}
extern "C" std::uint32_t sdapp_clock(void) { return ticks++; }
extern "C" int sdjob_cancelled(void) { return 0; }
extern "C" unsigned sdapp_link(unsigned op, const std::uint8_t *p, unsigned n,
                               std::uint8_t *out, unsigned cap, unsigned *got) {
  *got = 0;
  if (op == 5) {
    assert(cap == 36 && !opened_);
    opened_ = true;
    memcpy(out, grant.data(), 28);
    sd_put32(out + 28, 1);
    sd_put32(out + 32, lastseq);
    *got = 36;
    return 0;
  }
  if (op == 6) {
    assert(n == 5);
    lastseq = sd_u32(p);
    terminal_ = p[4] + 1;
    return 0;
  }
  if (op == 3) {
    closed_ = true;
    control(10, grant);
    return 0;
  }
  if (op == 2) {
    assert(peer.receive(p, n, ticks * 8, 123, 456));
    if (p[3] == SD_RESPONSE) {
      std::uint8_t response[240];
      assert(peer.answer(grant, response));
      ++index_;
      ++records;
      if (cancel_after && records == cancel_after)
        peer.cancel(grant);
    }
    return 0;
  }
  assert(op == 1);
  if (peer.phase == Peer::active) {
    if (index_ < requests.size())
      (void)peer.submit(grant, requests[index_].data(), requests[index_].size(),
                        ticks * 8);
    else
      (void)peer.finish(grant, ticks * 8);
  }
  *got = peer.take(out, ticks * 8);
  if (drop_ready && *got && out[3] == 5 && out[12] == 4) {
    *got = 0;
    drop_ready = 0;
  }
  return 0;
}
static void run(bool pass) {
  int r = sdjob_run();
  assert((r == 0) == pass);
  assert(closed_);
  assert(terminal_ == (pass ? 1U : 2U));
}
static void upload(const char *name, bool activate) {
  const std::string data = "finite checked data";
  Bytes b(12);
  sd_put32(b.data(), 17);
  sd_put32(b.data() + 4, data.size());
  sd_put32(
      b.data() + 8,
      sd_crc(reinterpret_cast<const std::uint8_t *>(data.data()), data.size()));
  auto p = path(name);
  b.insert(b.end(), p.begin(), p.end());
  add(SD_HELLO);
  add(SD_BEGIN, b);
  b.assign(8, 0);
  sd_put32(b.data(), 17);
  b.insert(b.end(), data.begin(), data.end());
  add(SD_WRITE, b);
  b.assign(4, 0);
  sd_put32(b.data(), 17);
  add(SD_FINISH, b);
  if (activate)
    add(SD_ACTIVATE, b);
}
int main() {
  char temp[] = "/tmp/sdjob-XXXXXX";
  auto root = mkdtemp(temp);
  assert(root);
  fs_root(root);
  {
    std::ofstream f(std::string(root) + "/existing");
    f << "original";
  }
  setup(descriptor(1, "/existing", ""));
  add(SD_HELLO);
  add(SD_STAT, path("/existing"));
  run(true);
  assert(records == 2);
  setup(descriptor(3, "", "/new"));
  upload("/new", true);
  run(true);
  assert(std::filesystem::exists(std::string(root) + "/new"));
  setup(descriptor(3, "", "/unfinished"));
  upload("/unfinished", false);
  run(false);
  assert(!std::filesystem::exists(std::string(root) + "/unfinished"));
  assert(std::filesystem::exists(std::string(root) + "/unfinished.p17part"));
  setup(descriptor(3, "", "/cancelled"));
  upload("/cancelled", true);
  cancel_after = 2;
  run(false);
  assert(!std::filesystem::exists(std::string(root) + "/cancelled"));
  setup(descriptor(3, "", "/admitted"));
  upload("/outside", true);
  run(false);
  assert(!std::filesystem::exists(std::string(root) + "/outside.p17meta"));
  setup(descriptor(3, "", "/existing"));
  upload("/existing", true);
  run(false);
  assert(!std::filesystem::exists(std::string(root) + "/existing.p17meta"));
  setup(descriptor(1, "/existing", ""));
  add(SD_REMOVE, Bytes{0, 9, '/', 'e', 'x', 'i', 's', 't', 'i', 'n', 'g'});
  run(false);
  assert(std::filesystem::exists(std::string(root) + "/existing"));
  setup(descriptor(1, "/../escape", ""));
  run(false);
  assert(records == 0);
  setup(descriptor(3, "", "/noack"));
  upload("/noack", true);
  drop_ready = 1;
  run(false);
  assert(!std::filesystem::exists(std::string(root) + "/noack.p17meta"));
  std::filesystem::create_directory(std::string(root) + "/emos");
  setup(descriptor(3, "", "/emos/sdjob.bin"));
  upload("/emos/sdjob.bin", true);
  run(false);
  assert(
      !std::filesystem::exists(std::string(root) + "/emos/sdjob.bin.p17meta"));
  std::filesystem::remove_all(root);
  puts("finite utility + actual peer/engine: admission, completion, scope, "
       "overwrite, cancellation, unfinished stage and lost READY pass");
}
