# INPUT-004: ESP-IDF 5.5.5 (Apache-2.0), commit
# b774170ff46c393eeb5e495ea37936038d3f4f4f, prints EP0 Error/STALL synchronously
# from the USB ISR through ESP_EARLY_LOGE. USB and rolling HDMI IRQs share core1
# in the matched P4-PC composition. ISR output is a source-supported scheduling
# risk; it is not yet the measured cause of the retained hotplug scanout fault.
# Keep all transport/error actions and notification semantics, adding pending
# log bits to the existing action batch. Print only in usbh_process task context
# after its lock is released, before any action can free the device. Same-kind
# errors coalesce within a pending batch, as existing action flags already do.
# Generate a derivative; never edit the SDK. Remove after qualifying an upstream
# replacement with task-owned error reporting, or after this bounded remedy is
# superseded. No transfer timing, retry, affinity, allocation or ABI change.
if(NOT DEFINED USBH_SOURCE)
  idf_component_get_property(usbh_dir usb COMPONENT_DIR)
  idf_component_get_property(usbh_target usb COMPONENT_LIB)
  set(USBH_SOURCE "${usbh_dir}/usbh.c")
  set(USBH_OUTPUT "${CMAKE_BINARY_DIR}/agon-extender-usb/usbh.c")
endif()
file(SHA256 "${USBH_SOURCE}" usbh_original_sha)
if(NOT usbh_original_sha STREQUAL "0c6e108d5ce61e7325da6b5d33fff603a0644bd033426e52ba8506fc7067a061")
  message(FATAL_ERROR "Unreviewed USBH source; EP0 task-logging patch refused")
endif()
file(READ "${USBH_SOURCE}" usbh_patched)
function(usb_ep0_replace_once label before after)
  string(FIND "${usbh_patched}" "${before}" position)
  if(position LESS 0)
    message(FATAL_ERROR "Expected USBH ${label} is absent")
  endif()
  string(LENGTH "${before}" before_length)
  math(EXPR remainder_start "${position}+${before_length}")
  string(SUBSTRING "${usbh_patched}" ${remainder_start} -1 remainder)
  string(FIND "${remainder}" "${before}" duplicate)
  if(NOT duplicate LESS 0)
    message(FATAL_ERROR "Expected exactly one USBH ${label}")
  endif()
  string(REPLACE "${before}" "${after}" result "${usbh_patched}")
  set(usbh_patched "${result}" PARENT_SCOPE)
endfunction()

set(usbh_before [=[    DEV_ACTION_PROP_NEW_DEV         = (1 << 6),     // Propagate a USBH_EVENT_NEW_DEV event
]=])
set(usbh_after [=[    DEV_ACTION_PROP_NEW_DEV         = (1 << 6),     // Propagate a USBH_EVENT_NEW_DEV event
    // Extender INPUT-004: diagnostics run first; original action bit values/order stay unchanged.
    DEV_ACTION_EP0_LOG_ERROR        = (1 << 7),     // Task-owned EP0 error message
    DEV_ACTION_EP0_LOG_STALL        = (1 << 8),     // Task-owned EP0 STALL message
]=])
usb_ep0_replace_once("pending log bits" "${usbh_before}" "${usbh_after}")

set(usbh_before [=[        action_flags = DEV_ACTION_EP0_FLUSH |
                       DEV_ACTION_EP0_DEQUEUE |
                       DEV_ACTION_EP0_CLEAR;
        if (in_isr) {
            ESP_EARLY_LOGE(USBH_TAG, "Dev %d EP 0 Error", dev_obj->constant.address);
        } else {
            ESP_LOGE(USBH_TAG, "Dev %d EP 0 Error", dev_obj->constant.address);
        }
]=])
set(usbh_after [=[        action_flags = DEV_ACTION_EP0_FLUSH |
                       DEV_ACTION_EP0_DEQUEUE |
                       DEV_ACTION_EP0_CLEAR |
                       DEV_ACTION_EP0_LOG_ERROR;
]=])
usb_ep0_replace_once("EP0 error deferral" "${usbh_before}" "${usbh_after}")

set(usbh_before [=[        action_flags = DEV_ACTION_EP0_DEQUEUE | DEV_ACTION_EP0_CLEAR;
        if (in_isr) {
            ESP_EARLY_LOGE(USBH_TAG, "Dev %d EP 0 STALL", dev_obj->constant.address);
        } else {
            ESP_LOGE(USBH_TAG, "Dev %d EP 0 STALL", dev_obj->constant.address);
        }
]=])
set(usbh_after [=[        action_flags = DEV_ACTION_EP0_DEQUEUE | DEV_ACTION_EP0_CLEAR |
                       DEV_ACTION_EP0_LOG_STALL;
]=])
usb_ep0_replace_once("EP0 STALL deferral" "${usbh_before}" "${usbh_after}")

set(usbh_before [=[        USBH_EXIT_CRITICAL();
        ESP_LOGD(USBH_TAG, "Processing actions 0x%"PRIx32"", action_flags);
]=])
set(usbh_after [=[        USBH_EXIT_CRITICAL();
        // Extender INPUT-004: task context, outside the USBH lock and before device actions/free.
        // Repeated same-kind events coalesce per pending action batch; both kinds remain visible.
        if (action_flags & DEV_ACTION_EP0_LOG_ERROR) {
            ESP_LOGE(USBH_TAG, "Dev %d EP 0 Error", dev_obj->constant.address);
        }
        if (action_flags & DEV_ACTION_EP0_LOG_STALL) {
            ESP_LOGE(USBH_TAG, "Dev %d EP 0 STALL", dev_obj->constant.address);
        }
        ESP_LOGD(USBH_TAG, "Processing actions 0x%"PRIx32"", action_flags);
]=])
usb_ep0_replace_once("task-owned EP0 publication" "${usbh_before}" "${usbh_after}")

string(SHA256 usbh_derivative_sha "${usbh_patched}")
if(NOT usbh_derivative_sha STREQUAL "326a2505bebb74d21962da7191b7807e999f7b8ee85cfe993c852a828b1cfde3")
  message(FATAL_ERROR "USBH derivative differs from the reviewed EP0 task-logging patch")
endif()
get_filename_component(usbh_output_dir "${USBH_OUTPUT}" DIRECTORY)
file(MAKE_DIRECTORY "${usbh_output_dir}")
file(WRITE "${USBH_OUTPUT}" "${usbh_patched}")
message(STATUS "Extender USBH EP0 task-logging derivative SHA256 ${usbh_derivative_sha}")
if(DEFINED usbh_target)
  get_target_property(usbh_sources "${usbh_target}" SOURCES)
  set(usbh_selected_sources)
  set(usbh_replacements 0)
  foreach(source IN LISTS usbh_sources)
    if(IS_ABSOLUTE "${source}")
      set(absolute_source "${source}")
    else()
      set(absolute_source "${usbh_dir}/${source}")
    endif()
    if(absolute_source STREQUAL USBH_SOURCE)
      list(APPEND usbh_selected_sources "${USBH_OUTPUT}")
      math(EXPR usbh_replacements "${usbh_replacements}+1")
    else()
      list(APPEND usbh_selected_sources "${source}")
    endif()
  endforeach()
  if(NOT usbh_replacements EQUAL 1)
    message(FATAL_ERROR "Expected exactly one selected USBH translation unit")
  endif()
  set_property(TARGET "${usbh_target}" PROPERTY SOURCES "${usbh_selected_sources}")
endif()
