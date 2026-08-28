#include "extender/network/opaque_message.hpp"

#include <limits>

namespace agon::extender::network {

bool OpaqueMessageView::valid() const noexcept {
  if (segment_count == 0 || segment_count > segments.size() ||
      total_bytes == 0 || total_bytes > kOpaqueMessageMaximumBytes)
    return false;
  std::size_t observed = 0;
  for (std::size_t index = 0; index < segment_count; ++index) {
    auto const &segment = segments[index];
    if (segment.data == nullptr || segment.size == 0 ||
        observed > std::numeric_limits<std::size_t>::max() - segment.size)
      return false;
    observed += segment.size;
  }
  return observed == total_bytes;
}

OpaqueMessageLease::~OpaqueMessageLease() {
  release(OpaqueReleaseDisposition::Failed);
}

OpaqueMessageLease::OpaqueMessageLease(OpaqueMessageLease &&other) noexcept
    : view_(other.view_), context_(other.context_), release_(other.release_) {
  other.view_ = {};
  other.context_ = nullptr;
  other.release_ = nullptr;
}

OpaqueMessageLease &OpaqueMessageLease::operator=(
    OpaqueMessageLease &&other) noexcept {
  if (this == &other) return *this;
  release(OpaqueReleaseDisposition::Failed);
  view_ = other.view_;
  context_ = other.context_;
  release_ = other.release_;
  other.view_ = {};
  other.context_ = nullptr;
  other.release_ = nullptr;
  return *this;
}

bool OpaqueMessageLease::assign(
    std::uint64_t token, OpaqueMessageSegment const *segments,
    std::size_t segment_count, void *context,
    ReleaseFunction release_function) noexcept {
  if (valid() || segments == nullptr || context == nullptr ||
      release_function == nullptr || segment_count == 0 ||
      segment_count > view_.segments.size())
    return false;

  OpaqueMessageView candidate{};
  candidate.token = token;
  candidate.segment_count = segment_count;
  for (std::size_t index = 0; index < segment_count; ++index) {
    candidate.segments[index] = segments[index];
    if (candidate.total_bytes >
        std::numeric_limits<std::size_t>::max() - segments[index].size)
      return false;
    candidate.total_bytes += segments[index].size;
  }
  if (!candidate.valid()) return false;

  view_ = candidate;
  context_ = context;
  release_ = release_function;
  return true;
}

bool OpaqueMessageLease::valid() const noexcept {
  return release_ != nullptr && view_.valid();
}

OpaqueMessageView OpaqueMessageLease::view() const noexcept {
  return valid() ? view_ : OpaqueMessageView{};
}

void OpaqueMessageLease::release(
    OpaqueReleaseDisposition disposition) noexcept {
  if (release_ == nullptr) return;
  auto const callback = release_;
  auto *const context = context_;
  auto const token = view_.token;
  view_ = {};
  context_ = nullptr;
  release_ = nullptr;
  callback(context, token, disposition);
}

}  // namespace agon::extender::network
