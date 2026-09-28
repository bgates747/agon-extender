#include "extender/storage/webdav/connection.hpp"
#include "extender/storage/webdav/wire_backend.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <unistd.h>
extern "C" {
int service_init(const char *, std::uint32_t);
void service_stop(void);
unsigned service_request(const std::uint8_t *, unsigned, std::uint8_t *);
void fs_root(const char *);
void fs_fault(unsigned, unsigned);
}
using namespace agon::extender::webdav;
namespace spool = agon::extender::spool;
namespace fs = std::filesystem;
// Real EMOSlet C file engine, host filesystem, simulated READY/transport only.
struct Local : Channel {
  bool active = false, dropActivate = false, corruptReply = false;
  unsigned calls = 0, enters = 0;
  std::uint32_t session = 0;
  spool::Binding binding{};
  int enter(const Operation &op, spool::Binding &b,
            std::uint32_t &sid) override {
    assert(!active);
    active = true;
    ++enters;
    b = {};
    b[0] = 1;
    b[8] = 1;
    sd_put32(b.data() + 12, ++session);
    b[16] = 1;
    b[24] = 1;
    b[25] = op.method == "PUT"        ? 3
            : op.method == "GET"      ? 4
            : op.method == "MKCOL"    ? 5
            : op.method == "MOVE"     ? 6
            : op.method == "COPY"     ? 7
            : op.method == "DELETE"   ? 8
            : op.method == "PROPFIND" ? 2
                                      : 1;
    binding = b;
    sid = session;
    assert(service_init("/", 1));
    return 200;
  }
  int exchange(const spool::Binding &b, const std::uint8_t *p, unsigned n,
               std::uint8_t *out, unsigned &count) override {
    assert(active && b == binding);
    ++calls;
    count = service_request(p, n, out);
    if (dropActivate && p[12] == SD_ACTIVATE)
      return 503;
    if (corruptReply && p[12] != SD_HELLO)
      out[16] ^= 1;
    return count ? 200 : 500;
  }
  int leave(const spool::Binding &b) override {
    assert(active && binding == b);
    active = false;
    service_stop();
    return 200;
  }
  void cancel(const spool::Binding &b) override {
    assert(active && binding == b);
    active = false;
    service_stop();
  }
};
struct In : Input {
  std::string s;
  size_t at = 0;
  explicit In(std::string data = "") : s(std::move(data)) {}
  int read(void *p, size_t n) override {
    n = std::min(n, s.size() - at);
    std::memcpy(p, s.data() + at, n);
    at += n;
    return n;
  }
};
struct Out : Output {
  int status = 0;
  std::string body;
  bool aborted = false;
  bool begin(int s, const std::map<std::string, std::string> &,
             std::int64_t) override {
    status = s;
    return true;
  }
  bool write(const void *p, size_t n) override {
    body.append(static_cast<const char *>(p), n);
    return true;
  }
  void abort() override { aborted = true; }
};
Out run(Adapter &a, const std::string &m, const std::string &p,
        std::map<std::string, std::string> h = {},
        const std::string &data = "") {
  In input(data);
  Out out;
  a.handle({m, p, h}, input, out);
  assert(!out.aborted);
  return out;
}
std::string read(const fs::path &p) {
  std::ifstream f(p, std::ios::binary);
  return {std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()};
}
struct MemoryStream : Stream {
  std::string input, output;
  size_t at = 0, fragment = 7;
  bool closed = false;
  int read(void *p, size_t n) override {
    n = std::min({n, fragment, input.size() - at});
    std::memcpy(p, input.data() + at, n);
    at += n;
    return n;
  }
  int send(const void *p, size_t n) override {
    n = std::min(n, fragment);
    output.append(static_cast<const char *>(p), n);
    return n;
  }
  void close() override { closed = true; }
};
int main() {
  MemoryStream busy;
  busy.input = "HEAD /autoexec.txt HTTP/1.1\r\nHost: test\r\n\r\n";
  rejectConnection(busy);
  assert(busy.closed && busy.at == busy.input.size());
  assert(busy.output.find("HTTP/1.1 503 ") == 0);

  char temp[] = "/tmp/webdav-wire-XXXXXX";
  std::string root = mkdtemp(temp), disk = root + "/agon", stage = root + "/p4";
  fs::create_directory(disk);
  fs::create_directory(stage);
  fs_root(disk.c_str());
  Local channel;
  WireBackend backend(channel, stage, 65536);
  Adapter adapter(backend, "http://local");
  std::string payload;
  for (unsigned i = 0; i < 9999; ++i)
    payload += char(i);
  assert(run(adapter, "MKCOL", "/test").status == 201);
  assert(run(adapter, "PUT", "/test/a",
             {{"content-length", std::to_string(payload.size())}}, payload)
             .status == 201);
  assert(read(disk + "/test/a") == payload && fs::is_empty(stage));
  auto result = run(adapter, "GET", "/test/a");
  assert(result.status == 200 && result.body == payload && fs::is_empty(stage));
  result = run(adapter, "GET", "/test/a", {{"range", "bytes=333-777"}});
  assert(result.status == 206 && result.body == payload.substr(333, 445));
  assert(run(adapter, "PROPFIND", "/test", {{"depth", "1"}}).status == 207);
  assert(
      run(adapter, "PUT", "/test/a", {{"content-length", "3"}}, "NEW").status ==
      204);
  assert(read(disk + "/test/a") == "NEW" &&
         read(disk + "/test/a.p17bak") == payload);
  // Raw HTTP parsing, read-ahead and Finder body decoding through the actual
  // wire backend/file engine, with partial transport reads AND writes.
  for (unsigned fragment : {1U, 7U, 1024U}) {
    MemoryStream stream;
    stream.fragment = fragment;
    std::string path = "/http" + std::to_string(fragment);
    stream.input = "PUT " + path +
                   " HTTP/1.1\r\nHost: local\r\nExpect: "
                   "100-continue\r\nTransfer-Encoding: "
                   "chunked\r\nX-Expected-Entity-Length: "
                   "6\r\n\r\n3\r\nabc\r\n3\r\ndef\r\n0\r\n\r\n";
    serveConnection(adapter, stream);
    assert(stream.closed && stream.output.find("HTTP/1.1 100 Continue") == 0 &&
           stream.output.find("HTTP/1.1 201 Created") != std::string::npos &&
           read(disk + path) == "abcdef");
  }
  for (auto headers :
       {"Host: local\r\nContent-Length: 0\r\nContent-Length: 0",
        "Host: local\r\nContent-Length: 0\r\nTransfer-Encoding: chunked",
        "Host: local\r\n Folded: bad", "X: no-host"}) {
    auto before = channel.enters;
    MemoryStream stream;
    stream.input =
        std::string("PUT /invalid HTTP/1.1\r\n") + headers + "\r\n\r\n";
    serveConnection(adapter, stream);
    assert(stream.output.find("HTTP/1.1 400") == 0 && before == channel.enters);
  }
  {
    MemoryStream stream;
    stream.input = "HEAD /test/a HTTP/1.1\r\nHost: local\r\n\r\n";
    serveConnection(adapter, stream);
    assert(stream.closed &&
           stream.output.find("Content-Length: 3") != std::string::npos &&
           stream.output.substr(stream.output.size() - 4) == "\r\n\r\n");
  }
  // No hidden cleanup of retained backups: another replace is a recovery error.
  assert(run(adapter, "PUT", "/test/a", {{"content-length", "4"}}, "NOPE")
             .status == 500);
  assert(read(disk + "/test/a") == "NEW");
  // Test isolates the intentional retained local stage before continuing. This
  // cleanup is not a production recovery policy.
  for (auto &p : fs::directory_iterator(stage))
    fs::remove_all(p);
  assert(run(adapter, "MOVE", "/test/a", {{"destination", "/test/moved"}})
             .status == 201);
  assert(!fs::exists(disk + "/test/a") && read(disk + "/test/moved") == "NEW");
  assert(run(adapter, "MKCOL", "/tree").status == 201);
  assert(run(adapter, "MKCOL", "/tree/empty").status == 201);
  assert(run(adapter, "PUT", "/tree/file",
             {{"content-length", std::to_string(payload.size())}}, payload)
             .status == 201);
  assert(run(adapter, "COPY", "/tree", {{"destination", "/copied"}}).status ==
         201);
  assert(read(disk + "/copied/file") == payload &&
         fs::is_directory(disk + "/copied/empty") && fs::is_empty(stage));
  assert(run(adapter, "COPY", "/tree",
             {{"destination", "/shallow"}, {"depth", "0"}})
                 .status == 201 &&
         fs::is_empty(disk + "/shallow"));
  assert(run(adapter, "DELETE", "/copied").status == 204 &&
         !fs::exists(disk + "/copied"));
  assert(run(adapter, "DELETE", "/").status == 400 &&
         fs::exists(disk + "/tree/file"));
  // Root protection runs before child deletion. Missing ACK after actual rename
  // preserves both committed remote bytes and uncertain P4 evidence.
  channel.dropActivate = true;
  result = run(adapter, "PUT", "/uncertain", {{"content-length", "3"}}, "ACK");
  assert(result.status == 503 && read(disk + "/uncertain") == "ACK");
  spool::Store<> store(stage, 65536);
  spool::Info info;
  assert(store.inspect(info) == spool::Result::ok &&
         info.state == spool::State::uncertain);
  assert(
      run(adapter, "PUT", "/next", {{"content-length", "3"}}, "NEW").status ==
          500 &&
      !fs::exists(disk + "/next"));
  for (auto &p : fs::directory_iterator(stage))
    fs::remove_all(p);
  channel.dropActivate = false;
  channel.corruptReply = true;
  unsigned before = channel.calls;
  result = run(adapter, "GET", "/tree/file");
  assert(result.status == 500 && channel.calls == before + 2 &&
         !channel.active);
  channel.corruptReply = false;
  // Remote short-write error leaves destination absent and stage recoverable.
  fs_fault(3, 2);
  result = run(adapter, "PUT", "/short", {{"content-length", "3"}}, "BAD");
  assert(result.status >= 400 && !fs::exists(disk + "/short"));
  fs::remove_all(root);
  std::cout
      << "WebDAV -> wire backend -> real EMOSlet engine: checked transfers, "
         "range, tree operations, backup and lost ACK passed\n";
}
