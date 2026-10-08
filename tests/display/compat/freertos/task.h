#pragma once
// Extend the retained scheduling substrate with the standard FreeRTOS type
// used by the shared worker allocator. Target timing is tested on hardware.
#include_next <freertos/task.h>
using TaskFunction_t = void (*)(void *);
