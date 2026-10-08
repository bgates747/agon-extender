// HDMI02-P02: task-owned decorated snapshot and SDK scaler. No live renderer
// pointers cross the PPA wait; lifecycle caller joins output before reset.
#pragma once
#include <cstddef>
#include <cstdint>
namespace agon::extender::display {
class HdmiPpaScaler {
 public:
  bool initialize();
  void reset();
  std::uint8_t *source() { return source_; }
  bool scale(std::uint8_t *output, std::size_t bytes);
 private:
  std::uint8_t *source_{};
  void *client_{};
};
}
