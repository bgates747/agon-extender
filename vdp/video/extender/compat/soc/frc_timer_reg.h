// PORT-003 Phase A compatibility shim for an inherited vdp-gl include.
//
// vdp-gl all-the-plots includes the classic ESP32 FRC1 register header from
// broad fabutils.h even though the retained displaycontroller.cpp does not use
// that timer. ESP32-P4 has no such header or peripheral contract. The macros
// below keep the unused inline declarations parseable and route any accidental
// runtime use to a project-owned fail-fast function; they do not emulate FRC1.
#pragma once

#include <cstdint>
#include "soc/soc.h"

[[noreturn]] std::uintptr_t agon_extender_removed_frc_timer_register();

#define FRC_TIMER_LOAD_REG(timer) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_CTRL_REG(timer) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_COUNT_REG(timer) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_ENABLE 0U
#define FRC_TIMER_PRESCALER_1 0U
#define FRC_TIMER_PRESCALER_16 0U
#define FRC_TIMER_PRESCALER_256 0U
