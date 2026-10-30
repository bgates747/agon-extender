# INPUT-004: ESP-IDF 5.5.5 USB host initializes only one selected PHY.
# Backport Espressif esp-usb PR402 / 48b250fa36e92c64a37c333dc548c84cb48c6eac
# (Apache-2.0) into generated output, retaining the pinned SDK/HCD/HAL.
# https://github.com/espressif/esp-usb/pull/402
# Adaptations for this older source: SOC_USB_OTG_PERIPH_NUM replaces the later
# HCD_NUM_PORTS alias; existing calloc supplies zero handles; preserve this
# version's separate HCD uninstall labels and release PHYs on partial init.
# Default FIFOs/common interrupt priority match upstream's initial dual API.
# Remove after selecting and qualifying an SDK with native dual-host support.
if(NOT DEFINED USB_DUAL_SOURCE)
  idf_component_get_property(usb_dual_dir usb COMPONENT_DIR)
  idf_component_get_property(usb_dual_target usb COMPONENT_LIB)
  set(USB_DUAL_SOURCE "${usb_dual_dir}/usb_host.c")
  set(USB_DUAL_OUTPUT "${CMAKE_BINARY_DIR}/agon-extender-usb/usb_host.c")
endif()
file(SHA256 "${USB_DUAL_SOURCE}" original_sha)
if(NOT original_sha STREQUAL "90c363001ce460d2d1648db89f2db4a7aab126446ce2f6840e27c462a009f83f")
  message(FATAL_ERROR "Unreviewed USB host source; dual-host backport refused")
endif()
get_filename_component(usb_dual_output_dir "${USB_DUAL_OUTPUT}" DIRECTORY)
file(MAKE_DIRECTORY "${usb_dual_output_dir}")
set(usb_dual_patch "${CMAKE_CURRENT_LIST_DIR}/../compat/usb_dual_host/usb_host.patch")
execute_process(COMMAND patch --batch --fuzz=0 --silent --output "${USB_DUAL_OUTPUT}"
                "${USB_DUAL_SOURCE}" "${usb_dual_patch}"
                RESULT_VARIABLE patch_result OUTPUT_VARIABLE patch_stdout ERROR_VARIABLE patch_stderr)
if(NOT patch_result EQUAL 0)
  file(REMOVE "${USB_DUAL_OUTPUT}")
  message(FATAL_ERROR "Bounded USB dual-host patch failed: ${patch_stdout} ${patch_stderr}")
endif()
file(SHA256 "${USB_DUAL_OUTPUT}" patched_sha)
message(STATUS "Extender USB dual-host derivative SHA256 ${patched_sha}")
if(DEFINED usb_dual_target)
  get_target_property(usb_dual_sources "${usb_dual_target}" SOURCES)
  set(usb_dual_selected)
  set(usb_dual_replacements 0)
  foreach(source IN LISTS usb_dual_sources)
    if(IS_ABSOLUTE "${source}")
      set(absolute_source "${source}")
    else()
      set(absolute_source "${usb_dual_dir}/${source}")
    endif()
    if(absolute_source STREQUAL USB_DUAL_SOURCE)
      list(APPEND usb_dual_selected "${USB_DUAL_OUTPUT}")
      math(EXPR usb_dual_replacements "${usb_dual_replacements}+1")
    else()
      list(APPEND usb_dual_selected "${source}")
    endif()
  endforeach()
  if(NOT usb_dual_replacements EQUAL 1)
    message(FATAL_ERROR "Expected exactly one selected USB host translation unit")
  endif()
  set_property(TARGET "${usb_dual_target}" PROPERTY SOURCES "${usb_dual_selected}")
endif()
