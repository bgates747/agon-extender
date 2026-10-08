// Task/ISR state for panel-owned framebuffers. The adapter serializes every
// access with its portMUX; same-core publication makes the driver selection
// and the later submission metadata store safe across callback interruption.
#pragma once
namespace agon::extender::display {
class HdmiBufferOwnership {
 public:
  bool pending() const noexcept { return pending_; }
  unsigned submittedIndex() const noexcept { return submitted_; }
  unsigned writable(bool doubled) const noexcept { return doubled ? 1u - front_ : front_; }
  void submitted(unsigned index) noexcept { submitted_ = index; pending_ = true; }
  void frameComplete() noexcept {
    if (pending_) { front_ = submitted_; pending_ = false; }
  }
  void reset() noexcept { front_ = submitted_ = 0; pending_ = false; }
 private:
  unsigned front_{}, submitted_{};
  bool pending_{};
};
} // namespace agon::extender::display
