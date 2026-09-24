# Existing HDMI driver path

## Executive summary

Use the existing Espressif LT8912B driver and Olimex board integration as the
starting point. No custom HDMI signalling or bridge-register implementation is
needed merely to obtain output. This is a research finding, not a tested EDP
integration or permission to replace the current renderer.

## Located implementations

1. Espressif publishes [esp_lcd_lt8912b](https://components.espressif.com/components/espressif/esp_lcd_lt8912b/versions/0.2.1/readme),
registry version0.2.1 at review. It integrates the LT8912B MIPI-DSI-to-HDMI bridge
with esp_lcd; register control uses I2C. Driver documentation specifies RGB888.
2. Olimex's pinned repository already includes driver version0.2.0 under
`SOFTWARE/ESP-IDF/p4_production_test/components/esp-bsp/components/lcd/esp_lcd_lt8912b/`.
Its manifest requires ESP-IDF>=5.3. The production-test README identifies IDF5.5
as its tested environment. This copied package's exact identity is bounded by
Olimex commit89a7b96e2ec4c3f28b55d768dfda3ba8a86846bd; do not assume pristine
identity to an Espressif release solely from its version string.
3. The same tree's `bsp/esp32_p4_function_ev_board/esp32_p4_function_ev_board.c`
contains the actual bridge/panel initialization, I2C IO handles, DSI/DPI setup
and timing presets. Despite the generic BSP directory name, inspect Olimex's
copy and board schematic before adopting GPIO/power settings. It invokes
`esp_lcd_new_panel_lt8912b`. Olimex's committed sdkconfig selects1280x720@60Hz.
4. `components/pt_display/` and `main/main.c` supply the HDMI/LVGL production-test
application. LVGL is the example renderer, not a requirement to replace EDP's
stock-derived drawing implementation. Reuse driver/panel initialization beneath
EDP's final-output adapter, subject to a future integration contract.

## Integration boundaries

EDP retains stock-compatible framebuffer/rendering semantics. The output adapter
must supply the driver's required RGB888 output representation, including sprite
and Copper composition; do not change internal framebuffer format merely to
match the display driver. Scaling, output timing selection, buffering, ownership,
DMA/cache coherency and presentation completion need an explicit design/test
before integration. A working vendor test does not establish Agon60Hz gameplay.

The board's HDMI bridge is an output transport, not a sprite/Copper renderer.
No claim of simultaneous independent DSI LCD and HDMI output is made. First
board validation should reproduce the unmodified Olimex HDMI test before EDP
integration, after separate bench authorization. No builds or flashes performed.
