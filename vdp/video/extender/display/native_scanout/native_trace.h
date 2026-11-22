// Experimental startup trace. Times are microseconds from the retirement that
// requests the selected top block. UINT32_MAX denotes an unobserved milestone.
#pragma once
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
#include <stdbool.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

enum nr_trace_event {
    NR_T_RETIRE_12, NR_T_RETIRE_13, NR_T_RETIRE_14, // relative tail for either carrier
    NR_T_ENQUEUED, NR_T_DEQUEUED,
    NR_T_WAKE_LOCK_WAIT, NR_T_WAKE_LOCK_HELD, NR_T_WAKE_BEGIN, NR_T_WAKE_END,
    NR_T_GATE_WAIT, NR_T_GATE_OPEN, NR_T_GATE_BYPASS,
    NR_T_READ_LOCK_WAIT, NR_T_READ_LOCK_HELD, NR_T_OWNED, NR_T_BOUND,
    NR_T_RENDER_BEGIN, NR_T_RENDER_END, NR_T_CLEAR, NR_T_ALREADY_BLACK,
    NR_T_CACHE_BEGIN, NR_T_CACHE_END, NR_T_CACHE_SKIP,
    NR_T_PUBLISH_WAIT, NR_T_PUBLISH_HELD, NR_T_PUBLISHED, NR_T_DECISION, NR_T_COUNT
};
enum nr_trace_row_phase { NR_ROW_NONE, NR_ROW_ACTIVE, NR_ROW_INACTIVE, NR_ROW_LOCK, NR_ROW_COMPOSE, NR_ROW_EXPAND };
enum nr_trace_admission { NR_ADMIT_UNKNOWN, NR_ADMIT_UNBOUND_BLACK, NR_ADMIT_INACTIVE, NR_ADMIT_LIVE };
enum nr_trace_site {
    NR_SITE_REARM, NR_SITE_RETIRE, NR_SITE_SUCCESSOR, NR_SITE_ENQUEUE,
    NR_SITE_INVALID, NR_SITE_UNDERRUN, NR_SITE_OWNERSHIP, NR_SITE_PUBLISH
};

typedef struct {
    uint32_t stamp[NR_T_COUNT], row_cursor;
    uint32_t target_armed, target_frame, limit_us;
    uint32_t epoch, retired, queue_depth, slot_frame, slot_block, slot_ready;
    uint32_t rearmed, fault, site, fault_frame, fault_block;
} agon_native_trace_t;

// Classify the stock readiness latch even if the worker has advanced past
// the initial ACTIVE cursor. A live row of black pixels is still admitted.
static inline enum nr_trace_admission nr_admission(uint32_t cursor, const uint32_t *stamp)
{
    switch (cursor >> 16) {
    case NR_ROW_ACTIVE: case NR_ROW_LOCK: case NR_ROW_COMPOSE: case NR_ROW_EXPAND:
        return NR_ADMIT_LIVE;
    case NR_ROW_INACTIVE:
        return NR_ADMIT_INACTIVE;
    default:
        if (stamp[NR_T_CLEAR] != UINT32_MAX || stamp[NR_T_ALREADY_BLACK] != UINT32_MAX)
            return NR_ADMIT_UNBOUND_BLACK;
        return NR_ADMIT_UNKNOWN;
    }
}

// Returns the sealed first boot-epoch decision, even after panel replacement.
bool agon_native_get_startup_trace(agon_native_trace_t *out);
uint32_t *agon_native_trace_row_cursor(void);
static inline void agon_native_trace_row(uint32_t *cursor, enum nr_trace_row_phase phase, unsigned row)
{
    __atomic_signal_fence(__ATOMIC_SEQ_CST);
    __atomic_store_n(cursor, ((uint32_t)phase << 16) | (row & 0xffff), __ATOMIC_RELAXED);
    __atomic_signal_fence(__ATOMIC_SEQ_CST);
}
#ifdef __cplusplus
}
#endif
#endif
