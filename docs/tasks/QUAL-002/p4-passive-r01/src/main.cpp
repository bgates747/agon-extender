// BENCH-ONLY PASSIVE GPIO IMAGE -- NOT PRODUCT FIRMWARE.
//
// This image exists solely to support an incremental light2-harness-r02
// construction check. It places every P4 pad connected by that harness into
// input-only/high-impedance mode with internal pulls disabled, then idles.
// It intentionally initializes no Extender transport, network, UART, PARLIO,
// display, or application service.

#include <Arduino.h>
#include <driver/gpio.h>

#include <array>

namespace {

constexpr std::array<gpio_num_t, 14> kHarnessPins = {
    GPIO_NUM_9,  GPIO_NUM_10, GPIO_NUM_11, GPIO_NUM_12, GPIO_NUM_13,
    GPIO_NUM_14, GPIO_NUM_15, GPIO_NUM_17, GPIO_NUM_20, GPIO_NUM_21,
    GPIO_NUM_22, GPIO_NUM_23, GPIO_NUM_32, GPIO_NUM_33,
};

}  // namespace

void setup() {
  for (const gpio_num_t pin : kHarnessPins) {
    gpio_reset_pin(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT);
    gpio_pullup_dis(pin);
    gpio_pulldown_dis(pin);
  }
}

void loop() {
  delay(1000);
}

