#pragma once
// Development-only HTTP/storage boundary. Never calls UART or mainboard POSIX.
// See README.md for the mandatory admission and completion implementation
// fence.
#include "protocol.hpp"
#include <array>
#include <atomic>
#include <functional>
namespace agon::extender::webdav {
struct Request {
  std::string method, uri;
  std::map<std::string, std::string>
      headers; // lower-case, duplicate-free at HTTP boundary
  std::string header(const char *key) const {
    auto i = headers.find(key);
    return i == headers.end() ? "" : i->second;
  }
};
struct Entry {
  std::string path;
  std::uint32_t size = 0;
  bool directory = false;
};
struct Operation {
  std::string method, source, destination;
  bool overwrite = false, recursive = false;
};
struct Outcome {
  int status = 200;
  unsigned completed = 0;
  std::string failedPath;
};
struct Output {
  virtual ~Output() = default;
  // length -1 means chunked response; output MUST abort on incomplete writes.
  virtual bool begin(int status,
                     const std::map<std::string, std::string> &headers,
                     std::int64_t length) = 0;
  virtual bool write(const void *, size_t) = 0;
  virtual void abort() = 0;
};
struct Backend {
  virtual ~Backend() = default;
  // begin MUST obtain exact EMOS READY for this immutable operation, no queue.
  // Busy/unavailable/stale=503. Test stubs do not implement that protocol.
  virtual int begin(const Operation &) = 0;
  // finish waits for a matching terminal mainboard result and closes the grant.
  // Uncertain result is non-2xx even when local stage is complete.
  virtual int finish() = 0;
  virtual void
  cancel() = 0; // retire, never resubmit; preserve uncertain evidence
  virtual int stat(const std::string &, Entry &) = 0; // 200 or 404 or error
  virtual int list(const std::string &,
                   const std::function<bool(const Entry &)> &) = 0;
  // Snapshot must be complete/verified on P4 SD, not live mainboard reads.
  // Snapshot remains readable after finish() until releaseSnapshot().
  virtual int snapshot(const std::string &, std::uint32_t &size) = 0;
  virtual int readSnapshot(std::uint32_t, void *, size_t, size_t &) = 0;
  virtual void releaseSnapshot() = 0;
  // put must consume Body to its validated end, seal stage, checked transfer,
  // journal activation and await exact commit ACK. No target truncation
  // fallback.
  virtual Outcome put(const std::string &, std::uint32_t, bool, Body &) = 0;
  virtual Outcome mkdir(const std::string &) = 0;
  virtual Outcome move(const std::string &, const std::string &, bool) = 0;
  virtual Outcome copy(const std::string &, const std::string &, bool,
                       bool) = 0;
  virtual Outcome remove(const std::string &) = 0; // root preflight, depth <=16
};
inline const char *reason(int n) {
  switch (n) {
  case 200:
    return "OK";
  case 201:
    return "Created";
  case 204:
    return "No Content";
  case 206:
    return "Partial Content";
  case 207:
    return "Multi-Status";
  case 304:
    return "Not Modified";
  case 417:
    return "Expectation Failed";
  case 502:
    return "Bad Gateway";
  case 400:
    return "Bad Request";
  case 403:
    return "Forbidden";
  case 404:
    return "Not Found";
  case 405:
    return "Method Not Allowed";
  case 409:
    return "Conflict";
  case 411:
    return "Length Required";
  case 412:
    return "Precondition Failed";
  case 413:
    return "Content Too Large";
  case 415:
    return "Unsupported Media Type";
  case 416:
    return "Range Not Satisfiable";
  case 422:
    return "Unprocessable Content";
  case 501:
    return "Not Implemented";
  case 503:
    return "Service Unavailable";
  case 507:
    return "Insufficient Storage";
  default:
    return "Internal Server Error";
  }
}
class Adapter {
public:
  explicit Adapter(Backend &backend, std::string origin)
      : backend_(backend), origin_(std::move(origin)) {}
  void handle(const Request &, Input &, Output &);

private:
  Backend &backend_;
  std::string origin_;
  std::atomic_flag busy_ = ATOMIC_FLAG_INIT;
};
} // namespace agon::extender::webdav
