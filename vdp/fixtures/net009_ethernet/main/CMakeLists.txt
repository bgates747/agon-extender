idf_component_register(SRCS "main.cpp" "transfer.cpp" INCLUDE_DIRS "." "../../esp8266_uart/main"
  REQUIRES esp_eth esp_netif esp_event esp_timer esp_driver_usb_serial_jtag vfs lwip)
target_compile_features(${COMPONENT_LIB} PRIVATE cxx_std_17)
target_compile_definitions(${COMPONENT_LIB} PRIVATE NET009_SOURCE_COMMIT="${NET009_SOURCE_COMMIT}")
