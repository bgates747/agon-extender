// HTTP reads a copy; only the retained UART console owner receives records.
#pragma once
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "latest.hpp"
namespace agon::extender::telemetry {
inline portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
inline Latest latest;
inline bool receive(const std::uint8_t *p,unsigned n,std::uint32_t now) {
  portENTER_CRITICAL(&mutex);bool ok=latest.receive(p,n,now);portEXIT_CRITICAL(&mutex);return ok;
}
inline Snapshot snapshot() {
  portENTER_CRITICAL(&mutex);auto s=latest.snapshot();portEXIT_CRITICAL(&mutex);return s;
}
inline void reset() {portENTER_CRITICAL(&mutex);latest.reset();portEXIT_CRITICAL(&mutex);}
}
