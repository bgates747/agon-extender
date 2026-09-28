#pragma once
#include "../webdav/wire_backend.hpp"
#include "peer.hpp"
namespace agon::extender::storage::admission {
// Target adapter locks the existing console queue; host tests provide the same
// serialization without UART/RTOS. No callback below performs file or socket
// I/O.
struct Access {
  virtual ~Access() = default;
  virtual void locked(const std::function<void(Peer &)> &) = 0;
  virtual bool manualBusy() = 0; // called under the queue lock
  virtual std::uint32_t now() = 0;
  virtual void pause() = 0;
};
class Channel final : public webdav::Channel {
  Access &access_;
  bool sameJob(const Binding &a, const Binding &b) {
    return !std::memcmp(a.data(), b.data(), 16);
  }
  template <class F> bool wait(unsigned ms, F predicate) {
    auto start = access_.now();
    unsigned spins = 1000000;
    do {
      if (predicate())
        return true;
      access_.pause();
    } while (--spins && access_.now() - start < ms);
    return false;
  }

  void handBack() {
    // Wait for the previous job's return-to-CLI poll before completing HTTP.
    // This is not admission or a queue for a new request. A key/app may win;
    // after 200 ms return the already-known outcome without changing it.
    wait(200, [&] {
      bool idle = false;
      access_.locked([&](Peer &p) { idle = p.idleReady(access_.now()); });
      return idle;
    });
  }
public:
  explicit Channel(Access &a) : access_(a) {}
  int enter(const webdav::Operation &op, Binding &binding,
            std::uint32_t &session) override {
    unsigned cls = op.method == "HEAD"       ? 1
                   : op.method == "PROPFIND" ? 2
                   : op.method == "PUT"      ? 3
                   : op.method == "GET"      ? 4
                   : op.method == "MKCOL"    ? 5
                   : op.method == "MOVE"     ? 6
                   : op.method == "COPY"     ? 7
                   : op.method == "DELETE"   ? 8
                                             : 0;
    std::string src = cls == 3 || cls == 5 ? "" : op.source;
    std::string dst = cls == 3 || cls == 5 ? op.source : op.destination;
    if (!cls || src.size() > 120 || dst.size() > 120)
      return 400;
    std::vector<std::uint8_t> d(8);
    d[0] = cls;
    d[1] = (op.overwrite ? 1 : 0) |
           ((op.recursive && (cls == 2 || cls == 7 || cls == 8)) ? 2 : 0);
    // MOVE replacement is rejected by Adapter/backend before any rename.
    if (cls == 6)
      d[1] = 0;
    sd_put16(d.data() + 2, src.size());
    sd_put16(d.data() + 4, dst.size());
    d.insert(d.end(), src.begin(), src.end());
    d.insert(d.end(), dst.begin(), dst.end());
    bool accepted = false;
    access_.locked([&](Peer &p) {
      if (!access_.manualBusy() &&
          p.reserve(d.data(), d.size(), access_.now())) {
        binding = p.binding;
        accepted = true;
      }
    });
    if (!accepted)
      return 503;
    bool done = false, ready = false;
    wait(1500, [&] {
      access_.locked([&](Peer &p) {
        p.expire(access_.now());
        if (!sameJob(binding, p.binding)) {
          done = true;
          return;
        }
        binding = p.binding;
        ready = p.phase == Peer::active;
        done = ready || p.phase == Peer::failed || p.phase == Peer::closed;
        if (ready)
          session = p.fileSession();
      });
      return done;
    });
    if (!ready) {
      cancel(binding);
      return 503;
    }
    return 200;
  }
  int exchange(const Binding &b, const std::uint8_t *data, unsigned n,
               std::uint8_t *out, unsigned &got) override {
    bool submitted = false;
    got = 0;
    access_.locked(
        [&](Peer &p) { submitted = p.submit(b, data, n, access_.now()); });
    if (!submitted)
      return 503;
    bool broken = false;
    wait(60000, [&] {
      access_.locked([&](Peer &p) {
        p.expire(access_.now());
        broken = p.binding != b || p.phase != Peer::active;
        if (!broken)
          got = p.answer(b, out);
      });
      return broken || got;
    });
    if (!got) {
      cancel(b);
      return 503;
    }
    return 200;
  }
  int leave(const Binding &b) override {
    bool finishing = false;
    access_.locked([&](Peer &p) { finishing = p.finish(b, access_.now()); });
    if (!finishing) {
      cancel(b);
      return 503;
    }
    bool done = false, ok = false;
    wait(5500, [&] {
      access_.locked([&](Peer &p) {
        p.expire(access_.now());
        if (p.binding != b) {
          done = true;
          return;
        }
        done = p.phase == Peer::closed || p.phase == Peer::failed;
        ok = p.phase == Peer::closed && p.success;
        if (done)
          p.retire();
      });
      return done;
    });
    if (!done)
      cancel(b);
    if (done)
      handBack();
    return done && ok ? 200 : 503;
  }
  void cancel(const Binding &b) override {
    access_.locked([&](Peer &p) { p.cancel(b); });
    wait(5500, [&] {
      bool done = false;
      access_.locked([&](Peer &p) {
        p.expire(access_.now());
        if (p.binding != b) {
          done = true;
          return;
        }
        done = !p.owned();
        if (done)
          p.retire();
      });
      return done;
    });
    handBack();
  }
};
} // namespace agon::extender::storage::admission
