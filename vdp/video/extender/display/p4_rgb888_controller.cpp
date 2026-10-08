// RGB-001 experiment. Adapted from retained FabGL VGA64Controller (GPLv3).
// Common Canvas rasterizers and one-byte Native asset/background contracts remain
// unchanged; this file replaces physical pixel access, fills and scroll copies.
// Production experimentation borrows HDMI pixels with a720p stride. Logical
// swaps wait for actual DMA release; ordinary primitives perform no frame copy.
// Owned compact rows remain available to the host golden test substrate only.
// PORT-003 R1: select the original native-row implementation without the
// classic ESP32 physical engine. Drawing/palette methods remain upstream.
// AGON_EXTENDER_STOCK_ROWS_PROOF is synchronous. STOCK_RUNTIME shares only
// this native allocation/peripheral exclusion and binds its own worker/output.
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


#include <alloca.h>
#include <stdarg.h>
#include <math.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#if !defined(AGON_EXTENDER_STOCK_ROWS_PROOF) && !defined(AGON_EXTENDER_STOCK_RUNTIME)
#include "soc/i2s_struct.h"
#include "soc/i2s_reg.h"
#include "driver/periph_ctrl.h"
#include "soc/rtc.h"
#include "esp_spi_flash.h"
#endif
#include "esp_heap_caps.h"
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "extender/display/rolling/bridge.h"
#endif

#include "fabutils.h"
#include "extender/display/p4_rgb888_controller.hpp"
#include "extender/display/hdmi_geometry.hpp"
#if !defined(AGON_EXTENDER_STOCK_ROWS_PROOF) && !defined(AGON_EXTENDER_STOCK_RUNTIME)
#include "devdrivers/swgenerator.h"
#endif



#pragma GCC optimize ("O2")




#if defined(AGON_EXTENDER_STOCK_ROWS_PROOF) || defined(AGON_EXTENDER_STOCK_RUNTIME)
#define AGON_EXTENDER_VGA_ISR(handler) nullptr
#else
#define AGON_EXTENDER_VGA_ISR(handler) handler
#endif

#undef VGA_PIXEL
#undef VGA_PIXELINROW
#undef VGA_INVERT_PIXEL
#define VGA_PIXELINROW(row,x) agon::extender::display::Rgb888PixelRef((uint8_t*)(row)+(x)*3)
#define VGA_PIXEL(x,y) VGA_PIXELINROW(m_viewPort[y],x)
#define VGA_INVERT_PIXEL(x,y) (VGA_PIXEL(x,y) ^= 63)

namespace fabgl {




#define VGA64_COLUMNSQUANTUM 16


/*************************************************************************************/
/* P4Rgb888Controller definitions */


P4Rgb888Controller * P4Rgb888Controller::s_instance = nullptr;



P4Rgb888Controller::P4Rgb888Controller()
  : VGAPalettedController(VGA64_LinesCount, VGA64_COLUMNSQUANTUM, NativePixelFormat::SBGR2222, 1, 3, nullptr)
{
  s_instance = this;
}


void P4Rgb888Controller::setupDefaultPalette()
{
  for (int colorIndex = 0; colorIndex < 16; ++colorIndex) {
    RGB888 rgb888((Color)colorIndex);
    setPaletteItem(colorIndex, rgb888);
  }
}


void P4Rgb888Controller::setPaletteItem(int index, RGB888 const & color)
{
}


std::function<uint8_t(RGB888 const &)> P4Rgb888Controller::getPixelLambda(PaintMode mode)
{
  switch (mode) {
    case PaintMode::XOR:
      return [&] (RGB888 const & color) { return preparePixel(color) & 63; };
    default: // PaintMode::Set, et al
      return [&] (RGB888 const & color) { return preparePixel(color); };
  }
}


std::function<void(int X, int Y, uint8_t colorIndex)> P4Rgb888Controller::setPixelLambda(PaintMode mode)
{
  switch (mode) {
    case PaintMode::Set:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) = pattern; };
    case PaintMode::OR:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) |= pattern; };
    case PaintMode::ORNOT:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) |= (~pattern) & 63; };
    case PaintMode::AND:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) &= pattern; };
    case PaintMode::ANDNOT:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) &= ((~pattern) & 63) | m_HVSync; };
    case PaintMode::XOR:
      return [&] (int X, int Y, uint8_t pattern) { VGA_PIXEL(X, Y) ^= pattern; };
    case PaintMode::Invert:
      return [&] (int X, int Y, uint8_t pattern) { VGA_INVERT_PIXEL(X, Y); };
    default:  // PaintMode::NoOp
      return [&] (int X, int Y, uint8_t pattern) { return; };
  }
}


