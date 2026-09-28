/* SPDX-License-Identifier: CC0-1.0
 * Initialization table from OLIMEX/ESP32-P4-DevKit commit
 * 26705d36407a07324348927dfd30fbf4ffc1d94c, SOFTWARE/Demo_Examples/mipi_dsi/
 * main/mipi_dsi_lcd_example_main.c (Espressif 2023-2025).
 * V2-only adapter: retains table/timing; omits LVGL, V1 expander, GPIO20 probe.
 * Two scanout buffers are owned by the output task and DSI completion protocol.
 */
#include "config.hpp"
#if AGON_EXTENDER_LCD
#include "esp_lcd_st7701.h"
#include "esp_lcd_panel_ops.h"
#include "esp_ldo_regulator.h"
#include "esp_log.h"
#include "hal/mipi_dsi_host_ll.h"
#include "hal/mipi_dsi_brg_ll.h"
static const st7701_lcd_init_cmd_t lcd_init_cmds[] = {
    // Command2 BK3 Selection: Enable the BK function of Command2
    {0xFF, (uint8_t []){0x77, 0x01, 0x00, 0x00, 0x13}, 5, 0},
    // Unknown
    {0xEF, (uint8_t []){0x08}, 1, 0},

    // Command2 BK0 Selection: Enable the BK function of Command2
    {0xFF, (uint8_t []){0x77, 0x01, 0x00, 0x00, 0x10}, 5, 0},
    // Display Line Setting
    {0xC0, (uint8_t []){0x4f, 0x00}, 2, 0},
    // Porch Control
    {0xC1, (uint8_t []){0x10, 0x0c}, 2, 0},
    // Inversion selection & Frame Rate Control
    {0xC2, (uint8_t []){0x07, 0x14}, 2, 0},
    // Unknown
    {0xCC, (uint8_t []){0x10}, 1, 0},
    // Positive Voltage Gamma Control
    {0xB0, (uint8_t []){0x0a, 0x18, 0x1e, 0x12, 0x16, 0x0c, 0x0e, 0x0d, 0x0c, 0x29, 0x06, 0x14, 0x13, 0x29, 0x33, 0x1c}, 16, 0},
    // Negative Voltage Gamma Control
    {0xB1, (uint8_t []){0x0a, 0x19, 0x21, 0x0a, 0x0c, 0x00, 0x0c, 0x03, 0x03, 0x23, 0x01, 0x0e, 0x0c, 0x27, 0x2b, 0x1c}, 16, 0},

    // Command2 BK1 Selection: Enable the BK function of Command2
    {0xFF, (uint8_t []){0x77, 0x01, 0x00, 0x00, 0x11}, 5, 0},
    // Vop Amplitude setting
    {0xB0, (uint8_t []){0x5d}, 1, 0},
    // VCOM amplitude setting
    {0xB1, (uint8_t []){0x61}, 1, 0},
    // VGH Voltage setting
    {0xB2, (uint8_t []){0x84}, 1, 0},
    // TEST Command Setting
    {0xB3, (uint8_t []){0x80}, 1, 0},
    // VGL Voltage setting
    {0xB5, (uint8_t []){0x4d}, 1, 0},
    // Power Control 1
    {0xB7, (uint8_t []){0x85}, 1, 0},
    // Power Control 2
    {0xB8, (uint8_t []){0x20}, 1, 0},
    // Source pre_drive timing set1
    {0xC1, (uint8_t []){0x78}, 1, 0},
    // Source EQ2 Setting
    {0xC2, (uint8_t []){0x78}, 1, 0},
    // MIPI Setting 1
    {0xD0, (uint8_t []){0x88}, 1, 0},
    // GIP Code
    {0xE0, (uint8_t []){0x00, 0x00, 0x02}, 3, 0},
    {0xE1, (uint8_t []){0x06, 0xa0, 0x08, 0xa0, 0x05, 0xa0, 0x07, 0xa0, 0x00, 0x44, 0x44}, 11, 0},
    {0xE2, (uint8_t []){0x20, 0x20, 0x44, 0x44, 0x96, 0xa0, 0x00, 0x00, 0x96, 0xa0, 0x00, 0x00}, 12, 0},
    {0xE3, (uint8_t []){0x00, 0x00, 0x22, 0x22}, 4, 0},
    {0xE4, (uint8_t []){0x44, 0x44}, 2, 0},
    {0xE5, (uint8_t []){0x0d, 0x91, 0xa0, 0xa0, 0x0f, 0x93, 0xa0, 0xa0, 0x09, 0x8d, 0xa0, 0xa0, 0x0b, 0x8f, 0xa0, 0xa0}, 16, 0},
    {0xE6, (uint8_t []){0x00, 0x00, 0x22, 0x22}, 4, 0},
    {0xE7, (uint8_t []){0x44, 0x44}, 2, 0},
    {0xE8, (uint8_t []){0x0c, 0x90, 0xa0, 0xa0, 0x0e, 0x92, 0xa0, 0xa0, 0x08, 0x8c, 0xa0, 0xa0, 0x0a, 0x8e, 0xa0, 0xa0}, 16, 0},
    {0xE9, (uint8_t []){0x36, 0x00}, 2, 0},
    {0xEB, (uint8_t []){0x00, 0x01, 0xe4, 0xe4, 0x44, 0x88, 0x40}, 7, 0},
    {0xED, (uint8_t []){0xff, 0x45, 0x67, 0xfa, 0x01, 0x2b, 0xcf, 0xff, 0xff, 0xfc, 0xb2, 0x10, 0xaf, 0x76, 0x54, 0xff}, 16, 0},
    {0xEF, (uint8_t []){0x10, 0x0d, 0x04, 0x08, 0x3f, 0x1f}, 6, 0},

    // Command2 BK3 Selection: Enable the BK function of Command2
    // {0xFF, (uint8_t []){0x77, 0x01, 0x00, 0x00, 0x13}, 5, 0},
    // {0xE8, (uint8_t []){0x00, 0x0E}, 2, 0},
    // {0xE8, (uint8_t []){0x00, 0x0C}, 2, 20},
    // {0xE8, (uint8_t []){0x00, 0x00}, 2, 0},

    // Command2 BK0 Selection: Disable the BK function of Command2
    {0xFF, (uint8_t []){0x77, 0x01, 0x00, 0x00, 0x00}, 5, 0},
};

