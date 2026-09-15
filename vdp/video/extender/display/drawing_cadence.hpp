// QUAL-003/N04y: P4-only scheduling experiment. Logical/display cadence remains
// unchanged; this bounds queue waiting between CPU drawing opportunities.
#pragma once
#include <cstdint>
namespace agon::extender::display {
constexpr std::uint32_t drawingTimerPeriodUs(std::uint32_t logical, unsigned opportunities) {
 return opportunities ? logical/opportunities+(logical%opportunities!=0) : 0;
}
}
