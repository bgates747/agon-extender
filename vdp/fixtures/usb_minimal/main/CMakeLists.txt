idf_component_register(SRCS "usb_minimal.cpp"
                       INCLUDE_DIRS "${USB_MINIMAL_GENERATED_DIR}"
                       REQUIRES usb_host_hid usb esp_driver_gpio esp_driver_usb_serial_jtag esp_timer)
target_compile_features(${COMPONENT_LIB} PRIVATE cxx_std_17)
