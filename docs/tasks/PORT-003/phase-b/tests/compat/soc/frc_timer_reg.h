// Parse-only removed classic ESP32 timer surface. Runtime access must abort.
#pragma once
#include <cstdint>
[[noreturn]] std::uintptr_t agon_extender_removed_frc_timer_register();
#define FRC_TIMER_LOAD_REG(index) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_CTRL_REG(index) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_COUNT_REG(index) agon_extender_removed_frc_timer_register()
#define FRC_TIMER_ENABLE 0
#define REG_WRITE(reg, value) ((void)(reg), (void)(value))
#define REG_READ(reg) ((void)(reg), std::uint32_t{0})