std::function<void(uint8_t * row, int x, uint8_t colorIndex)> P4Rgb888Controller::setRowPixelLambda(PaintMode mode)
{
  switch (mode) {
    case PaintMode::Set:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) = pattern; };
    case PaintMode::OR:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) |= pattern; };
    case PaintMode::ORNOT:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) |= (~pattern & 63); };
    case PaintMode::AND:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) &= pattern; };
    case PaintMode::ANDNOT:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) &= (~pattern & 63) | m_HVSync; };
    case PaintMode::XOR:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) ^= pattern & 63; };
    case PaintMode::Invert:
      return [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row,x) ^= 63; };
    default:  // PaintMode::NoOp
      return [&] (uint8_t * row, int x, uint8_t pattern) { return; };
  }
}


std::function<void(int Y, int X1, int X2, uint8_t colorIndex)> P4Rgb888Controller::fillRowLambda(PaintMode mode)
{
  switch (mode) {
    case PaintMode::Set:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawFillRow(Y, X1, X2, pattern); };
    case PaintMode::OR:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawORRow(Y, X1, X2, pattern); };
    case PaintMode::ORNOT:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawORRow(Y, X1, X2, (~pattern & 63)); };
    case PaintMode::AND:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawANDRow(Y, X1, X2, pattern); };
    case PaintMode::ANDNOT:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawANDRow(Y, X1, X2, (~pattern & 63) | m_HVSync); };
    case PaintMode::XOR:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawXORRow(Y, X1, X2, pattern); };
    case PaintMode::Invert:
      return [&] (int Y, int X1, int X2, uint8_t pattern) { rawInvertRow(Y, X1, X2); };
    default:  // PaintMode::NoOp
      return [&] (int Y, int X1, int X2, uint8_t pattern) { return; };
  }
}


void P4Rgb888Controller::setPixelAt(PixelDesc const & pixelDesc, Rect & updateRect)
{
  auto paintMode = paintState().paintOptions.mode;
  genericSetPixelAt(pixelDesc, updateRect, getPixelLambda(paintMode), setPixelLambda(paintMode));
}


// coordinates are absolute values (not relative to origin)
// line clipped on current absolute clipping rectangle
void P4Rgb888Controller::absDrawLine(int X1, int Y1, int X2, int Y2, RGB888 color)
{
  auto paintMode = paintState().paintOptions.NOT ? PaintMode::NOT : paintState().paintOptions.mode;
  genericAbsDrawLine(X1, Y1, X2, Y2, color,
                     getPixelLambda(paintMode),
                     fillRowLambda(paintMode),
                     setPixelLambda(paintMode)
                     );
}


void P4Rgb888Controller::absFillRowScan(FillRowParams const & params, Rect & updateRect)
{
  genericFillRowScan(params, updateRect,
                     getPixelLambda(PaintMode::Set),
                     [&] (int y) { return (uint8_t*) m_viewPort[y]; },
                     [&] (uint8_t * row, int x) -> int { return uint8_t(VGA_PIXELINROW(row, x)); }
                     );
}


void P4Rgb888Controller::absFloodFill(FillRowParams const & params, Rect & updateRect)
{
  genericFloodFill(params, updateRect,
                   getPixelLambda(PaintMode::Set),
                   [&] (int y) { return (uint8_t*) m_viewPort[y]; },
                   [&] (uint8_t * row, int x) -> int { return uint8_t(VGA_PIXELINROW(row, x)); }
                   );
}


// parameters not checked
void P4Rgb888Controller::fillRow(int y, int x1, int x2, RGB888 color)
{
  // This version, passing an RGB888 color, is only used by shape drawing methods,
  // so we will pick fill method based on paint mode
  auto paintMode = paintState().paintOptions.mode;
  auto getPixel = getPixelLambda(paintMode);
  auto pixel = getPixel(color);
  auto fill = fillRowLambda(paintMode);
  fill(y, x1, x2, pixel);
}


