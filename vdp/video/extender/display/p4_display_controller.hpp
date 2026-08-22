// PORT-003 Phase A contract-only display controller.
//
// This type proves that the retained vdp-gl abstract/common renderer can bind
// to a project-owned ESP32-P4 concrete class. It is intentionally incapable of
// rendering. Every drawing, readback, or swap entry point fails visibly; a
// framebuffer, frame service, and output sink belong to later PORT-003 phases.
#pragma once

#include <memory>

#include "displaycontroller.h"

namespace agon::extender::display {

class P4DisplayControllerContractCanary final
    : public fabgl::GenericBitmappedDisplayController {
 public:
  void begin() override;
  void setResolution(char const *modeline, int view_port_width = -1,
                     int view_port_height = -1,
                     bool double_buffered = false) override;
  int colorsCount() override;
  fabgl::NativePixelFormat nativePixelFormat() override;
  void suspendBackgroundPrimitiveExecution() override;
  void resumeBackgroundPrimitiveExecution() override;
  void readScreen(fabgl::Rect const &rect, fabgl::RGB888 *destination) override;

  // Phase A link-evidence seam only. The canary calls this behind a volatile
  // false guard so the linker must retain the upstream common primitive
  // executor without pretending that any drawing path is functional.
  void retainCommonPrimitiveExecutorForLinkEvidence();

 protected:
  void setPixelAt(fabgl::PixelDesc const &pixel, fabgl::Rect &update) override;
  void absDrawLine(int x1, int y1, int x2, int y2, fabgl::RGB888 color) override;
  void fillRow(int y, int x1, int x2, fabgl::RGB888 color) override;
  void drawEllipse(fabgl::Size const &size, fabgl::Rect &update) override;
  void absDrawEllipseSheared(fabgl::EllipseShearedParams const &params,
                             fabgl::Rect &update) override;
  void drawArc(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void fillSegment(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void fillSector(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void clear(fabgl::Rect &update) override;
  void VScroll(int scroll, fabgl::Rect &update) override;
  void HScroll(int scroll, fabgl::Rect &update) override;
  void drawGlyph(fabgl::Glyph const &glyph, fabgl::GlyphOptions options,
                 fabgl::RGB888 pen, fabgl::RGB888 brush,
                 fabgl::Rect &update) override;
  void invertRect(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void swapFGBG(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void copyRect(fabgl::Rect const &source, fabgl::Rect &update) override;
  void swapBuffers() override;
  int getBitmapSavePixelSize() override;
  void rawDrawBitmap_Native(int dest_x, int dest_y, fabgl::Bitmap const *bitmap,
                            int x1, int y1, int x_count, int y_count) override;
  void rawDrawBitmap_Mask(int dest_x, int dest_y, fabgl::Bitmap const *bitmap,
                          void *saved_background, int x1, int y1, int x_count,
                          int y_count) override;
  void rawDrawBitmap_RGBA2222(int dest_x, int dest_y,
                              fabgl::Bitmap const *bitmap,
                              void *saved_background, int x1, int y1,
                              int x_count, int y_count) override;
  void rawDrawBitmap_RGBA8888(int dest_x, int dest_y,
                              fabgl::Bitmap const *bitmap,
                              void *saved_background, int x1, int y1,
                              int x_count, int y_count) override;
  void rawCopyToBitmap(int src_x, int src_y, int width, void *save_buffer,
                       int x1, int y1, int x_count, int y_count) override;
  void rawDrawBitmapWithMatrix_Mask(int dest_x, int dest_y,
                                    fabgl::Rect &drawing_rect,
                                    fabgl::Bitmap const *bitmap,
                                    float const *inverse) override;
  void rawDrawBitmapWithMatrix_RGBA2222(int dest_x, int dest_y,
                                        fabgl::Rect &drawing_rect,
                                        fabgl::Bitmap const *bitmap,
                                        float const *inverse) override;
  void rawDrawBitmapWithMatrix_RGBA8888(int dest_x, int dest_y,
                                        fabgl::Rect &drawing_rect,
                                        fabgl::Bitmap const *bitmap,
                                        float const *inverse) override;
};

std::unique_ptr<fabgl::BitmappedDisplayController>
makeP4DisplayControllerContractCanary();

}  // namespace agon::extender::display
