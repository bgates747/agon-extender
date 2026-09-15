#ifdef AGON_GRAPHICS_TIMING
#include "extender/diagnostics/graphics_timing.hpp"
#else
#define AGON_GRAPHICS_SCOPE(metric)
#endif
// PORT-003 R1: select the original native-row implementation without the
// classic ESP32 physical engine. Drawing/palette methods remain upstream.
// AGON_EXTENDER_STOCK_ROWS_PROOF is synchronous. STOCK_RUNTIME shares only
// this native allocation/peripheral exclusion and binds its own worker/output.
/*
  Created by Fabrizio Di Vittorio (fdivitto2013@gmail.com) - <http://www.fabgl.com>
  Copyright (c) 2019-2022 Fabrizio Di Vittorio.
  All rights reserved.


* Please contact fdivitto2013@gmail.com if you need a commercial license.


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
#if defined(AGON_EXTENDER_INTERNAL_FRAMEBUFFER)
#include "esp_log.h"
#endif

#include "fabutils.h"
#include "vgapalettedcontroller.h"
#if !defined(AGON_EXTENDER_STOCK_ROWS_PROOF) && !defined(AGON_EXTENDER_STOCK_RUNTIME)
#include "devdrivers/swgenerator.h"
#endif



#pragma GCC optimize ("O2")



namespace fabgl {





/*************************************************************************************/
/* VGAPalettedController definitions */


