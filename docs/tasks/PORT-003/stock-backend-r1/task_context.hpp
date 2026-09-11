// R1 selects synchronous, task-context rendering only. The unchanged upstream
// common renderer still contains an Xtensa ISR-only branch. Reject that branch
// if accidentally called; these declarations do not implement P4 ISR/FPU support.
#pragma once
#ifndef AGON_EXTENDER_STOCK_ROWS_PROOF
#error This boundary belongs only to the nondeployable native-row proof
#endif
#include <cstdint>
#include <cstdlib>
[[noreturn]] inline std::uint32_t xthal_get_cpenable() { std::abort(); }
[[noreturn]] inline void xthal_set_cpenable(std::uint32_t) { std::abort(); }
[[noreturn]] inline void xthal_save_cp0(std::uint32_t *) { std::abort(); }
[[noreturn]] inline void xthal_restore_cp0(std::uint32_t const *) { std::abort(); }
