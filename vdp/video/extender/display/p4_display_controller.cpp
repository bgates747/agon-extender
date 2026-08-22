// See p4_display_controller.hpp. This file must remain visibly non-functional
// until a later PORT-003 phase replaces each fail-fast contract method with a
// tested framebuffer implementation.
#include "extender/display/p4_display_controller.hpp"

#include <cstdlib>

#include "esp_log.h"

namespace agon::extender::display {
namespace {

[[noreturn]] void unavailable(char const *operation) {
  ESP_EARLY_LOGE("p4-display-contract-canary",
                 "unimplemented display operation invoked: %s", operation);
  std::abort();
}

}  // namespace

void P4DisplayControllerContractCanary::begin() {
  setResolution(nullptr, 1, 1, false);
}

void P4DisplayControllerContractCanary::setResolution(char const *, int width,
                                                       int height,
                                                       bool double_buffered) {
  if (double_buffered) unavailable("setResolution(double-buffered)");
  width = width > 0 ? width : 1;
  height = height > 0 ? height : 1;
  setScreenSize(width, height);
  m_viewPortWidth = width;
  m_viewPortHeight = height;
  setDoubleBuffered(false);
  resetPaintState();
}

int P4DisplayControllerContractCanary::colorsCount() { return 64; }

fabgl::NativePixelFormat P4DisplayControllerContractCanary::nativePixelFormat() {
  return fabgl::NativePixelFormat::SBGR2222;
}

void P4DisplayControllerContractCanary::suspendBackgroundPrimitiveExecution() {}
void P4DisplayControllerContractCanary::resumeBackgroundPrimitiveExecution() {}

void P4DisplayControllerContractCanary::
    retainCommonPrimitiveExecutorForLinkEvidence() {
  fabgl::Primitive flush(fabgl::PrimitiveCmd::Flush);
  fabgl::Rect update;
  execPrimitive(flush, update, false);
}

#define AGON_EXTENDER_UNAVAILABLE(method, signature) \
  void P4DisplayControllerContractCanary::method signature { unavailable(#method); }

AGON_EXTENDER_UNAVAILABLE(readScreen,
                          (fabgl::Rect const &, fabgl::RGB888 *))
AGON_EXTENDER_UNAVAILABLE(setPixelAt,
                          (fabgl::PixelDesc const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(absDrawLine,
                          (int, int, int, int, fabgl::RGB888))
AGON_EXTENDER_UNAVAILABLE(fillRow, (int, int, int, fabgl::RGB888))
AGON_EXTENDER_UNAVAILABLE(drawEllipse, (fabgl::Size const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(absDrawEllipseSheared,
                          (fabgl::EllipseShearedParams const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(drawArc, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(fillSegment, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(fillSector, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(clear, (fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(VScroll, (int, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(HScroll, (int, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(drawGlyph,
                          (fabgl::Glyph const &, fabgl::GlyphOptions,
                           fabgl::RGB888, fabgl::RGB888, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(invertRect, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(swapFGBG, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(copyRect, (fabgl::Rect const &, fabgl::Rect &))
AGON_EXTENDER_UNAVAILABLE(swapBuffers, ())
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmap_Native,
                          (int, int, fabgl::Bitmap const *, int, int, int, int))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmap_Mask,
                          (int, int, fabgl::Bitmap const *, void *, int, int,
                           int, int))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmap_RGBA2222,
                          (int, int, fabgl::Bitmap const *, void *, int, int,
                           int, int))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmap_RGBA8888,
                          (int, int, fabgl::Bitmap const *, void *, int, int,
                           int, int))
AGON_EXTENDER_UNAVAILABLE(rawCopyToBitmap,
                          (int, int, int, void *, int, int, int, int))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmapWithMatrix_Mask,
                          (int, int, fabgl::Rect &, fabgl::Bitmap const *,
                           float const *))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmapWithMatrix_RGBA2222,
                          (int, int, fabgl::Rect &, fabgl::Bitmap const *,
                           float const *))
AGON_EXTENDER_UNAVAILABLE(rawDrawBitmapWithMatrix_RGBA8888,
                          (int, int, fabgl::Rect &, fabgl::Bitmap const *,
                           float const *))

#undef AGON_EXTENDER_UNAVAILABLE

int P4DisplayControllerContractCanary::getBitmapSavePixelSize() {
  unavailable("getBitmapSavePixelSize");
}

std::unique_ptr<fabgl::BitmappedDisplayController>
makeP4DisplayControllerContractCanary() {
  return std::make_unique<P4DisplayControllerContractCanary>();
}

}  // namespace agon::extender::display
