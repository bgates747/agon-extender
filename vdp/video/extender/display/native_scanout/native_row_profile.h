// One rotating block every 16 physical frames. The tuple describes the worst
// sampled render call in this mode binding. These are elapsed core-1 cycles
// including lock waits/preemption; they do not measure the DMA interrupt phase.
#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    uint32_t generation, samples, frame, block, source_rows;
    uint32_t total_cycles, lock_wait_cycles, stock_cycles, expand_cycles;
} agon_native_row_profile_t;
void agon_native_get_row_profile(agon_native_row_profile_t *out);
#ifdef __cplusplus
}
#endif
