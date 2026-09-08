// PORT-010 round-trip bench composition, not production EDP firmware.
// GPIO22 receives eZ80 PC0; GPIO12 returns ACK to PC1 after exact receipt.
// This application contract starts at setup(), not during ROM/reset/startup.
#include <Arduino.h>
#include <driver/gpio.h>
#include <driver/uart.h>
#include <esp_log.h>
#include "uart_forward_match.hpp"
// Explicit generated-header path: hybrid CMake ignores PlatformIO -I flags.
#include "../../../.pio/uart-roundtrip/uart_roundtrip_probe_config.h"

namespace {
constexpr char kTag[] = "uart-forward";
constexpr char kMessage[] = UART_FORWARD_MESSAGE;
constexpr uart_port_t kUart = UART_NUM_1;
QueueHandle_t events;
UartForwardMatch matcher(reinterpret_cast<const uint8_t*>(kMessage), sizeof(kMessage) - 1, 0);
uint32_t last_report;
bool ack_sent = false;

void report() {
  char hex[129] = {};
  for (size_t i = 0; i < matcher.stored(); ++i)
    snprintf(hex + 2 * i, 3, "%02X", matcher.bytes()[i]);
  const auto state = matcher.state();
  const char* label = state == UartForwardMatch::State::pass ? "PASS" :
      state == UartForwardMatch::State::fail ? "FAIL" : "WAIT";
  ESP_LOGI(kTag, "UART FORWARD %s received=%u expected=%u hex=%s reason=%s build=%s",
           label, unsigned(matcher.count()), unsigned(sizeof(kMessage) - 1),
           hex, matcher.reason(), UART_FORWARD_BUILD_ID);
  last_report = millis();
}
}  // namespace

void setup() {
  // Include historical harness pads too, so this isolated composition does
  // not inherit a boot-active parallel/handshake GPIO from another target.
  for (int pin : {9, 10, 11, 12, 13, 14, 15, 17, 20, 21, 22, 23, 32, 33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin), GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t config = {};
  config.baud_rate = UART_FORWARD_BAUD;
  config.data_bits = UART_DATA_8_BITS;
  config.parity = UART_PARITY_DISABLE;
  config.stop_bits = UART_STOP_BITS_1;
  config.flow_ctrl = UART_HW_FLOWCTRL_DISABLE;
  config.source_clk = UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(kUart, &config));
  // GPIO12 is the only harness output; PC1 is the Agon RX input.
  // Drive no RTS and do not change Port C lane ownership during this run.
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12, 1));
  ESP_ERROR_CHECK(uart_set_pin(kUart, 12, 22,
                             UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
  ESP_ERROR_CHECK(uart_driver_install(kUart, 1024, 0, 16, &events, 0));
  matcher = UartForwardMatch(reinterpret_cast<const uint8_t*>(kMessage),
                            sizeof(kMessage) - 1, millis());
  ESP_LOGI(kTag, "UART FORWARD RECEIVER %s (%s)", UART_FORWARD_BUILD_ID, UART_FORWARD_STATUS);
  ESP_LOGI(kTag, "READY RX=GPIO22 baud=%u 8N1 flow=none TX=GPIO12 RTS=unconnected; deadline=180s",
           unsigned(UART_FORWARD_BAUD));
  report();
}

void loop() {
  const auto previous = matcher.state();
  uart_event_t event;
  if (xQueueReceive(events, &event, pdMS_TO_TICKS(10)) == pdTRUE) {
    if (event.type == UART_DATA) {
      size_t remaining = event.size;
      uint8_t data[64];
      while (remaining) {
        const int got = uart_read_bytes(kUart, data,
            remaining < sizeof(data) ? remaining : sizeof(data), 0);
        if (got <= 0) { matcher.error("UART event/read mismatch"); break; }
        matcher.feed(data, size_t(got), millis());
        remaining -= size_t(got);
      }
    } else {
      // Overflow, break, parity/framing errors (and unexpected events) fail
      // the entire observation. Never flush and resynchronise into a PASS.
      matcher.error("UART error event");
      ESP_LOGE(kTag, "UART event type=%d", int(event.type));
    }
  }
  // Drain queued events before declaring the quiet interval successful.
  if (uxQueueMessagesWaiting(events) == 0) matcher.poll(millis());
  if (matcher.state() == UartForwardMatch::State::pass && !ack_sent) {
    constexpr char ack[] = "ACK\r\n";
    // One bounded reply, after exact request plus quiet interval. No retry.
    if (uart_write_bytes(kUart, ack, sizeof(ack) - 1) != sizeof(ack) - 1 ||
        uart_wait_tx_done(kUart, pdMS_TO_TICKS(100)) != ESP_OK) {
      matcher.error("ACK transmission failed");
    } else {
      ack_sent = true;
      ESP_LOGI(kTag, "UART RETURN SENT count=5 hex=41434B0D0A build=%s", UART_FORWARD_BUILD_ID);
    }
  }
  if (matcher.state() != previous || uint32_t(millis() - last_report) >= 5000)
    report();
}
