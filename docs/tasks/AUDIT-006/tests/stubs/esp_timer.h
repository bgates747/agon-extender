// Deterministic host clock for the actual diagnostic scope/JSON adapter.
#pragma once
#include <cstdint>
extern std::int64_t diagnostic_test_now;
inline std::int64_t esp_timer_get_time() { return diagnostic_test_now; }
