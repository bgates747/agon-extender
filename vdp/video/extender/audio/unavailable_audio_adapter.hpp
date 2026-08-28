// PORT-003 Phase F deferred PORT-004 audio binding.
//
// The classic SoundGenerator must not enter this P4 image. These definitions
// close references from the retained header-defined parser and buffer cleanup
// while physical ingress is disconnected. They intentionally make no audio
// command, acknowledgement, timing, or output claim.
#pragma once

#include <cstdint>

inline std::uint8_t playNote(std::uint8_t, std::uint8_t, std::uint16_t,
                             std::uint16_t) noexcept {
  return 0;
}

inline std::uint8_t clearSample(std::uint16_t) noexcept { return 0; }
inline void resetSamples() noexcept {}

inline void VDUStreamProcessor::vdu_sys_audio() {}
