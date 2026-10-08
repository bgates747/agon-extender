#pragma once
#include <stdint.h>
typedef struct { uint32_t blocks, frames, invalid, underruns, sequence_errors, refills, total_us, max_us, over_budget, cache_errors, min_interval, copy_us; } strip_probe_stats;
void strip_probe_read(strip_probe_stats *out);
typedef struct { uint32_t copy_max_us, compose_max_us, compose_total_us, late, overlap, faults, min_ready_lead_us, preflight_strips; } strip_async_stats;
void strip_async_read(strip_async_stats *out);
// Task-context preflight, after the background is initialized, before panel start.
int strip_prime_and_check(void);
