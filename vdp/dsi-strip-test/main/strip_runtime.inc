/* SPRITE-001 r02: standalone DMA2D refill experiment; not a product driver.
 * Fixed DSI descriptors cycle through fixed internal-SRAM buffers. A single pinned
 * Espressif fbcpy handle has at most one transaction outstanding: its static
 * transaction configuration is NOT a concurrent multi-handle API. Allocate in
 * task context only. CPU cache ownership is explicitly handed to/from DMA.
 * Late generation detection aborts scanout. The ISR can detect a miss after
 * DMA has started the next block, so this is not a zero-corruption guarantee.
 */
#include "strip_probe.h"
#include "strip_config.h"
#include "stock_sprite_probe.h"
#include "esp_async_fbcpy.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_rom_sys.h"
#include <stdatomic.h>
#include <string.h>
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
static unsigned strip_ordinal;
static bool strip_last_pending;
static uint8_t *strip_buffers[STRIP_SLOTS], *strip_background;
static size_t strip_bytes;
static int64_t strip_previous_done;
static esp_async_fbcpy_handle_t strip_copier;
static dw_gdma_channel_handle_t strip_channel;
static struct { unsigned slot, block, tag; int64_t begin; } strip_job;

static void strip_max(atomic_uint *p, unsigned value) {
    if (value > atomic_load(p)) atomic_store(p, value);
}
static void strip_abort(void) {
    atomic_fetch_add(&strip_faults, 1);
    if (strip_channel) dw_gdma_channel_enable_ctrl(strip_channel, false);
}
static bool strip_sync(void *p, size_t size, unsigned flags) {
    if (esp_cache_msync(p, size, flags) == ESP_OK) return true;
    atomic_fetch_add(&strip_cache_errors, 1);
    strip_abort();
    return false;
}
static void strip_finish(void) {
    unsigned elapsed = esp_timer_get_time() - strip_job.begin;
    atomic_fetch_add(&strip_copy_us, elapsed);
    strip_max(&strip_copy_max, elapsed);
    if (!atomic_load(&strip_faults)) {
        uint8_t *dst = strip_buffers[strip_job.slot];
        if (!strip_sync(dst, strip_bytes, ESP_CACHE_MSYNC_FLAG_DIR_M2C)) {
            atomic_store(&strip_busy, false);
            return;
        }
        int64_t compose = esp_timer_get_time();
        stock_probe_compose(dst, strip_job.block * (480 / STRIP_BLOCKS),
                            480 / STRIP_BLOCKS, strip_job.tag / STRIP_BLOCKS);
        unsigned duration = esp_timer_get_time() - compose;
        atomic_fetch_add(&strip_compose_total, duration);
        strip_max(&strip_compose_max, duration);
        if (!strip_sync(dst, strip_bytes, ESP_CACHE_MSYNC_FLAG_DIR_C2M)) {
            atomic_store(&strip_busy, false);
            return;
        }
        strip_ready_time[strip_job.slot] = esp_timer_get_time();
        atomic_store(&strip_ready_tag[strip_job.slot], strip_job.tag);
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
        strip_abort();
    }
    atomic_store(&strip_busy, false);
}
static bool strip_copy_done(esp_async_fbcpy_handle_t handle,
                            esp_async_fbcpy_event_data_t *event, void *context) {
    (void)handle; (void)event; (void)context;
    strip_finish();
    return false;
}
static void strip_fill(unsigned slot, unsigned block, unsigned generation) {
    if (atomic_load(&strip_faults)) return;
    if (atomic_exchange(&strip_busy, true)) {
        atomic_fetch_add(&strip_overlap, 1);
        strip_abort();
        return;
    }
    strip_job.slot = slot; strip_job.block = block;
    strip_job.tag = generation * STRIP_BLOCKS + block;
    strip_job.begin = esp_timer_get_time();
    atomic_store(&strip_ready_tag[slot], UINT32_MAX);
    uint8_t *dst = strip_buffers[slot];
    unsigned rows = 480 / STRIP_BLOCKS, first_y = block * rows;
    unsigned top = first_y > 48 ? first_y : 48;
    unsigned bottom = first_y + rows < 432 ? first_y + rows : 432;
    // A recycled slot may previously have held logical pixels at these rows.
    // Borders at the left/right never contain sprites and stay zero.
    for (unsigned row = 0; row < rows; ++row)
        if (first_y + row < 48 || first_y + row >= 432)
            memset(dst + row * 848 * 3 + 168 * 3, 0, 512 * 3);
    if (!strip_sync(dst, strip_bytes,
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_INVALIDATE)) {
        atomic_store(&strip_busy, false);
        return;
    }
    if (bottom <= top) { strip_finish(); return; }
    esp_async_fbcpy_trans_desc_t transaction = {
        .src_buffer = strip_background, .dst_buffer = dst,
        .src_buffer_size_x = 848, .src_buffer_size_y = 480,
        .dst_buffer_size_x = 848, .dst_buffer_size_y = rows,
        .src_offset_x = 168, .src_offset_y = top,
        .dst_offset_x = 168, .dst_offset_y = top - first_y,
        .copy_size_x = 512, .copy_size_y = bottom - top,
        // Full color-space/type ID, not the deprecated zero-valued pixel enum.
        .pixel_format_unique_id = {.color_type_id = LCD_COLOR_FMT_RGB888},
    };
    // The helper consumes this stack descriptor synchronously into its retained
    // DMA descriptors. Those descriptors and our single job remain live to EOF.
    if (esp_async_fbcpy(strip_copier, &transaction, strip_copy_done, NULL) != ESP_OK) {
        atomic_store(&strip_busy, false);
        strip_abort();
    }
}
static void strip_configure(uint8_t *background, size_t bytes) {
    assert(STRIP_ROLLING && STRIP_BLOCKS >= 2 && STRIP_BLOCKS <= 15 && STRIP_BLOCKS % STRIP_SLOTS == 0);
    assert(bytes == 848 * 480 * 3 && bytes % (STRIP_BLOCKS * 64) == 0);
    strip_background = background; strip_bytes = bytes / STRIP_BLOCKS;
    for (unsigned i = 0; i < STRIP_SLOTS; ++i) {
        strip_buffers[i] = heap_caps_aligned_calloc(64, 1, strip_bytes,
            MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
        assert(strip_buffers[i]);
        atomic_store(&strip_ready_tag[i], UINT32_MAX);
    }
    esp_async_fbcpy_config_t config = {};
    ESP_ERROR_CHECK(esp_async_fbcpy_install(&config, &strip_copier));
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
    uint8_t *expected = heap_caps_malloc(strip_bytes, MALLOC_CAP_SPIRAM);
    if (!expected) return ESP_ERR_NO_MEM;
    for (unsigned block = 0; block < STRIP_BLOCKS; ++block) {
        memcpy(expected, strip_background + block * strip_bytes, strip_bytes);
        stock_probe_compose(expected, block * (480 / STRIP_BLOCKS), 480 / STRIP_BLOCKS, 1800);
        strip_fill(0, block, 1800);
        if (strip_wait() != ESP_OK || memcmp(expected, strip_buffers[0], strip_bytes)) {
            free(expected); return ESP_FAIL;
        }
        atomic_fetch_add(&strip_preflight, 1);
    }
    free(expected);
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
static bool strip_block_done(dw_gdma_channel_handle_t chan,
 const dw_gdma_trans_done_event_data_t *event, void *ctx) {
    (void)event; (void)ctx;
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
    unsigned next_tag = atomic_load(&strip_frames_done) * STRIP_BLOCKS + retired + 1;
    unsigned next_slot = next_tag % STRIP_SLOTS;
    if (retired >= STRIP_BLOCKS || atomic_load(&strip_ready_tag[next_slot]) != next_tag) {
        atomic_fetch_add(&strip_late, 1); strip_abort(); return false;
    }
    unsigned lead = now - strip_ready_time[next_slot];
    if (lead < atomic_load(&strip_min_lead)) atomic_store(&strip_min_lead, lead);
    if (retired == STRIP_BLOCKS - 1) strip_last_pending = true;
    else {
        unsigned next = (retired + STRIP_SLOTS) % STRIP_BLOCKS;
        unsigned generation = atomic_load(&strip_frames_done) + (retired + STRIP_SLOTS >= STRIP_BLOCKS);
        strip_fill(retired % STRIP_SLOTS, next, generation);
    }
    return false;
}
static bool strip_invalid_block(dw_gdma_channel_handle_t chan,
 const dw_gdma_break_event_data_t *event, void *ctx) {
    (void)event; (void)ctx;
    strip_channel = chan;
    atomic_fetch_add(&strip_invalid, 1); strip_abort();
    return false;
}
