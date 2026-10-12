idf_component_register(SRCS "main.c" "cpu.cpp" INCLUDE_DIRS "."
    PRIV_REQUIRES esp_driver_ppa esp_mm esp_psram esp_timer nvs_flash)
