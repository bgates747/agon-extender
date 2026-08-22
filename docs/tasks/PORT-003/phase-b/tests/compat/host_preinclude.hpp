// PORT-003 host compiler boundary for immutable upstream common renderer.
#pragma once

#include <cmath>
#include <cstdarg>
#include <cstdio>
#include <cstdint>
#include <cstring>

#include "esp_heap_caps.h"

// Upstream wraps transformed bitmap execution in Xtensa coprocessor state
// helpers. A POSIX host has no equivalent state contract; the actual floating
// point operation is executed normally and qualified by the fixtures.
inline std::uint32_t xthal_get_cpenable() noexcept { return 0; }
inline void xthal_set_cpenable(std::uint32_t) noexcept {}
inline void xthal_save_cp0(std::uint32_t *) noexcept {}
inline void xthal_restore_cp0(std::uint32_t const *) noexcept {}