// parameters not checked
void P4Rgb888Controller::rawFillRow(int y, int x1, int x2, uint8_t pattern)
{
  agon::extender::display::fillRgb888((uint8_t*)m_viewPort[y] + x1 * 3, x2 - x1 + 1, pattern);
}


// parameters not checked
void P4Rgb888Controller::rawORRow(int y, int x1, int x2, uint8_t pattern)
{
  auto row = m_viewPort[y];
  // naive implementation - just do whole row iteratively
  for (int x = x1; x <= x2; ++x) {
    VGA_PIXELINROW(row, x) |= pattern;
  }
}


// parameters not checked
void P4Rgb888Controller::rawANDRow(int y, int x1, int x2, uint8_t pattern)
{
  auto row = m_viewPort[y];
  // naive implementation - just do whole row iteratively
  for (int x = x1; x <= x2; ++x) {
    VGA_PIXELINROW(row, x) &= pattern;
  }
}


// parameters not checked
void P4Rgb888Controller::rawXORRow(int y, int x1, int x2, uint8_t pattern)
{
  auto row = m_viewPort[y];
  // naive implementation - just do whole row iteratively
  for (int x = x1; x <= x2; ++x) {
    VGA_PIXELINROW(row, x) ^= pattern;
  }
}


// parameters not checked
void P4Rgb888Controller::rawInvertRow(int y, int x1, int x2)
{
  auto row = m_viewPort[y];
  for (int x=x1; x<=x2; ++x) VGA_PIXELINROW(row,x) ^= 63;
}


void P4Rgb888Controller::rawCopyRow(int x1, int x2, int srcY, int dstY)
{
  // RGB-001 r02 / SCAN-001: the stock copy-scroll helper orders rows so a
  // destination never destroys an unread source. Distinct panel rows have
  // disjoint spans even with a centered viewport and the larger HDMI stride.
  auto src = (uint8_t*)m_viewPort[srcY] + x1 * 3;
  auto dst = (uint8_t*)m_viewPort[dstY] + x1 * 3;
  memcpy(dst, src, (x2 - x1 + 1) * 3);
}


void P4Rgb888Controller::swapRows(int yA, int yB, int x1, int x2)
{
  auto a=(uint8_t*)m_viewPort[yA] + x1*3;
  auto b=(uint8_t*)m_viewPort[yB] + x1*3;
  for(int i=0;i<(x2-x1+1)*3;++i) tswap(a[i],b[i]);
}


void P4Rgb888Controller::drawEllipse(Size const & size, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  genericDrawEllipse(size, updateRect, getPixelLambda(mode), setPixelLambda(mode));
}


void P4Rgb888Controller::absDrawEllipseSheared(EllipseShearedParams const & params, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  genericDrawEllipseSheared(params, updateRect, getPixelLambda(mode), setPixelLambda(mode));
}


void P4Rgb888Controller::drawArc(Rect const & rect, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  genericDrawArc(rect, updateRect, getPixelLambda(mode), setPixelLambda(mode));
}


void P4Rgb888Controller::fillSegment(Rect const & rect, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  genericFillSegment(rect, updateRect, getPixelLambda(mode), fillRowLambda(mode));
}


void P4Rgb888Controller::fillSector(Rect const & rect, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  genericFillSector(rect, updateRect, getPixelLambda(mode), fillRowLambda(mode));
}


void P4Rgb888Controller::clear(Rect & updateRect)
{
  hideSprites(updateRect);
  const auto pattern=preparePixel(getActualBrushColor());
  for(int y=0;y<m_viewPortHeight;++y) rawFillRow(y,0,m_viewPortWidth-1,pattern);
}


