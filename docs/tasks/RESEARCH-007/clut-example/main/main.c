/*
 * SPDX-License-Identifier: Apache-2.0
 * RESEARCH-007, ppa-clut-example-r05. Compile-only experimental test article.
 *
 * Operation/verification idioms adapted from Espressif's Apache-2.0 CLUT tests
 * in commit76b4cf1336168aad6d1db4b8d1d2743137db4092. See ../README.md.
 * The isolated build backports that upstream driver feature to IDF5.5.5;
 * unmodified5.5.5 cannot compile this API. Product sources/SDK stay untouched.
 *
 * This app does not initialize HDMI/DSI, networking, keyboard or SD services.
 * If separately authorized and flashed later, it exercises memory-to-memory
 * PPA conversion only. No hardware execution or performance claim is implied
 * by successful compilation. Public BLEND reads two inputs, even with zero
 * foreground alpha. All submissions and palette writes occur in task context.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "driver/ppa.h"
#include "esp_cache.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

#ifndef RESEARCH007_BUILD_ID
#define RESEARCH007_BUILD_ID "UNVERSIONED-DO-NOT-DEPLOY"
#endif

enum {
    WIDTH = 512, SOURCE_HEIGHT = 64, STRIP_ROWS = 32, SOURCE_TOP = 32,
    INDEX_BYTES = WIDTH * SOURCE_HEIGHT,
    MASK_BYTES = WIDTH * STRIP_ROWS,
    STRIP_BYTES = WIDTH * STRIP_ROWS * 3,
    GUARD_BYTES = 64,
};
_Static_assert(STRIP_BYTES % 64 == 0, "RGB output must be cache-line aligned");
_Static_assert(sizeof(color_pixel_argb8888_data_t) == 4, "Expected ARGB palette entry");
static const char *TAG = "indexed-strip";

static void *allocate_aligned(size_t bytes, uint32_t memory_caps)
{
    void *p = heap_caps_aligned_calloc(64, 1, bytes,
                                     memory_caps | MALLOC_CAP_8BIT | MALLOC_CAP_DMA);
    ESP_ERROR_CHECK(p ? ESP_OK : ESP_ERR_NO_MEM);
    return p;
}

static void make_palette(color_pixel_argb8888_data_t palette[256], unsigned theme)
{
    for (unsigned i = 0; i < 256; ++i) {
        /* Deliberately arbitrary RGB values, not RGB222 or a grayscale ramp. */
        palette[i].r = theme ? 255 - i : i;
        palette[i].g = (i * 73 + 19 + theme * 41) & 255;
        palette[i].b = theme ? (i * 29 + 7) & 255 : 255 - i;
        palette[i].a = 255;
    }
}

static esp_err_t check_strip(const uint8_t *pixels, const uint8_t *indices,
                             const color_pixel_argb8888_data_t palette[256])
{
    for (unsigned y = 0; y < STRIP_ROWS; ++y) {
        for (unsigned x = 0; x < WIDTH; ++x) {
            const unsigned index = indices[(SOURCE_TOP + y) * WIDTH + x];
            const color_pixel_argb8888_data_t expected = palette[index];
            const uint8_t *p = pixels + (y * WIDTH + x) * 3;
            /* RGB888 memory order is B,G,R; independent lookup, no backfill. */
            if (p[0] != expected.b || p[1] != expected.g || p[2] != expected.r) {
                ESP_LOGE(TAG, "Mismatch x=%u y=%u index=%u got=%02x%02x%02x expected=%02x%02x%02x",
                         x, y, index, p[2], p[1], p[0], expected.r, expected.g, expected.b);
                return ESP_FAIL;
            }
        }
    }
    for (unsigned i = 0; i < GUARD_BYTES; ++i) {
        if (pixels[STRIP_BYTES + i] != 0xA5) return ESP_FAIL;
    }
    return ESP_OK;
}

