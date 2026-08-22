// PORT-003 host-only task declarations; no task is created in Phase B.
#pragma once

#include "FreeRTOS.h"

inline TaskHandle_t xTaskGetCurrentTaskHandle() { return nullptr; }
inline std::uint32_t ulTaskNotifyTake(BaseType_t, TickType_t) { return 0; }
inline BaseType_t xTaskNotifyGive(TaskHandle_t) { return pdTRUE; }
inline void vTaskNotifyGiveFromISR(TaskHandle_t, BaseType_t *) {}
inline void vTaskDelete(TaskHandle_t) {}
inline void taskYIELD() {}
