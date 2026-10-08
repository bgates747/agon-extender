// Additive read-only browser metadata; independent of video/keyboard ownership.
#pragma once
#include "extender/display/mode_status.hpp"
#include <cstdio>
#include <esp_http_server.h>
#ifdef AGON_EXTENDER_HDMI
#include "extender/display/hdmi_output.hpp"
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
#include "extender/display/rgb888_pixel.hpp"
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "extender/display/rolling/strip_probe.h"
#include "esp_heap_caps.h"
#endif
namespace agon::extender::display_status {
inline esp_err_t handle(httpd_req_t *request) {
  display::ModeStatus value{};
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  httpd_resp_set_type(request,"application/json");
  if (!display::modeStatus.read(value)) {
    httpd_resp_set_status(request,"503 Service Unavailable");
    return httpd_resp_sendstr(request,"{\"available\":false}");
  }
#ifdef AGON_EXTENDER_HDMI
  const unsigned outputSize=display::hdmiOutput().outputSize();
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  // HDMI02-F: read-only fault evidence must remain reachable if a stopped DMA
  // prevents the output worker reaching its normal periodic serial report.
  strip_probe_stats strips{}; strip_async_stats copy{};
  strip_probe_read(&strips); strip_async_read(&copy);
  strip_fault_stats fault{}; strip_fault_read(&fault);
#endif
  char body[1024];
  const int length=snprintf(body,sizeof(body),
      "{\"available\":true,\"mode\":%u,\"width\":%u,\"height\":%u,"
      "\"colors\":%u,\"refresh_hz\":%u,\"double_buffered\":%s"
#if defined(AGON_EXTENDER_HDMI)
      ",\"output\":\"hdmi\",\"output_width\":%d,\"output_height\":%d,"
      "\"output_nominal_refresh_hz\":60,\"frame_clock\":\"dma-frame-complete\""
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
      ",\"render_storage\":\"%s\",\"render_memory\":\"%s\""
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      ",\"rolling\":{\"frames\":%u,\"faults\":%u,\"late\":%u,"
      "\"over_budget\":%u,\"underruns\":%u,\"refill_max_us\":%u,\"free_internal\":%u,"
      "\"invalid_blocks\":%u,\"sequence_errors\":%u,\"cache_errors\":%u,\"overlap\":%u,"
      "\"first_fault\":%u,\"first_error\":%u,\"queued\":%u,\"queue_wait_max_us\":%u}"
#endif
      "}",
      value.mode,value.width,value.height,value.colors,value.refresh_hz,
      value.double_buffered?"true":"false"
#ifdef AGON_EXTENDER_HDMI
      ,int(outputSize >> 16),int(outputSize & 65535)
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"rgb888":"native"
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"panel-direct":"native"
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      ,unsigned(strips.frames),unsigned(copy.faults),unsigned(copy.late),
      unsigned(strips.over_budget),unsigned(strips.underruns),unsigned(strips.max_us),
      unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
      unsigned(strips.invalid),unsigned(strips.sequence_errors),unsigned(strips.cache_errors),
      unsigned(copy.overlap),unsigned(fault.first_fault),unsigned(fault.first_error),
      unsigned(fault.queued),unsigned(fault.queue_wait_max_us)
#endif
      );
  if (length<0 || length>=int(sizeof(body)))
    return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Display status overflow");
  return httpd_resp_send(request,body,length);
}
}
