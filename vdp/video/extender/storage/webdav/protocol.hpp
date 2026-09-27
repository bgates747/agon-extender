#pragma once
// MIT adaptation; source revision and deliberate differences: PROVENANCE.md.
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <map>
#include <string>
#include <string_view>
#include <vector>
namespace agon::extender::webdav {
inline bool number(std::string_view s, std::uint32_t &out, unsigned base = 10) {
  if (s.empty())
    return false;
  out = 0;
  for (char c : s) {
    unsigned d = c >= '0' && c <= '9'   ? c - '0'
                 : c >= 'a' && c <= 'f' ? c - 'a' + 10
                 : c >= 'A' && c <= 'F' ? c - 'A' + 10
                                        : 99;
    if (d >= base || out > (0x7fffffffU - d) / base)
      return false;
    out = out * base + d;
  }
  return true;
}
inline bool path(std::string_view uri, std::string &out) {
  if (uri.empty() || uri.size() > 360 || uri[0] != '/')
    return false;
  out.clear();
  for (size_t i = 0; i < uri.size(); ++i) {
    unsigned char c = uri[i];
    if (c == '%') {
      std::uint32_t b;
      if (i + 2 >= uri.size() || !number(uri.substr(i + 1, 2), b, 16))
        return false;
      c = b;
      i += 2;
      if (c == '/')
        return false; // Reject alternate encoded path separators.
    }
    if (c < 32 || c >= 127 || std::strchr("\\:%*?\"<>|#", c))
      return false;
    out += char(c);
    if (out.size() > 120)
      return false;
  }
  if (out.size() > 1 && out.back() == '/')
    out.pop_back();
  if (out == "/")
    return true;
  size_t start = 1;
  for (size_t i = 1; i <= out.size(); ++i)
    if (i == out.size() || out[i] == '/') {
      auto s = out.substr(start, i - start);
      if (s.empty() || s == "." || s == ".." || s.back() == '.' ||
          s.back() == ' ')
        return false;
      start = i + 1;
    }
  return true;
}
inline std::string encode(std::string_view s) {
  static const char hex[] = "0123456789ABCDEF";
  std::string out;
  for (unsigned char c : s)
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
        (c >= '0' && c <= '9') || std::strchr("-_.~/", c))
      out += char(c);
    else {
      out += '%';
      out += hex[c >> 4];
      out += hex[c & 15];
    }
  return out;
}
inline std::string xml(std::string_view s) {
  std::string o;
  for (char c : s) {
    switch (c) {
    case '&':
      o += "&amp;";
      break;
    case '<':
      o += "&lt;";
      break;
    case '>':
      o += "&gt;";
      break;
    case '\"':
      o += "&quot;";
      break;
    case '\'':
      o += "&apos;";
      break;
    default:
      o += c;
    }
  }
  return o;
}
inline std::string folded(std::string s) {
  for (char &c : s)
    if (c >= 'A' && c <= 'Z')
      c += 32;
  return s;
}
inline bool overlap(const std::string &a, const std::string &b) {
  auto x = folded(a), y = folded(b);
  return x == y || x == "/" || y == "/" || x.rfind(y + "/", 0) == 0 ||
         y.rfind(x + "/", 0) == 0;
}
struct Range {
  std::uint32_t start = 0, count = 0;
  bool partial = false;
};
inline int range(std::string_view s, std::uint32_t size, Range &r) {
  r = {0, size, false};
  if (s.empty() || s.substr(0, 6) != "bytes=" || s.find(',') != s.npos)
    return 200;
  s.remove_prefix(6);
  auto dash = s.find('-');
  if (dash == s.npos)
    return 400;
  std::uint32_t a = 0, b = 0;
  if (dash == 0) {
    if (!number(s.substr(1), b))
      return 400;
    if (!b || !size)
      return 416;
    a = b >= size ? 0 : size - b;
    b = size - 1;
  } else {
    if (!number(s.substr(0, dash), a))
      return 400;
    if (dash + 1 == s.size())
      b = size ? size - 1 : 0;
    else if (!number(s.substr(dash + 1), b))
      return 400;
    if (!size || a >= size || b < a)
      return 416;
    b = std::min(b, size - 1);
  }
  r = {a, b - a + 1, true};
  return 206;
}
// Raw body input: negative means timeout/disconnect/error; no unbounded
// retries.
struct Input {
  virtual ~Input() = default;
  virtual int read(void *, size_t) = 0;
};
// One request/connection. Caller closes connection after response; pipelining
// is not supported, so no hidden parser buffer can be mistaken for another
// request.
class Body {
public:
  Body(Input &in, std::uint32_t length, bool chunked)
      : in_(in), expected_(length), chunked_(chunked) {}
  int read(void *dst, size_t cap) {
    if (bad_ || done_)
      return bad_ ? -1 : 0;
    if (!chunked_) {
      if (total_ == expected_) {
        done_ = true;
        return 0;
      }
      return data(dst, std::min<size_t>(cap, expected_ - total_));
    }
    while (!left_) {
      if (needCRLF_) {
        char c[2];
        if (!exact(c, 2) || c[0] != '\r' || c[1] != '\n')
          return fail();
        needCRLF_ = false;
      }
      std::string line;
      if (!readline(line))
        return fail();
      // No ignored chunk extensions/trailers: reject forms not implemented.
      if (!number(line, left_, 16))
        return fail();
      if (!left_) {
        if (!readline(line) || !line.empty() || total_ != expected_)
          return fail();
        done_ = true;
        return 0;
      }
      if (left_ > expected_ - total_)
        return fail();
    }
    int n = data(dst, std::min<size_t>(cap, left_));
    if (n > 0) {
      left_ -= n;
      if (!left_)
        needCRLF_ = true;
    }
    return n;
  }
  bool finished() const { return done_ && !bad_; }

private:
  int fail() {
    bad_ = true;
    return -1;
  }
  bool exact(char *p, size_t n) {
    while (n) {
      int k = in_.read(p, n);
      if (k <= 0 || size_t(k) > n)
        return false;
      p += k;
      n -= k;
    }
    return true;
  }
  bool readline(std::string &s) {
    s.clear();
    char c;
    for (unsigned i = 0; i < 40; ++i) {
      if (!exact(&c, 1))
        return false;
      if (c == '\r') {
        return exact(&c, 1) && c == '\n';
      }
      if (c == '\n')
        return false;
      s += c;
    }
    return false;
  }
  int data(void *p, size_t n) {
    if (!n)
      return fail();
    int k = in_.read(p, n);
    if (k <= 0 || size_t(k) > n)
      return fail();
    total_ += k;
    return k;
  }
  Input &in_;
  std::uint32_t expected_, total_ = 0, left_ = 0;
  bool chunked_, needCRLF_ = false, bad_ = false, done_ = false;
};
} // namespace agon::extender::webdav
