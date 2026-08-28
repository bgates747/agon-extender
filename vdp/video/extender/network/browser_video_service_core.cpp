#include "extender/network/browser_video_service_core.hpp"

#include <limits>
#include <utility>

namespace agon::extender::network {

void BrowserVideoServiceCore::increment(std::uint32_t &counter) noexcept {
  if (counter != std::numeric_limits<std::uint32_t>::max()) ++counter;
}

VideoConnectResult BrowserVideoServiceCore::connect(
    VideoClientId client) noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  if (client < 0 || state_ != VideoClientState::Disconnected) {
    increment(metrics_.clients_refused);
    return VideoConnectResult::Busy;
  }
  client_ = client;
  last_successful_token_ = 0;
  state_ = VideoClientState::Idle;
  increment(metrics_.clients_accepted);
  return VideoConnectResult::Accepted;
}

VideoCreditResult BrowserVideoServiceCore::requestFrame(
    VideoClientId client) noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  if (client != client_ || state_ == VideoClientState::Disconnected)
    return VideoCreditResult::InvalidClient;
  if (state_ != VideoClientState::Idle) {
    increment(metrics_.protocol_errors);
    return VideoCreditResult::ProtocolError;
  }
  state_ = VideoClientState::CreditPending;
  increment(metrics_.credits_accepted);
  return VideoCreditResult::Accepted;
}

VideoPrepareResult BrowserVideoServiceCore::tryPrepare(
    OpaqueMessageProvider &provider) noexcept {
  VideoClientId reserved_client = kNoVideoClient;
  std::uint64_t last_token = 0;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    if (state_ != VideoClientState::CreditPending)
      return VideoPrepareResult::NoCredit;
    reserved_client = client_;
    last_token = last_successful_token_;
    state_ = VideoClientState::Sending;
  }

  OpaqueMessageLease acquired;
  auto const result = provider.tryAcquireAfter(last_token, acquired);

  OpaqueMessageLease abandoned;
  VideoPrepareResult outcome = VideoPrepareResult::ProviderInvalid;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    if (state_ != VideoClientState::Sending || client_ != reserved_client) {
      abandoned = std::move(acquired);
      outcome = VideoPrepareResult::Disconnected;
    } else if (result == OpaqueAcquireResult::Acquired && acquired.valid()) {
      sending_ = std::move(acquired);
      outcome = VideoPrepareResult::Prepared;
    } else if (result == OpaqueAcquireResult::NoNewMessage) {
      state_ = VideoClientState::CreditPending;
      outcome = VideoPrepareResult::NoNewMessage;
    } else if (result == OpaqueAcquireResult::Unavailable) {
      state_ = VideoClientState::Idle;
      increment(metrics_.provider_unavailable);
      outcome = VideoPrepareResult::ProviderUnavailable;
    } else {
      state_ = VideoClientState::Idle;
      increment(metrics_.provider_invalid);
      outcome = VideoPrepareResult::ProviderInvalid;
    }
  }
  if (abandoned.valid())
    abandoned.release(OpaqueReleaseDisposition::Disconnected);
  return outcome;
}

OpaqueMessageView BrowserVideoServiceCore::sendingView(
    VideoClientId client) const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  if (state_ != VideoClientState::Sending || client != client_)
    return {};
  return sending_.view();
}

void BrowserVideoServiceCore::complete(
    VideoClientId client, OpaqueReleaseDisposition disposition) noexcept {
  OpaqueMessageLease completed;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    if (state_ != VideoClientState::Sending || client != client_ ||
        !sending_.valid())
      return;
    auto const token = sending_.view().token;
    completed = std::move(sending_);
    if (disposition == OpaqueReleaseDisposition::Sent) {
      last_successful_token_ = token;
      increment(metrics_.sends_completed);
    } else {
      increment(metrics_.sends_failed);
    }
    state_ = VideoClientState::Idle;
  }
  completed.release(disposition);
}

bool BrowserVideoServiceCore::disconnect(VideoClientId client) noexcept {
  OpaqueMessageLease abandoned;
  bool released = false;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    if (client != client_ || state_ == VideoClientState::Disconnected)
      return false;
    released = sending_.valid();
    abandoned = std::move(sending_);
    state_ = VideoClientState::Disconnected;
    client_ = kNoVideoClient;
    last_successful_token_ = 0;
    if (released) increment(metrics_.disconnect_releases);
  }
  if (abandoned.valid())
    abandoned.release(OpaqueReleaseDisposition::Disconnected);
  return true;
}

VideoClientState BrowserVideoServiceCore::state() const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  return state_;
}

VideoClientId BrowserVideoServiceCore::client() const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  return client_;
}

std::uint64_t BrowserVideoServiceCore::lastSuccessfulToken() const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  return last_successful_token_;
}

BrowserVideoServiceMetrics BrowserVideoServiceCore::metrics() const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  return metrics_;
}

}  // namespace agon::extender::network