esp_lcd_panel_handle_t extender_lcd_panel_create(void) {
    static esp_ldo_channel_handle_t ldo;
    esp_ldo_channel_config_t power = {.chan_id=3, .voltage_mv=2500};
    ESP_ERROR_CHECK(esp_ldo_acquire_channel(&power, &ldo));
    esp_lcd_dsi_bus_handle_t bus;
    esp_lcd_dsi_bus_config_t bus_config = {.bus_id=0,.num_data_lanes=1,
        .phy_clk_src=MIPI_DSI_PHY_CLK_SRC_DEFAULT,.lane_bit_rate_mbps=500};
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus_config,&bus));
    esp_lcd_panel_io_handle_t io;
    esp_lcd_dbi_io_config_t dbi={.virtual_channel=0,.lcd_cmd_bits=8,.lcd_param_bits=8};
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_dbi(bus,&dbi,&io));
    esp_lcd_dpi_panel_config_t dpi={.virtual_channel=0,
        .dpi_clk_src=MIPI_DSI_DPI_CLK_SRC_DEFAULT,.dpi_clock_freq_mhz=16,
        .pixel_format=LCD_COLOR_PIXEL_FORMAT_RGB888,.num_fbs=2,
        .video_timing={.h_size=480,.v_size=640,
            .hsync_pulse_width=4,.hsync_back_porch=20,.hsync_front_porch=10,
            .vsync_pulse_width=4,.vsync_back_porch=14,.vsync_front_porch=8},
        .in_color_format=LCD_COLOR_FMT_RGB888,.out_color_format=LCD_COLOR_FMT_RGB888};
    st7701_vendor_config_t vendor={.init_cmds=lcd_init_cmds,
        .init_cmds_size=sizeof(lcd_init_cmds)/sizeof(lcd_init_cmds[0]),
        .mipi_config={.dsi_bus=bus,.dpi_config=&dpi},.flags.use_mipi_interface=1};
    esp_lcd_panel_dev_config_t dev={.reset_gpio_num=-1,
        .rgb_ele_order=LCD_RGB_ELEMENT_ORDER_RGB,.bits_per_pixel=24,.vendor_config=&vendor};
    esp_lcd_panel_handle_t panel;
    ESP_ERROR_CHECK(esp_lcd_new_panel_st7701(io,&dev,&panel));
    // LCD-001 diagnostic only. IDF5.4.1 truncates each timing product;
    // IDF5.5.5 rounds them and compensates the total. At 500Mbps/16MHz
    // the former gives 15+78+1875+39=2007 host byte clocks, versus2008.
    // No pixel/channel rewrite. Remove this comparison after root-cause review.
#if AGON_EXTENDER_LCD_LEGACY_TIMING
    const float ratio=500.0f/16.0f/8.0f;
    mipi_dsi_host_ll_dpi_set_horizontal_timing(MIPI_DSI_LL_GET_HOST(0),
        (uint32_t)(4*ratio),(uint32_t)(20*ratio),
        (uint32_t)(480*ratio),(uint32_t)(10*ratio));
    ESP_LOGI("lcd","Using IDF5.4.1 host timing calculation: 15/78/1875/39");
#endif
    ESP_LOGI("lcd","Bridge pixel format register=%08lx, horizontal=%08lx/%08lx",
        (unsigned long)MIPI_DSI_LL_GET_BRG(0)->pixel_type.val,
        (unsigned long)MIPI_DSI_LL_GET_BRG(0)->dpi_h_cfg0.val,
        (unsigned long)MIPI_DSI_LL_GET_BRG(0)->dpi_h_cfg1.val);
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_sleep(panel,false));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel,true));
    return panel;
}
#endif
