// Two task callers: HTTP producer and the existing console/UART owner.
#pragma once
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_timer.h>
#include "sd_service.hpp"
#include "webdav/runtime.hpp"
#if AGON_EXTENDER_STAGED_WEBDAV
#include "admission/peer.hpp"
#include "application/mailbox.hpp"
#include <esp_random.h>
#endif
#include "../diagnostics/admission/config.hpp"
#if AGON_EXTENDER_ADMISSION_PROBE
#include "../diagnostics/admission/peer.hpp"
#include <esp_random.h>
#endif
namespace agon::extender::storage {
inline portMUX_TYPE sd_mutex=portMUX_INITIALIZER_UNLOCKED;
inline SdService sd_service;
#if AGON_EXTENDER_STAGED_WEBDAV
#if AGON_EXTENDER_ADMISSION_PROBE
#error Diagnostic admission and staged runtime cannot own the same queue
#endif
inline admission::Peer sd_peer;
inline application::Mailbox sd_application;
inline bool sd_runtime_ready=false;
#endif
inline unsigned sdTake(std::uint8_t *out,std::uint32_t now) {
  portENTER_CRITICAL(&sd_mutex);
  now = std::uint32_t(esp_timer_get_time() / 1000);
#if AGON_EXTENDER_STAGED_WEBDAV
  auto n=sd_runtime_ready?sd_application.take(out):0;
  if(!n && !sd_application.owned)n=sd_runtime_ready?sd_peer.take(out,now):0;
  if(!n&&!sd_peer.owned()&&!sd_application.owned)n=sd_service.take(out,now);
#elif AGON_EXTENDER_ADMISSION_PROBE
  auto n=admission_probe.take(out);
  if(!n)n=sd_service.take(out,now);
#else
  auto n=sd_service.take(out,now);
#endif
  portEXIT_CRITICAL(&sd_mutex);return n;
}
inline void sdTransportLost() {
  // Console owner fences pins before entering this shared producer boundary.
  portENTER_CRITICAL(&sd_mutex);
  sd_service.transportLost();
#if AGON_EXTENDER_STAGED_WEBDAV
  sd_peer.transportLost();sd_application.transportLost();
#endif
  portEXIT_CRITICAL(&sd_mutex);
}
inline void sdReceive(const std::uint8_t *p,unsigned n,std::uint32_t now) {
#if AGON_EXTENDER_STAGED_WEBDAV
  auto a=esp_random(),b=esp_random();
  portENTER_CRITICAL(&sd_mutex);
  now = std::uint32_t(esp_timer_get_time() / 1000);
  if(!sd_runtime_ready)sd_service.receive(p,n,now);
  else if(sd_application.receive(p,n,now,sd_peer.owned()||sd_service.online(now))) {}
  else if(!sd_peer.receive(p,n,now,a,b)&&!sd_peer.owned())sd_service.receive(p,n,now);
#elif AGON_EXTENDER_ADMISSION_PROBE
  auto a=esp_random(),b=esp_random();
  portENTER_CRITICAL(&sd_mutex);
  if(!admission_probe.receive(p,n,now,a,b))sd_service.receive(p,n,now);
#else
  portENTER_CRITICAL(&sd_mutex);sd_service.receive(p,n,now);
#endif
  portEXIT_CRITICAL(&sd_mutex);
}
inline unsigned sdPost(const std::uint8_t *p,unsigned n,std::uint8_t *out,
                       unsigned &out_length,std::uint32_t now) {
  portENTER_CRITICAL(&sd_mutex);
#if AGON_EXTENDER_STAGED_WEBDAV
  if(sd_peer.owned()||sd_application.owned){out_length=0;portEXIT_CRITICAL(&sd_mutex);return 503;}
#endif
  auto result=sd_service.post(p,n,out,out_length,now);
  portEXIT_CRITICAL(&sd_mutex);return result;
}
inline void sdStatus(std::uint32_t now,bool &online,bool &pending,std::uint32_t &boot) {
  portENTER_CRITICAL(&sd_mutex);online=sd_service.online(now);
  pending=sd_service.pending();boot=sd_service.boot();portEXIT_CRITICAL(&sd_mutex);
}
}
