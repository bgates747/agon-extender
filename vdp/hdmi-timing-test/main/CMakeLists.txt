# IDF extracts component dependencies in a separate script invocation. The
# frozen build selection is also visible there before normal project flags.
if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/../mode0-probe.enabled")
    set(pattern_source "../mode0/mode0_pattern.c")
    set(artwork EMBED_FILES "../mode0/mode0_rgba2222.bin")
else()
    set(pattern_source "../pattern.c")
endif()
if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/../pair-probe.enabled" OR EXISTS "${CMAKE_CURRENT_LIST_DIR}/../mode0-probe.enabled")
    set(pair_console_component esp_driver_usb_serial_jtag esp_driver_gpio vfs)
endif()
idf_component_register(SRCS "main.c" "${pattern_source}" ${artwork}
    INCLUDE_DIRS ".."
    PRIV_REQUIRES esp_lcd esp_driver_i2c esp_lcd_lt8912b esp_hw_support
                  esp_timer esp_mm esp_driver_ppa ${pair_console_component})
