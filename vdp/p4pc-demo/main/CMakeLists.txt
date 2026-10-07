idf_component_register(SRCS "main.c" "render_reference.c" INCLUDE_DIRS "."
    REQUIRES esp32_p4_function_ev_board lvgl esp_timer esp_driver_usb_serial_jtag
             sd_card_test lan_test esp_codec_dev esp_app_format)
# P4PC-001: LVGL 9.6.0~1 sizes TLSF's maximum pool at compile time.
# r06's inherited 64 KiB exhausted; r07's runtime 1 MiB addition was rejected.
# Configure 1 MiB in prepare.py and allocate dynamically: the fixed IDF
# SPIRAM_USE_MALLOC/ALWAYSINTERNAL=16384 settings place this large allocation
# in PSRAM. Avoid a 1 MiB internal static array; retain measured pool headroom.
idf_component_get_property(playground_lvgl_lib lvgl__lvgl COMPONENT_LIB)
target_compile_definitions(${playground_lvgl_lib} PRIVATE
    LV_MEM_POOL_ALLOC=malloc LV_MEM_POOL_INCLUDE="stdlib.h")
