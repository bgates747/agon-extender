// PORT-003 Phase A architecture compatibility boundary.
//
// vdp-gl all-the-plots assumes Xtensa coprocessor state helpers even in its
// common bitmapped controller. ESP32-P4 is RISC-V and its floating-point path
// does not use that Xtensa save/restore contract. These compile-only no-ops are
// force-included only by the contract-canary environment. They must be removed
// or replaced by a reviewed runtime policy before transformed bitmap execution
// is qualified.
#pragma once

#if defined(__riscv) && defined(__cplusplus)
#include <stdint.h>

inline uint32_t xthal_get_cpenable() noexcept { return 0; }
inline void xthal_set_cpenable(uint32_t) noexcept {}
inline void xthal_save_cp0(uint32_t *) noexcept {}
inline void xthal_restore_cp0(uint32_t const *) noexcept {}
#endif
