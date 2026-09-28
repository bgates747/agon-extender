#pragma once
#include "connection.hpp"
namespace agon::extender::webdav {
// Keep one byte until the owner releases its grant, spool and media lease.
// Content-Length clients may issue their next request before TCP close. Without
// this boundary they observe success while the old worker still owns resources.
// This is response completion ordering, not a pending-request queue.
class CompletionStream final : public Stream {
  Stream &wire_;
  unsigned char tail_ = 0;
  bool pending_ = false;
public:
  explicit CompletionStream(Stream &wire) : wire_(wire) {}
  int read(void *p, size_t n) override { return wire_.read(p, n); }
  int send(const void *p, size_t n) override {
    if (!n) return 0;
    if (pending_) {
      int sent = wire_.send(&tail_, 1);
      if (sent != 1) return -1;
      pending_ = false;
    }
    const auto *b = static_cast<const unsigned char *>(p);
    if (n > 1) {
      int sent = wire_.send(b, n - 1);
      if (sent <= 0) return -1;
      if (size_t(sent) != n - 1) return sent;
    }
    tail_ = b[n - 1];
    pending_ = true;
    return int(n);
  }
  void close() override {} // owner completes only after resource teardown
  void complete() {
    if (pending_) {
      (void)wire_.send(&tail_, 1);
      pending_ = false;
    }
    wire_.close();
  }
};
}
