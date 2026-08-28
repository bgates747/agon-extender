#include "extender/web/browser_video_provider.hpp"

#include <limits>
#include <utility>

namespace agon::extender::web {
namespace {

constexpr std::uint8_t kRgb888PixelFormat = 1;
constexpr std::uint8_t kFullFrameFlag = 1U << 0U;
constexpr std::uint8_t kPresentBoundaryFlag = 1U << 1U;

void put16(std::uint8_t *destination, std::uint16_t value) noexcept {
  destination[0] = static_cast<std::uint8_t>(value);
  destination[1] = static_cast<std::uint8_t>(value >> 8U);
}

void put32(std::uint8_t *destination, std::uint32_t value) noexcept {
  destination[0] = static_cast<std::uint8_t>(value);
  destination[1] = static_cast<std::uint8_t>(value >> 8U);
  destination[2] = static_cast<std::uint8_t>(value >> 16U);
  destination[3] = static_cast<std::uint8_t>(value >> 24U);
}

}  // namespace

BrowserVideoProvider::BrowserVideoProvider(
    display::PresentationSnapshotPool &pool) noexcept
    : pool_(pool) {}

BrowserVideoProvider::~BrowserVideoProvider() {
  display::PresentationSnapshotLease abandoned;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    abandoned = std::move(snapshot_);
    active_token_ = 0;
  }
}

void BrowserVideoProvider::increment(std::uint32_t &counter) noexcept {
  if (counter != std::numeric_limits<std::uint32_t>::max()) ++counter;
}

bool BrowserVideoProvider::encodeHeader(
    display::ImmutableSnapshotView const &snapshot) noexcept {
  constexpr std::size_t bytes_per_pixel = 3;
  if (snapshot.data == nullptr || snapshot.width == 0 || snapshot.height == 0 ||
      snapshot.width > display::kPresentationSnapshotMaximumWidth ||
      snapshot.height > display::kPresentationSnapshotMaximumHeight ||
      snapshot.width > std::numeric_limits<std::uint16_t>::max() ||
      snapshot.height > std::numeric_limits<std::uint16_t>::max() ||
      snapshot.stride_bytes != snapshot.width * bytes_per_pixel ||
      snapshot.payload_bytes != snapshot.stride_bytes * snapshot.height ||
      snapshot.payload_bytes > display::kPresentationSnapshotBytesPerSlot ||
      snapshot.stride_bytes > std::numeric_limits<std::uint32_t>::max() ||
      snapshot.payload_bytes > std::numeric_limits<std::uint32_t>::max() ||
      snapshot.present_period_us > std::numeric_limits<std::uint32_t>::max())
    return false;

  header_ = {};
  header_[0] = 'E';
  header_[1] = 'V';
  header_[2] = 'F';
  header_[3] = '1';
  header_[4] = 1;
  header_[5] = static_cast<std::uint8_t>(kEvf1HeaderBytes);
  header_[6] = kRgb888PixelFormat;
  header_[7] = kFullFrameFlag | kPresentBoundaryFlag;
  put32(header_.data() + 8,
        static_cast<std::uint32_t>(snapshot.generation));
  put16(header_.data() + 12,
        static_cast<std::uint16_t>(snapshot.width));
  put16(header_.data() + 14,
        static_cast<std::uint16_t>(snapshot.height));
  put32(header_.data() + 16,
        static_cast<std::uint32_t>(snapshot.stride_bytes));
  put32(header_.data() + 20,
        static_cast<std::uint32_t>(snapshot.payload_bytes));
  put32(header_.data() + 24,
        static_cast<std::uint32_t>(snapshot.present_period_us));
  return true;
}

network::OpaqueAcquireResult BrowserVideoProvider::tryAcquireAfter(
    std::uint64_t last_successful_token,
    network::OpaqueMessageLease &lease) noexcept {
  if (lease.valid()) return network::OpaqueAcquireResult::Invalid;

  std::lock_guard<std::mutex> guard(mutex_);
  if (!pool_.enabled() || snapshot_.valid())
    return network::OpaqueAcquireResult::Unavailable;
  if (!pool_.tryAcquireLatest(last_successful_token, snapshot_)) {
    increment(metrics_.no_new_message);
    return network::OpaqueAcquireResult::NoNewMessage;
  }

  auto const view = snapshot_.view();
  if (!encodeHeader(view)) {
    snapshot_.release();
    increment(metrics_.invalid_snapshot);
    return network::OpaqueAcquireResult::Invalid;
  }

  network::OpaqueMessageSegment const segments[] = {
      {header_.data(), header_.size()},
      {view.data, view.payload_bytes},
  };
  active_token_ = view.generation;
  if (!lease.assign(active_token_, segments, 2, this, &releaseOpaque)) {
    snapshot_.release();
    active_token_ = 0;
    increment(metrics_.invalid_snapshot);
    return network::OpaqueAcquireResult::Invalid;
  }
  increment(metrics_.acquired);
  return network::OpaqueAcquireResult::Acquired;
}

void BrowserVideoProvider::releaseOpaque(
    void *context, std::uint64_t token,
    network::OpaqueReleaseDisposition disposition) noexcept {
  static_cast<BrowserVideoProvider *>(context)->release(token, disposition);
}

void BrowserVideoProvider::release(
    std::uint64_t token,
    network::OpaqueReleaseDisposition disposition) noexcept {
  display::PresentationSnapshotLease completed;
  {
    std::lock_guard<std::mutex> guard(mutex_);
    if (!snapshot_.valid() || active_token_ != token) return;
    completed = std::move(snapshot_);
    active_token_ = 0;
    if (disposition == network::OpaqueReleaseDisposition::Sent)
      increment(metrics_.released_sent);
    else if (disposition == network::OpaqueReleaseDisposition::Disconnected)
      increment(metrics_.released_disconnected);
    else
      increment(metrics_.released_failed);
  }
}

BrowserVideoProviderMetrics BrowserVideoProvider::metrics() const noexcept {
  std::lock_guard<std::mutex> guard(mutex_);
  return metrics_;
}

}  // namespace agon::extender::web
