cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED AGON_COMPONENT_DIR OR NOT EXISTS "${AGON_COMPONENT_DIR}/CMakeLists.txt")
  message(FATAL_ERROR "AGON_COMPONENT_DIR must name a generated component")
endif()
if(NOT DEFINED AGON_DEPENDENCIES_LOCK)
  message(FATAL_ERROR "AGON_DEPENDENCIES_LOCK is required")
endif()
if(NOT DEFINED AGON_VDP_ROOT OR NOT EXISTS "${AGON_VDP_ROOT}/partitions.csv")
  message(FATAL_ERROR "AGON_VDP_ROOT must name the maintained VDP source root")
endif()

set(EXTRA_COMPONENT_DIRS "${AGON_COMPONENT_DIR}")
if(DEFINED AGON_HDMI_COMPONENT_DIR)
  if(NOT EXISTS "${AGON_HDMI_COMPONENT_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "AGON_HDMI_COMPONENT_DIR must name the pinned bridge component")
  endif()
  list(APPEND EXTRA_COMPONENT_DIRS "${AGON_HDMI_COMPONENT_DIR}")
endif()
set(DEPENDENCIES_LOCK "${AGON_DEPENDENCIES_LOCK}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
# PlatformIO's hybrid driver omitted -Wall from managed components even though
# the shared sdkconfig disables default warnings-as-errors. Native IDF enables
# a GCC 14 false-positive in esp-modbus 2.1.3; suppress only that diagnostic so
# the retained, exactly pinned dependency builds without patching vendor code.
add_compile_options(-Wno-stringop-truncation)
idf_build_set_property(DEPENDENCIES_LOCK "${DEPENDENCIES_LOCK}")
project(agon_extender)

if(AGON_ROLLING_SCANOUT)
  include("${AGON_VDP_ROOT}/video/extender/display/rolling/strip_driver.cmake")
endif()

if(AGON_DSP_LIFETIME_FIX)
  include("${AGON_VDP_ROOT}/pio/dsp_matrix_lifetime.cmake")
endif()

if(AGON_USB_FSLS_ONLY)
  include("${AGON_VDP_ROOT}/native/usb_fsls_only.cmake")
  idf_component_get_property(agon_target agon_vdp COMPONENT_LIB)
  target_compile_definitions(${agon_target} PRIVATE AGON_EXTENDER_USB_FSLS_ONLY=1)
endif()
