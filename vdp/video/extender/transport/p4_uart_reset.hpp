// Private reset quarantine, not normal packet-preserving UART parking.
// Caller has completed P4BootRelease on the sole installing core. No function
// here binds GPIO. IDF 5.5.5 flush is RX-only; TX has no driver ring in this
// composition. Resetting a FIFO does not prove the shift register is idle.
#pragma once
#include "console_uart_owner.hpp"
#include <freertos/queue.h>
#include <hal/uart_ll.h>
namespace agon::extender::transport {
inline bool discardConsoleUart(QueueHandle_t events) noexcept {
  if(xPortGetCoreID()!=consoleUartOwnerCore || !events)return false;
  if(uart_disable_intr_mask(UART_NUM_1,UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY)!=ESP_OK)
    return false;
  uart_ll_txfifo_rst(UART_LL_GET_HW(UART_NUM_1));
  if(uart_flush_input(UART_NUM_1)!=ESP_OK)return false;
  return xQueueReset(events)==pdPASS;
}
inline bool consoleUartResetIdle() noexcept {
  return xPortGetCoreID()==consoleUartOwnerCore &&
      uart_wait_tx_done(UART_NUM_1,0)==ESP_OK;
}
}
