#include "connection.hpp"
namespace agon::extender::webdav {
#include <cstdio>
namespace {
class Connection : public Input, public Output {
  Stream &stream_;
  std::array<char, 1024> buffer_{};
  size_t at_ = 0, end_ = 0;
  bool chunked_ = false, started_ = false, failed_ = false, expect_ = false;
  std::int64_t remaining_ = -1;
  bool send(const void *p, size_t n) {
    auto bytes = static_cast<const char *>(p);
    while (n) {
      int got = stream_.send(bytes, n);
      if (got <= 0 || size_t(got) > n) {
        abort();
        return false;
      }
      bytes += got;
      n -= got;
    }
    return true;
  }

public:
  explicit Connection(Stream &s) : stream_(s) {}
  void expect() { expect_ = true; }
  int read(void *p, size_t cap) override {
    if (failed_)
      return -1;
    if (expect_) {
      expect_ = false;
      const char *line = "HTTP/1.1 100 Continue\r\n\r\n";
      if (!send(line, std::strlen(line)))
        return -1;
    }
    if (at_ == end_) {
      int n = stream_.read(buffer_.data(), buffer_.size());
      if (n <= 0 || size_t(n) > buffer_.size())
        return -1;
      at_ = 0;
      end_ = n;
    }
    size_t n = std::min(cap, end_ - at_);
    std::memcpy(p, buffer_.data() + at_, n);
    at_ += n;
    return n;
  }
  bool begin(int status, const std::map<std::string, std::string> &headers,
             std::int64_t length) override {
    if (started_ || failed_)
      return false;
    started_ = true;
    expect_ = false;
    chunked_ = length < 0;
    remaining_ = length;
    std::string head =
        "HTTP/1.1 " + std::to_string(status) + " " + reason(status) + "\r\n";
    for (auto &h : headers)
      head += h.first + ": " + h.second + "\r\n";
    if (status != 204 && status != 304)
      head += chunked_ ? "Transfer-Encoding: chunked\r\n"
                       : "Content-Length: " + std::to_string(length) + "\r\n";
    head += "\r\n";
    return send(head.data(), head.size());
  }
  bool write(const void *p, size_t n) override {
    if (!started_ || failed_)
      return false;
    if (!n)
      return true;
    if (chunked_) {
      char hex[24];
      int len = std::snprintf(hex, sizeof(hex), "%x\r\n", unsigned(n));
      if (!send(hex, len) || !send(p, n) || !send("\r\n", 2))
        return false;
    } else {
      if (remaining_ < 0 || n > std::uint64_t(remaining_)) {
        abort();
        return false;
      }
      if (!send(p, n))
        return false;
      remaining_ -= n;
    }
    return true;
  }
  void abort() override { failed_ = true; }
  void end(bool head) {
    if (!failed_ && started_) {
      if (chunked_)
        send("0\r\n\r\n", 5);
      else if (remaining_ && !head)
        abort();
    }
    stream_.close();
  }
  void error(int status) {
    begin(status, {{"Connection", "close"}}, 0);
    end(false);
  }
};
bool fieldChar(char c) {
  if (!c)
    return false;
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || std::strchr("!#$%&'*+-.^_`|~", c);
}
} // namespace
void serveConnection(Adapter &adapter, Stream &stream) {
  Connection io(stream);
  std::string head;
  char c;
  while (head.size() < 4096) {
    if (io.read(&c, 1) != 1) {
      stream.close();
      return;
    }
    head += c;
    if (head.size() >= 4 && head.compare(head.size() - 4, 4, "\r\n\r\n") == 0)
      break;
  }
  if (head.size() < 4 || head.compare(head.size() - 4, 4, "\r\n\r\n") != 0) {
    io.error(413);
    return;
  }
  auto end = head.find("\r\n"), space = head.find(' '),
       second = head.find(' ', space + 1);
  if (space == head.npos || second == head.npos || second >= end ||
      head.substr(second + 1, end - second - 1) != "HTTP/1.1" || space > 16) {
    io.error(400);
    return;
  }
  Request q;
  q.method = head.substr(0, space);
  q.uri = head.substr(space + 1, second - space - 1);
  size_t pos = end + 2;
  while (pos < head.size() - 2) {
    end = head.find("\r\n", pos);
    auto colon = head.find(':', pos);
    if (end == head.npos || colon == head.npos || colon >= end ||
        colon == pos) {
      io.error(400);
      return;
    }
    std::string name = head.substr(pos, colon - pos);
    for (char ch : name)
      if (!fieldChar(ch)) {
        io.error(400);
        return;
      }
    name = folded(name);
    auto a = colon + 1, b = end;
    while (a < b && (head[a] == ' ' || head[a] == '\t'))
      ++a;
    while (b > a && (head[b - 1] == ' ' || head[b - 1] == '\t'))
      --b;
    std::string value = head.substr(a, b - a);
    for (unsigned char ch : value)
      if ((ch < 32 && ch != '\t') || ch == 127) {
        io.error(400);
        return;
      }
    if (q.headers.count(name) || q.headers.size() >= 32) {
      io.error(400);
      return;
    }
    q.headers[name] = value;
    pos = end + 2;
  }
  if (q.header("host").empty()) {
    io.error(400);
    return;
  }
  if (q.headers.count("transfer-encoding"))
    q.headers["transfer-encoding"] = folded(q.header("transfer-encoding"));
  if (q.headers.count("expect")) {
    if (folded(q.header("expect")) != "100-continue") {
      io.error(417);
      return;
    }
    io.expect();
  }
  adapter.handle(q, io, io);
  io.end(q.method == "HEAD");
}
} // namespace agon::extender::webdav
