// P4 binds original rendering to task context only. The retained common source
// contains a classic Xtensa ISR/FPU branch; entering it is a binding error.
// These abort boundaries provide no dummy ISR or coprocessor implementation.
#pragma once
#ifndef AGON_EXTENDER_STOCK_RUNTIME
#error This boundary requires the original-controller P4 runtime selection
#endif
#ifdef __cplusplus
#include <cstdint>
#include <cstdlib>
[[noreturn]] inline std::uint32_t xthal_get_cpenable() { std::abort(); }
[[noreturn]] inline void xthal_set_cpenable(std::uint32_t) { std::abort(); }
[[noreturn]] inline void xthal_save_cp0(std::uint32_t *) { std::abort(); }
[[noreturn]] inline void xthal_restore_cp0(std::uint32_t const *) { std::abort(); }
#endif // __cplusplus: the hybrid build also force-includes this header in C.
