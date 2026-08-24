// PORT-003 Phase E host compiler boundary for retained common rendering.
#pragma once

#include <cmath>
#include <cstdarg>
#include <cstdio>
#include <cstdint>
#include <cstring>

#include "esp_heap_caps.h"

inline std::uint32_t xthal_get_cpenable() noexcept { return 0; }
inline void xthal_set_cpenable(std::uint32_t) noexcept {}
inline void xthal_save_cp0(std::uint32_t *) noexcept {}
inline void xthal_restore_cp0(std::uint32_t const *) noexcept {}
