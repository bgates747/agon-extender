// RGB-001 experimental CPU backend, derived from retained FabGL VGA64Controller.
// GPLv3; see the original copyright/license below. Physical rows are packed BGR888,
// while VDU colours, Native assets and saved sprite backgrounds retain RGB222 semantics.
// No physical VGA ISR is used. Only the explicit RGB-001 build selects this class.
/*
* This library and related software is available under GPL v3.

  FabGL is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  FabGL is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with FabGL.  If not, see <http://www.gnu.org/licenses/>.
 */


#pragma once



/**
 * @file
 *
 * @brief This file contains fabgl::P4Rgb888Controller definition.
 */


#include <stdint.h>
#include <stddef.h>
#include <atomic>
#include <functional>

#include "driver/gpio.h"

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#include "fabglconf.h"
#include "fabutils.h"
#include "devdrivers/swgenerator.h"
#include "displaycontroller.h"
#include "dispdrivers/vgapalettedcontroller.h"
#include "extender/display/rgb888_pixel.hpp"
#include "extender/display/rgb888_panel_storage.hpp"



#define VGA64_LinesCount 4




namespace fabgl {



/**
* @brief Represents the VGA 64 colors bitmapped controller
*
* This controller works in the same way as other VGA controllers based on VGAPalettedController, but works with a framebuffer that is the
* same as with VGAController, and does not actually support a palette.  This controller however supports "hardware sprites".
*
* In contrast to other palette-based controllers, the performance impact of this controller has not been properly measured.
* Benchmark testing seems to indicate performance essentially on-par with VGAController.
*
*
* This example initializes VGA Controller with 64 colors (all visible at the same time) at 640x350:
*
*     fabgl::P4Rgb888Controller displayController;
*     // the default assigns GPIO22 and GPIO21 to Red, GPIO19 and GPIO18 to Green, GPIO5 and GPIO4 to Blue, GPIO23 to HSync and GPIO15 to VSync
*     displayController.begin();
*     displayController.setResolution(VGA_640x350_70Hz);
*/
class P4Rgb888Controller : public VGAPalettedController {

public:

  P4Rgb888Controller();
  using VGAPalettedController::setResolution;
  void setResolution(VGATimings const &, int = -1, int = -1, bool = false) override;
  void bindPanelStorage(agon::extender::display::Rgb888PanelStorage const &storage) { m_panel = storage; }
  bool panelStorage() const { return m_panel.count != 0; }
  unsigned preparePanelFrame(int &marker);
  void copyRgb888Row(int y, uint8_t *destination, uint8_t *signal);
  void encodeSignalRow(int y, uint8_t *signal);
  bool overlayIntersectsRow(int y);

  // unwanted methods
  P4Rgb888Controller(P4Rgb888Controller const&) = delete;
  void operator=(P4Rgb888Controller const&)  = delete;


  /**
   * @brief Returns the singleton instance of P4Rgb888Controller class
   *
   * @return A pointer to P4Rgb888Controller singleton object
   */
  static P4Rgb888Controller * instance() { return s_instance; }

  void readScreen(Rect const & rect, RGB888 * destBuf);

  /**
   * @brief Determines color of specified palette item
   *
   * @param index Palette item (0..15)
   * @param color Color to assign to this item
   *
   * Example:
   *
   *     // Color item 0 is pure Red
   *     displayController.setPaletteItem(0, RGB888(255, 0, 0));
   */
  void setPaletteItem(int index, RGB888 const & color);


protected:

  bool allocateViewPort() override;
  void freeViewPort() override;
  void swapBuffers() override;
  void prepareForDrawing() override;

  void setupDefaultPalette();

  void packSignals(int index, uint8_t packed222, void * signals) {};


private:

  unsigned panelIndex(volatile uint8_t **rows) const;
  void restorePanelOverlays(unsigned index);
  void composePanelOverlays(unsigned index);
  agon::extender::display::Rgb888PanelStorage m_panel{};
  uint8_t *m_overlayBackground[2]{};
  uint8_t *m_overlayRows[2]{};
  bool m_overlaysActive[2]{};

  // methods to get lambdas to get/set pixels
  std::function<uint8_t(RGB888 const &)> getPixelLambda(PaintMode mode);
  std::function<void(int X, int Y, uint8_t colorIndex)> setPixelLambda(PaintMode mode);
  std::function<void(uint8_t * row, int x, uint8_t colorIndex)> setRowPixelLambda(PaintMode mode);
  std::function<void(int Y, int X1, int X2, uint8_t colorIndex)> fillRowLambda(PaintMode mode);

  // abstract method of BitmappedDisplayController
  void setPixelAt(PixelDesc const & pixelDesc, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void drawEllipse(Size const & size, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void drawArc(Rect const & rect, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void fillSegment(Rect const & rect, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void fillSector(Rect const & rect, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void clear(Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void VScroll(int scroll, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void HScroll(int scroll, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void drawGlyph(Glyph const & glyph, GlyphOptions glyphOptions, RGB888 penColor, RGB888 brushColor, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void invertRect(Rect const & rect, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void copyRect(Rect const & source, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void swapFGBG(Rect const & rect, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmap_Native(int destX, int destY, Bitmap const * bitmap, int X1, int Y1, int XCount, int YCount);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmap_Mask(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmap_RGBA2222(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmap_RGBA8888(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount);

  // abstract method of BitmappedDisplayController
  void rawCopyToBitmap(int srcX, int srcY, int width, void * saveBuffer, int X1, int Y1, int XCount, int YCount);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmapWithMatrix_Mask(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmapWithMatrix_RGBA2222(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix);

  // abstract method of BitmappedDisplayController
  void rawDrawBitmapWithMatrix_RGBA8888(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix);

  // abstract method of BitmappedDisplayController
  void fillRow(int y, int x1, int x2, RGB888 color);

  void rawFillRow(int y, int x1, int x2, uint8_t colorIndex);

  void rawORRow(int y, int x1, int x2, uint8_t colorIndex);

  void rawANDRow(int y, int x1, int x2, uint8_t colorIndex);

  void rawXORRow(int y, int x1, int x2, uint8_t colorIndex);

  void rawInvertRow(int y, int x1, int x2);

  void rawCopyRow(int x1, int x2, int srcY, int dstY);

  void swapRows(int yA, int yB, int x1, int x2);

  // abstract method of BitmappedDisplayController
  void absDrawLine(int X1, int Y1, int X2, int Y2, RGB888 color);
  void absFillRowScan(FillRowParams const & params, Rect & updateRect);
  void absFloodFill(FillRowParams const & params, Rect & updateRect);
  void absDrawEllipseSheared(EllipseShearedParams const & params, Rect & updateRect);

  // abstract method of BitmappedDisplayController
  int getBitmapSavePixelSize() { return 1; }




  static P4Rgb888Controller *    s_instance;

  volatile uint16_t           m_packedPaletteIndexPair_to_signals[1];

};



} // end of namespace





