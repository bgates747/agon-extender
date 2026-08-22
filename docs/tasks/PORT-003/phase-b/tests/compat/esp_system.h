// Parse-only ESP-IDF declarations required by upstream fabutils.h.
#pragma once
#include <cstdlib>
#include <cstdint>
using gpio_num_t = int;
using gpio_mode_t = int;
using intr_handler_t = void (*)(void *);
using intr_handle_t = void *;
constexpr gpio_num_t GPIO_NUM_MAX = 64;
