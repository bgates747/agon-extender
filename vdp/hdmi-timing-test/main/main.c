/* HDMI-002 standalone fixture: deliberately no Agon/SD/network/input startup.
 * Reuses HdmiOutput's proven P4-PC LDO/I2C/DSI/LT8912B sequence. Only timing,
 * clock selection and a static pattern differ. The bridge component is the
 * unchanged pinned Olimex source; no speculative receiver/relock workaround.
 * DMA completion counts establish progression, not HDMI picture correctness.
 */
#include <inttypes.h>
#include <stdatomic.h>
#include <string.h>
#include <assert.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c_master.h"
#include "driver/ppa.h"
#include "esp_heap_caps.h"
#include "esp_ldo_regulator.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_lt8912b.h"
#include "esp_cache.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "soc/hp_sys_clkrst_struct.h"
#include "build_identity.h"
#include "pattern.h"
#include "timing_config.h"

static const char *TAG = "hdmi-timing";
static atomic_uint frames;

#if TEST_PPA_SCALE_320
/* HDMI-002: static SDK experiment, NOT the live renderer or sprite pipeline.
 * IDF5.5.5 PPA SRM is bilinear. Compose sprites before scaling in any future
 * integration; background-only scaling would break coordinates/occlusion.
 * Finish every write/check before panel init starts scanout. This isolated
 * timing excludes competing renderer/network/scanout PSRAM traffic.
 */
