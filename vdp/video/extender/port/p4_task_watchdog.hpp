// ESP32-P4 task-watchdog binding for retained Agon VDP startup.
//
// Official VDP v2.16.0 disables each classic-ESP32 IDLE watchdog through
// Arduino's disableCore*WDT() helpers. With the pinned Arduino-ESP32 3.3.11
// and ESP-IDF 5.5.5 combination, those helpers remove the watched tasks but
// leave ESP-IDF's IDLE hooks feeding them, causing a continuous
// "esp_task_wdt_reset: task not found" flood. This adapter preserves the
// upstream no-IDLE-watchdog intent through ESP-IDF's hook-aware public API.

#pragma once

namespace agon::extender::port {

// Remove both P4 IDLE tasks and their feed hooks from the task watchdog while
// leaving the watchdog service initialized for future explicit subscribers.
// Returns false if ESP-IDF rejects the reconfiguration; callers must stop P4
// startup rather than continue into an unqualified error-flooding state.
bool disableRetainedVdpIdleWatchdogs();

}  // namespace agon::extender::port
