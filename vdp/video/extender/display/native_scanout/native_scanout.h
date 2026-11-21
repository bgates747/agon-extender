// P4 DSI adapter. Pixel callbacks run in the core-1 worker. Unbind joins any
// in-flight callback before returning the caller's native controller to it.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "esp_lcd_types.h"

#ifdef __cplusplus
extern "C" {
#endif
// slot_black starts true only for a fully cleared, DMA-visible slot. The
// renderer leaves it true only when the complete slot is still known black.
// True on both entry and exit means no pixel writes or cache sync are needed.
typedef bool (*agon_native_render_t)(void *, uint8_t *, unsigned first_y, unsigned rows,
                                     unsigned width, unsigned height, unsigned slot, uint32_t frame, bool *slot_black);
typedef void (*agon_native_wake_t)(void *);
esp_err_t agon_native_bind(esp_lcd_panel_handle_t panel, void *context,
                           agon_native_render_t render, agon_native_wake_t draw_wake);
void agon_native_unbind(esp_lcd_panel_handle_t panel);
bool agon_native_failed(esp_lcd_panel_handle_t panel);
esp_err_t agon_dpi_stop(esp_lcd_panel_handle_t panel);

enum agon_native_fault {
    AGON_NATIVE_OK, AGON_NATIVE_SEQUENCE, AGON_NATIVE_INVALID, AGON_NATIVE_QUEUE,
    AGON_NATIVE_BUDGET, AGON_NATIVE_RENDER, AGON_NATIVE_CACHE, AGON_NATIVE_UNDERRUN
};
typedef struct {
    uint32_t epoch, width, height, frames, blocks, ready, ticks, max_queue;
    uint32_t max_refill_us, min_lead_us, max_queue_us, max_render_us, max_sync_us;
    uint32_t min_draw_gap_us, worst_frame, worst_block, worst_queue_us, worst_render_us, worst_sync_us;
    uint32_t fault, fault_frame, fault_block, fault_elapsed_us;
    uint32_t fault_queue_us, fault_render_us, fault_sync_us;
    uint32_t underruns, invalid, rejected, histogram[17];
} agon_native_stats_t;
// min_lead_us is SW ready -> next block callback. It includes interrupt
// latency and is not a hardware fetch timestamp. UINT32_MAX = no observation.
void agon_native_get_stats(agon_native_stats_t *out);
bool agon_native_get_last_fault(agon_native_stats_t *out);
#ifdef __cplusplus
}
#endif