static void scaled_pattern(uint8_t *output)
{
    const size_t source_bytes = 320 * 240 * 3;
    const size_t output_bytes = TEST_WIDTH * TEST_HEIGHT * 3;
    assert(TEST_WIDTH == 848 && TEST_HEIGHT == 480);
    const size_t alignment = CONFIG_CACHE_L1_CACHE_LINE_SIZE > CONFIG_CACHE_L2_CACHE_LINE_SIZE
        ? CONFIG_CACHE_L1_CACHE_LINE_SIZE : CONFIG_CACHE_L2_CACHE_LINE_SIZE;
    assert(((uintptr_t)output % alignment) == 0 && output_bytes % alignment == 0);
    uint8_t *source = heap_caps_aligned_alloc(alignment, source_bytes,
                                            MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    ESP_ERROR_CHECK(source ? ESP_OK : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(hdmi_timing_pattern_bgr888(source, source_bytes, 320 * 3, 320, 240)
                    ? ESP_OK : ESP_ERR_INVALID_SIZE);
    memset(output, 0, output_bytes);
    // PPA invalidates its destination before DMA; first preserve black sidebars.
    ESP_ERROR_CHECK(esp_cache_msync(output, output_bytes, ESP_CACHE_MSYNC_FLAG_DIR_C2M));
    ppa_client_handle_t client;
    ppa_client_config_t config = {.oper_type = PPA_OPERATION_SRM, .max_pending_trans_num = 1};
    ESP_ERROR_CHECK(ppa_register_client(&config, &client));
    ppa_srm_oper_config_t operation = {
        .in = {.buffer = source, .pic_w = 320, .pic_h = 240,
               .block_w = 320, .block_h = 240, .srm_cm = PPA_SRM_COLOR_MODE_RGB888},
        .out = {.buffer = output, .buffer_size = output_bytes,
                .pic_w = TEST_WIDTH, .pic_h = TEST_HEIGHT,
                .block_offset_x = 104, .srm_cm = PPA_SRM_COLOR_MODE_RGB888},
        .rotation_angle = PPA_SRM_ROTATION_ANGLE_0, .scale_x = 2.0f, .scale_y = 2.0f,
        .mode = PPA_TRANS_MODE_BLOCKING,
    };
    int64_t total = 0, minimum = INT64_MAX, maximum = 0;
    for (unsigned i = 0; i < 10; ++i) {
        int64_t start = esp_timer_get_time();
        ESP_ERROR_CHECK(ppa_do_scale_rotate_mirror(client, &operation));
        int64_t elapsed = esp_timer_get_time() - start;
        total += elapsed;
        if (elapsed < minimum) minimum = elapsed;
        if (elapsed > maximum) maximum = elapsed;
    }
    ESP_ERROR_CHECK(esp_cache_msync(output, output_bytes, ESP_CACHE_MSYNC_FLAG_DIR_M2C));
    unsigned changed = 0, sidebar_errors = 0, uniform_errors = 0, uniform_checks = 0;
    for (unsigned y = 0; y < 480; ++y) {
        for (unsigned x = 0; x < 848; ++x) {
            const uint8_t *pixel = output + (y * 848 + x) * 3;
            if (x < 104 || x >= 744) {
                sidebar_errors += pixel[0] != 0 || pixel[1] != 0 || pixel[2] != 0;
                continue;
            }
            unsigned sx = (x - 104) / 2, sy = y / 2;
            const uint8_t *original = source + (sy * 320 + sx) * 3;
            changed += memcmp(pixel, original, 3) != 0;
            // Uniform 3x3 neighborhoods must preserve exact colors regardless
            // of bilinear phase; this detects channel/stride/placement errors.
            bool uniform = sx > 0 && sx < 319 && sy > 0 && sy < 239;
            for (int dy = -1; uniform && dy <= 1; ++dy)
                for (int dx = -1; uniform && dx <= 1; ++dx)
                    uniform = memcmp(original, source +
                        (((int)sy + dy) * 320 + (int)sx + dx) * 3, 3) == 0;
            if (uniform) {
                ++uniform_checks;
                uniform_errors += memcmp(pixel, original, 3) != 0;
            }
        }
    }
    ESP_LOGI(TAG, "PPA 320x240->640x480 x104 bilinear: 10 isolated blocking calls us min=%"
             PRId64 " mean=%.1f max=%" PRId64, minimum, total / 10.0, maximum);
    ESP_LOGI(TAG, "PPA pixels: different_from_nearest=%u/307200 uniform_errors=%u/%u sidebar_errors=%u",
             changed, uniform_errors, uniform_checks, sidebar_errors);
    ESP_ERROR_CHECK(uniform_checks > 0 && uniform_errors == 0 && sidebar_errors == 0
                    ? ESP_OK : ESP_FAIL);
    ESP_ERROR_CHECK(ppa_unregister_client(client));
    heap_caps_free(source);
    // Add carrier boundary only after checking the PPA left the sidebars black.
    for (unsigned x = 0; x < 848; ++x) {
        memset(output + x * 3, 255, 3);
        memset(output + (479 * 848 + x) * 3, 255, 3);
    }
    for (unsigned y = 0; y < 480; ++y) {
        memset(output + y * 848 * 3, 255, 3);
        memset(output + (y * 848 + 847) * 3, 255, 3);
    }
}
#endif
static bool IRAM_ATTR frame_done(esp_lcd_panel_handle_t panel,
                                esp_lcd_dpi_panel_event_data_t *data, void *ctx)
{
    (void)panel; (void)data; (void)ctx;
    atomic_fetch_add_explicit(&frames, 1, memory_order_relaxed);
    return false;
}

static void display_task(void *unused)
{
    (void)unused;
    ESP_LOGI(TAG, "%s experimental; static visual validation", HDMI_TEST_BUILD_ID);
    ESP_LOGI(TAG, "%ux%u active; PPA scale experiment=%u; no Agon services",
             TEST_WIDTH, TEST_HEIGHT, TEST_PPA_SCALE_320);
    esp_ldo_channel_handle_t power;
    esp_ldo_channel_config_t power_config = {.chan_id = 3, .voltage_mv = 2500};
    ESP_ERROR_CHECK(esp_ldo_acquire_channel(&power_config, &power));

    i2c_master_bus_handle_t i2c;
    i2c_master_bus_config_t i2c_config = {
        .i2c_port = I2C_NUM_0, .sda_io_num = GPIO_NUM_7, .scl_io_num = GPIO_NUM_8,
        .clk_source = I2C_CLK_SRC_DEFAULT, .flags.enable_internal_pullup = true,
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&i2c_config, &i2c));
    esp_lcd_panel_io_handle_t io[3];
    for (unsigned i = 0; i < 3; ++i) {
        esp_lcd_panel_io_i2c_config_t config = {
            .scl_speed_hz = 400000, .dev_addr = 0x48 + i,
            .control_phase_bytes = 1, .lcd_cmd_bits = 8, .lcd_param_bits = 8,
            .flags.disable_control_phase = true,
        };
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(i2c, &config, &io[i]));
    }

    /* HDMI-002: use supported PLL240 and match DPI, DSI and bridge timing.
     * Supply the realized clock to avoid IDF's hidden porch compensation.
     * Native probes never create doubled pixels or invoke PPA.
     */
    const float pixel_mhz = 240.0f / TEST_DIVIDER;
    ESP_LOGI(TAG, "PLL240/%u: calculated %.3fHz; custom timing",
             TEST_DIVIDER, 240000000.0 / TEST_DIVIDER);

    esp_lcd_dsi_bus_handle_t dsi;
    esp_lcd_dsi_bus_config_t bus = {
        .bus_id = 0, .num_data_lanes = 2,
        .phy_clk_src = MIPI_DSI_PHY_CLK_SRC_DEFAULT, .lane_bit_rate_mbps = TEST_LANE_MBPS,
    };
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus, &dsi));
    esp_lcd_dpi_panel_config_t dpi = {
        .dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_PLL_F240M, .dpi_clock_freq_mhz = pixel_mhz,
        .virtual_channel = 0, .in_color_format = LCD_COLOR_FMT_RGB888,
        .out_color_format = LCD_COLOR_FMT_RGB888, .num_fbs = 1,
        .video_timing = {
            .h_size = TEST_WIDTH, .v_size = TEST_HEIGHT,
            .hsync_front_porch = TEST_HFP, .hsync_pulse_width = TEST_HS, .hsync_back_porch = TEST_HBP,
            .vsync_front_porch = TEST_VFP, .vsync_pulse_width = TEST_VS, .vsync_back_porch = TEST_VBP,
        },
        .flags.disable_lp = true, .flags.use_dma2d = false,
    };
    lt8912b_vendor_config_t vendor = {
        .video_timing = {
            .hfp = TEST_HFP, .hs = TEST_HS, .hbp = TEST_HBP, .hact = TEST_WIDTH, .htotal = TEST_HTOTAL,
            .vfp = TEST_VFP, .vs = TEST_VS, .vbp = TEST_VBP, .vact = TEST_HEIGHT, .vtotal = TEST_VTOTAL,
            .h_polarity = true, .v_polarity = true, .vic = 0,
            .aspect_ratio = TEST_WIDE ? LT8912B_ASPECT_RATION_16_9 : LT8912B_ASPECT_RATION_4_3,
            // Only the bridge's disabled internal-pattern path uses this integer.
            .pclk_mhz = (uint32_t)pixel_mhz,
        },
        .mipi_config = {.dsi_bus = dsi, .dpi_config = &dpi, .lane_num = 2},
    };
    esp_lcd_panel_dev_config_t config = {
        .bits_per_pixel = 24, .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
        .reset_gpio_num = -1, .vendor_config = &vendor,
    };
    esp_lcd_panel_lt8912b_io_t bridge_io = {io[0], io[1], io[2]};
    esp_lcd_panel_handle_t panel;
    ESP_ERROR_CHECK(esp_lcd_new_panel_lt8912b(&bridge_io, &config, &panel));
    void *pixels;
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_get_frame_buffer(panel, 1, &pixels));
#if TEST_PPA_SCALE_320
    scaled_pattern(pixels);
