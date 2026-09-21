// Browser status only: the VDU owner publishes; HTTP never reads a live Canvas.
// Atomic fields and a generation check reject a snapshot spanning a mode change.
#pragma once
#include <atomic>
#include <cstdint>
namespace agon::extender::display {
struct ModeStatus {
  unsigned mode, width, height, colors, refresh_hz;
  bool double_buffered;
};
class ModeStatusStore {
 public:
  void invalidate() noexcept { valid_.store(false); }
  void publish(ModeStatus value) noexcept {
    generation_.fetch_add(1);
    mode_=value.mode; width_=value.width; height_=value.height;
    colors_=value.colors; refresh_=value.refresh_hz; double_=value.double_buffered;
    valid_=true;
    generation_.fetch_add(1);
  }
  bool read(ModeStatus &value) const noexcept {
    const auto before=generation_.load();
    if ((before & 1U) || !valid_.load()) return false;
    value={mode_.load(),width_.load(),height_.load(),colors_.load(),
           refresh_.load(),double_.load()};
    return valid_.load() && before==generation_.load();
  }
 private:
  std::atomic<unsigned> generation_{0},mode_{0},width_{0},height_{0},colors_{0},refresh_{0};
  std::atomic<bool> valid_{false},double_{false};
};
inline ModeStatusStore modeStatus;
}
