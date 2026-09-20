// Process-task-owned processed input FIFO. The caller supplies already mapped
// keycode/raw ASCII, stock virtual key and modifiers; no PS/2 or browser layout
// translation happens here. Drain each item through the retained VDP effects
// before the next item, because its event queue coalesces mutable key state.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

namespace agon::extender::input {
struct ProcessedKey {
  std::uint8_t keycode{}, modifiers{}, virtual_key{}, down{}, ascii{};
  bool query{}; // synthetic stock &99 request, not a new physical transition
};
class ProcessedKeyboard final {
 public:
  static constexpr std::size_t capacity = 16;
  bool push(ProcessedKey event) noexcept {
    if (event.virtual_key > 248 || event.down > 1 || size_ == capacity)
      return false;
    queue_[(head_ + size_) % capacity] = event;
    ++size_;
    return true;
  }
  bool pop(ProcessedKey &event) noexcept {
    if (!size_) return false;
    event = queue_[head_]; head_ = (head_ + 1) % capacity; --size_;
    if (!event.query) {
      modifiers_ = event.modifiers;
      held_[event.virtual_key] = event.down;
    }
    return true;
  }
  std::size_t size() const noexcept { return size_; }
  std::uint8_t modifiers() const noexcept { return modifiers_; }
  bool isDown(unsigned key) const noexcept { return key < held_.size() && held_[key]; }
  bool queryFault() const noexcept { return query_fault_; }
  void pushQuery(ProcessedKey event) noexcept {
    event.query = true;
    if (!push(event)) query_fault_ = true;
  }
  void reset() noexcept {
    head_ = size_ = 0; modifiers_ = 0; held_.fill(false); query_fault_ = false;
  }
 private:
  std::array<ProcessedKey, capacity> queue_{};
  std::size_t head_{}, size_{};
  std::uint8_t modifiers_{};
  std::array<bool, 249> held_{};
  bool query_fault_{};
};
inline ProcessedKeyboard &processedKeyboard() noexcept {
  static ProcessedKeyboard keyboard;
  return keyboard;
}
}  // namespace agon::extender::input
