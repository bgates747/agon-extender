#include "extender/storage/webdav/staged_put.hpp"
#include <cassert>
#include <filesystem>
#include <iostream>
#include <unistd.h>
using namespace agon::extender::webdav;
namespace spool = agon::extender::spool;
struct In : Input {
  std::string bytes;
  size_t at = 0, fragment = 7;
  explicit In(std::string s = "") : bytes(std::move(s)) {}
  int read(void *p, size_t n) override {
    n = std::min({n, fragment, bytes.size() - at});
    if (n)
      std::memcpy(p, bytes.data() + at, n);
    at += n;
    return int(n);
  }
};
struct Out : Output {
  int status = 0;
  std::int64_t length = 0;
  std::string body;
  std::map<std::string, std::string> headers;
  bool aborted = false, fail = false;
  bool begin(int s, const std::map<std::string, std::string> &h,
             std::int64_t n) override {
    status = s;
    headers = h;
    length = n;
    return !fail;
  }
  bool write(const void *p, size_t n) override {
    if (fail)
      return false;
    body.append(static_cast<const char *>(p), n);
    return true;
  }
  void abort() override { aborted = true; }
};
// Deliberately a storage/admission TEST DOUBLE, not an EMOS or network peer.
// Staged PUT below uses the actual on-disk P4 Store with real temp files.
struct Fake : Backend {
  std::map<std::string, std::string> files{{"/file", "abcdef"},
                                           {"/dir/a&b", "child"}};
  std::vector<std::string> dirs{"/", "/dir"};
  int begins = 0, finishes = 0, cancels = 0, mutations = 0, reads = 0,
      releases = 0, denial = 200, terminal = 200, commitStatus = 200,
      listError = 200;
  bool active = false;
  std::string snapshotBytes, root;
  Operation operation;
  std::function<void()> onBegin;
  Outcome mutationError{};
  Fake() {
    char tmp[] = "/tmp/webdav-test-XXXXXX";
    root = mkdtemp(tmp);
  }
  ~Fake() { std::filesystem::remove_all(root); }
  int begin(const Operation &o) override {
    ++begins;
    if (denial != 200)
      return denial;
    assert(!active);
    active = true;
    operation = o;
    if (onBegin)
      onBegin();
    return 200;
  }
  int finish() override {
    assert(active);
    ++finishes;
    active = false;
    return terminal;
  }
  void cancel() override {
    assert(active);
    ++cancels;
    active = false;
  }
  int stat(const std::string &p, Entry &e) override {
    assert(active);
    if (std::find(dirs.begin(), dirs.end(), p) != dirs.end()) {
      e = {p, 0, true};
      return 200;
    }
    auto i = files.find(p);
    if (i == files.end())
      return 404;
    e = {p, std::uint32_t(i->second.size()), false};
    return 200;
  }
  int list(const std::string &p,
           const std::function<bool(const Entry &)> &emit) override {
    if (listError != 200)
      return listError;
    for (auto &i : files) {
      auto parent = i.first.substr(0, i.first.rfind('/'));
      if (parent.empty())
        parent = "/";
      if (parent == p &&
          !emit({i.first, std::uint32_t(i.second.size()), false}))
        return 507;
    }
    for (auto &i : dirs)
      if (i != "/") {
        auto parent = i.substr(0, i.rfind('/'));
        if (parent.empty())
          parent = "/";
        if (parent == p && !emit({i, 0, true}))
          return 507;
      }
    return 200;
  }
  int snapshot(const std::string &p, std::uint32_t &size) override {
    snapshotBytes = files.at(p);
    size = snapshotBytes.size();
    return 200;
  }
  int readSnapshot(std::uint32_t at, void *p, size_t n, size_t &got) override {
    assert(!active);
    ++reads;
    got = std::min(n, snapshotBytes.size() - at);
    std::memcpy(p, snapshotBytes.data() + at, got);
    return 200;
  }
  void releaseSnapshot() override {
    ++releases;
    snapshotBytes.clear();
  }
  Outcome put(const std::string &p, std::uint32_t n, bool replace,
              Body &body) override {
    assert(active);
    spool::Store<> store(root, 65536);
    spool::Job j;
    j.size = n;
    auto *b = j.binding.data();
    b[0] = 1;
    b[8] = 1;
    b[12] = 1;
    b[16] = 1;
    b[24] = 1;
    b[25] = 3;
    auto *d = j.descriptor.data();
    d[0] = 3;
    d[1] = replace;
    std::string src = "/incoming";
    sd_put16(d + 2, src.size());
    sd_put16(d + 4, p.size());
    std::memcpy(d + 8, src.data(), src.size());
    std::memcpy(d + 8 + src.size(), p.data(), p.size());
    j.descriptorSize = 8 + src.size() + p.size();
    std::string remoteStage;
    return stagedPut(
        store, j, body,
        [&](auto &s, const auto &job) {
          std::array<char, 4096> buf{};
          std::uint32_t at = 0;
          while (at < n) {
            size_t got = 0;
            assert(s.read(job.binding, at, buf.data(), buf.size(), got) ==
                   spool::Result::ok);
            assert(got);
            remoteStage.append(buf.data(), got);
            at += got;
          }
          return 200;
        },
        [&](const auto &) {
          if (commitStatus != 200)
            return commitStatus;
          if (!replace && files.count(p))
            return 412;
          ++mutations;
          files[p] = remoteStage;
          return 200;
        });
  }
  Outcome mkdir(const std::string &p) override {
    ++mutations;
    dirs.push_back(p);
    return mutationError;
  }
  Outcome move(const std::string &a, const std::string &b,
               bool replace) override {
    assert(!replace);
    ++mutations;
    files[b] = files.at(a);
    files.erase(a);
    return mutationError;
  }
  Outcome copy(const std::string &a, const std::string &b, bool,
               bool recursive) override {
    assert(recursive == operation.recursive);
    ++mutations;
    if (files.count(a))
      files[b] = files.at(a);
    return mutationError;
  }
  Outcome remove(const std::string &p) override {
    if (p == "/")
      return {403, 0, {}};
    ++mutations;
    files.erase(p);
    return mutationError;
  }
};
static Out run(Adapter &a, std::string m, std::string p,
               std::map<std::string, std::string> h = {},
               std::string body = "") {
  In in(std::move(body));
  Out out;
  a.handle({m, p, h}, in, out);
  return out;
}
int main() {
  {
    Fake f;
    Adapter a(f, "http://local:8080");
    auto r = run(a, "OPTIONS", "/");
    assert(r.status == 200 && f.begins == 0 && !r.headers.count("DAV"));
    assert(r.headers.at("Allow").find("LOCK") == std::string::npos);
    assert(run(a, "LOCK", "/file").status == 405 && f.begins == 0);
    for (auto p : {"/../file", "/a%2fb", "/a%00b", "/a%", "/a%0", "/x//y",
                   "/x.", "/file?foo", "/a\\b"})
      assert(run(a, "GET", p).status == 400);
    assert(f.begins == 0);
    f.denial = 503;
    assert(run(a, "GET", "/file").status == 503 && f.finishes == 0 &&
           f.reads == 0);
  }
  {
    Fake f;
    Adapter a(f, "http://local");
    f.onBegin = [&] { assert(run(a, "DELETE", "/file").status == 503); };
    auto r = run(a, "GET", "/file");
    assert(r.status == 200 && r.body == "abcdef" && f.mutations == 0 &&
           f.begins == 1 && f.finishes == 1 && f.releases == 1);
    f.onBegin = {};
    r = run(a, "GET", "/file", {{"range", "bytes=2-4"}});
    assert(r.status == 206 && r.body == "cde" &&
           r.headers.at("Content-Range") == "bytes 2-4/6");
    assert(run(a, "GET", "/file", {{"range", "bytes=-2"}}).body == "ef");
    assert(run(a, "GET", "/file", {{"range", "bytes=4-999"}}).body == "ef");
    assert(run(a, "GET", "/file", {{"range", "bytes=99-"}}).status == 416);
    assert(run(a, "GET", "/file", {{"range", "bytes=2x-4"}}).status == 400);
    assert(run(a, "GET", "/file", {{"range", "bytes=0-1,3-4"}}).body ==
           "abcdef");
    r = run(a, "HEAD", "/file");
    assert(r.status == 200 && r.body.empty() && r.length == 6);
    assert(run(a, "GET", "/dir").status == 405);
    assert(run(a, "GET", "/missing").status == 404);
    f.terminal = 500;
    r = run(a, "GET", "/file");
    assert(r.status == 500 && r.body.empty());
  }
  {
    Fake f;
    Adapter a(f, "http://local");
    auto r = run(a, "PROPFIND", "/", {{"depth", "1"}});
    assert(r.status == 207 && r.body.find("<D:collection/>") != r.body.npos &&
           r.body.find("/file") != r.body.npos);
    assert(run(a, "PROPFIND", "/", {{"depth", "infinity"}}).status == 403);
    assert(run(a, "PROPFIND", "/").status == 403);
    std::string body = "<?xml version=\"1.0\"?><propfind "
                       "xmlns=\"DAV:\"><prop><getcontentlength/><getetag/"
                       "><q:custom xmlns:q=\"urn:test\"/></prop></propfind>";
    r = run(a, "PROPFIND", "/file",
            {{"depth", "0"}, {"content-length", std::to_string(body.size())}},
            body);
    assert(r.status == 207 && r.body.find("404 Not Found") != r.body.npos &&
           r.body.find("urn:test") != r.body.npos &&
           r.body.find(">6<") != r.body.npos);
    for (auto bad :
         {"<!DOCTYPE x><x/>", "<D:propfind/>",
          "<propfind xmlns=\"DAV:\"><allprop/><allprop/></propfind>",
          "<propfind "
          "xmlns=\"DAV:\"><prop><getetag>bad</getetag></prop></propfind>"})
      assert(run(a, "PROPFIND", "/",
                 {{"depth", "0"},
                  {"content-length", std::to_string(std::strlen(bad))}},
                 bad)
                 .status == 400);
    f.listError = 503;
    assert(run(a, "PROPFIND", "/", {{"depth", "1"}}).status == 503);
    f.listError = 200;
    for (unsigned i = 0; i < 513; ++i)
      f.files["/many" + std::to_string(i)] = "";
    assert(run(a, "PROPFIND", "/", {{"depth", "1"}}).status == 507);
  }
  {
    Fake f;
    Adapter a(f, "http://local");
    assert(run(a, "PUT", "/new", {{"content-length", "3"}}, "xyz").status ==
           201);
    assert(f.files["/new"] == "xyz");
    assert(run(a, "PUT", "/new", {{"content-length", "1"}}, "Q").status == 204);
    assert(f.files["/new"] == "Q");
    assert(run(a, "PUT", "/new",
               {{"content-length", "1"}, {"if-none-match", "*"}}, "Z")
               .status == 412);
    assert(f.files["/new"] == "Q");
    assert(run(a, "PUT", "/absent",
               {{"content-length", "1"}, {"if-match", "*"}}, "Z")
               .status == 412);
    assert(run(a, "PUT", "/new",
               {{"content-length", "1"}, {"if-match", "\"bogus\""}}, "Z")
               .status == 501);
    assert(run(a, "PUT", "/empty", {{"content-length", "0"}}).status == 201);
    assert(f.files["/empty"].empty());
    assert(run(a, "PUT", "/new").status == 411);
    assert(run(a, "MKCOL", "/folder").status == 201);
    assert(run(a, "MKCOL", "/folder").status == 405);
    assert(run(a, "MKCOL", "/folder2", {{"content-length", "1"}}, "x").status ==
           415);
    assert(run(a, "MOVE", "/new", {{"destination", "http://elsewhere/target"}})
               .status == 502);
    assert(
        run(a, "MOVE", "/new", {{"destination", "/file"}, {"overwrite", "F"}})
            .status == 412);
    assert(run(a, "MOVE", "/new", {{"destination", "/file"}}).status == 501);
    assert(run(a, "MOVE", "/new", {{"destination", "http://local/moved"}})
               .status == 201);
    assert(!f.files.count("/new"));
    assert(run(a, "COPY", "/moved", {{"destination", "/file"}}).status == 204);
    assert(f.files["/file"] == "Q");
    assert(run(a, "COPY", "/dir", {{"destination", "/dir/sub"}}).status == 403);
    assert(run(a, "DELETE", "/file").status == 204);
    assert(!f.files.count("/file"));
    assert(run(a, "DELETE", "/").status == 403);
    f.mutationError = {507, 3, "/dir/problem"};
    auto r = run(a, "DELETE", "/dir");
    assert(r.status == 207 &&
           r.body.find("507 Insufficient Storage") != r.body.npos &&
           r.body.find("3 completed") != r.body.npos);
  }
  // Finder-style raw chunks across arbitrary input fragment boundaries.
  for (unsigned fragment = 1; fragment < 12; ++fragment) {
    Fake f;
    Adapter a(f, "http://local");
    In in("3\r\nabc\r\n3\r\ndef\r\n0\r\n\r\n");
    in.fragment = fragment;
    Out out;
    a.handle(
        {"PUT",
         "/chunk",
         {{"transfer-encoding", "chunked"}, {"x-expected-entity-length", "6"}}},
        in, out);
    assert(out.status == 201 && f.files["/chunk"] == "abcdef" &&
           f.mutations == 1);
  }
  for (auto body :
       {"3\r\nabc\r\n", "3\r\nabc\r\n0\r\n\r\n", "7\r\nabcdefg\r\n0\r\n\r\n",
        "6x\r\nabcdef\r\n0\r\n\r\n", "6\r\nabcdefX\n0\r\n\r\n",
        "6\r\nabcdef\r\n0\r\nX: y\r\n\r\n"}) {
    Fake f;
    Adapter a(f, "http://local");
    auto r = run(
        a, "PUT", "/file",
        {{"transfer-encoding", "chunked"}, {"x-expected-entity-length", "6"}},
        body);
    assert(r.status == 400 && f.files["/file"] == "abcdef" && f.mutations == 0);
  }
  {
    Fake f;
    Adapter a(f, "http://local");
    assert(run(a, "PUT", "/file", {{"content-length", "6"}}, "abc").status ==
               400 &&
           f.mutations == 0);
    assert(run(a, "PUT", "/file",
               {{"content-length", "6"},
                {"transfer-encoding", "chunked"},
                {"x-expected-entity-length", "6"}},
               "abcdef")
               .status == 400);
    assert(run(a, "PUT", "/file", {{"transfer-encoding", "chunked"}}, "abcdef")
               .status == 400);
    assert(run(a, "PUT", "/file", {{"content-length", "65537"}}).status ==
               507 &&
           f.mutations == 0);
    f.commitStatus = 500;
    assert(run(a, "PUT", "/file", {{"content-length", "3"}}, "NEW").status ==
               500 &&
           f.mutations == 0);
    spool::Store<> store(f.root, 65536);
    spool::Info info;
    assert(store.inspect(info) == spool::Result::ok &&
           info.state == spool::State::uncertain);
    assert(run(a, "PUT", "/file", {{"content-length", "3"}}, "NEW").status ==
           500); // retained slot prevents a hidden retry
  }
  {
    Fake f;
    Adapter a(f, "http://local");
    In in;
    Out out;
    out.fail = true;
    a.handle({"GET", "/file", {}}, in, out);
    assert(out.aborted && f.releases == 1 && !f.active);
  }
  std::cout << "WebDAV methods, admission, conditions, ranges, XML, real spool "
               "and fragmented bodies passed\n";
}
