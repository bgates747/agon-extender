// Two task callers: HTTP producer and the existing console/UART owner.
#pragma once
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "sd_service.hpp"
namespace agon::extender::storage {
inline portMUX_TYPE sd_mutex=portMUX_INITIALIZER_UNLOCKED;
inline SdService sd_service;
inline unsigned sdTake(std::uint8_t *out,std::uint32_t now) {
  portENTER_CRITICAL(&sd_mutex);auto n=sd_service.take(out,now);
  portEXIT_CRITICAL(&sd_mutex);return n;
}
inline void sdReceive(const std::uint8_t *p,unsigned n,std::uint32_t now) {
  portENTER_CRITICAL(&sd_mutex);sd_service.receive(p,n,now);portEXIT_CRITICAL(&sd_mutex);
}
inline unsigned sdPost(const std::uint8_t *p,unsigned n,std::uint8_t *out,
                       unsigned &out_length,std::uint32_t now) {
  portENTER_CRITICAL(&sd_mutex);auto result=sd_service.post(p,n,out,out_length,now);
  portEXIT_CRITICAL(&sd_mutex);return result;
}
inline void sdStatus(std::uint32_t now,bool &online,bool &pending,std::uint32_t &boot) {
  portENTER_CRITICAL(&sd_mutex);online=sd_service.online(now);
  pending=sd_service.pending();boot=sd_service.boot();portEXIT_CRITICAL(&sd_mutex);
}
}
