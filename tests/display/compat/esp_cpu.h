// Host-side synthetic cycle counter; scheduling tests check units/ordering only.
#pragma once
#include <chrono>
#include <cstdint>
inline uint32_t esp_cpu_get_cycle_count() {
  return static_cast<uint32_t>(std::chrono::steady_clock::now().time_since_epoch().count());
}
