idf_component_register(SRCS "probe.cpp" INCLUDE_DIRS "."
  REQUIRES esp_driver_uart esp_driver_gpio esp_driver_usb_serial_jtag esp_timer esp_hw_support vfs)
target_compile_features(${COMPONENT_LIB} PRIVATE cxx_std_17)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  NET008_BUILD_ID="${NET008_BUILD_ID}" NET008_SOURCE_COMMIT="${NET008_SOURCE_COMMIT}")
