#pragma once

namespace agon::extender::port {
// P4 compatibility boundary for inherited Agon VDP v2.16.0 / vdp-gl
// all-the-plots casts (QUAL-003 RX09 N02-N06). Check before narrowing; ordered
// comparisons also reject NaN and infinities. Preserve stock truncation for
// representable values. Remove when upstream supplies equivalent guards.
inline bool fitsTruncatedInt16(float value) noexcept {
    return value > -32769.0f && value < 32768.0f;
}
inline bool fitsTruncatedInt32(float value) noexcept {
    // Binary32 has no representable fraction just below INT32_MIN.
    return value >= -2147483648.0f && value < 2147483648.0f;
}
inline bool fitsBitmapByteCount(double value) noexcept {
    return value >= 0.0 && value < 4294967296.0;
}
}
