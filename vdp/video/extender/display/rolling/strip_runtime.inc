/* SPRITE-001 r04: experimental full-application DMA2D rolling scanout.
 * Fixed DSI descriptors cycle through fixed internal-SRAM buffers. A single pinned
 * Espressif fbcpy handle has at most one transaction outstanding: its static
 * transaction configuration is NOT a concurrent multi-handle API. Allocate in
 * task context only. CPU cache ownership is explicitly handed to/from DMA.
 * Late generation detection aborts scanout. The ISR can detect a miss after
 * DMA has started the next block, so this is not a zero-corruption guarantee.
 */
#include "strip_probe.h"
#include "strip_config.h"
#include "bridge.h"
#include "esp_async_fbcpy.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_rom_sys.h"
#include <stdatomic.h>
#include <string.h>
// Maximum-size SRAM is retained; live geometry changes only after shutdown.
static unsigned strip_width=STRIP_WIDTH, strip_height=STRIP_HEIGHT, strip_blocks=STRIP_BLOCKS;
unsigned agon_scanout_width(void) {return strip_width;}
unsigned agon_scanout_height(void) {return strip_height;}
static atomic_uint strip_blocks_done, strip_frames_done, strip_invalid;
static atomic_uint strip_underruns, strip_sequence_errors;
static atomic_uint strip_refills, strip_total_us, strip_max_us, strip_over_budget;
static atomic_uint strip_copy_us, strip_copy_max, strip_compose_max, strip_compose_total;
static atomic_uint strip_cache_errors, strip_min_interval = UINT32_MAX;
static atomic_uint strip_late, strip_overlap, strip_faults, strip_preflight;
static atomic_uint strip_min_lead = UINT32_MAX;
static atomic_uint strip_ready_tag[STRIP_SLOTS];
static int64_t strip_ready_time[STRIP_SLOTS];
static atomic_bool strip_busy;
static atomic_bool strip_stopping;
static atomic_uint strip_first_fault, strip_first_error, strip_queued, strip_queue_wait_max;
// HDMI02-O: three slots permit one active copy plus one waiting refill. A
//32-row scanout interval is ~1030us, less than the unchanged1600us guard.
// Aborting on every busy arrival discarded safe slack in the third slot.
// Protect only queue ownership, never memcpy/cache/composition, against nested
// DMA IRQs. There is still exactly one fbcpy transaction/descriptor set in use.
static portMUX_TYPE strip_mux = portMUX_INITIALIZER_UNLOCKED;
typedef struct { unsigned slot, block, tag; int64_t begin; } strip_request;
static strip_request strip_pending;
static bool strip_pending_valid;
static unsigned strip_ordinal;
static bool strip_last_pending;
static uint8_t *strip_buffers[STRIP_SLOTS], *strip_background;
static size_t strip_bytes;
static uint8_t *strip_backgrounds[2];
static agon_scanout_frame strip_scene;
static unsigned strip_front_index;
static int strip_slot_left[STRIP_SLOTS], strip_slot_top[STRIP_SLOTS];
static int strip_slot_width[STRIP_SLOTS], strip_slot_height[STRIP_SLOTS];
unsigned agon_scanout_front(void) {return strip_front_index;}
static int64_t strip_previous_done;
static esp_async_fbcpy_handle_t strip_copier;
static dw_gdma_channel_handle_t strip_channel;
static strip_request strip_job;
static int64_t strip_copy_begin;

