// PORT-003 adapter from immutable presentation snapshots to EVF1 opaque bytes.
//
// This is the only production component that knows both snapshot metadata and
// EVF1. PORT-006 receives a two-segment opaque lease and never sees pixels as
// anything other than immutable bytes.
#pragma once

#include <array>
#include <cstdint>
#include <mutex>

#include "extender/display/presentation_snapshot_pool.hpp"
#include "extender/network/opaque_message.hpp"

namespace agon::extender::web {

inline constexpr std::size_t kEvf1HeaderBytes = 32;

struct BrowserVideoProviderMetrics {
  std::uint32_t acquired{};
  std::uint32_t no_new_message{};
  std::uint32_t invalid_snapshot{};
  std::uint32_t released_sent{};
  std::uint32_t released_failed{};
  std::uint32_t released_disconnected{};
};

class BrowserVideoProvider final
    : public network::OpaqueMessageProvider {
 public:
  explicit BrowserVideoProvider(
      display::PresentationSnapshotPool &pool) noexcept;
  ~BrowserVideoProvider() override;

  network::OpaqueAcquireResult tryAcquireAfter(
      std::uint64_t last_successful_token,
      network::OpaqueMessageLease &lease) noexcept override;

  BrowserVideoProviderMetrics metrics() const noexcept;

 private:
  static void releaseOpaque(
      void *context, std::uint64_t token,
      network::OpaqueReleaseDisposition disposition) noexcept;
  static void increment(std::uint32_t &counter) noexcept;
  bool encodeHeader(display::ImmutableSnapshotView const &snapshot) noexcept;
  void release(std::uint64_t token,
               network::OpaqueReleaseDisposition disposition) noexcept;

  display::PresentationSnapshotPool &pool_;
  mutable std::mutex mutex_;
  std::array<std::uint8_t, kEvf1HeaderBytes> header_{};
  display::PresentationSnapshotLease snapshot_{};
  std::uint64_t active_token_{};
  BrowserVideoProviderMetrics metrics_{};
};

}  // namespace agon::extender::web
