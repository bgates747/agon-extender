// PORT-011 diagnostic peer. GPIO22 RX, GPIO12 TX, GPIO23 CTS and GPIO11 RTS.
// P4 deliberately controls RTS in software; UART1 hardware gates TX on CTS.
// This contract begins in setup(), not in ROM/reset. No product activation.
#include <Arduino.h>
#include <driver/gpio.h>
#include <driver/uart.h>
#include <esp_log.h>
#include <hal/uart_ll.h>
#include "uart_flow_peer.hpp"
#include "../../../.pio/uart-flow/uart_flow_probe_config.h"

namespace {
constexpr uart_port_t port = UART_NUM_1;
constexpr char tag[] = "uart-flow";
QueueHandle_t events;
UartFlowPeer peer;
uint32_t last_report;
bool outputs_released;

void cancel_outputs() {
  if (outputs_released) return;
  // ESP-IDF 5.5.5 uart_flush only discards RX. A blocked TX must not remain
  // deliverable on a later CTS edge. Disconnect the physical TX first, disable
  // its completion/FIFO interrupts, then reset the owned UART's TX FIFO.
  // RX stays live so late bytes/errors can still invalidate this run. There
  // is no TX ring/DMA/other writer in this composition. Replace the LL reset
  // if the pinned public driver gains a TX-abort API; never use RX flush here.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(port, UART_INTR_TX_DONE | UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(port));
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_11));
  for (int pin : {11,12}) {
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  outputs_released = true;
}
void report() {
  if (peer.state == UartFlowPeer::State::waiting)
    ESP_LOGI(tag, "UART FLOW WAIT received=0 cts=%d build=%s", gpio_get_level(GPIO_NUM_23), UART_FLOW_BUILD_ID);
  else if (peer.state == UartFlowPeer::State::pass)
    ESP_LOGI(tag, "UART FLOW PASS received=6 ack=9 blocked=1 cancelled=1 build=%s", UART_FLOW_BUILD_ID);
  else if (peer.state == UartFlowPeer::State::fail)
    ESP_LOGE(tag, "UART FLOW FAIL reason=%s build=%s", peer.reason, UART_FLOW_BUILD_ID);
  last_report = millis();
}
}
void setup() {
  for (int pin : {9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin), GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11, 1)); // Stop Agon before enabling RTS output.
  ESP_ERROR_CHECK(gpio_set_direction(GPIO_NUM_11, GPIO_MODE_OUTPUT));
  uart_config_t config = {};
  config.baud_rate = 115200; config.data_bits = UART_DATA_8_BITS;
  config.parity = UART_PARITY_DISABLE; config.stop_bits = UART_STOP_BITS_1;
  config.flow_ctrl = UART_HW_FLOWCTRL_CTS; config.source_clk = UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(port, &config));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12, 1));
  ESP_ERROR_CHECK(uart_set_pin(port, 12, 22, UART_PIN_NO_CHANGE, 23));
  // gpio_get_level observes CTS alongside the matrix input used by UART.
  ESP_ERROR_CHECK(gpio_input_enable(GPIO_NUM_23));
  ESP_ERROR_CHECK(uart_driver_install(port, 1024, 0, 16, &events, 0));
  peer.since = millis();
  ESP_LOGI(tag, "UART FLOW RECEIVER %s (%s)", UART_FLOW_BUILD_ID, UART_FLOW_STATUS);
  ESP_LOGI(tag, "RX=22 TX=12 CTS=23 RTS=11 baud=115200 8N1; HIGH=stop LOW=ready");
  report();
}
void loop() {
  uint8_t data[128]; size_t count = 0;
  uart_event_t event;
  while (xQueueReceive(events, &event, 0) == pdTRUE) {
    if (event.type != UART_DATA) {
      peer.fail("UART error event");
      ESP_LOGE(tag, "UART FLOW EVENT type=%d build=%s", int(event.type), UART_FLOW_BUILD_ID);
    }
  }
  const int got = uart_read_bytes(port, data, sizeof(data), 0);
  if (got < 0) peer.fail("UART read error");
  else count = size_t(got);
  const bool stop = gpio_get_level(GPIO_NUM_23) != 0;
  bool idle = false;
  if (!outputs_released) {
    const esp_err_t result = uart_wait_tx_done(port, 0);
    if (result != ESP_OK && result != ESP_ERR_TIMEOUT) peer.fail("UART TX status error");
    idle = result == ESP_OK;
  }
  auto action = peer.tick(millis(), stop, idle, data, count);
  using A = UartFlowPeer::Action;
  if (action == A::allow_forward) {
    ESP_LOGI(tag, "UART FLOW FORWARD RELEASE min_hold_ms=1000 build=%s", UART_FLOW_BUILD_ID);
    ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11, 0));
  } else if (action == A::stop_forward) {
    ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11, 1));
    ESP_LOGI(tag, "UART FLOW REQUEST count=6 hex=464C4F570D0A build=%s", UART_FLOW_BUILD_ID);
  } else if (action == A::queue_ack) {
    if (uart_tx_chars(port, UartFlowPeer::ack, sizeof(UartFlowPeer::ack)-1) != sizeof(UartFlowPeer::ack)-1)
      peer.fail("ACK enqueue failed");
    else ESP_LOGI(tag, "UART FLOW ACK QUEUED cts=stop build=%s", UART_FLOW_BUILD_ID);
  } else if (action == A::ack_sent) {
    ESP_LOGI(tag, "UART FLOW ACK SENT count=9 hex=464C4F5741434B0D0A build=%s", UART_FLOW_BUILD_ID);
  } else if (action == A::queue_blocked) {
    if (uart_tx_chars(port, "!", 1) != 1) peer.fail("blocked enqueue failed");
    else ESP_LOGI(tag, "UART FLOW BLOCKED QUEUED cts=stop build=%s", UART_FLOW_BUILD_ID);
  } else if (action == A::cancel_tx) {
    cancel_outputs();
    ESP_LOGI(tag, "UART FLOW BLOCKED TIMEOUT cancelled=1 build=%s", UART_FLOW_BUILD_ID);
  }
  if (peer.state == UartFlowPeer::State::fail) cancel_outputs();
  if (action != A::none || uint32_t(millis()-last_report) >= 5000) report();
  delay(1);
}
