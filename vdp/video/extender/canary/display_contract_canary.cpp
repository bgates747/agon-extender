// PORT-003 Phase A compile/link canary. This sketch creates the same abstract
// controller ownership shape expected by the official VDP facade and binds a
// real vendored fabgl::Canvas to it. It intentionally performs no drawing and
// is never a qualified firmware artifact.
#include <Arduino.h>

#include <climits>
#include <cstdint>
#include <memory>
#include <type_traits>

#include "canvas.h"
#include "extender/display/p4_display_controller.hpp"

using agon::extender::display::P4DisplayControllerContractCanary;

static_assert(CHAR_BIT == 8);
static_assert(sizeof(std::uint8_t) == 1);
static_assert(sizeof(std::uint16_t) == 2);
static_assert(sizeof(std::uint32_t) == 4);
static_assert(sizeof(fabgl::RGB888) == 3);
static_assert(static_cast<std::uint8_t>(fabgl::NativePixelFormat::Mono) == 0);
static_assert(static_cast<std::uint8_t>(fabgl::NativePixelFormat::SBGR2222) == 1);
static_assert(static_cast<std::uint8_t>(fabgl::NativePixelFormat::RGB565BE) == 2);
static_assert(static_cast<std::uint8_t>(fabgl::NativePixelFormat::PALETTE16) == 6);
static_assert(std::is_base_of_v<fabgl::GenericBitmappedDisplayController,
                               P4DisplayControllerContractCanary>);
static_assert(std::is_convertible_v<P4DisplayControllerContractCanary *,
                                    fabgl::BitmappedDisplayController *>);

namespace {

std::unique_ptr<fabgl::BitmappedDisplayController> controller;
std::unique_ptr<fabgl::Canvas> canvas;
volatile int contract_width = 0;
volatile bool retain_common_renderer_probe = false;

}  // namespace

void setup() {
  controller = agon::extender::display::makeP4DisplayControllerContractCanary();
  controller->begin();
  if (retain_common_renderer_probe) {
    static_cast<P4DisplayControllerContractCanary *>(controller.get())
        ->retainCommonPrimitiveExecutorForLinkEvidence();
  }
  canvas = std::make_unique<fabgl::Canvas>(controller.get());
  contract_width = canvas->getWidth();
}

void loop() { delay(1000); }