static void exercise_destination(ppa_client_handle_t client, const uint8_t *indices,
                                  const uint8_t *alpha, uint32_t memory_caps,
                                  const char *region)
{
    uint8_t *out = allocate_aligned(STRIP_BYTES + GUARD_BYTES, memory_caps);
    ppa_blend_oper_config_t operation = {
        .in_bg = {
            .buffer = indices, .pic_w = WIDTH, .pic_h = SOURCE_HEIGHT,
            .block_w = WIDTH, .block_h = STRIP_ROWS, .block_offset_y = SOURCE_TOP,
            .blend_cm = PPA_BLEND_COLOR_MODE_L8,
        },
        .in_fg = {
            .buffer = alpha, .pic_w = WIDTH, .pic_h = STRIP_ROWS,
            .block_w = WIDTH, .block_h = STRIP_ROWS,
            .blend_cm = PPA_BLEND_COLOR_MODE_A8,
        },
        .out = {
            .buffer = out, .buffer_size = STRIP_BYTES + GUARD_BYTES,
            .pic_w = WIDTH, .pic_h = STRIP_ROWS,
            .blend_cm = PPA_BLEND_COLOR_MODE_RGB888,
        },
        .bg_alpha_update_mode = PPA_ALPHA_NO_CHANGE,
        .fg_alpha_update_mode = PPA_ALPHA_NO_CHANGE,
        .mode = PPA_TRANS_MODE_BLOCKING,
    };

    /* Driver must reject an indexed input until its palette is loaded. */
    ESP_ERROR_CHECK(ppa_do_blend(client, &operation) == ESP_ERR_INVALID_STATE
                        ? ESP_OK : ESP_FAIL);
    color_pixel_argb8888_data_t palette[256];
    for (unsigned theme = 0; theme < 2; ++theme) {
        make_palette(palette, theme);
        /* Prior transaction is blocking/completed: no shared CLUT update race. */
        ESP_ERROR_CHECK(ppa_set_color_lookup_table(PPA_CLUT_BLEND_BG, palette, 256));
        memset(out, 0xCC, STRIP_BYTES);
        memset(out + STRIP_BYTES, 0xA5, GUARD_BYTES);
        ESP_ERROR_CHECK(esp_cache_msync(out, STRIP_BYTES + GUARD_BYTES,
                                       ESP_CACHE_MSYNC_FLAG_DIR_C2M));
        ESP_ERROR_CHECK(ppa_do_blend(client, &operation));
        /* Include the guard cache line: the driver's picture-only sync cannot
         * make a physical overrun into that extra line visible to this check. */
        ESP_ERROR_CHECK(esp_cache_msync(out, STRIP_BYTES + GUARD_BYTES,
                                       ESP_CACHE_MSYNC_FLAG_DIR_M2C));
        ESP_ERROR_CHECK(check_strip(out, indices, palette));
        ESP_LOGI(TAG, "%s theme=%u: 512x32 RGB888 strip verified; indices unchanged",
                 region, theme);
    }
    ESP_ERROR_CHECK(ppa_set_color_lookup_table(PPA_CLUT_BLEND_BG, NULL, 0));
    ESP_ERROR_CHECK(ppa_do_blend(client, &operation) == ESP_ERR_INVALID_STATE
                        ? ESP_OK : ESP_FAIL);
    heap_caps_free(out);
}

void app_main(void)
{
    ESP_LOGI(TAG, "%s experimental; memory conversion only, no HDMI", RESEARCH007_BUILD_ID);
    uint8_t *indices = allocate_aligned(INDEX_BYTES, MALLOC_CAP_SPIRAM);
    uint8_t *alpha = allocate_aligned(MASK_BYTES, MALLOC_CAP_SPIRAM);
    for (unsigned y = 0; y < SOURCE_HEIGHT; ++y) {
        for (unsigned x = 0; x < WIDTH; ++x) indices[y * WIDTH + x] = (x + 17 * y) & 255;
    }
    /* The driver flushes the selected lower half only. Publish the untouched
     * upper half too before the final whole-source physical integrity check. */
    ESP_ERROR_CHECK(esp_cache_msync(indices, INDEX_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_C2M));
    /* Zeroed A8 foreground is transparent, but its DMA read still occurs. */
    ppa_client_handle_t client;
    const ppa_client_config_t config = {
        .oper_type = PPA_OPERATION_BLEND, .max_pending_trans_num = 1,
    };
    ESP_ERROR_CHECK(ppa_register_client(&config, &client));
    exercise_destination(client, indices, alpha, MALLOC_CAP_INTERNAL, "SRAM");
    exercise_destination(client, indices, alpha, MALLOC_CAP_SPIRAM, "PSRAM");
    /* Inspect physical PSRAM input contents rather than stale CPU cache lines. */
    ESP_ERROR_CHECK(esp_cache_msync(indices, INDEX_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_M2C));
    for (unsigned y = 0; y < SOURCE_HEIGHT; ++y) {
        for (unsigned x = 0; x < WIDTH; ++x) {
            ESP_ERROR_CHECK(indices[y * WIDTH + x] == ((x + 17 * y) & 255) ? ESP_OK : ESP_FAIL);
        }
    }
    ESP_ERROR_CHECK(ppa_unregister_client(client));
    heap_caps_free(alpha);
    heap_caps_free(indices);
    ESP_LOGI(TAG, "All memory-conversion checks completed; scanout/performance not tested");
}