VGAPalettedController::VGAPalettedController(int linesCount, int columnsQuantum, NativePixelFormat nativePixelFormat, int viewPortRatioDiv, int viewPortRatioMul, intr_handler_t isrHandler, int signalTableSize)
  : m_columnsQuantum(columnsQuantum),
    m_nativePixelFormat(nativePixelFormat),
    m_viewPortRatioDiv(viewPortRatioDiv),
    m_viewPortRatioMul(viewPortRatioMul),
    m_isrHandler(isrHandler),
    m_signalTableSize(signalTableSize)
{
  m_linesCount = linesCount;
  m_lines   = (volatile uint8_t**) heap_caps_malloc(sizeof(uint8_t*) * m_linesCount, MALLOC_CAP_32BIT | MALLOC_CAP_INTERNAL);
  m_palette = (RGB222*) heap_caps_malloc(sizeof(RGB222) * getPaletteSize(), MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
  createPalette(0);
  uint16_t signalList[2] = { 0, 0 };
  m_signalList = createSignalList(signalList, 1);
  m_currentSignalItem = m_signalList;
}


VGAPalettedController::~VGAPalettedController()
{
  heap_caps_free(m_palette);
  heap_caps_free(m_lines);
  for (auto it = m_signalMaps.begin(); it != m_signalMaps.end();) {
    if (it->second) {
      heap_caps_free((void *)it->second);
    }
    it = m_signalMaps.erase(it);
  }
  deleteSignalList(m_signalList);
}


void VGAPalettedController::init()
{
  VGABaseController::init();

  m_doubleBufferOverDMA      = false;
}


void VGAPalettedController::end()
{
  VGABaseController::end();
}


void VGAPalettedController::suspendBackgroundPrimitiveExecution()
{
  VGABaseController::suspendBackgroundPrimitiveExecution();
}

// make sure view port height is divisible by m_linesCount, view port width is divisible by m_columnsQuantum
void VGAPalettedController::checkViewPortSize()
{
  m_viewPortHeight &= ~(m_linesCount - 1);
  m_viewPortWidth  &= ~(m_columnsQuantum - 1);
}


void VGAPalettedController::allocateViewPort()
{
#if defined(AGON_EXTENDER_STOCK_RUNTIME)
  uint32_t caps = MALLOC_CAP_8BIT | MALLOC_CAP_SPIRAM;
#if defined(AGON_EXTENDER_INTERNAL_FRAMEBUFFER)
  // QUAL-003 N04p, optional diagnostic: upstream uses INTERNAL here. The P4
  // port chose PSRAM for mode capacity. Try the stock capability only when a
  // whole framebuffer fits one block plus stock reserve in the original control.
  // N04ab optionally uses stock pools below; neither policy trades away rows.
  // Fallback is explicit and is not evidence of internal-memory benefit.
  const size_t required = size_t(m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul)
                        * m_viewPortHeight * (isDoubleBuffered() ? 2u : 1u);
  const size_t available = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
  bool eligible = true;
#if defined(AGON_EXTENDER_INTERNAL_GAME_MODE)
  // N04q: do not consume internal memory for preceding startup modes. This
  // is a bounded mode20 comparison, not a general mode-capacity policy.
  eligible = m_viewPortWidth == 512 && m_viewPortHeight == 384
          && !isDoubleBuffered()
          && m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul == 512;
#endif
#if defined(AGON_EXTENDER_INTERNAL_POOLS)
  // QUAL-003 N04ab: the unchanged stock allocator accepts multiple pools.
  // A shortened attempt must be discarded before any row pointers publish.
  const size_t total = heap_caps_get_free_size(MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
  if (eligible && total >= required + FABGLIB_MINFREELARGESTBLOCK
      && available >= FABGLIB_MINFREELARGESTBLOCK)
    caps = MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL;
  const int requestedHeight = m_viewPortHeight;
  VGABaseController::allocateViewPort(caps, m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul);
  if ((caps & MALLOC_CAP_INTERNAL) && m_viewPortHeight != requestedHeight) {
    VGABaseController::freeViewPort();
    m_viewPortHeight = requestedHeight;
    caps = MALLOC_CAP_8BIT | MALLOC_CAP_SPIRAM;
    VGABaseController::allocateViewPort(caps, m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul);
  }
  ESP_LOGI("np-fb-pools", "requested=%d actual=%d free_before=%u free_after=%u",
           requestedHeight, m_viewPortHeight, unsigned(total),
           unsigned(heap_caps_get_free_size(MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL)));
#else
  if (eligible && available >= required + FABGLIB_MINFREELARGESTBLOCK)
    caps = MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL;
#endif
  ESP_LOGI("np-fb-memory", "width=%d height=%d bytes=%u largest=%u selected=%s",
           m_viewPortWidth, m_viewPortHeight, unsigned(required), unsigned(available),
           caps & MALLOC_CAP_INTERNAL ? "internal" : "psram-fallback");
#endif
#if !defined(AGON_EXTENDER_INTERNAL_POOLS)
  VGABaseController::allocateViewPort(caps, m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul);
#endif
#else
  VGABaseController::allocateViewPort(MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL, m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul);
#endif

  for (int i = 0; i < m_linesCount; ++i)
    m_lines[i] = (uint8_t*) heap_caps_malloc(m_viewPortWidth, MALLOC_CAP_DMA);
}


void VGAPalettedController::freeViewPort()
{
  VGABaseController::freeViewPort();

  for (int i = 0; i < m_linesCount; ++i) {
    heap_caps_free((void*)m_lines[i]);
    m_lines[i] = nullptr;
  }
}


void VGAPalettedController::setResolution(VGATimings const& timings, int viewPortWidth, int viewPortHeight, bool doubleBuffered)
{
  VGABaseController::setResolution(timings, viewPortWidth, viewPortHeight, doubleBuffered);

  s_viewPort        = m_viewPort;
  s_viewPortVisible = m_viewPortVisible;

  // fill view port
  for (int i = 0; i < m_viewPortHeight; ++i)
    memset((void*)(m_viewPort[i]), nativePixelFormat() == NativePixelFormat::SBGR2222 ? m_HVSync : 0, m_viewPortWidth / m_viewPortRatioDiv * m_viewPortRatioMul);

  deletePalette(65535);
  setupDefaultPalette();
  updateRGB2PaletteLUT();

  uint16_t signalList[2] = { 0, 0 };
  updateSignalList(signalList, 1);

#if !defined(AGON_EXTENDER_STOCK_ROWS_PROOF) && !defined(AGON_EXTENDER_STOCK_RUNTIME)
  calculateAvailableCyclesForDrawings();

  // must be started before interrupt alloc
  startGPIOStream();

  // ESP_INTR_FLAG_LEVEL1: should be less than PS2Controller interrupt level, necessary when running on the same core
  if (m_isr_handle == nullptr) {
    CoreUsage::setBusiestCore(FABGLIB_VIDEO_CPUINTENSIVE_TASKS_CORE);
    esp_intr_alloc_pinnedToCore(ETS_I2S1_INTR_SOURCE, ESP_INTR_FLAG_LEVEL1 | ESP_INTR_FLAG_IRAM, m_isrHandler, this, &m_isr_handle, FABGLIB_VIDEO_CPUINTENSIVE_TASKS_CORE);
    I2S1.int_clr.val     = 0xFFFFFFFF;
    I2S1.int_ena.out_eof = 1;
  }
#endif

  resumeBackgroundPrimitiveExecution();
}


void VGAPalettedController::onSetupDMABuffer(lldesc_t volatile * buffer, bool isStartOfVertFrontPorch, int scan, bool isVisible, int visibleRow)
{
  if (isVisible) {
    buffer->buf = (uint8_t *) m_lines[visibleRow % m_linesCount];

    // generate interrupt every half m_linesCount
    if ((scan == 0 && (visibleRow % (m_linesCount / 2)) == 0)) {
      if (visibleRow == 0)
        s_frameResetDesc = buffer;
      buffer->eof = 1;
    }
  }
}


int VGAPalettedController::getPaletteSize()
{
  switch (nativePixelFormat()) {
    case NativePixelFormat::PALETTE2:
      return 2;
    case NativePixelFormat::PALETTE4:
      return 4;
    case NativePixelFormat::PALETTE8:
      return 8;
    case NativePixelFormat::PALETTE16:
      return 16;
    default:
      return 0;
  }
}

void VGAPalettedController::setPaletteItem(int index, RGB888 const & color)
{
  setItemInPalette(0, index, color);
}


void VGAPalettedController::setItemInPalette(uint16_t paletteId, int index, RGB888 const & color)
{
  AGON_STOCK_NATIVE_GUARD;
  if (m_signalMaps.find(paletteId) == m_signalMaps.end()) {
    if (!createPalette(paletteId)) {
      return;
    }
  }
  index %= getPaletteSize();
  if (paletteId == 0) {
    m_palette[index] = color;
  }
  auto packed222 = RGB888toPackedRGB222(color);
  packSignals(index, packed222, m_signalMaps[paletteId]);
}



// rebuild m_packedRGB222_to_PaletteIndex
void VGAPalettedController::updateRGB2PaletteLUT()
{
  AGON_STOCK_NATIVE_GUARD;
  auto paletteSize = getPaletteSize();
  for (int r = 0; r < 4; ++r)
    for (int g = 0; g < 4; ++g)
      for (int b = 0; b < 4; ++b) {
        double H1, S1, V1;
        rgb222_to_hsv(r, g, b, &H1, &S1, &V1);
        int bestIdx = 0;
        int bestDst = 1000000000;
        for (int i = 0; i < paletteSize; ++i) {
          double H2, S2, V2;
          rgb222_to_hsv(m_palette[i].R, m_palette[i].G, m_palette[i].B, &H2, &S2, &V2);
          double AH = H1 - H2;
          double AS = S1 - S2;
          double AV = V1 - V2;
          int dst = AH * AH + AS * AS + AV * AV;
          if (dst <= bestDst) {  // "<=" to prioritize higher indexes
            bestIdx = i;
            bestDst = dst;
            if (bestDst == 0)
              break;
          }
        }
        m_packedRGB222_to_PaletteIndex[r | (g << 2) | (b << 4)] = bestIdx;
      }
}


bool VGAPalettedController::createPalette(uint16_t paletteId)
{
  AGON_STOCK_PALETTE_GUARD;
  if (m_signalTableSize == 0) {
    return false;
  }
  if (m_signalMaps.find(paletteId) == m_signalMaps.end()) {
    m_signalMaps[paletteId] = heap_caps_malloc(m_signalTableSize, MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
    if (!m_signalMaps[paletteId]) {
      m_signalMaps.erase(paletteId);
      // create failed
      return false;
    }
    if (paletteId == 0) {
      return true;
    }
  }
  // Duplicate palette 0 into new palette
  if (paletteId != 0) {
    memcpy(m_signalMaps[paletteId], m_signalMaps[0], m_signalTableSize);
  }
  return true;
}


void VGAPalettedController::deletePalette(uint16_t paletteId)
{
  AGON_STOCK_PALETTE_GUARD;
  if (paletteId == 0) {
    return;
  }
  if (paletteId == 65535) {
    // iterate over all palettes and delete them using deletePalette
    for (auto it = m_signalMaps.begin(); it != m_signalMaps.end(); ++it) {
      deletePalette(it->first);
    }
    return;
  }
  if (m_signalMaps.find(paletteId) != m_signalMaps.end()) {
    auto signals = m_signalMaps[paletteId];
    auto signalItem = m_signalList;
    while (signalItem) {
      if (signalItem->signals == signals) {
        signalItem->signals = m_signalMaps[0];
      }
      signalItem = signalItem->next;
    }
    heap_caps_free(m_signalMaps[paletteId]);
    m_signalMaps.erase(paletteId);
  }
}


void VGAPalettedController::deleteSignalList(PaletteListItem * item)
{
  if (item) {
    deleteSignalList(item->next);
    heap_caps_free(item);
  }
}


void VGAPalettedController::updateSignalList(uint16_t * rawList, int entries)
{
  AGON_STOCK_PALETTE_GUARD;
  // Walk list, updating existing signal list
  // creating new list if we exceed the current list,
  // deleting any remaining items if we have fewer entries
  PaletteListItem * item = m_signalList;
  int row = 0;

  while (entries) {
    auto rows = rawList[0];
    auto paletteID = rawList[1];
    rawList += 2;

    row += rows;
    item->endRow = row;
    if (m_signalMaps.find(paletteID) != m_signalMaps.end()) {
      item->signals = m_signalMaps[paletteID];
    } else {
      item->signals = m_signalMaps[0];
    }

    entries--;

    if (entries) {
      if (item->next) {
        item = item->next;
      } else {
        item->next = createSignalList(rawList, entries, row);
        return;
      }
    }
  }

  if (item->next) {
    deleteSignalList(item->next);
    item->next = NULL;
  }
}


PaletteListItem * VGAPalettedController::createSignalList(uint16_t * rawList, int entries, int row)
{
  PaletteListItem * item = (PaletteListItem *) heap_caps_malloc(sizeof(PaletteListItem), MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
  auto rows = rawList[0];
  auto paletteID = rawList[1];

  item->endRow = row + rows;

  if (m_signalMaps.find(paletteID) != m_signalMaps.end()) {
    item->signals = m_signalMaps[paletteID];
  } else {
    item->signals = m_signalMaps[0];
  }

  if (entries > 1) {
    item->next = createSignalList(rawList + 2, entries - 1, row + rows);
  } else {
    item->next = NULL;
  }

  return item;
}


void * IRAM_ATTR VGAPalettedController::getSignalsForScanline(int scanLine) {
  if (scanLine < m_currentSignalItem->endRow) {
    return m_currentSignalItem->signals;
  }
  while (m_currentSignalItem->next && (scanLine >= m_currentSignalItem->endRow)) {
    m_currentSignalItem = m_currentSignalItem->next;
  }
  return m_currentSignalItem->signals;
}


void VGAPalettedController::swapBuffers()
{
  VGABaseController::swapBuffers();
  s_viewPort        = m_viewPort;
  s_viewPortVisible = m_viewPortVisible;
}


// Chance to overwrite a scan line in the output DMA buffer.
void IRAM_ATTR VGAPalettedController::decorateScanLinePixels(uint8_t * pixels, uint16_t scanRow) {
  drawSpriteScanLine(pixels, scanRow, s_scanWidth, s_viewPortHeight);
}

void IRAM_ATTR VGAPalettedController::rawDrawSpriteScanline(uint8_t * pixelData, Sprite * sprite, int scanRow, int scanWidth, int viewportHeight) {
  auto spriteFrame = sprite->getFrame();
  if (!spriteFrame) {
    return;
  }
  int spriteWidth = spriteFrame->width;
  int spriteHeight = spriteFrame->height;

  int spriteY = sprite->y;
  int spriteYend = spriteY + spriteHeight;
  if (scanRow < spriteY) return;
  if (scanRow >= spriteYend) return;
  int offsetY = scanRow - spriteY;

  int spriteX = sprite->x;
  if (spriteX >= scanWidth) return;
  int spriteXend = spriteX + spriteWidth;
  if (spriteXend <= 0) return;

  int offsetX = spriteX < 0 ? -spriteX : 0;
  int drawWidth = spriteXend > scanWidth ?
      scanWidth - spriteX :
      spriteWidth - offsetX;
  if (drawWidth <= 0) return;

  switch (spriteFrame->format) {
    case PixelFormat::RGBA8888: {
        auto src = (const uint32_t*)(spriteFrame->data) + (offsetY * spriteWidth) + offsetX;
        auto pos = spriteX + offsetX;
        while (drawWidth--) {
          auto src_pix = *src++;
          if (src_pix & 0xFF000000) {
            auto r = (src_pix & 0x000000C0) >> (8-2);
            auto g = (src_pix & 0x0000C000) >> (16-4);
            auto b = (src_pix & 0x00C00000) >> (24-6);
            pixelData[pos^2] = r | g | b | m_HVSync;
          }
          pos++;
        }
      }
      break;

    case PixelFormat::RGBA2222: {
        auto src = spriteFrame->data + (offsetY * spriteWidth) + offsetX;
        auto pos = spriteX + offsetX;
        if (sprite->paintOptions.mode == PaintMode::XOR) {
          // XOR mode
          while (drawWidth--) {
            if (*src & 0xC0) {
              auto rgb = *src & 0x3F;
              pixelData[pos^2] ^= rgb;
            }
            src++;
            pos++;
          }
        } else {
          // normal mode
          while (drawWidth--) {
            if (*src & 0xC0) {
              auto rgb = *src & 0x3F;
              pixelData[pos^2] = rgb | m_HVSync;
            }
            src++;
            pos++;
          }
        }
      }
      break;
  }
}

void IRAM_ATTR VGAPalettedController::drawSpriteScanLine(uint8_t * pixelData, int scanRow, int scanWidth, int viewportHeight) {
  AGON_GRAPHICS_SCOPE(ScanlineDecoration);
  // text cursor
  auto text = textCursor();
  if (text && text->visible) {
    rawDrawSpriteScanline(pixelData, text, scanRow, scanWidth, viewportHeight);
  }

  // normal sprites
  for (int i = 0; i < spritesCount(); ++i) {
    Sprite * sprite = getSprite(i);
    if (sprite->hardware && sprite->visible && sprite->allowDraw) {
      rawDrawSpriteScanline(pixelData, sprite, scanRow, scanWidth, viewportHeight);
    }
  }
  // mouse cursor
  auto mouse = mouseCursor();
  if (mouse->visible) {
    rawDrawSpriteScanline(pixelData, mouse, scanRow, scanWidth, viewportHeight);
  }
}

} // end of namespace

