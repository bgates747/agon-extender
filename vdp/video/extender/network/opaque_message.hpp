// PORT-006 bounded opaque-message ownership contract.
//
// The network owner may observe segment addresses and a token, but it may not
// parse, copy, or retain their application meaning. A successful provider
// acquisition transfers exactly one release obligation into this move-only
// lease. The destructor reports an abandoned lease as failed.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace agon::extender::network {

inline constexpr std::size_t kOpaqueMessageMaximumSegments = 2;
inline constexpr std::size_t kOpaqueMessageMaximumBytes = 2'359'328;

enum class OpaqueAcquireResult : std::uint8_t {
  Acquired,
  NoNewMessage,
  Unavailable,
  Invalid,
};

enum class OpaqueReleaseDisposition : std::uint8_t {
  Sent,
  Failed,
  Disconnected,
};

struct OpaqueMessageSegment {
  std::uint8_t const *data{};
  std::size_t size{};
};

struct OpaqueMessageView {
  std::uint64_t token{};
  std::array<OpaqueMessageSegment, kOpaqueMessageMaximumSegments> segments{};
  std::size_t segment_count{};
  std::size_t total_bytes{};

  bool valid() const noexcept;
};

class OpaqueMessageLease final {
 public:
  using ReleaseFunction = void (*)(void *, std::uint64_t,
                                   OpaqueReleaseDisposition) noexcept;

  OpaqueMessageLease() noexcept = default;
  ~OpaqueMessageLease();

  OpaqueMessageLease(OpaqueMessageLease const &) = delete;
  OpaqueMessageLease &operator=(OpaqueMessageLease const &) = delete;
  OpaqueMessageLease(OpaqueMessageLease &&other) noexcept;
  OpaqueMessageLease &operator=(OpaqueMessageLease &&other) noexcept;

  bool assign(std::uint64_t token, OpaqueMessageSegment const *segments,
              std::size_t segment_count, void *context,
              ReleaseFunction release) noexcept;
  bool valid() const noexcept;
  OpaqueMessageView view() const noexcept;
  void release(OpaqueReleaseDisposition disposition) noexcept;

 private:
  OpaqueMessageView view_{};
  void *context_{};
  ReleaseFunction release_{};
};

class OpaqueMessageProvider {
 public:
  virtual ~OpaqueMessageProvider() = default;
  virtual OpaqueAcquireResult tryAcquireAfter(
      std::uint64_t last_successful_token,
      OpaqueMessageLease &lease) noexcept = 0;
};

}  // namespace agon::extender::network
