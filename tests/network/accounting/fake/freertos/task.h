#pragma once
#include <cstdint>
using TaskHandle_t=void*;
constexpr int pdPASS=1;
#define pdMS_TO_TICKS(n) (n)
int xTaskCreate(void(*)(void*),const char*,unsigned,void*,unsigned,TaskHandle_t*);
void vTaskDelay(unsigned);
void vTaskDelete(void*);
