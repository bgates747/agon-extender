#pragma once
// One foreground owner for the physical P4 card, including mount/provisioning.
// Nonblocking: concurrent local HTTP/staging work reports busy, never queues.
#include <atomic>
#include <string>
namespace agon::extender::local_sd {
inline std::atomic_flag mediaOwned = ATOMIC_FLAG_INIT;
class MediaLease {
  bool held_;

public:
  MediaLease() : held_(!mediaOwned.test_and_set()) {}
  ~MediaLease() {
    if (held_)
      mediaOwned.clear();
  }
  MediaLease(const MediaLease &) = delete;
  MediaLease &operator=(const MediaLease &) = delete;
  explicit operator bool() const { return held_; }
};
inline std::string mediaFold(std::string s) {
  for (char &c : s)
    if (c >= 'A' && c <= 'Z')
      c += 32;
  return s;
}
inline bool privateSpool(const std::string &path) {
  auto p = mediaFold(path);
  return p == "/tmp/extender/spool" || p.rfind("/tmp/extender/spool/", 0) == 0;
}
inline bool spoolAncestor(const std::string &path) {
  auto p = mediaFold(path);
  return p == "/" || p == "/tmp" || p == "/tmp/extender";
}
// Caller MUST hold MediaLease. No formatter, unmount or recovery-file deletion.
bool prepareSpool(std::string &vfsDirectory) noexcept;
} // namespace agon::extender::local_sd
