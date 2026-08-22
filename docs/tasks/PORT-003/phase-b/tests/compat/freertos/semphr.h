// PORT-003 host-only semaphore declarations; unused by synchronous fixtures.
#pragma once

#include "FreeRTOS.h"

inline BaseType_t xSemaphoreTake(SemaphoreHandle_t, TickType_t) { return pdTRUE; }
inline BaseType_t xSemaphoreGive(SemaphoreHandle_t) { return pdTRUE; }
