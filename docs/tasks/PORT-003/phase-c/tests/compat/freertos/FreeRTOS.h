// PORT-003 Phase C host-only FreeRTOS types for concurrent queue/wait tests.
#pragma once

#include <cstddef>
#include <cstdint>

using BaseType_t = int;
using UBaseType_t = unsigned;
using TickType_t = std::uint32_t;

struct PhaseCHostQueue;
struct PhaseCHostTask;
using QueueHandle_t = PhaseCHostQueue *;
using TaskHandle_t = PhaseCHostTask *;
using SemaphoreHandle_t = void *;

constexpr BaseType_t pdTRUE = 1;
constexpr BaseType_t pdFALSE = 0;
constexpr BaseType_t pdPASS = 1;
constexpr TickType_t portMAX_DELAY = UINT32_MAX;
constexpr int tskNO_AFFINITY = -1;

#define pdMS_TO_TICKS(value) (static_cast<TickType_t>(value))
#define IRAM_ATTR
