cmake_minimum_required(VERSION 3.16)

# INPUT-004 diagnostic firmware, not the Extender product build. The host builder
# supplies identity/board constants from maintained inputs and vendors the exact
# pristine HID 1.2.1 component into components/usb_host_hid with dependency
# resolution disabled. Never read a machine-local board identity from this tree.
foreach(required USB_MINIMAL_BUILD_ID USB_MINIMAL_SOURCE_COMMIT
                 USB_MINIMAL_HUB_RESET_GPIO USB_MINIMAL_HUB_ASSERT_MS
                 USB_MINIMAL_HUB_RECOVERY_MS)
  if(NOT DEFINED ${required} OR "${${required}}" STREQUAL "")
    message(FATAL_ERROR "Explicit ${required} is required")
  endif()
endforeach()
if(NOT USB_MINIMAL_BUILD_ID MATCHES "^[A-Za-z0-9._-]+$")
  message(FATAL_ERROR "USB_MINIMAL_BUILD_ID must be a plain identified build name")
endif()
string(LENGTH "${USB_MINIMAL_SOURCE_COMMIT}" commit_length)
if(NOT commit_length EQUAL 40 OR NOT USB_MINIMAL_SOURCE_COMMIT MATCHES "^[0-9a-fA-F]+$")
  message(FATAL_ERROR "USB_MINIMAL_SOURCE_COMMIT must be the full source commit")
endif()
foreach(value USB_MINIMAL_HUB_RESET_GPIO USB_MINIMAL_HUB_ASSERT_MS USB_MINIMAL_HUB_RECOVERY_MS)
  if(NOT "${${value}}" MATCHES "^[0-9]+$")
    message(FATAL_ERROR "${value} must be an unsigned decimal integer")
  endif()
endforeach()
if(USB_MINIMAL_HUB_RESET_GPIO GREATER 54 OR USB_MINIMAL_HUB_ASSERT_MS LESS 1 OR
   USB_MINIMAL_HUB_ASSERT_MS GREATER 1000 OR USB_MINIMAL_HUB_RECOVERY_MS LESS 1 OR
   USB_MINIMAL_HUB_RECOVERY_MS GREATER 1000)
  message(FATAL_ERROR "Board hub constants are outside the bounded P4 fixture contract")
endif()
if(NOT "$ENV{IDF_COMPONENT_MANAGER}" STREQUAL "0")
  message(FATAL_ERROR "Set IDF_COMPONENT_MANAGER=0; use the reviewed local HID component")
endif()
set(hid_manifest "${CMAKE_CURRENT_LIST_DIR}/components/usb_host_hid/idf_component.yml")
if(NOT EXISTS "${hid_manifest}")
  message(FATAL_ERROR "Builder must supply pristine pinned components/usb_host_hid")
endif()
file(READ "${hid_manifest}" hid_metadata)
if(NOT hid_metadata MATCHES "version: ['\"]?1\\.2\\.1['\"]?([\r\n]|$)")
  message(FATAL_ERROR "Only pristine USB Host HID 1.2.1 is selected")
endif()

set(USB_MINIMAL_GENERATED_DIR "${CMAKE_BINARY_DIR}/usb-minimal-generated")
file(MAKE_DIRECTORY "${USB_MINIMAL_GENERATED_DIR}")
configure_file("${CMAKE_CURRENT_LIST_DIR}/usb_minimal_config.h.in"
               "${USB_MINIMAL_GENERATED_DIR}/usb_minimal_config.h" @ONLY)
set(COMPONENTS main) # Only the fixture and its transitive SDK/HID dependencies.
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(extender_usb_minimal)
if(NOT IDF_TARGET STREQUAL "esp32p4" OR NOT CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG OR
   NOT CONFIG_ESP_CONSOLE_SECONDARY_NONE OR NOT CONFIG_USB_HOST_HUBS_SUPPORTED)
  message(FATAL_ERROR "Fixture requires P4, USB Serial/JTAG-only console and onboard hub support")
endif()
if(CONFIG_ESP_COREDUMP_ENABLE_TO_FLASH)
  message(FATAL_ERROR "Fixture must not write a coredump partition")
endif()
include("${CMAKE_CURRENT_LIST_DIR}/fsls_only.cmake")
