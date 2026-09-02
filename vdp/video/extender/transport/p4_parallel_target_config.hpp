// Production ESP32-P4 forward-parallel endpoint plan.
//
// These constants contain no r01 branch.  PORT-008-D002 established that the
// same endpoint tuple is used by the present qualification circuit and the
// intended circuit.  Electrical qualification remains outside this file.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace agon::extender::transport {

struct P4ParallelTargetConfig final {
  inline static constexpr std::array<int, 8> kDataPins{
      22, 12, 23, 11, 32, 10, 33, 9};
  inline static constexpr int kClockPin = 14;
  inline static constexpr int kValidPin = 13;
  inline static constexpr int kForwardBankAEnablePin = 15;
  inline static constexpr int kForwardBankBEnablePin = 17;
  inline static constexpr int kReturnBankEnablePin = 21;
  inline static constexpr int kReadyPin = 20;

  // The pinned PARLIO API requires a declared external clock frequency even
  // though this slave uses a divide-by-one external source.  10 MHz is the
  // predecessor receiver's conservative configured ceiling, not a measured
  // r01 frequency or a qualified production timing claim.
  inline static constexpr std::uint32_t kConfiguredExternalClockHz =
      10'000'000;
};

constexpr bool p4ParallelTargetPinsAreUnique() noexcept {
  std::array<int, 14> const pins{
      P4ParallelTargetConfig::kDataPins[0],
      P4ParallelTargetConfig::kDataPins[1],
      P4ParallelTargetConfig::kDataPins[2],
      P4ParallelTargetConfig::kDataPins[3],
      P4ParallelTargetConfig::kDataPins[4],
      P4ParallelTargetConfig::kDataPins[5],
      P4ParallelTargetConfig::kDataPins[6],
      P4ParallelTargetConfig::kDataPins[7],
      P4ParallelTargetConfig::kClockPin,
      P4ParallelTargetConfig::kValidPin,
      P4ParallelTargetConfig::kForwardBankAEnablePin,
      P4ParallelTargetConfig::kForwardBankBEnablePin,
      P4ParallelTargetConfig::kReturnBankEnablePin,
      P4ParallelTargetConfig::kReadyPin,
  };
  for (std::size_t left = 0; left < pins.size(); ++left) {
    for (std::size_t right = left + 1; right < pins.size(); ++right) {
      if (pins[left] == pins[right]) return false;
    }
  }
  return true;
}

static_assert(p4ParallelTargetPinsAreUnique(),
              "parallel data, handshake, and control pins must not overlap");

}  // namespace agon::extender::transport
