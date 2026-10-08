#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
unsigned stock_probe_population(unsigned frame);
void stock_probe_compose(uint8_t *strip, unsigned first_y, unsigned rows, unsigned frame);
#ifdef __cplusplus
}
#endif
