// QUAL-003/N04y: P4-only scheduling experiment. Logical/display cadence remains
// unchanged; this bounds queue waiting between CPU drawing opportunities.
#pragma once
#include <cstdint>
namespace agon::extender::display {
constexpr std::uint32_t drawingTimerPeriodUs(std::uint32_t logical, bool twice) {
 return twice ? logical/2+logical%2 : logical;
}
}
