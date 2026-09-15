#pragma once
#include <cmath>
#include <cstdint>

namespace agon::extender::port {
// Stock v2.16.0 types.h casts negative float results directly to unsigned.
// Xtensa and RISC-V disagree there (QUAL-003 Rally r03). Fixed formats are
// signed values stored as bits. Validate before any integral cast, truncate
// toward zero, then use defined signed-integer -> unsigned conversion.
// Invalid/nonfinite results have no portable stock oracle: reject the entire
// buffered transform, preserving its old destination. No clamping or invented
// coordinates. Keep this seam until upstream supplies equivalent semantics.
inline bool encodeFixed(float input, bool width16, int shift,
                        std::uint32_t &output) noexcept {
    const float scaled = std::ldexp(input, shift);
    if (!std::isfinite(scaled)) return false;
    const float truncated = std::trunc(scaled);
    const float lower = width16 ? -32768.0f : -2147483648.0f;
    const float upper = width16 ? 32768.0f : 2147483648.0f;
    // Upper bound is exclusive: INT32_MAX rounds upward when stored as float.
    if (truncated < lower || truncated >= upper) return false;
    const auto signedValue = static_cast<std::int32_t>(truncated);
    output = width16 ? static_cast<std::uint16_t>(signedValue)
                     : static_cast<std::uint32_t>(signedValue);
    return true;
}
}
