// Additive read-only browser metadata; independent of video/keyboard ownership.
#pragma once
#include "extender/display/mode_status.hpp"
#include <cstdio>
#include <esp_http_server.h>
#ifdef AGON_EXTENDER_DIRECT_RGB888
#include "extender/display/rgb888_pixel.hpp"
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
  char body[384];
  const int length=snprintf(body,sizeof(body),
      "{\"available\":true,\"mode\":%u,\"width\":%u,\"height\":%u,"
      "\"colors\":%u,\"refresh_hz\":%u,\"double_buffered\":%s"
#if defined(AGON_EXTENDER_HDMI)
      ",\"output\":\"hdmi\",\"output_width\":1280,\"output_height\":720,"
      "\"output_nominal_refresh_hz\":60,\"frame_clock\":\"dma-frame-complete\""
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
      ",\"render_storage\":\"%s\",\"render_memory\":\"%s\""
#endif
      "}",
      value.mode,value.width,value.height,value.colors,value.refresh_hz,
      value.double_buffered?"true":"false"
#ifdef AGON_EXTENDER_DIRECT_RGB888
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"rgb888":"native"
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"panel-direct":"native"
#endif
      );
  return httpd_resp_send(request,body,length);
}
}
