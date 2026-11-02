#pragma once
#include <cstdint>
using portMUX_TYPE=int;
using BaseType_t=int;
using UBaseType_t=unsigned;
using TaskHandle_t=void *;
using TaskFunction_t=void(*)(void *);
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(x) (void)(x)
#define portEXIT_CRITICAL(x) (void)(x)
#define pdPASS 1
#define tskNO_AFFINITY -1
