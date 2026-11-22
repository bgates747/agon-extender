# IDF extracts component dependencies in a separate script invocation. The
# frozen build selection is also visible there before normal project flags.
if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/../pair-probe.enabled")
    set(pair_console_component esp_driver_usb_serial_jtag esp_driver_gpio)
endif()
idf_component_register(SRCS "main.c" "../pattern.c"
    INCLUDE_DIRS ".."
    PRIV_REQUIRES esp_lcd esp_driver_i2c esp_lcd_lt8912b esp_hw_support
                  esp_timer esp_mm esp_driver_ppa ${pair_console_component})
