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
# INPUT-004 also retains one failed LS-control stage/HAL reason per pipe until
# task-context URB dequeue. The ISR only copies scalar data under the existing
# HCD lock; no successful-stage/report logging or added transfer delays.
# Remove this diagnostic after the LS enumeration cause is established and
# durable error reporting replaces it, or when replacing the pinned HCD.
# Independently backport the missing non-control IN pre-DMA cache clean from
# espressif/esp-usb 630f1c4e61f71d62bb57ff1b840931da24c3329f (USB 1.6.0):
# https://github.com/espressif/esp-usb/blob/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb/src/hcd_dwc.c
# This is not a diagnosis of the initial EP0 failure: CTRL was already synced.
# Remove the cache backport after selecting and qualifying an SDK containing it.
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
set(patched "${original}")
function(usb_hcd_replace_once label before after)
  string(FIND "${patched}" "${before}" position)
  if(position LESS 0)
    message(FATAL_ERROR "Expected USB HCD ${label} is absent")
  endif()
  string(LENGTH "${before}" before_length)
  math(EXPR remainder_start "${position}+${before_length}")
  string(SUBSTRING "${patched}" ${remainder_start} -1 remainder)
  string(FIND "${remainder}" "${before}" duplicate)
  if(NOT duplicate LESS 0)
    message(FATAL_ERROR "Expected exactly one USB HCD ${label}")
  endif()
  string(REPLACE "${before}" "${after}" result "${patched}")
  set(patched "${result}" PARENT_SCOPE)
endfunction()

set(before "    usb_dwc_hal_port_toggle_reset(port->hal, true);")
set(after "    // Extender P4-PC: IDF 5.5.5 FSLS-only backport; see native/usb_fsls_only.cmake.\n    if (port->hal->constant_config.hsphy_type != 0) {\n        usb_dwc_ll_hcfg_set_fsls_supp_only(port->hal->dev);\n    }\n    usb_dwc_hal_port_toggle_reset(port->hal, true);")
usb_hcd_replace_once("root-port reset" "${before}" "${after}")

set(before "    if ((is_in == done) || is_ctrl) {")
set(after [=[    // Espressif USB 1.6.0/630f1c4: clean every buffer before DMA, including IN.
    // CTRL was already cleaned; this independent fix does not diagnose LS EP0.
    if (!done || is_in || is_ctrl) {]=])
usb_hcd_replace_once("pre-DMA cache ownership" "${before}" "${after}")

set(before "struct pipe_obj {")
set(after [=[// Extender INPUT-004: one failed LS-control URB, protected by the HCD lock.
// No key/report bytes; consumed by matching task-context dequeue before reuse.
typedef struct {
    urb_t *urb;
    uint16_t frame;
    uint8_t stage;
    uint8_t hal_error;
} extender_ls_error_t;

struct pipe_obj {
    extender_ls_error_t extender_ls_error;]=])
usb_hcd_replace_once("private LS diagnostic storage" "${before}" "${after}")

set(before [=[        usb_dwc_hal_chan_error_t chan_error = usb_dwc_hal_chan_get_error(chan_obj);
        pipe->last_event = pipe_decode_error_event(chan_error);]=])
set(after [=[        usb_dwc_hal_chan_error_t chan_error = usb_dwc_hal_chan_get_error(chan_obj);
        // Extender INPUT-004: capture only failed LS control traffic, under ISR HCD lock.
        // _buffer_parse clears the stage; defer all logging until task-context dequeue.
        if (pipe->ep_char.type == USB_DWC_XFER_TYPE_CTRL && pipe->ep_char.ls_via_fs_hub) {
            dma_buffer_block_t *failed = pipe->buffers[pipe->multi_buffer_control.rd_idx];
            pipe->extender_ls_error.urb = failed->urb;
            pipe->extender_ls_error.stage = failed->flags.ctrl.cur_stg;
            pipe->extender_ls_error.hal_error = chan_error;
            pipe->extender_ls_error.frame = usb_dwc_hal_port_get_cur_frame_num(pipe->port->hal);
        }
        pipe->last_event = pipe_decode_error_event(chan_error);]=])
usb_hcd_replace_once("LS error ISR snapshot" "${before}" "${after}")

set(before [=[urb_t *hcd_urb_dequeue(hcd_pipe_handle_t pipe_hdl)
{
    pipe_t *pipe = (pipe_t *)pipe_hdl;
    urb_t *urb;
]=])
set(after [=[urb_t *hcd_urb_dequeue(hcd_pipe_handle_t pipe_hdl)
{
    pipe_t *pipe = (pipe_t *)pipe_hdl;
    urb_t *urb;
    extender_ls_error_t ls_error = {0};
    usb_dwc_hal_ep_char_t ls_ep_char = {0};
    usb_speed_t ls_port_speed = USB_SPEED_LOW;
]=])
usb_hcd_replace_once("LS dequeue local snapshot" "${before}" "${after}")

set(before [=[        urb = TAILQ_FIRST(&pipe->done_urb_tailq);
        TAILQ_REMOVE(&pipe->done_urb_tailq, urb, tailq_entry);
]=])
set(after [=[        urb = TAILQ_FIRST(&pipe->done_urb_tailq);
        // Extender INPUT-004: copy/consume only the diagnosed URB under the HCD lock.
        if (pipe->extender_ls_error.urb == urb) {
            ls_error = pipe->extender_ls_error;
            ls_ep_char = pipe->ep_char;
            ls_port_speed = pipe->port->speed;
            pipe->extender_ls_error.urb = NULL;
        }
        TAILQ_REMOVE(&pipe->done_urb_tailq, urb, tailq_entry);
]=])
usb_hcd_replace_once("LS diagnosed URB ownership" "${before}" "${after}")

set(before [=[    HCD_EXIT_CRITICAL();
    return urb;
}
]=])
set(after [=[    HCD_EXIT_CRITICAL();
    // Extender INPUT-004: task context, outside HCD lock, detached scalar copies only.
    if (ls_error.urb != NULL) {
        ESP_LOGE(HCD_DWC_TAG, "LS control failed: addr=%u ep=%u port_speed=%u ls_pre=%u mps=%u stage=%u hal_error=%u frame=%u",
                 (unsigned)ls_ep_char.dev_addr, (unsigned)ls_ep_char.bEndpointAddress,
                 (unsigned)ls_port_speed, (unsigned)ls_ep_char.ls_via_fs_hub,
                 (unsigned)ls_ep_char.mps, (unsigned)ls_error.stage,
                 (unsigned)ls_error.hal_error, (unsigned)ls_error.frame);
    }
    return urb;
}
]=])
usb_hcd_replace_once("LS task-context publication" "${before}" "${after}")
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
  # Native USB selection also defers upstream EP0 ISR logging. Standalone HCD
  # recipe checks supply USB_HCD_SOURCE and do not select another SDK unit.
  include("${CMAKE_CURRENT_LIST_DIR}/usb_ep0_task_logging.cmake")
endif()