#else
    ESP_ERROR_CHECK(hdmi_timing_pattern_bgr888(pixels, TEST_WIDTH * TEST_HEIGHT * 3,
                                              TEST_WIDTH * 3, TEST_WIDTH, TEST_HEIGHT)
                    ? ESP_OK : ESP_ERR_INVALID_SIZE);
#endif
    ESP_ERROR_CHECK(esp_cache_msync(pixels, TEST_WIDTH * TEST_HEIGHT * 3,
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_UNALIGNED));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    esp_lcd_dpi_panel_event_callbacks_t callbacks = {.on_frame_buf_complete = frame_done};
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_register_event_callbacks(panel, &callbacks, NULL));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_LOGI(TAG, "DPI source selector=%u divider=%u (register readback)",
             (unsigned)HP_SYS_CLKRST.peri_clk_ctrl03.reg_mipi_dsi_dpiclk_src_sel,
             (unsigned)HP_SYS_CLKRST.peri_clk_ctrl03.reg_mipi_dsi_dpiclk_div_num + 1);
    ESP_LOGI(TAG, "Pattern held; %ux%u total; calculated %.6fHz; +H/+V; VIC0",
             TEST_HTOTAL, TEST_VTOTAL, 240000000.0 / TEST_DIVIDER / TEST_HTOTAL / TEST_VTOTAL);
    ESP_LOGI(TAG, "Visual validation - screenshot requested; all four white edges should show");
    uint32_t before = atomic_load(&frames);
    int64_t previous = esp_timer_get_time();
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        int64_t now = esp_timer_get_time();
        uint32_t count = atomic_load(&frames);
        ESP_LOGI(TAG, "DMA frames=%" PRIu32 " interval_us=%" PRId64 " rate=%.3f/s hdmi_hpd=%u",
                 count, now - previous, (count - before) * 1000000.0 / (now - previous),
                 esp_lcd_panel_lt8912b_is_ready(panel));
        before = count; previous = now;
    }
}

void app_main(void)
{
    if (xTaskCreatePinnedToCore(display_task, "pattern", 8192, NULL, 5, NULL, 1) != pdPASS)
        ESP_ERROR_CHECK(ESP_ERR_NO_MEM);
}
