// PORT-003 Phase B transactional logical-plane ownership contract.
//
// The allocator is injected both to select P4 memory capabilities later and
// to prove every allocation-failure boundary on the host. Configuration must
// never destroy the last valid mode until all replacement planes exist.
#pragma once

#include <cstddef>
#include <cstdint>

#include "extender/display/native_pixel_codec.hpp"

namespace agon::extender::display {

struct ModeDescriptor {
  std::size_t width;
  std::size_t height;
  NativePixelFormat format;
  bool double_buffered;
  std::uint8_t native_save_sync_bits;
};

struct Allocator {
  void *context;
  void *(*allocate)(void *context, std::size_t size);
  void (*deallocate)(void *context, void *allocation);
};

enum class ConfigureResult : std::uint8_t {
  Ok,
  InvalidDimensions,
  InvalidFormat,
  InvalidSyncBits,
  SizeOverflow,
  InvalidAllocator,
  FirstPlaneAllocationFailed,
  SecondPlaneAllocationFailed,
};

struct PlaneView {
  std::uint8_t *data;
  std::size_t size;
  std::size_t stride;
};

struct ConstPlaneView {
  std::uint8_t const *data;
  std::size_t size;
  std::size_t stride;
};

class PlaneStorage final {
 public:
  explicit PlaneStorage(Allocator allocator) noexcept;
  ~PlaneStorage();

  PlaneStorage(PlaneStorage const &) = delete;
  PlaneStorage &operator=(PlaneStorage const &) = delete;
  PlaneStorage(PlaneStorage &&other) noexcept;
  PlaneStorage &operator=(PlaneStorage &&other) noexcept;

  ConfigureResult configure(ModeDescriptor const &mode) noexcept;
  void release() noexcept;

  bool configured() const noexcept;
  ModeDescriptor const &mode() const noexcept;
  PlaneView drawingPlane() noexcept;
  PlaneView visiblePlane() noexcept;
  ConstPlaneView drawingPlane() const noexcept;
  ConstPlaneView visiblePlane() const noexcept;

 private:
  Allocator allocator_;
  ModeDescriptor mode_{};
  std::uint8_t *planes_[2]{};
  std::size_t plane_size_{};
  std::size_t stride_{};
  bool configured_{};
};

}  // namespace agon::extender::display