// scroll < 0 -> scroll UP
// scroll > 0 -> scroll DOWN
void P4Rgb888Controller::VScroll(int scroll, Rect & updateRect)
{
  if (panelStorage()) {
    // Fixed DMA row addresses cannot follow pointer rotation. Reuse stock's
    // copy/fill algorithm unchanged: copy only the scrolling field rather than
    // exchanging both sidebars and then the entire physical row (r01). This
    // reduces memory work; it does not make single-buffer scanout atomic.
    genericVScroll(scroll, updateRect,
                   [&] (int x1, int x2, int srcY, int dstY) { rawCopyRow(x1, x2, srcY, dstY); },
                   [&] (int y, int x1, int x2, RGB888 color) { rawFillRow(y, x1, x2, preparePixel(color)); });
    return;
  }
  genericVScroll(scroll, updateRect,
                 [&] (int yA, int yB, int x1, int x2)      { swapRows(yA, yB, x1, x2); },              // swapRowsCopying
                 [&] (int yA, int yB)                    { tswap(m_viewPort[yA], m_viewPort[yB]); },
                 [&] (int y, int x1, int x2, RGB888 color) { rawFillRow(y, x1, x2, preparePixel(color)); }         // rawFillRow
                );
}


// Scrolling by 1, 2, 3 and 4 pixels is optimized. Also scrolling multiples of 4 (8, 16, 24...) is optimized.
// Scrolling by other values requires up to three steps (scopose scrolling by 1, 2, 3 or 4): for example scrolling by 5 is scomposed to 4 and 1, scrolling
// by 6 is 4 + 2, etc.
// Horizontal scrolling region start and size (X2-X1+1) must be aligned to 32 bits, otherwise the unoptimized (very slow) version is used.
void P4Rgb888Controller::HScroll(int scroll, Rect & updateRect)
{
  hideSprites(updateRect);
  const auto &r=paintState().scrollingRegion;
  const int width=r.X2-r.X1+1;
  const int amount=tmin(width,abs(scroll));
  const auto pattern=preparePixel(getActualBrushColor());
  if(!amount)return;
  for(int y=r.Y1;y<=r.Y2;++y) {
    auto row=(uint8_t*)m_viewPort[y] + r.X1*3;
    if(scroll<0) {
      memmove(row,row+amount*3,(width-amount)*3);
      rawFillRow(y,r.X2-amount+1,r.X2,pattern);
    } else {
      memmove(row+amount*3,row,(width-amount)*3);
      rawFillRow(y,r.X1,r.X1+amount-1,pattern);
    }
  }
}


void P4Rgb888Controller::drawGlyph(Glyph const & glyph, GlyphOptions glyphOptions, RGB888 penColor, RGB888 brushColor, Rect & updateRect)
{
  auto mode = paintState().paintOptions.mode;
  auto getPixel = getPixelLambda(mode);
  auto setRowPixel = setRowPixelLambda(mode);
  genericDrawGlyph(glyph, glyphOptions, penColor, brushColor, updateRect,
                   getPixel,
                   [&] (int y) { return (uint8_t*) m_viewPort[y]; },
                   setRowPixel
                  );
}


void P4Rgb888Controller::invertRect(Rect const & rect, Rect & updateRect)
{
  genericInvertRect(rect, updateRect,
                    [&] (int Y, int X1, int X2) { rawInvertRow(Y, X1, X2); }
                   );
}


void P4Rgb888Controller::swapFGBG(Rect const & rect, Rect & updateRect)
{
  genericSwapFGBG(rect, updateRect,
                  [&] (RGB888 const & color)                  { return preparePixel(color); },
                  [&] (int y)                                 { return (uint8_t*) m_viewPort[y]; },
                  [&] (uint8_t * row, int x)                  { return uint8_t(VGA_PIXELINROW(row, x)); },
                  [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) = pattern; }
                 );
}


// Slow operation!
// supports overlapping of source and dest rectangles
void P4Rgb888Controller::copyRect(Rect const & source, Rect & updateRect)
{
  genericCopyRect(source, updateRect,
                  [&] (int y)                                 { return (uint8_t*) m_viewPort[y]; },
                  [&] (uint8_t * row, int x)                  { return uint8_t(VGA_PIXELINROW(row, x)); },
                  [&] (uint8_t * row, int x, uint8_t pattern) { VGA_PIXELINROW(row, x) = pattern; }
                 );
}


