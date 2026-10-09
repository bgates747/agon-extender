// PORT-008 F02c2b2: install UART from the existing process owner, not setup's
// Arduino task. IDF 5.5.5 attaches the UART ISR to the installing core. Parking
// uses a local critical section, so its caller and this ISR must share a core.
#pragma once
#include <driver/uart.h>
#include <freertos/FreeRTOS.h>

namespace agon::extender::transport {
inline constexpr int consoleUartOwnerCore = 0;
inline esp_err_t startConsoleUart(QueueHandle_t *events) {
  if (xPortGetCoreID() != consoleUartOwnerCore) return ESP_ERR_INVALID_STATE;
  auto result = uart_driver_install(UART_NUM_1,4096,0,32,events,0);
  if (result != ESP_OK) return result;
  // Match stock HardwareSerial's two-symbol idle timeout, after installation.
  return uart_set_rx_timeout(UART_NUM_1,2);
}
} // namespace agon::extender::transport
