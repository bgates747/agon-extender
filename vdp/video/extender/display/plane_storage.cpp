// See plane_storage.hpp.
//
// This file replaces classic vdp-gl VGA allocation and viewport ownership;
// those routines are fingerprinted as replace-platform in PORT-003 Phase B.
// The allocate-all/commit/release-old order is intentional and must not be
// simplified into destructive reconfiguration.
#include "extender/display/plane_storage.hpp"

#include <cstring>

namespace agon::extender::display {
namespace {

PlaneView mutableView(std::uint8_t *data, std::size_t size,
                      std::size_t stride) noexcept {
  return {data, data == nullptr ? 0 : size, data == nullptr ? 0 : stride};
}

ConstPlaneView constView(std::uint8_t const *data, std::size_t size,
                         std::size_t stride) noexcept {
  return {data, data == nullptr ? 0 : size, data == nullptr ? 0 : stride};
}

}  // namespace

PlaneStorage::PlaneStorage(Allocator allocator) noexcept : allocator_(allocator) {}

PlaneStorage::~PlaneStorage() { release(); }

PlaneStorage::PlaneStorage(PlaneStorage &&other) noexcept
    : allocator_(other.allocator_),
      mode_(other.mode_),
      planes_{other.planes_[0], other.planes_[1]},
      drawing_index_(other.drawing_index_),
      visible_index_(other.visible_index_),
      plane_size_(other.plane_size_),
      stride_(other.stride_),
      configured_(other.configured_) {
  other.planes_[0] = nullptr;
  other.planes_[1] = nullptr;
  other.drawing_index_ = 0;
  other.visible_index_ = 0;
  other.plane_size_ = 0;
  other.stride_ = 0;
  other.configured_ = false;
}

PlaneStorage &PlaneStorage::operator=(PlaneStorage &&other) noexcept {
  if (this == &other) return *this;
  release();
  allocator_ = other.allocator_;
  mode_ = other.mode_;
  planes_[0] = other.planes_[0];
  planes_[1] = other.planes_[1];
  drawing_index_ = other.drawing_index_;
  visible_index_ = other.visible_index_;
  plane_size_ = other.plane_size_;
  stride_ = other.stride_;
  configured_ = other.configured_;
  other.planes_[0] = nullptr;
  other.planes_[1] = nullptr;
  other.drawing_index_ = 0;
  other.visible_index_ = 0;
  other.plane_size_ = 0;
  other.stride_ = 0;
  other.configured_ = false;
  return *this;
}

ConfigureResult PlaneStorage::configure(ModeDescriptor const &mode) noexcept {
  if (mode.width == 0 || mode.height == 0) {
    return ConfigureResult::InvalidDimensions;
  }
  if ((mode.native_save_sync_bits & 0x3F) != 0) {
    return ConfigureResult::InvalidSyncBits;
  }
  if (allocator_.allocate == nullptr || allocator_.deallocate == nullptr) {
    return ConfigureResult::InvalidAllocator;
  }
  std::size_t new_stride = 0;
  CodecResult codec = NativePixelCodec::rowStride(mode.format, mode.width, new_stride);
  if (codec == CodecResult::InvalidFormat) return ConfigureResult::InvalidFormat;
  if (codec != CodecResult::Ok) return ConfigureResult::SizeOverflow;
  std::size_t new_size = 0;
  codec = NativePixelCodec::planeSize(mode.format, mode.width, mode.height, new_size);
  if (codec == CodecResult::InvalidFormat) return ConfigureResult::InvalidFormat;
  if (codec != CodecResult::Ok) return ConfigureResult::SizeOverflow;

  auto *first = static_cast<std::uint8_t *>(
      allocator_.allocate(allocator_.context, new_size));
  if (first == nullptr) return ConfigureResult::FirstPlaneAllocationFailed;
  std::memset(first, 0, new_size);
  std::uint8_t *second = nullptr;
  if (mode.double_buffered) {
    second = static_cast<std::uint8_t *>(
        allocator_.allocate(allocator_.context, new_size));
    if (second == nullptr) {
      allocator_.deallocate(allocator_.context, first);
      return ConfigureResult::SecondPlaneAllocationFailed;
    }
    std::memset(second, 0, new_size);
  }

  std::uint8_t *old_first = planes_[0];
  std::uint8_t *old_second = planes_[1];
  planes_[0] = first;
  planes_[1] = second;
  mode_ = mode;
  visible_index_ = 0;
  drawing_index_ = mode.double_buffered ? 1 : 0;
  plane_size_ = new_size;
  stride_ = new_stride;
  configured_ = true;
  if (old_second != nullptr) allocator_.deallocate(allocator_.context, old_second);
  if (old_first != nullptr) allocator_.deallocate(allocator_.context, old_first);
  return ConfigureResult::Ok;
}

bool PlaneStorage::swapPlanes() noexcept {
  if (!configured_ || !mode_.double_buffered) return false;
  std::uint8_t temporary = visible_index_;
  visible_index_ = drawing_index_;
  drawing_index_ = temporary;
  return true;
}

void PlaneStorage::release() noexcept {
  if (planes_[1] != nullptr && allocator_.deallocate != nullptr) {
    allocator_.deallocate(allocator_.context, planes_[1]);
  }
  if (planes_[0] != nullptr && allocator_.deallocate != nullptr) {
    allocator_.deallocate(allocator_.context, planes_[0]);
  }
  planes_[0] = nullptr;
  planes_[1] = nullptr;
  drawing_index_ = 0;
  visible_index_ = 0;
  plane_size_ = 0;
  stride_ = 0;
  configured_ = false;
  mode_ = {};
}

bool PlaneStorage::configured() const noexcept { return configured_; }
ModeDescriptor const &PlaneStorage::mode() const noexcept { return mode_; }

PlaneView PlaneStorage::drawingPlane() noexcept {
  return mutableView(planes_[drawing_index_], plane_size_, stride_);
}

PlaneView PlaneStorage::visiblePlane() noexcept {
  return mutableView(planes_[visible_index_], plane_size_, stride_);
}

ConstPlaneView PlaneStorage::drawingPlane() const noexcept {
  return constView(planes_[drawing_index_], plane_size_, stride_);
}

ConstPlaneView PlaneStorage::visiblePlane() const noexcept {
  return constView(planes_[visible_index_], plane_size_, stride_);
}

std::uint8_t PlaneStorage::drawingPlaneIdentity() const noexcept {
  return drawing_index_;
}

std::uint8_t PlaneStorage::visiblePlaneIdentity() const noexcept {
  return visible_index_;
}

}  // namespace agon::extender::display
