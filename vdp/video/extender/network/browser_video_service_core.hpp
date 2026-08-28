// Platform-neutral one-client/one-credit service core.
//
// The ESP-IDF adapter owns sockets and task execution. This core owns only the
// bounded client, credit, and opaque-lease transitions so those rules can be
// qualified on the host without an Ethernet stack.
#pragma once

#include <cstdint>
#include <mutex>

#include "extender/network/opaque_message.hpp"

namespace agon::extender::network {

using VideoClientId = int;
inline constexpr VideoClientId kNoVideoClient = -1;

enum class VideoClientState : std::uint8_t {
  Disconnected,
  Idle,
  CreditPending,
  Sending,
};

enum class VideoConnectResult : std::uint8_t { Accepted, Busy };
enum class VideoCreditResult : std::uint8_t {
  Accepted,
  InvalidClient,
  ProtocolError,
};
enum class VideoPrepareResult : std::uint8_t {
  Prepared,
  NoCredit,
  NoNewMessage,
  Disconnected,
  ProviderUnavailable,
  ProviderInvalid,
};

struct BrowserVideoServiceMetrics {
  std::uint32_t clients_accepted{};
  std::uint32_t clients_refused{};
  std::uint32_t credits_accepted{};
  std::uint32_t protocol_errors{};
  std::uint32_t sends_completed{};
  std::uint32_t sends_failed{};
  std::uint32_t disconnect_releases{};
  std::uint32_t provider_unavailable{};
  std::uint32_t provider_invalid{};
};

class BrowserVideoServiceCore final {
 public:
  VideoConnectResult connect(VideoClientId client) noexcept;
  VideoCreditResult requestFrame(VideoClientId client) noexcept;
  VideoPrepareResult tryPrepare(OpaqueMessageProvider &provider) noexcept;

  // The ESP-IDF HTTP task is the sole caller while a synchronous send is in
  // progress. Socket close callbacks execute on that same task, so pointers
  // copied from this view cannot race a close callback in the target adapter.
  OpaqueMessageView sendingView(VideoClientId client) const noexcept;
  void complete(VideoClientId client,
                OpaqueReleaseDisposition disposition) noexcept;
  bool disconnect(VideoClientId client) noexcept;

  VideoClientState state() const noexcept;
  VideoClientId client() const noexcept;
  std::uint64_t lastSuccessfulToken() const noexcept;
  BrowserVideoServiceMetrics metrics() const noexcept;

 private:
  static void increment(std::uint32_t &counter) noexcept;

  mutable std::mutex mutex_;
  VideoClientState state_{VideoClientState::Disconnected};
  VideoClientId client_{kNoVideoClient};
  std::uint64_t last_successful_token_{};
  OpaqueMessageLease sending_{};
  BrowserVideoServiceMetrics metrics_{};
};

}  // namespace agon::extender::network
