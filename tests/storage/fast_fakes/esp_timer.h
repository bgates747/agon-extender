#pragma once
#include <cstdint>
inline std::int64_t fakeTime=1000;
inline std::int64_t esp_timer_get_time(){return ++fakeTime;}
