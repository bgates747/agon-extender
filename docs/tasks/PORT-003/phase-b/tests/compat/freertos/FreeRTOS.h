// PORT-003 host-only compatibility types; see ../README.md.
#pragma once

#include <cstddef>
#include <cstdint>

#define IRAM_ATTR
#define portMAX_DELAY UINT32_MAX
#define pdTRUE 1
#define pdFALSE 0
#define pdMS_TO_TICKS(value) static_cast<std::uint32_t>(value)

using BaseType_t = int;
using UBaseType_t = unsigned int;
using TickType_t = std::uint32_t;
using TaskHandle_t = void *;
using SemaphoreHandle_t = void *;

struct PhaseBHostQueue;
using QueueHandle_t = PhaseBHostQueue *;
