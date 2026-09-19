// HTTP owns request admission; console owner alone turns events into packets.
#pragma once
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "browser_capture.hpp"
namespace agon::extender::input {
inline portMUX_TYPE remote_mutex=portMUX_INITIALIZER_UNLOCKED;
inline InputOwner remote_keyboard;
template<class F> inline auto remoteLocked(F fn) {
  portENTER_CRITICAL(&remote_mutex);auto result=fn(remote_keyboard);
  portEXIT_CRITICAL(&remote_mutex);return result;
}
}