static void strip_max(atomic_uint *p, unsigned value) {
    if (value > atomic_load(p)) atomic_store(p, value);
}
static void strip_note_fault(unsigned reason, unsigned error) {
    // The sentinel excludes concurrent writers; readers report pending as0.
    unsigned expected=STRIP_FAULT_NONE;
    if(atomic_compare_exchange_strong(&strip_first_fault,&expected,UINT32_MAX)) {
        atomic_store(&strip_first_error,error);
        atomic_store(&strip_first_fault,reason);
    }
}
static void strip_note_underrun(void) {
    strip_note_fault(STRIP_FAULT_UNDERRUN,0);
    atomic_fetch_add(&strip_underruns,1);
}
static void strip_abort(unsigned reason, unsigned error) {
    strip_note_fault(reason,error);
    atomic_fetch_add(&strip_faults, 1);
    if (!atomic_load(&strip_stopping) && strip_channel)
        dw_gdma_channel_enable_ctrl(strip_channel, false);
}
static bool strip_sync(void *p, size_t size, unsigned flags) {
    esp_err_t error=esp_cache_msync(p, size, flags);
    if (error == ESP_OK) return true;
    atomic_fetch_add(&strip_cache_errors, 1);
    strip_abort(STRIP_FAULT_CACHE,error);
    return false;
}
static void strip_start(strip_request request);
static void strip_release_job(void) {
    strip_request next={};bool dispatch=false;
    portENTER_CRITICAL_SAFE(&strip_mux);
    if(strip_pending_valid && !atomic_load(&strip_faults) && !atomic_load(&strip_stopping)) {
        next=strip_pending;dispatch=true; // busy stays set across handoff
    } else atomic_store(&strip_busy,false);
    strip_pending_valid=false;
    portEXIT_CRITICAL_SAFE(&strip_mux);
    if(dispatch)strip_start(next);
}
static void strip_finish(void) {
    unsigned elapsed = esp_timer_get_time() - strip_copy_begin;
    atomic_fetch_add(&strip_copy_us, elapsed);
    strip_max(&strip_copy_max, elapsed);
    if (!atomic_load(&strip_faults) && !atomic_load(&strip_stopping)) {
        uint8_t *dst = strip_buffers[strip_job.slot];
        if (!strip_sync(dst, strip_bytes, ESP_CACHE_MSYNC_FLAG_DIR_M2C)) {
            strip_release_job();
            return;
        }
        int64_t compose = esp_timer_get_time();
        agon_scanout_compose(dst, strip_job.block * (STRIP_ROWS), STRIP_ROWS);
        unsigned duration = esp_timer_get_time() - compose;
        atomic_fetch_add(&strip_compose_total, duration);
        strip_max(&strip_compose_max, duration);
        if (!strip_sync(dst, strip_bytes, ESP_CACHE_MSYNC_FLAG_DIR_C2M)) {
            strip_release_job();
            return;
        }
    }
    // Negative control is a deliberate post-composition hold; the independent
    // duration gate must detect it even when it delays the DSI callback itself.
    if (STRIP_INJECT_LATE_TAG && strip_job.tag == STRIP_INJECT_LATE_TAG)
        esp_rom_delay_us(STRIP_REFILL_LIMIT_US + 2000);
    elapsed = esp_timer_get_time() - strip_job.begin;
    atomic_fetch_add(&strip_refills, 1);
    atomic_fetch_add(&strip_total_us, elapsed);
    strip_max(&strip_max_us, elapsed);
    if (elapsed > STRIP_REFILL_LIMIT_US) {
        atomic_fetch_add(&strip_over_budget, 1);
        strip_abort(STRIP_FAULT_BUDGET,elapsed);
    }
    // Publish only after the full retirement-to-ready deadline, including queue
    // wait, has passed its check. Never publish a late or cancelled strip.
    if(!atomic_load(&strip_faults) && !atomic_load(&strip_stopping)) {
        strip_ready_time[strip_job.slot]=esp_timer_get_time();
        atomic_store(&strip_ready_tag[strip_job.slot],strip_job.tag);
    }
    strip_release_job();
}
static bool strip_copy_done(esp_async_fbcpy_handle_t handle,
                            esp_async_fbcpy_event_data_t *event, void *context) {
    (void)handle; (void)event; (void)context;
    strip_finish();
    return false;
}
static void strip_fill(unsigned slot, unsigned block, unsigned generation) {
    strip_request request={slot,block,generation*strip_blocks+block,esp_timer_get_time()};
    bool dispatch=false,overflow=false;
    portENTER_CRITICAL_SAFE(&strip_mux);
    if (!atomic_load(&strip_faults) && !atomic_load(&strip_stopping)) {
        if(!atomic_load(&strip_busy)) {atomic_store(&strip_busy,true);dispatch=true;}
        else if(!strip_pending_valid) {
            strip_pending=request;strip_pending_valid=true;
            atomic_fetch_add(&strip_queued,1);
        } else overflow=true;
    }
    portEXIT_CRITICAL_SAFE(&strip_mux);
    if(overflow) {
        atomic_fetch_add(&strip_overlap, 1);
        strip_abort(STRIP_FAULT_OVERLAP,request.tag);
    }
    if(dispatch)strip_start(request);
}
static void strip_start(strip_request request) {
    strip_job=request;strip_copy_begin=esp_timer_get_time();
    unsigned slot=request.slot,block=request.block;
    strip_max(&strip_queue_wait_max,strip_copy_begin-request.begin);
    if(atomic_load(&strip_faults) || atomic_load(&strip_stopping)) {strip_release_job();return;}
    atomic_store(&strip_ready_tag[slot], UINT32_MAX);
    if(block==0) {
        strip_scene=agon_scanout_latch();
        strip_background=strip_backgrounds[strip_scene.background];
    }
    uint8_t *dst = strip_buffers[slot];
    if(strip_slot_left[slot]!=strip_scene.left || strip_slot_top[slot]!=strip_scene.top ||
       strip_slot_width[slot]!=strip_scene.width || strip_slot_height[slot]!=strip_scene.height) {
        memset(dst,0,strip_bytes);
        strip_slot_left[slot]=strip_scene.left;strip_slot_top[slot]=strip_scene.top;
        strip_slot_width[slot]=strip_scene.width;strip_slot_height[slot]=strip_scene.height;
    }
    unsigned rows = STRIP_ROWS, first_y = block * rows;
    unsigned top = first_y > (unsigned)strip_scene.top ? first_y : (unsigned)strip_scene.top;
    unsigned end = strip_scene.top + strip_scene.height;
    unsigned bottom = first_y + rows < end ? first_y + rows : end;
    // A recycled slot may previously have held logical pixels at these rows.
    // Borders at the left/right never contain sprites and stay zero.
    for (unsigned row = 0; row < rows; ++row)
        if (first_y + row < (unsigned)strip_scene.top || first_y + row >= end)
            memset(dst + row * strip_width * 3 + strip_scene.left * 3, 0, strip_scene.width * 3);
    if (!strip_sync(dst, strip_bytes,
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_INVALIDATE)) {
        strip_release_job();
        return;
    }
    if (!strip_scene.width || bottom <= top) { strip_finish(); return; }
    // The persistent panel source can be written by the other CPU in single-
    // buffered mode. Clean this aligned source strip before DMA2D reads it.
    // This retains single-buffer scanout tearing semantics, not frame atomicity.
    if(!strip_sync(strip_background+first_y*strip_width*3, strip_bytes, ESP_CACHE_MSYNC_FLAG_DIR_C2M)) {
        strip_release_job();return;
    }
    esp_async_fbcpy_trans_desc_t transaction = {
        .src_buffer = strip_background, .dst_buffer = dst,
        .src_buffer_size_x = strip_width, .src_buffer_size_y = strip_height,
        .dst_buffer_size_x = strip_width, .dst_buffer_size_y = rows,
        .src_offset_x = strip_scene.left, .src_offset_y = top,
        .dst_offset_x = strip_scene.left, .dst_offset_y = top - first_y,
        .copy_size_x = strip_scene.width, .copy_size_y = bottom - top,
        // Full color-space/type ID, not the deprecated zero-valued pixel enum.
        .pixel_format_unique_id = {.color_type_id = LCD_COLOR_FMT_RGB888},
    };
    // The helper consumes this stack descriptor synchronously into its retained
    // DMA descriptors. Those descriptors and our single job remain live to EOF.
    // Pinned IDF dma2d.c frees the previous RX/TX channels before user EOF.
    // Dispatching one waiting refill from that callback is therefore supported;
    // do not introduce another fbcpy handle sharing its static transaction config.
    esp_err_t error=esp_async_fbcpy(strip_copier, &transaction, strip_copy_done, NULL);
    if (error != ESP_OK) {
        strip_abort(STRIP_FAULT_SUBMIT,error);
        strip_release_job();
    }
}
static esp_err_t strip_reserve(void) {
    // AUTO reserves maximum-size848 slots before task/asset allocation fragments
    // SRAM. Retain them across both carrier sizes; live stride is separate.
    const size_t bytes = STRIP_WIDTH * STRIP_ROWS * 3;
    for(unsigned i=0;i<STRIP_SLOTS;++i) {
        if(strip_buffers[i])continue;
        strip_buffers[i]=heap_caps_aligned_calloc(64,1,bytes,
            MALLOC_CAP_INTERNAL|MALLOC_CAP_DMA|MALLOC_CAP_8BIT);
        if(!strip_buffers[i])return ESP_ERR_NO_MEM;
    }
    return ESP_OK;
}
static void strip_stop(void) {
    atomic_store(&strip_stopping,true);
    strip_channel=NULL;
}
static esp_err_t strip_shutdown(void) {
    // Called after DSI DMA deletion, before the driver frees its PSRAM planes.
    strip_stop();
    int64_t deadline = esp_timer_get_time() + 1000000;
    while (atomic_load(&strip_busy) && esp_timer_get_time() < deadline) vTaskDelay(1);
    if (atomic_load(&strip_busy)) return ESP_ERR_TIMEOUT;
    if (strip_copier) {
        ESP_RETURN_ON_ERROR(esp_async_fbcpy_uninstall(strip_copier), "rolling", "DMA2D teardown");
        strip_copier = NULL;
    }
#ifndef AGON_EXTENDER_HDMI_AUTO
    for (unsigned i=0; i<STRIP_SLOTS; ++i) {
        heap_caps_free(strip_buffers[i]);strip_buffers[i]=NULL;
    }
#endif
    strip_bytes=0;strip_background=NULL;
    strip_pending_valid=false;
    strip_backgrounds[0]=strip_backgrounds[1]=NULL;
    return ESP_OK;
}
static esp_err_t strip_configure(uint8_t *background0,uint8_t *background1, size_t bytes,
                                 unsigned width,unsigned height) {
    assert(width<=STRIP_WIDTH && height<=STRIP_HEIGHT && height%STRIP_ROWS==0);
    strip_width=width;strip_height=height;strip_blocks=height/STRIP_ROWS;
    assert(STRIP_ROLLING && strip_blocks >= 2 && strip_blocks <= 15 && strip_blocks % STRIP_SLOTS == 0);
    assert(bytes == strip_width * strip_height * 3 && bytes % (strip_blocks * 64) == 0);
    assert(!strip_bytes && !strip_copier);
    atomic_uint *counters[]={&strip_blocks_done,&strip_frames_done,&strip_invalid,
        &strip_underruns,&strip_sequence_errors,&strip_refills,&strip_total_us,
        &strip_max_us,&strip_over_budget,&strip_copy_us,&strip_copy_max,
        &strip_compose_max,&strip_compose_total,&strip_cache_errors,&strip_late,
        &strip_overlap,&strip_faults,&strip_preflight,&strip_first_fault,&strip_first_error,
        &strip_queued,&strip_queue_wait_max};
    for(unsigned i=0;i<sizeof(counters)/sizeof(counters[0]);++i)atomic_store(counters[i],0);
    atomic_store(&strip_min_interval,UINT32_MAX);atomic_store(&strip_min_lead,UINT32_MAX);
    atomic_store(&strip_busy,false);
    atomic_store(&strip_stopping,false);strip_pending_valid=false;
    strip_previous_done=0;strip_ordinal=0;strip_last_pending=false;
    strip_front_index=0;memset(&strip_scene,0,sizeof(strip_scene));
    memset(strip_slot_width,0,sizeof(strip_slot_width));
    memset(strip_slot_height,0,sizeof(strip_slot_height));
    memset(strip_slot_left,0,sizeof(strip_slot_left));
    memset(strip_slot_top,0,sizeof(strip_slot_top));
    strip_backgrounds[0]=background0;strip_backgrounds[1]=background1;
    strip_background = background0; strip_bytes = bytes / strip_blocks;
    ESP_RETURN_ON_ERROR(strip_reserve(), "rolling", "strip slots unavailable");
    for(unsigned i=0;i<STRIP_SLOTS;++i) {
        memset(strip_buffers[i],0,strip_bytes);
        atomic_store(&strip_ready_tag[i],UINT32_MAX);
    }
    esp_async_fbcpy_config_t config = {};
    return esp_async_fbcpy_install(&config, &strip_copier);
}
static uintptr_t strip_address(unsigned block, uint8_t *background) {
    (void)background;
    return (uintptr_t)strip_buffers[block % STRIP_SLOTS];
}
static int strip_wait(void) {
    int64_t end = esp_timer_get_time() + 1000000;
    while (atomic_load(&strip_busy) && esp_timer_get_time() < end) vTaskDelay(1);
    return atomic_load(&strip_busy) || atomic_load(&strip_faults) ? ESP_FAIL : ESP_OK;
}
int strip_prime_and_check(void) {
    // Called before scanout. No racing with the DMA reader, no periodic task.
    if (!strip_bytes || !strip_copier) return ESP_ERR_INVALID_STATE;
    for (unsigned slot = 0; slot < STRIP_SLOTS; ++slot) {
        strip_fill(slot, slot, 0);
        if (strip_wait() != ESP_OK) return ESP_FAIL;
    }
    // Exclude task-context preflight/priming from runtime duration statistics.
    atomic_store(&strip_refills, 0); atomic_store(&strip_total_us, 0);
    atomic_store(&strip_max_us, 0); atomic_store(&strip_over_budget, 0);
    atomic_store(&strip_copy_us, 0); atomic_store(&strip_copy_max, 0);
    atomic_store(&strip_compose_max, 0); atomic_store(&strip_compose_total, 0);
    return ESP_OK;
}
void strip_probe_read(strip_probe_stats *out) {
    out->blocks = atomic_load(&strip_blocks_done); out->frames = atomic_load(&strip_frames_done);
    out->invalid = atomic_load(&strip_invalid); out->underruns = atomic_load(&strip_underruns);
    out->sequence_errors = atomic_load(&strip_sequence_errors);
    out->refills = atomic_load(&strip_refills); out->total_us = atomic_load(&strip_total_us);
    out->max_us = atomic_load(&strip_max_us); out->over_budget = atomic_load(&strip_over_budget);
    out->cache_errors = atomic_load(&strip_cache_errors); out->min_interval = atomic_load(&strip_min_interval);
    out->copy_us = atomic_load(&strip_copy_us);
}
void strip_async_read(strip_async_stats *out) {
    out->copy_max_us = atomic_load(&strip_copy_max); out->compose_max_us = atomic_load(&strip_compose_max);
    out->compose_total_us = atomic_load(&strip_compose_total); out->late = atomic_load(&strip_late);
    out->overlap = atomic_load(&strip_overlap); out->faults = atomic_load(&strip_faults);
    out->min_ready_lead_us = atomic_load(&strip_min_lead); out->preflight_strips = atomic_load(&strip_preflight);
}
void strip_fault_read(strip_fault_stats *out) {
    unsigned reason=atomic_load(&strip_first_fault);
    out->first_fault=reason==UINT32_MAX?0:reason;
    out->first_error=out->first_fault?atomic_load(&strip_first_error):0;
    out->queued=atomic_load(&strip_queued);out->queue_wait_max_us=atomic_load(&strip_queue_wait_max);
}
static bool strip_block_done(dw_gdma_channel_handle_t chan,
 const dw_gdma_trans_done_event_data_t *event, void *ctx) {
    (void)event; (void)ctx;
    if(atomic_load(&strip_stopping))return false;
    strip_channel = chan;
    if (atomic_load(&strip_faults)) { dw_gdma_channel_enable_ctrl(chan, false); return false; }
    int64_t now = esp_timer_get_time();
    if (strip_previous_done) {
        unsigned delta = now - strip_previous_done;
        if (delta < atomic_load(&strip_min_interval)) atomic_store(&strip_min_interval, delta);
    }
    strip_previous_done = now;
    unsigned retired = strip_ordinal++;
    atomic_fetch_add(&strip_blocks_done, 1);
    unsigned next_tag = atomic_load(&strip_frames_done) * strip_blocks + retired + 1;
    unsigned next_slot = next_tag % STRIP_SLOTS;
    if (retired >= strip_blocks || atomic_load(&strip_ready_tag[next_slot]) != next_tag) {
        atomic_fetch_add(&strip_late, 1); strip_abort(STRIP_FAULT_LATE,next_tag); return false;
    }
    unsigned lead = now - strip_ready_time[next_slot];
    if (lead < atomic_load(&strip_min_lead)) atomic_store(&strip_min_lead, lead);
    if (retired == strip_blocks - 1) strip_last_pending = true;
    else {
        unsigned next = (retired + STRIP_SLOTS) % strip_blocks;
        unsigned generation = atomic_load(&strip_frames_done) + (retired + STRIP_SLOTS >= strip_blocks);
        strip_fill(retired % STRIP_SLOTS, next, generation);
    }
    return false;
}
static bool strip_invalid_block(dw_gdma_channel_handle_t chan,
 const dw_gdma_break_event_data_t *event, void *ctx) {
    (void)event; (void)ctx;
    if(atomic_load(&strip_stopping))return false;
    strip_channel = chan;
    atomic_fetch_add(&strip_invalid, 1); strip_abort(STRIP_FAULT_INVALID,0);
    return false;
}
