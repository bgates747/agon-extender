#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct { uint32_t blocks, frames, invalid, underruns, sequence_errors, refills, total_us, max_us, over_budget, cache_errors, min_interval, copy_us; } strip_probe_stats;
void strip_probe_read(strip_probe_stats *out);
typedef struct { uint32_t copy_max_us, compose_max_us, compose_total_us, late, overlap, faults, min_ready_lead_us, preflight_strips; } strip_async_stats;
void strip_async_read(strip_async_stats *out);
// First observed fault is retained even if stopping DMA later causes underrun.
enum { STRIP_FAULT_NONE, STRIP_FAULT_CACHE, STRIP_FAULT_BUDGET,
       STRIP_FAULT_OVERLAP, STRIP_FAULT_SUBMIT, STRIP_FAULT_LATE,
       STRIP_FAULT_INVALID, STRIP_FAULT_UNDERRUN, STRIP_FAULT_SEQUENCE };
typedef struct { uint32_t first_fault, first_error, queued, queue_wait_max_us; } strip_fault_stats;
void strip_fault_read(strip_fault_stats *out);
// Task-context preflight, after the background is initialized, before panel start.
int strip_prime_and_check(void);

#ifdef __cplusplus
}
#endif
