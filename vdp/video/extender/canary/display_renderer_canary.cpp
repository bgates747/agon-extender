// PORT-003 Phase B compile/link canary. It constructs the synchronous logical
// controller and retained Canvas but performs no drawing, deployment, or
// physical display qualification.
#include <Arduino.h>

#include <climits>
#include <cstdint>
#include <memory>
#include <type_traits>

#include "canvas.h"
#include "extender/display/p4_display_controller.hpp"

using agon::extender::display::P4DisplayController;

static_assert(CHAR_BIT == 8);
static_assert(sizeof(fabgl::RGB888) == 3);
static_assert(std::is_base_of_v<fabgl::GenericBitmappedDisplayController,
                               P4DisplayController>);
static_assert(std::is_convertible_v<P4DisplayController *,
                                    fabgl::BitmappedDisplayController *>);

namespace {
std::unique_ptr<fabgl::BitmappedDisplayController> controller;
std::unique_ptr<fabgl::Canvas> canvas;
volatile int contract_width = 0;
}  // namespace

void setup() {
  controller = agon::extender::display::makeP4DisplayController();
  controller->begin();
  canvas = std::make_unique<fabgl::Canvas>(controller.get());
  contract_width = canvas->getWidth();
}

void loop() { delay(1000); }