// no bounds check is done!
void P4Rgb888Controller::readScreen(Rect const & rect, RGB888 * destBuf)
{
  prepareForDrawing();
  for (int y = rect.Y1; y <= rect.Y2; ++y) {
    uint8_t * row = (uint8_t*) m_viewPort[y];
    for (int x = rect.X1; x <= rect.X2; ++x, ++destBuf) {
      uint8_t rawpix = VGA_PIXELINROW(row, x);
      *destBuf = RGB888((rawpix & 3) * 85, ((rawpix >> 2) & 3) * 85, ((rawpix >> 4) & 3) * 85);
    }
  }
}


void P4Rgb888Controller::rawDrawBitmap_Native(int destX, int destY, Bitmap const * bitmap, int X1, int Y1, int XCount, int YCount)
{
  genericRawDrawBitmap_Native(destX, destY, (uint8_t*) bitmap->data, bitmap->width, X1, Y1, XCount, YCount,
                              [&] (int y) { return (uint8_t*) m_viewPort[y]; },   // rawGetRow
                              [&] (uint8_t * row, int x, uint8_t src) { VGA_PIXELINROW(row, x) = src; }  // rawSetPixelInRow
                             );
}


void P4Rgb888Controller::rawDrawBitmap_Mask(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);
  auto getPixel = getPixelLambda(paintMode);
  auto pattern = getPixel(paintState().paintOptions.swapFGBG ? paintState().penColor : bitmap->foregroundColor);
  genericRawDrawBitmap_Mask(destX, destY, bitmap, (uint8_t*)saveBackground, X1, Y1, XCount, YCount,
                            [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                            [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                            [&] (uint8_t * row, int x) { setRowPixel(row, x, pattern); }      // rawSetPixelInRow
                           );
}


void P4Rgb888Controller::rawDrawBitmap_RGBA2222(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);

  if (paintState().paintOptions.swapFGBG) {
    // used for bitmap plots to indicate drawing with BG color instead of bitmap color
    auto bg = preparePixel(paintState().penColor);
    genericRawDrawBitmap_RGBA2222(destX, destY, bitmap, (uint8_t*)saveBackground, X1, Y1, XCount, YCount,
                                  [&] (int y)                             { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                  [&] (uint8_t * row, int x)              { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                  [&] (uint8_t * row, int x, uint8_t src) { setRowPixel(row, x, bg); }           // rawSetPixelInRow
                                );
    return;
  }

  genericRawDrawBitmap_RGBA2222(destX, destY, bitmap, (uint8_t*)saveBackground, X1, Y1, XCount, YCount,
                                [&] (int y)                             { return (uint8_t*) m_viewPort[y]; },              // rawGetRow
                                [&] (uint8_t * row, int x)              { return uint8_t(VGA_PIXELINROW(row, x)); },                // rawGetPixelInRow
                                [&] (uint8_t * row, int x, uint8_t src) { setRowPixel(row, x, m_HVSync | (src & 0x3f)); }  // rawSetPixelInRow
                               );
}


void P4Rgb888Controller::rawDrawBitmap_RGBA8888(int destX, int destY, Bitmap const * bitmap, void * saveBackground, int X1, int Y1, int XCount, int YCount)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);

  if (paintState().paintOptions.swapFGBG) {
    // used for bitmap plots to indicate drawing with BG color instead of bitmap color
    auto bg = preparePixel(paintState().penColor);
    genericRawDrawBitmap_RGBA8888(destX, destY, bitmap, (uint8_t*)saveBackground, X1, Y1, XCount, YCount,
                                  [&] (int y)                                      { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                  [&] (uint8_t * row, int x)                       { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                  [&] (uint8_t * row, int x, RGBA8888 const & src) { setRowPixel(row, x, bg); }           // rawSetPixelInRow
                                  );
    return;
  }

  genericRawDrawBitmap_RGBA8888(destX, destY, bitmap, (uint8_t*)saveBackground, X1, Y1, XCount, YCount,
                                 [&] (int y)                                      { return (uint8_t*) m_viewPort[y]; },   // rawGetRow
                                 [&] (uint8_t * row, int x)                       { return uint8_t(VGA_PIXELINROW(row, x)); },     // rawGetPixelInRow
                                 [&] (uint8_t * row, int x, RGBA8888 const & src) { setRowPixel(row, x, m_HVSync | (src.R >> 6) | (src.G >> 6 << 2) | (src.B >> 6 << 4)); }   // rawSetPixelInRow
                                );
}


void P4Rgb888Controller::rawCopyToBitmap(int srcX, int srcY, int width, void * saveBuffer, int X1, int Y1, int XCount, int YCount)
{
  genericRawCopyToBitmap(srcX, srcY, width, (uint8_t*)saveBuffer, X1, Y1, XCount, YCount,
                        [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                        [&] (uint8_t * row, int x) { return 0xC0 | VGA_PIXELINROW(row, x); }     // rawGetPixelInRow
                      );
}


void P4Rgb888Controller::rawDrawBitmapWithMatrix_Mask(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);
  auto getPixel = getPixelLambda(paintMode);
  auto pattern = getPixel(paintState().paintOptions.swapFGBG ? paintState().penColor : bitmap->foregroundColor);
  genericRawDrawTransformedBitmap_Mask(destX, destY, drawingRect, bitmap, invMatrix,
                                          [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                          // [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                          [&] (uint8_t * row, int x) { setRowPixel(row, x, pattern); }  // rawSetPixelInRow
                                         );
}


void P4Rgb888Controller::rawDrawBitmapWithMatrix_RGBA2222(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);

  if (paintState().paintOptions.swapFGBG) {
    // used for bitmap plots to indicate drawing with BG color instead of bitmap color
    auto bg = preparePixel(paintState().penColor);
    genericRawDrawTransformedBitmap_RGBA2222(destX, destY, drawingRect, bitmap, invMatrix,
                                            [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                            // [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                            [&] (uint8_t * row, int x, uint8_t src) { setRowPixel(row, x, bg); }  // rawSetPixelInRow
                                          );
    return;
  }

  genericRawDrawTransformedBitmap_RGBA2222(destX, destY, drawingRect, bitmap, invMatrix,
                                          [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                          // [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                          [&] (uint8_t * row, int x, uint8_t src) { setRowPixel(row, x, src); }  // rawSetPixelInRow
                                         );
}


void P4Rgb888Controller::rawDrawBitmapWithMatrix_RGBA8888(int destX, int destY, Rect & drawingRect, Bitmap const * bitmap, const float * invMatrix)
{
  auto paintMode = paintState().paintOptions.mode;
  auto setRowPixel = setRowPixelLambda(paintMode);

  if (paintState().paintOptions.swapFGBG) {
    // used for bitmap plots to indicate drawing with BG color instead of bitmap color
    auto bg = preparePixel(paintState().penColor);
    genericRawDrawTransformedBitmap_RGBA8888(destX, destY, drawingRect, bitmap, invMatrix,
                                            [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                            // [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                            [&] (uint8_t * row, int x, RGBA8888 const & src) { setRowPixel(row, x, bg); }           // rawSetPixelInRow
                                          );
    return;
  }

  genericRawDrawTransformedBitmap_RGBA8888(destX, destY, drawingRect, bitmap, invMatrix,
                                          [&] (int y)                { return (uint8_t*) m_viewPort[y]; },  // rawGetRow
                                          // [&] (uint8_t * row, int x) { return uint8_t(VGA_PIXELINROW(row, x)); },    // rawGetPixelInRow
                                          [&] (uint8_t * row, int x, RGBA8888 const & src) { setRowPixel(row, x, m_HVSync | (src.R >> 6) | (src.G >> 6 << 2) | (src.B >> 6 << 4)); }   // rawSetPixelInRow
                                         );
}



void P4Rgb888Controller::setResolution(VGATimings const &t,int w,int h,bool doubled) {
  VGAPalettedController::setResolution(t,w,h,doubled);
  if(!isViewPortAllocated())return;
  for(int y=0;y<m_viewPortHeight;++y) {
    memset((void*)m_viewPort[y],0,m_viewPortWidth*3);
    if(doubled)memset((void*)m_viewPortVisible[y],0,m_viewPortWidth*3);
  }
}

bool P4Rgb888Controller::allocateViewPort() {
  if(!panelStorage()) return VGAPalettedController::allocateViewPort();
  if(m_viewPortWidth>848 || m_viewPortWidth>m_panel.width || m_viewPortHeight>m_panel.height ||
     m_panel.stride<std::size_t(m_panel.width)*3 ||
     (isDoubleBuffered() && (m_panel.count<2 || !m_panel.swap))) return false;
  const auto count=isDoubleBuffered()?2u:1u;
  volatile uint8_t **rows[2]{};
  for(unsigned i=0;i<count;++i) {
    rows[i]=static_cast<volatile uint8_t **>(heap_caps_malloc(m_viewPortHeight*sizeof(uint8_t*),MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
#ifndef AGON_EXTENDER_ROLLING_SCANOUT
    m_overlayBackground[i]=static_cast<uint8_t *>(heap_caps_malloc(m_viewPortWidth*m_viewPortHeight,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    m_overlayRows[i]=static_cast<uint8_t *>(heap_caps_malloc(m_viewPortHeight,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
    if(!rows[i] || !m_overlayBackground[i] || !m_overlayRows[i]) {
#else
    if(!rows[i]) {
#endif
      for(unsigned j=0;j<2;++j) {heap_caps_free(rows[j]);heap_caps_free(m_overlayBackground[j]);heap_caps_free(m_overlayRows[j]);m_overlayBackground[j]=m_overlayRows[j]=nullptr;}
      return false;
    }
    if(m_overlayRows[i])memset(m_overlayRows[i],0,m_viewPortHeight);
  }
  const int x=(m_panel.width-m_viewPortWidth)/2,y=(m_panel.height-m_viewPortHeight)/2;
  for(unsigned i=0;i<count;++i) {
    const auto index=isDoubleBuffered()?i:m_panel.front;
    // Mode-boundary initialization only. No per-presentation720p clear.
    memset(m_panel.buffers[index],0,m_panel.stride*m_panel.height);
    for(int row=0;row<m_viewPortHeight;++row)
      rows[i][row]=m_panel.buffers[index]+(y+row)*m_panel.stride+x*3;
  }
  // Overlay storage is indexed by physical buffer, as are the row descriptors.
  if(count==1 && m_panel.front==1) {
    tswap(m_overlayBackground[0],m_overlayBackground[1]);
    tswap(m_overlayRows[0],m_overlayRows[1]);
  }
  bindBorrowedViewPort(rows[isDoubleBuffered()?1-m_panel.front:0],rows[isDoubleBuffered()?m_panel.front:0]);
  return true;
}

void P4Rgb888Controller::freeViewPort() {
  // m_viewPortMemoryPool is null for borrowed pixels; the base frees descriptors
  // and allocation state, never the LCD owner's pixel memory.
  VGAPalettedController::freeViewPort();
  for(unsigned i=0;i<2;++i) {heap_caps_free(m_overlayBackground[i]);heap_caps_free(m_overlayRows[i]);m_overlayBackground[i]=m_overlayRows[i]=nullptr;}
  m_overlaysActive[0]=m_overlaysActive[1]=false;
}

unsigned P4Rgb888Controller::panelIndex(volatile uint8_t **rows) const {
  const auto address=reinterpret_cast<uintptr_t>(rows[0]);
  const auto second=reinterpret_cast<uintptr_t>(m_panel.buffers[1]);
  return second && address>=second && address<second+m_panel.stride*m_panel.height ? 1u:0u;
}

void P4Rgb888Controller::restorePanelOverlays(unsigned index) {
  if(!m_overlaysActive[index])return;
  auto rows=panelIndex(m_viewPort)==index?m_viewPort:m_viewPortVisible;
  for(int y=0;y<m_viewPortHeight;++y) if(m_overlayRows[index][y]) {
    auto row=(uint8_t*)rows[y];
    for(int x=0;x<m_viewPortWidth;++x) VGA_PIXELINROW(row,x)=m_overlayBackground[index][y*m_viewPortWidth+x];
    m_overlayRows[index][y]=0;
  }
  m_overlaysActive[index]=false;
}

void P4Rgb888Controller::prepareForDrawing() {
  if(panelStorage() && m_viewPort) restorePanelOverlays(panelIndex(m_viewPort));
}

void P4Rgb888Controller::composePanelOverlays(unsigned index) {
  auto rows=panelIndex(m_viewPort)==index?m_viewPort:m_viewPortVisible;
  restorePanelOverlays(index);
  alignas(8)uint8_t signal[848];
  for(int y=0;y<m_viewPortHeight;++y) if(overlayIntersectsRow(y)) {
    auto row=(uint8_t*)rows[y];
    for(int x=0;x<m_viewPortWidth;++x) {
      auto pixel=uint8_t(VGA_PIXELINROW(row,x));
      m_overlayBackground[index][y*m_viewPortWidth+x]=pixel;
      signal[x^2]=m_HVSync|pixel;
    }
    decorateScanLinePixels(signal,y);
    agon::extender::display::expandSignalRowToHdmi(signal,row,0,m_viewPortWidth);
    m_overlayRows[index][y]=1;
    m_overlaysActive[index]=true;
  }
}

void P4Rgb888Controller::swapBuffers() {
  if(!panelStorage()) {VGAPalettedController::swapBuffers();return;}
  AGON_STOCK_NATIVE_GUARD;
  if(!isDoubleBuffered()) return;
  const unsigned target=panelIndex(m_viewPort);
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  if(!agon_scanout_stage(this,target,m_viewPortWidth,m_viewPortHeight))return;
#else
  composePanelOverlays(target);
#endif
  // This callback runs a core1 submission task independent of the drawing
  // drain. Holding native exclusion here cannot prevent that task or DMA from
  // progressing. The ordinary SwapBuffers waiter is notified only afterward.
  if(!m_panel.swap(m_panel.context,target)) return; // detached-mode cancellation
  VGAPalettedController::swapBuffers();
  restorePanelOverlays(panelIndex(m_viewPort));
}

unsigned P4Rgb888Controller::preparePanelFrame(int &marker) {
  const unsigned index=panelIndex(m_viewPortVisible);
  // Double-buffer overlays are completed on the back before each explicit
  // swap; never draw into its scanned front during an ordinary presentation.
#ifndef AGON_EXTENDER_ROLLING_SCANOUT
  if(!isDoubleBuffered()) composePanelOverlays(index);
#endif
  auto row=m_viewPortVisible[0];
  auto pixel=[&](int x){return uint8_t(VGA_PIXELINROW(row,x))&63;};
  marker=-1;
  if(m_viewPortWidth>=20 && pixel(0)==63 && pixel(1)==0 && pixel(18)==0 && pixel(19)==63) {
    unsigned a=0,b=0;for(int i=0;i<8;++i){a|=(pixel(2+i)!=0)<<i;b|=(pixel(10+i)!=0)<<i;}
    if((a^b)==255 && a<40)marker=a;
  }
  return index;
}

bool P4Rgb888Controller::overlayIntersectsRow(int y) {
  auto intersects=[y](Sprite *s) {
    if(!s||!s->visible)return false;
    auto frame=s->getFrame();
    return frame && y>=s->y && y<s->y+frame->height;
  };
  if(intersects(textCursor()) || intersects(mouseCursor()))return true;
  for(int i=0;i<spritesCount();++i) {
    auto s=getSprite(i);
    if(s->hardware && s->allowDraw && intersects(s))return true;
  }
  return false;
}

void P4Rgb888Controller::encodeSignalRow(int y,uint8_t *signal) {
  auto row=(uint8_t*)m_viewPortVisible[y];
  for(int x=0;x<m_viewPortWidth;++x) signal[x^2]=m_HVSync | uint8_t(VGA_PIXELINROW(row,x));
  decorateScanLinePixels(signal,y);
}

void P4Rgb888Controller::copyRgb888Row(int y,uint8_t *destination,uint8_t *signal) {
  // Keep overlays out of the persistent logical background. Only rows with a
  // visible overlay need the stock RGB222 decorator; ordinary rows are memcpy.
  // All pixel/overlay access occurs under the runtime adapter's native guard.
  if(overlayIntersectsRow(y)) {
    encodeSignalRow(y,signal);
    agon::extender::display::expandSignalRowToHdmi(signal,destination,0,m_viewPortWidth);
  } else {
    memcpy(destination,(void const*)m_viewPortVisible[y],m_viewPortWidth*3);
    // The benchmark's 20-pixel identity marker is read without converting the
    // rest of the image. Signal bytes are also useful to host correctness tests.
    for(int x=0;x<tmin(20,int(m_viewPortWidth));++x)
      signal[x^2]=m_HVSync | uint8_t(VGA_PIXELINROW(m_viewPortVisible[y],x));
  }
}

} // namespace fabgl
