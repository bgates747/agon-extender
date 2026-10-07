# P4-PC experiment: ESP-IDF 5.5.5 (Apache-2.0), commit
# b774170ff46c393eeb5e495ea37936038d3f4f4f, lacks usb_host_config_t.fsls_only.
# Its host stack rejects FS/LS devices behind an HS hub (BOARD-001 serial proof).
# Backport the current Espressif HAL ordering: set HCFG.FSLSSupp immediately
# before asserting each root-port reset, only on the HS-capable controller.
# Reference: esp-idf/components/esp_hal_usb/usb_dwc_hal.c,
# usb_dwc_hal_port_toggle_reset(), reviewed 2026-10-04.
# https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html#full-low-speed-only-host
# Generate a derivative; never edit the SDK. Remove after upgrading to an SDK
# with the public fsls_only setting and qualifying that replacement on P4-PC.
# This limits the onboard hub's upstream link to 12 Mbit/s; wiring is unchanged.
if(NOT DEFINED USB_HCD_SOURCE)
  idf_component_get_property(usb_dir usb COMPONENT_DIR)
  idf_component_get_property(usb_target usb COMPONENT_LIB)
  set(USB_HCD_SOURCE "${usb_dir}/hcd_dwc.c")
  set(USB_HCD_OUTPUT "${CMAKE_BINARY_DIR}/agon-extender-usb/hcd_dwc.c")
endif()
file(SHA256 "${USB_HCD_SOURCE}" original_sha)
if(NOT original_sha STREQUAL "33fea9059ee546d1c773fc5e86ed0c294e600e645c4c14e0788ce879f596280b")
  message(FATAL_ERROR "Unreviewed USB HCD source; FSLS patch refused")
endif()
file(READ "${USB_HCD_SOURCE}" original)
set(before "    usb_dwc_hal_port_toggle_reset(port->hal, true);")
set(after "    // Extender P4-PC: IDF 5.5.5 FSLS-only backport; see native/usb_fsls_only.cmake.\n    if (port->hal->constant_config.hsphy_type != 0) {\n        usb_dwc_ll_hcfg_set_fsls_supp_only(port->hal->dev);\n    }\n    usb_dwc_hal_port_toggle_reset(port->hal, true);")
string(FIND "${original}" "${before}" position)
if(position LESS 0)
  message(FATAL_ERROR "Expected USB root-port reset is absent")
endif()
string(REPLACE "${before}" "${after}" patched "${original}")
get_filename_component(output_dir "${USB_HCD_OUTPUT}" DIRECTORY)
file(MAKE_DIRECTORY "${output_dir}")
file(WRITE "${USB_HCD_OUTPUT}" "${patched}")
file(SHA256 "${USB_HCD_OUTPUT}" patched_sha)
message(STATUS "Extender USB FSLS derivative SHA256 ${patched_sha}")
if(DEFINED usb_target)
  get_target_property(usb_sources "${usb_target}" SOURCES)
  set(selected_sources)
  set(replacements 0)
  foreach(source IN LISTS usb_sources)
    if(IS_ABSOLUTE "${source}")
      set(absolute_source "${source}")
    else()
      set(absolute_source "${usb_dir}/${source}")
    endif()
    if(absolute_source STREQUAL USB_HCD_SOURCE)
      list(APPEND selected_sources "${USB_HCD_OUTPUT}")
      math(EXPR replacements "${replacements}+1")
    else()
      list(APPEND selected_sources "${source}")
    endif()
  endforeach()
  if(NOT replacements EQUAL 1)
    message(FATAL_ERROR "Expected exactly one selected USB HCD translation unit")
  endif()
  set_property(TARGET "${usb_target}" PROPERTY SOURCES "${selected_sources}")
endif()
