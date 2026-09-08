#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

// PORT-009 one-shot diagnostic, not a VDU packet parser. A substring match
// never counts as success. Even bytes/errors arriving after PASS invalidate it.
class UartForwardMatch {
 public:
  enum class State { waiting, receiving, pass, fail };
  UartForwardMatch(const uint8_t* expected, size_t length, uint32_t armed)
      : expected_(expected), length_(length), armed_(armed) {}

  void error(const char* reason) {
    if (state_ != State::fail) reason_ = reason;
    state_ = State::fail;
  }
  void feed(const uint8_t* bytes, size_t size, uint32_t now) {
    if (!size) return;
    poll(now);  // Data arriving after a deadline cannot rescue a timed-out run.
    if (state_ == State::waiting) {
      state_ = State::receiving;
      first_ = now;
    }
    last_ = now;
    for (size_t i = 0; i < size; ++i) {
      if (count_ < received_.size()) received_[count_] = bytes[i];
      if (count_ >= length_) error("extra bytes");
      else if (bytes[i] != expected_[count_]) error("byte mismatch");
      ++count_;
    }
  }
  void poll(uint32_t now) {
    if (state_ == State::waiting && uint32_t(now - armed_) >= 180000)
      error("no data within 180 seconds");
    if (state_ != State::receiving) return;
    if (count_ == length_ && uint32_t(now - last_) >= 200)
      state_ = State::pass;
    else if (uint32_t(now - first_) >= 3000)
      error("incomplete message within 3 seconds");
  }
  State state() const { return state_; }
  const char* reason() const { return reason_; }
  size_t count() const { return count_; }
  size_t stored() const { return count_ < received_.size() ? count_ : received_.size(); }
  const uint8_t* bytes() const { return received_.data(); }

 private:
  const uint8_t* expected_;
  size_t length_;
  uint32_t armed_, first_ = 0, last_ = 0;
  State state_ = State::waiting;
  const char* reason_ = "none";
  size_t count_ = 0;
  std::array<uint8_t, 64> received_{};
};
