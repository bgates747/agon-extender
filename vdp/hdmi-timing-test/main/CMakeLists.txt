idf_component_register(SRCS "main.c" "../pattern.c"
    INCLUDE_DIRS ".."
    PRIV_REQUIRES esp_lcd esp_driver_i2c esp_lcd_lt8912b esp_hw_support
                  esp_timer esp_mm)
