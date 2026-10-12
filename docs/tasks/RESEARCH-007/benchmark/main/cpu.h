#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
void cpu_signal(const uint8_t *src, uint8_t *dst, unsigned width, unsigned rows);
void cpu_linear(const uint8_t *src, uint8_t *dst, unsigned width, unsigned rows);
void cpu_reorder(const uint8_t *src, uint8_t *dst, unsigned bytes);
#ifdef __cplusplus
}
#endif
