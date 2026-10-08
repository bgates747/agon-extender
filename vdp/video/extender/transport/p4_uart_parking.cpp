#include "p4_uart_parking.hpp"
#include <driver/gpio.h>
#include <esp_rom_gpio.h>
#include <hal/uart_ll.h>
#include <soc/uart_periph.h>

namespace agon::extender::transport {
void P4UartParking::isolateInputs() noexcept {
  // Reuse IDF 5.5.5 uart.c uart_release_pin's RX disconnection idiom.
  // CTS is deliberately tied HIGH (blocked), unlike driver's deletion path.
  // Masking interrupts alone would leave RX sampling the parallel payload.
  esp_rom_gpio_connect_in_signal(GPIO_MATRIX_CONST_ONE_INPUT,
      UART_PERIPH_SIGNAL(UART_NUM_1, SOC_UART_RX_PIN_IDX), false);
  esp_rom_gpio_connect_in_signal(GPIO_MATRIX_CONST_ONE_INPUT,
      UART_PERIPH_SIGNAL(UART_NUM_1, SOC_UART_CTS_PIN_IDX), false);
}
bool P4UartParking::releaseOutputs() noexcept {
  // Try both even when the first fails. UART ISR may update peripheral RTS,
  // but these disabled pad output enables prevent it from driving the bus.
  auto tx = gpio_set_direction(gpio_num_t(tx_), GPIO_MODE_INPUT);
  auto rts = gpio_set_direction(gpio_num_t(rts_), GPIO_MODE_INPUT);
  return tx == ESP_OK && rts == ESP_OK;
}
P4UartParking::Result P4UartParking::park(bool boundary, bool quiet) noexcept {
  if (state_ == State::failed) return Result::fault;
  if (state_ == State::parked) return Result::ready;
  if (!boundary || !quiet || xPortGetCoreID() != irqCore_) return Result::busy;
  // Includes the shift register. Zero wait; caller owns a bounded deadline.
  auto tx = uart_wait_tx_done(UART_NUM_1, 0);
  if (tx != ESP_OK) return tx == ESP_ERR_TIMEOUT ? Result::busy : Result::fault;

  taskENTER_CRITICAL(&mux_);
  // Installation-core restriction matters: it excludes the driver's ISR
  // between FIFO and ring inspection. A cross-core caller must not use this
  // as a quiescence proof. F02c2b must arrange owner/ISR affinity explicitly.
  size_t buffered = 0;
  auto rx = uart_get_buffered_data_len(UART_NUM_1, &buffered);
  auto *hw = UART_LL_GET_HW(UART_NUM_1);
  Result result = Result::busy;
  if (xPortGetCoreID() != irqCore_) result = Result::busy;
  else if (rx != ESP_OK) result = Result::fault;
  else if (!buffered && !uart_ll_get_rxfifo_len(hw) && uart_ll_is_tx_idle(hw)) {
    isolateInputs();
    bool released = releaseOutputs();
    state_ = released ? State::parked : State::failed;
    result = released ? Result::ready : Result::fault;
  }
  taskEXIT_CRITICAL(&mux_);
  return result;
}
P4UartParking::Result P4UartParking::restore(bool released, bool peer) noexcept {
  if (state_ == State::failed) return Result::fault;
  if (state_ != State::parked || !released || !peer || xPortGetCoreID() != irqCore_)
    return Result::busy;
  // The driver retains its ring, configuration and pin bookkeeping. IDF
  // uart_set_pin rebinds even unchanged pin numbers; -1 would mean NO CHANGE,
  // not release. No driver deletion, FIFO reset or synthetic key-up here.
  if (uart_set_pin(UART_NUM_1, tx_, rx_, rts_, cts_) != ESP_OK) {
    isolateInputs();
    releaseOutputs();
    state_ = State::failed; // No ready acknowledgement after partial restore.
    return Result::fault;
  }
  state_ = State::uart;
  return Result::ready;
}
} // namespace agon::extender::transport
