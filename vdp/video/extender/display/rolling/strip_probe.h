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
// Breakdown of the first over-budget refill, not unrelated cumulative maxima.
// submit_to_callback includes descriptor setup, DMA2D admission, DMA and IRQ
// delivery; it is deliberately not advertised as hardware transfer time.
typedef struct { uint32_t available, queue_us, prepare_us, source_cache_us,
    submit_to_callback_us, finish_us, driver_phases_valid, descriptor_us,
    admission_us, channel_setup_us, dma_and_irq_us, handoff_us; } strip_budget_stats;
void strip_budget_read(strip_budget_stats *out);
// Pinned rolling-only fbcpy derivative. Ignore every other copy client's tag.
// Stages: descriptors prepared, channels picked, DMA about to start, driver EOF.
void agon_scanout_copy_phase(void *context, unsigned phase);
// Task-context preflight, after the background is initialized, before panel start.
int strip_prime_and_check(void);

#ifdef __cplusplus
}
#endif
