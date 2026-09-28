#include "extender/storage/webdav/completion_stream.hpp"
#include <string>
#include "extender/storage/admission/channel.hpp"
#include <cassert>
#include <cstdio>
using namespace agon::extender::storage::admission;
struct Fixture {
  Peer peer;
  unsigned sequence = 0, now = 1;
  std::uint8_t p[240]{}, out[240]{};
  Binding b{};
  unsigned call(unsigned op, unsigned result = 0, unsigned extra = 0) {
    sd_header(p, 4, 1, ++sequence, op, result, 28 + extra);
    std::memcpy(p + 20, b.data(), 28);
    sd_seal(p);
    assert(peer.receive(p, 48 + extra, now, 123, 456));
    return peer.take(out, now);
  }
  void hello() {
    b = {};
    b[26] = 1;
    assert(call(1) == 48);
    std::memcpy(b.data(), out + 20, 28);
    b[26] = 0;
    sd_put32(b.data() + 8, 1);
  }
  void poll() { assert(call(2) == 48); }
  void offer() {
    hello();
    poll();
    assert(out[13] == 1);
    std::uint8_t d[] = {3, 0, 0, 0, 2, 0, 0, 0, '/', 'x'};
    assert(peer.reserve(d, sizeof d, now));
    poll();
    assert(!out[13]);
    b = peer.binding;
    sd_put32(b.data() + 16, 7);
    assert(call(3) == 48);
    assert(peer.phase == Peer::claimed);
  }
  void ready() {
    offer();
    sd_put16(p + 48, 0);
    assert(call(6, 0, 2) == 66);
    assert(sd_u16(out + 48) == 10);
    assert(sd_u32(out + 52) == sd_crc(out + 56, 10));
    assert(call(4) == 48);
    assert(peer.phase == Peer::active);
  }
};
struct QuietAccess : Access {
  Fixture &f;
  bool busy = false;
  explicit QuietAccess(Fixture &v) : f(v) {}
  void locked(const std::function<void(Peer &)> &fn) override { fn(f.peer); }
  bool manualBusy() override { return busy; }
  std::uint32_t now() override { return f.now; }
  void pause() override { ++f.now; }
};
int main() {
  { // A quiet cancelled operation is unsuccessful, but cleanup is healthy.
    Fixture f; f.ready();
    f.peer.cancel(f.b, true); f.peer.cancel(f.b, true);
    assert(f.call(7)==49 && f.out[13]==0 && f.out[48]==1);
    f.p[48]=0; assert(f.call(9,0,1)==48 && f.out[13]==0);
    assert(f.call(10)==48 && f.peer.phase==Peer::closed && !f.peer.success);
  }
  { // In-flight data cannot be downgraded to a clean cancellation.
    Fixture f; f.ready(); std::uint8_t request[20];
    sd_header(request,SD_REQUEST,f.peer.fileSession(),1,SD_HELLO,0,0);sd_seal(request);
    assert(f.peer.submit(f.b,request,20,f.now));
    f.peer.cancel(f.b,true); f.peer.cancel(f.b,true);
    assert(f.call(7)==49 && f.out[13]==8);
  }
  { // A prior transport fault remains poisoned even if later called orderly.
    Fixture f; f.ready(); f.peer.cancel(f.b); f.peer.cancel(f.b,true);
    assert(f.call(7)==49 && f.out[13]==8);
  }
  {
    Fixture f;
    assert(!f.peer.reserve(f.p, 10, 1));
    f.ready();
    std::uint8_t request[20], reply[20];
    auto sid = sd_crc(f.b.data(), 28);
    if (!sid)
      sid = 1;
    sd_header(request, SD_REQUEST, sid, 1, SD_HELLO, 0, 0);
    sd_seal(request);
    assert(f.peer.submit(f.b, request, 20, f.now));
    assert(!f.peer.submit(f.b, request, 20, f.now));
    assert(f.peer.take(f.out, f.now) == 20);
    assert(!f.peer.take(f.out, f.now));
    sd_header(reply, SD_RESPONSE, sid, 2, SD_HELLO, 0, 0);
    sd_seal(reply);
    f.peer.receive(reply, 20, f.now, 1, 2);
    assert(!f.peer.answer(f.b, f.out));
    sd_put32(reply + 8, 1);
    sd_seal(reply);
    f.peer.receive(reply, 20, f.now, 1, 2);
    assert(f.peer.answer(f.b, f.out) == 20);
    assert(f.peer.finish(f.b, f.now));
    assert(f.call(7) == 49 && f.out[48] == 1);
    f.p[48] = 1;
    assert(f.call(9, 0, 1) == 48);
    assert(f.call(10) == 48);
    assert(f.peer.phase == Peer::closed && f.peer.success);
    auto completed = f.peer.binding;
    f.hello(); // resident re-entry can precede HTTP worker wakeup
    f.poll();
    assert(f.peer.phase == Peer::closed && f.peer.success);
    assert(f.peer.binding == completed);
    f.peer.retire();
    assert(f.peer.phase == Peer::idle);
    assert(!f.peer.reserve(f.p, 10, f.now));
  }
  {
    Fixture f;
    f.offer();
    f.now += 1001;
    f.peer.expire(f.now);
    assert(f.peer.phase == Peer::failed);
    assert(!f.peer.success);
  }
  {
    Fixture f;
    f.ready();
    auto b = f.b;
    b[12]++;
    assert(!f.peer.finish(b, f.now));
    f.peer.cancel(f.b);
    assert(f.call(7) == 49 && f.out[13] == 8);
    f.p[48] = 3;
    f.call(9, 7, 1);
    f.call(10, 7);
    assert(!f.peer.success);
  }
  {
    Fixture f;
    f.ready();
    f.now += 5001;
    f.peer.expire(f.now);
    assert(f.peer.phase == Peer::failed);
  }
  {
    Fixture f;
    f.offer(); // identical request replays reply; changed duplicate invalidates
               // grant
    assert(f.peer.receive(f.p, 48, f.now, 9, 9));
    assert(f.peer.take(f.out, f.now) == 48);
    f.p[13] = 9;
    sd_seal(f.p);
    assert(f.peer.receive(f.p, 48, f.now, 9, 9));
    assert(f.peer.phase == Peer::failed);
  }
  {
    Fixture f;
    f.ready();
    f.hello();
    assert(f.peer.phase == Peer::failed);
    assert(!f.peer.success);
  }
  {
    Fixture f;
    f.hello();
    f.poll();
    f.now += 151;
    std::uint8_t d[] = {1, 0, 1, 0, 0, 0, 0, 0, '/'};
    assert(!f.peer.reserve(d, sizeof d, f.now));
    f.poll();
    assert(f.peer.reserve(d, sizeof d, f.now));
    sd_put32(f.b.data() + 8, 2);
    f.poll();
    assert(f.peer.phase == Peer::failed);
  }
  {
    Fixture f;
    f.ready();
    std::uint8_t q[20];
    sd_header(q, SD_REQUEST, 999, 1, SD_HELLO, 0, 0);
    sd_seal(q);
    assert(!f.peer.submit(f.b, q, 20, f.now));
    sd_put32(q + 4, f.peer.fileSession());
    sd_seal(q);
    q[16] ^= 1;
    assert(!f.peer.submit(f.b, q, 20, f.now));
  }
  {
    Fixture f;
    f.hello();
    f.poll();
    QuietAccess access(f);
    Channel channel(access);
    Binding b;
    std::uint32_t session = 0;
    access.busy = true;
    assert(channel.enter({"HEAD", "/", "", false, false}, b, session) == 503);
    assert(f.peer.phase == Peer::idle);
    access.busy = false;
    assert(channel.enter({"HEAD", "/", "", false, false}, b, session) == 503);
    assert(f.now < 1600 &&
           f.peer.phase ==
               Peer::idle); // missing DECIDE retires; no deferred job
    assert(channel.enter({"HEAD", "/", "", false, false}, b, session) == 503);
  }
  {
    Fixture f;
    f.ready();
    // A different task sampled its clock just before this grant was created.
    f.peer.expire(f.now - 1);
    assert(f.peer.phase == Peer::active);
    f.peer.expire(f.now + 5001);
    assert(f.peer.phase == Peer::failed);
  }
  {
    struct Wire : agon::extender::webdav::Stream {
      std::string bytes; bool closed = false;
      int read(void *, size_t) override { return 0; }
      int send(const void *p, size_t n) override {
        n = std::min<size_t>(n, 2); // exercise partial writes
        bytes.append(static_cast<const char *>(p), n); return n;
      }
      void close() override { closed = true; }
    } wire;
    agon::extender::webdav::CompletionStream stream(wire);
    std::string text = "HTTP response";
    size_t at = 0;
    while (at < text.size()) {
      int n = stream.send(text.data() + at, text.size() - at);
      assert(n > 0); at += n;
    }
    stream.close();
    assert(!wire.closed && wire.bytes == text.substr(0, text.size() - 1));
    stream.complete();
    assert(wire.closed && wire.bytes == text);
  }
  puts("admission peer: grant lifecycle, single-flight data, stale replies, "
       "cancellation, duplicate conflict and timeouts pass");
}
