// Additive read-only browser metadata; independent of video/keyboard ownership.
#pragma once
#include "extender/display/mode_status.hpp"
#include <cstdio>
#include <esp_http_server.h>
namespace agon::extender::display_status {
inline esp_err_t handle(httpd_req_t *request) {
  display::ModeStatus value{};
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  httpd_resp_set_type(request,"application/json");
  if (!display::modeStatus.read(value)) {
    httpd_resp_set_status(request,"503 Service Unavailable");
    return httpd_resp_sendstr(request,"{\"available\":false}");
  }
  char body[256];
  const int length=snprintf(body,sizeof(body),
      "{\"available\":true,\"mode\":%u,\"width\":%u,\"height\":%u,"
      "\"colors\":%u,\"refresh_hz\":%u,\"double_buffered\":%s}",
      value.mode,value.width,value.height,value.colors,value.refresh_hz,
      value.double_buffered?"true":"false");
  return httpd_resp_send(request,body,length);
}
}
