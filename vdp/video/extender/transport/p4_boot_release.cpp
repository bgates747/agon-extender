#include "p4_boot_release.hpp"
#include <driver/gpio.h>
#include <driver/uart.h>
#include <freertos/FreeRTOS.h>
#include <esp_rom_gpio.h>
#include <soc/uart_periph.h>

namespace agon::extender::transport {
bool P4BootRelease::releasePads() noexcept {
  // Same IDF release-input idiom as P4UartParking: disconnected RX and blocked
  // CTS. This is boot isolation, not a claim that an active packet drained.
  esp_rom_gpio_connect_in_signal(GPIO_MATRIX_CONST_ONE_INPUT,
      UART_PERIPH_SIGNAL(UART_NUM_1,SOC_UART_RX_PIN_IDX),false);
  esp_rom_gpio_connect_in_signal(GPIO_MATRIX_CONST_ONE_INPUT,
      UART_PERIPH_SIGNAL(UART_NUM_1,SOC_UART_CTS_PIN_IDX),false);
  bool ok=true;
  for (int pin:data_) {
    // Direction first: remove even a stale GPIO driver before clearing mux.
    // Try every lane even if a previous SDK operation failed.
    if (gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT)!=ESP_OK) ok=false;
    if (gpio_reset_pin(gpio_num_t(pin))!=ESP_OK) ok=false;
    if (gpio_pullup_dis(gpio_num_t(pin))!=ESP_OK) ok=false;
    if (gpio_pulldown_dis(gpio_num_t(pin))!=ESP_OK) ok=false;
  }
  released_=ok;
  return ok;
}
bool P4BootRelease::begin(P4ParallelHandover &h) noexcept {
  if (xPortGetCoreID()!=core_) return false;
  failed_=true;initial_=true;h.cancel();
  // Withdraw READY first; preload its high latch while still an input. Never
  // publish release until ALL data directions and control inputs are set.
  bool ok=gpio_set_direction(gpio_num_t(ready_),GPIO_MODE_INPUT)==ESP_OK;
  if (gpio_reset_pin(gpio_num_t(ready_))!=ESP_OK) ok=false;
  if (gpio_pullup_dis(gpio_num_t(ready_))!=ESP_OK) ok=false;
  if (gpio_pulldown_dis(gpio_num_t(ready_))!=ESP_OK) ok=false;
  if (!releasePads()) ok=false;
  for (int pin:{clock_,valid_}) {
    if (gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT)!=ESP_OK) ok=false;
    if (gpio_reset_pin(gpio_num_t(pin))!=ESP_OK) ok=false;
    if (gpio_pullup_dis(gpio_num_t(pin))!=ESP_OK) ok=false;
    if (gpio_pulldown_dis(gpio_num_t(pin))!=ESP_OK) ok=false;
  }
  if (gpio_set_level(gpio_num_t(ready_),1)!=ESP_OK) ok=false;
  if (ok && gpio_set_direction(gpio_num_t(ready_),GPIO_MODE_OUTPUT)!=ESP_OK) ok=false;
  failed_=!ok;
  if (!ok) gpio_set_direction(gpio_num_t(ready_),GPIO_MODE_INPUT);
  return ok;
}
P4BootRelease::Result P4BootRelease::poll(P4ParallelHandover &h, bool uartRestored) noexcept {
  if (failed_ || xPortGetCoreID()!=core_) return fault;
  // No payload/entry actions are supported by this boot-only adapter.
  if (h.phase()>P4ParallelHandover::uart) return fault;
  if (h.phase()==P4ParallelHandover::recoveryRelease && !initial_) {
    // External cancellation must begin a new physical fence, not borrow the
    // old release completion after a coordinator enabled UART outputs.
    failed_=true;return fault;
  }
  std::uint8_t done=released_?P4ParallelHandover::released:0;
  if (gpio_get_level(gpio_num_t(valid_))) done|=P4ParallelHandover::validHigh;
  if (gpio_get_level(gpio_num_t(clock_))) done|=P4ParallelHandover::clockHigh;
  if (uartRestored && h.phase()==P4ParallelHandover::recoveryUart)
    done|=P4ParallelHandover::uartUp;
  const auto action=h.step(done);
  initial_=false;
  if (gpio_set_level(gpio_num_t(ready_),h.readyN())!=ESP_OK) {
    h.cancel();failed_=true;releasePads();
    gpio_set_direction(gpio_num_t(ready_),GPIO_MODE_INPUT);
    return fault;
  }
  if (action==P4ParallelHandover::release) {
    // After UART became live a reset requires a NEW exclusive fence; the old
    // released_ bit is no longer a current pad-release completion.
    released_=false;failed_=true;
    return fault;
  }
  if (action==P4ParallelHandover::restore) return restore;
  if (action==P4ParallelHandover::live) {released_=false;return live;}
  return waiting;
}
} // namespace agon::extender::transport
