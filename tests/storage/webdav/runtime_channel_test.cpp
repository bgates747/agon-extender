// Actual HTTP -> Channel -> P4 Peer -> finite EMOS utility -> checked engine.
// Two host threads replace the console transport and foreground execution only.
#include "extender/storage/admission/channel.hpp"
#include "extender/storage/webdav/connection.hpp"
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <thread>
extern "C" {
int sdjob_run(void);
void fs_root(const char *);
}
using namespace agon::extender;
using storage::admission::Binding;
using storage::admission::Peer;
static Peer peer;
static std::mutex mutex_;
static Binding grant;
static unsigned sequence;
static std::atomic<bool> stop{false}, eligible{false};
static unsigned jobs;
static std::atomic<unsigned> failed_jobs{0};
static auto epoch = std::chrono::steady_clock::now();
static std::uint32_t now() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             std::chrono::steady_clock::now() - epoch)
      .count();
}
extern "C" std::uint32_t sdapp_clock(void) {
  return std::uint64_t(now()) * 120 / 1000;
}
extern "C" int sdjob_cancelled(void) { return 0; }
extern "C" unsigned sdapp_link(unsigned op, const std::uint8_t *p, unsigned n,
                               std::uint8_t *out, unsigned cap, unsigned *got) {
  if (op == 1)
    std::this_thread::sleep_for(std::chrono::microseconds(100));
  std::lock_guard<std::mutex> lock(mutex_);
  *got = 0;
  if (op == 5) {
    assert(cap == 36);
    memcpy(out, grant.data(), 28);
    sd_put32(out + 28, 1);
    sd_put32(out + 32, sequence);
    *got = 36;
    return 0;
  }
  if (op == 6) {
    sequence = sd_u32(p);
    return 0;
  }
  if (op == 3)
    return 0;
  if (op == 2) {
    assert(peer.receive(p, n, now(), 123, 456));
    return 0;
  }
  assert(op == 1);
  *got = peer.take(out, now());
  return 0;
}
static unsigned control(unsigned op, unsigned status = 0) {
  std::uint8_t p[48], r[240];
  sd_header(p, 4, 1, ++sequence, op, status, 28);
  memcpy(p + 20, grant.data(), 28);
  sd_seal(p);
  assert(peer.receive(p, sizeof p, now(), 123, 456));
  assert(peer.take(r, now()) == 48);
  if (op == 1) {
    memcpy(grant.data(), r + 20, 28);
    grant[26] = 0;
    sd_put32(grant.data() + 8, 1);
  }
  return r[13];
}
static void resident() {
  {
    std::lock_guard<std::mutex> lock(mutex_);
    grant = {};
    grant[26] = 1;
    control(1);
    control(2);
    eligible = true;
  }
  while (!stop) {
    bool run = false;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      if (peer.phase == Peer::armed) {
        control(2);
        grant = peer.binding;
        sd_put32(grant.data() + 16, jobs + 1);
        control(3);
        run = true;
      } else if (peer.phase == Peer::idle) {
        grant =
            {}; // retain negotiated incarnation from peer's most recent binding
        // The resident owns its link independently of a P4 job.
        sd_put32(grant.data(), 123);
        sd_put32(grant.data() + 4, 456);
        sd_put32(grant.data() + 8, jobs + 1);
        control(2);
        eligible = true;
      }
    }
    if (run) {
      int result = sdjob_run();
      if(result)++failed_jobs;
      std::lock_guard<std::mutex> lock(mutex_);
      control(10, result ? 7 : 0);
      ++jobs;
      eligible = false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
}
struct Access : storage::admission::Access {
  void locked(const std::function<void(Peer &)> &f) override {
    std::lock_guard<std::mutex> lock(mutex_);
    f(peer);
  }
  bool manualBusy() override { return false; }
  std::uint32_t now() override { return ::now(); }
  void pause() override {
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
};
struct Stream : webdav::Stream {
  std::string request, response;
  size_t at = 0;
  bool closed = false;
  explicit Stream(std::string s) : request(std::move(s)) {}
  int read(void *p, size_t n) override {
    n = std::min(n, request.size() - at);
    if (n > 37)
      n = 37;
    memcpy(p, request.data() + at, n);
    at += n;
    return n;
  }
  int send(const void *p, size_t n) override {
    response.append(static_cast<const char *>(p), n);
    return n;
  }
  void close() override { closed = true; }
};
int main() {
  char dir[] = "/tmp/runtime-job-XXXXXX";
  assert(mkdtemp(dir));
  std::string root = dir;
  std::filesystem::create_directory(root + "/agon");
  std::filesystem::create_directory(root + "/spool");
  fs_root((root + "/agon").c_str());
  std::thread worker(resident);
  Access access;
  storage::admission::Channel channel(access);
  while (!eligible)
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  auto request = [&](const std::string &text, unsigned status) {
    webdav::WireBackend backend(channel, root + "/spool", 1024 * 1024);
    webdav::Adapter adapter(backend, "http://host:8081");
    Stream stream(text);
    webdav::serveConnection(adapter, stream);
    if (stream.response.rfind("HTTP/1.1 " + std::to_string(status), 0) != 0) {
      fprintf(stderr, "Unexpected response: %s\n", stream.response.c_str());
      abort();
    }
    return stream.response;
  };
  request("PUT /hello HTTP/1.1\r\nHost: host:8081\r\nContent-Length: "
          "5\r\n\r\nhello",
          201);
  auto get = request("GET /hello HTTP/1.1\r\nHost: host:8081\r\n\r\n", 200);
  assert(get.substr(get.size() - 5) == "hello");
  request(
      "MKCOL /folder HTTP/1.1\r\nHost: host:8081\r\nContent-Length: 0\r\n\r\n",
      201);
  request("COPY /hello HTTP/1.1\r\nHost: host:8081\r\nDestination: "
          "/folder/copied\r\nOverwrite: F\r\n\r\n",
          201);
  request("PROPFIND /folder HTTP/1.1\r\nHost: host:8081\r\nDepth: "
          "1\r\nContent-Length: 0\r\n\r\n",
          207);
  request("MOVE /folder/copied HTTP/1.1\r\nHost: host:8081\r\nDestination: "
          "/folder/moved\r\nOverwrite: F\r\n\r\n",
          201);
  request("DELETE /folder HTTP/1.1\r\nHost: host:8081\r\n\r\n", 204);
  assert(!std::filesystem::exists(root + "/agon/folder"));
  // EOF while staging on P4: no Agon destination, no failed utility return,
  // no re-handshake by this resident model, and a fresh operation succeeds.
  request("PUT /aborted HTTP/1.1\r\nHost: host:8081\r\nContent-Length: 99\r\n\r\nshort",400);
  assert(!std::filesystem::exists(root+"/agon/aborted"));
  auto again=request("GET /hello HTTP/1.1\r\nHost: host:8081\r\n\r\n",200);
  assert(again.substr(again.size()-5)=="hello");
  assert(!failed_jobs);
  stop = true;
  worker.join();
  assert(jobs == 9);
  std::filesystem::remove_all(root);
  puts("actual HTTP, Channel, Peer, finite MOSlet and engine: "
       "PUT/GET/MKCOL/COPY/PROPFIND/MOVE/recursive DELETE pass");
}
