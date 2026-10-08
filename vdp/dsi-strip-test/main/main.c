/* HDMI-002 standalone fixture: deliberately no Agon/SD/network/input startup.
 * Reuses HdmiOutput's proven P4-PC LDO/I2C/DSI/LT8912B sequence. Only timing,
 * clock selection and a static pattern differ. The bridge component is the
 * unchanged pinned Olimex source; no speculative receiver/relock workaround.
 * DMA completion counts establish progression, not HDMI picture correctness.
 */
#include <inttypes.h>
#include <stdatomic.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c_master.h"
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
#include "strip_probe.h"
#include "strip_config.h"
#include "stock_sprite_probe.h"

static const char *TAG = "hdmi-timing";
static atomic_uint frames;
static atomic_uint load_steps, load_late, load_max_us;
static void memory_load_task(void *unused) {
    (void)unused;
    uint8_t *scratch = heap_caps_calloc(1, 848 * 480 * 3, MALLOC_CAP_SPIRAM);
    assert(scratch);
    while (atomic_load(&frames) < 3600) vTaskDelay(pdMS_TO_TICKS(10));
    ESP_LOGI(TAG, "Separate-core256x336 scroll traffic begins; this is not an Agon game run");
    int64_t next = esp_timer_get_time();
    for (;;) {
        int64_t before = esp_timer_get_time();
        if (before < next) { vTaskDelay(1); continue; }
        for (int y = 335; y > 0; --y)
            memmove(scratch + (48 + y) * 848 * 3 + 128 * 3,
                    scratch + (47 + y) * 848 * 3 + 128 * 3, 256 * 3);
        memset(scratch + 48 * 848 * 3 + 128 * 3, atomic_load(&load_steps), 256 * 3);
        unsigned duration = esp_timer_get_time() - before;
        if (duration > atomic_load(&load_max_us)) atomic_store(&load_max_us, duration);
        atomic_fetch_add(&load_steps, 1);
        next += 16667;
        if (esp_timer_get_time() > next) { atomic_fetch_add(&load_late, 1); next = esp_timer_get_time() + 16667; }
    }
}
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
    ESP_LOGI(TAG, "%s experimental; multiblock visual validation", HDMI_TEST_BUILD_ID);
    ESP_LOGI(TAG, "848x480; centered512x384 at168,48; no Agon services");
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

    /* HDMI-002 r02: APLL DPI selector3 is not established on v1.3 silicon;
     * the old register table calls it invalid and the earlier r10 test stalled.
     * Use supported PLL240/7 and MATCH the producer, DSI and bridge blanking.
     * This is deliberately custom848x480, not a claim of exact VESA DMT0Eh.
     * 480Mbps lanes give1.75 byteclocks/pixel: all horizontal fields are exact.
     * Specifying the realized clock prevents IDF's hidden porch compensation.
     */
    ESP_LOGI(TAG, "Supported PLL240/7: calculated34285714.286Hz; custom timing");

    esp_lcd_dsi_bus_handle_t dsi;
    esp_lcd_dsi_bus_config_t bus = {
        .bus_id = 0, .num_data_lanes = 2,
        .phy_clk_src = MIPI_DSI_PHY_CLK_SRC_DEFAULT, .lane_bit_rate_mbps = 480,
    };
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus, &dsi));
    esp_lcd_dpi_panel_config_t dpi = {
        .dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_PLL_F240M, .dpi_clock_freq_mhz = 240.0f / 7.0f,
        .virtual_channel = 0, .in_color_format = LCD_COLOR_FMT_RGB888,
        .out_color_format = LCD_COLOR_FMT_RGB888, .num_fbs = 1,
        .video_timing = {
            .h_size = 848, .v_size = 480,
            .hsync_front_porch = 32, .hsync_pulse_width = 112, .hsync_back_porch = 112,
            .vsync_front_porch = 6, .vsync_pulse_width = 8, .vsync_back_porch = 23,
        },
        .flags.disable_lp = true, .flags.use_dma2d = false,
    };
    lt8912b_vendor_config_t vendor = {
        .video_timing = {
            .hfp = 32, .hs = 112, .hbp = 112, .hact = 848, .htotal = 1104,
            .vfp = 6, .vs = 8, .vbp = 23, .vact = 480, .vtotal = 517,
            .h_polarity = true, .v_polarity = true, .vic = 0,
            .aspect_ratio = LT8912B_ASPECT_RATION_16_9,
            // Only the bridge's disabled internal-pattern path uses this integer.
            .pclk_mhz = 34,
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
    ESP_ERROR_CHECK(hdmi_timing_pattern_bgr888(pixels, 848 * 480 * 3,
                                              848 * 3, 848, 480)
                    ? ESP_OK : ESP_ERR_INVALID_SIZE);
    // Deliberate centered-output variant: omit the timing fixture's outer labels.
    for (unsigned y = 0; y < 480; ++y) {
        uint8_t *row = (uint8_t *)pixels + y * 848 * 3;
        if (y < 48 || y >= 432) memset(row, 0, 848 * 3);
        else { memset(row, 0, 168 * 3); memset(row + 680 * 3, 0, 168 * 3); }
    }
    ESP_ERROR_CHECK(esp_cache_msync(pixels, 848 * 480 * 3,
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_UNALIGNED));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    esp_lcd_dpi_panel_event_callbacks_t callbacks = {.on_frame_buf_complete = frame_done};
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_register_event_callbacks(panel, &callbacks, NULL));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_LOGI(TAG, "DMA2D preflight: all12 strips match CPU reference; buffers primed");
    ESP_LOGI(TAG, "DPI source selector=%u divider=%u (register readback)",
             (unsigned)HP_SYS_CLKRST.peri_clk_ctrl03.reg_mipi_dsi_dpiclk_src_sel,
             (unsigned)HP_SYS_CLKRST.peri_clk_ctrl03.reg_mipi_dsi_dpiclk_div_num + 1);
    ESP_LOGI(TAG, "Pattern held; 1104x517 total; calculated60.069440Hz; +H/+V; VIC0");
    ESP_LOGI(TAG, "Visual validation - screenshot requested; centered image border should show; outer borders deliberately black");
    uint32_t before = atomic_load(&frames);
    int64_t previous = esp_timer_get_time();
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        int64_t now = esp_timer_get_time();
        uint32_t count = atomic_load(&frames);
        ESP_LOGI(TAG, "DMA frames=%" PRIu32 " interval_us=%" PRId64 " rate=%.3f/s hdmi_hpd=%u",
                 count, now - previous, (count - before) * 1000000.0 / (now - previous),
                 esp_lcd_panel_lt8912b_is_ready(panel));
        strip_probe_stats probe; strip_probe_read(&probe);
        ESP_LOGI(TAG, "strip blocks=%u rolling=%u completed=%lu frames=%lu invalid=%lu underruns=%lu sequence_errors=%lu",
                 STRIP_BLOCKS, STRIP_ROLLING, (unsigned long)probe.blocks,
                 (unsigned long)probe.frames, (unsigned long)probe.invalid,
                 (unsigned long)probe.underruns, (unsigned long)probe.sequence_errors);
        ESP_LOGI(TAG, "refill count=%lu mean_us=%.2f max_us=%lu over_limit=%lu cache_errors=%lu min_block_interval_us=%lu sprites=%u",
          (unsigned long)probe.refills, probe.refills ? (double)probe.total_us / probe.refills : 0.,
          (unsigned long)probe.max_us, (unsigned long)probe.over_budget,
          (unsigned long)probe.cache_errors, (unsigned long)probe.min_interval, stock_probe_population(probe.frames));
        ESP_LOGI(TAG, "refill copy_mean_us=%.2f scratch=internal-SRAM",
                 probe.refills ? (double)probe.copy_us / probe.refills : 0.);
        strip_async_stats async; strip_async_read(&async);
        ESP_LOGI(TAG, "async copy_max_us=%lu compose_max_us=%lu compose_total_us=%lu late=%lu overlap=%lu faults=%lu min_ready_lead_us=%lu preflight=%lu",
            (unsigned long)async.copy_max_us, (unsigned long)async.compose_max_us,
            (unsigned long)async.compose_total_us, (unsigned long)async.late,
            (unsigned long)async.overlap, (unsigned long)async.faults,
            (unsigned long)async.min_ready_lead_us, (unsigned long)async.preflight_strips);
        ESP_LOGI(TAG, "load steps=%lu late=%lu max_us=%lu",
                 (unsigned long)atomic_load(&load_steps), (unsigned long)atomic_load(&load_late),
                 (unsigned long)atomic_load(&load_max_us));
        ESP_LOGI(TAG, "strip_rows=%u scratch_bytes=%u refill_limit_us=%u free_internal=%u",
                 480 / STRIP_BLOCKS, STRIP_SLOTS * (848 * 480 * 3 / STRIP_BLOCKS), STRIP_REFILL_LIMIT_US,
                 (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
        before = count; previous = now;
    }
}

void app_main(void)
{
    if (xTaskCreatePinnedToCore(memory_load_task, "scroll-load", 4096, NULL, 4, NULL, 0) != pdPASS)
        ESP_ERROR_CHECK(ESP_ERR_NO_MEM);
    if (xTaskCreatePinnedToCore(display_task, "pattern", 8192, NULL, 5, NULL, 1) != pdPASS)
        ESP_ERROR_CHECK(ESP_ERR_NO_MEM);
}
