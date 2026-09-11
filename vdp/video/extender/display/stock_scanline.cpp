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

// Verbatim portable bodies from all-the-plots physical ISRs.
// Provenance: docs/tasks/PORT-003/stock-backend-r2/scanline-spans.json.
#include "extender/display/stock_scanline.hpp"
#include <cstring>

namespace agon::extender::display {

template<>
void StockScanlineController<fabgl::VGA2Controller>::prepareStockRowQuiescent(
    int scanLine, std::uint8_t *signalRow) {
  auto ctrl = this;
  auto const width = this->m_viewPortWidth;
  std::uint8_t *lines[] = {signalRow};
  int lineIndex = 0;
  if (scanLine == 0) this->m_currentSignalItem = this->m_signalList;
      auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
      auto dest = (uint64_t*) lines[lineIndex];
      uint8_t* decpix = (uint8_t*) dest;
      auto const packedPaletteIndexOctet_to_signals = (uint64_t *) ctrl->getSignalsForScanline(scanLine);

      // optimization warn: horizontal resolution must be a multiple of 16!
      for (int col = 0; col < width; col += 16) {

        auto src1 = *(src + 0);
        auto src2 = *(src + 1);

        PSRAM_HACK;

        auto v1 = packedPaletteIndexOctet_to_signals[src1];
        auto v2 = packedPaletteIndexOctet_to_signals[src2];

        *(dest + 0) = v1;
        *(dest + 1) = v2;

        dest += 2;
        src += 2;
        
      }

      ctrl->decorateScanLinePixels(decpix, scanLine);
}

template<>
void StockScanlineController<fabgl::VGA4Controller>::prepareStockRowQuiescent(
    int scanLine, std::uint8_t *signalRow) {
  auto ctrl = this;
  auto const width = this->m_viewPortWidth;
  std::uint8_t *lines[] = {signalRow};
  int lineIndex = 0;
  if (scanLine == 0) this->m_currentSignalItem = this->m_signalList;
      auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
      auto dest = (uint32_t*) lines[lineIndex];
      uint8_t* decpix = (uint8_t*) dest;
      auto const packedPaletteIndexQuad_to_signals = (uint32_t *) ctrl->getSignalsForScanline(scanLine);

      // optimization warn: horizontal resolution must be a multiple of 16!
      for (int col = 0; col < width; col += 16) {

        auto src1 = *(src + 0);
        auto src2 = *(src + 1);
        auto src3 = *(src + 2);
        auto src4 = *(src + 3);

        PSRAM_HACK;

        auto v1 = packedPaletteIndexQuad_to_signals[src1];
        auto v2 = packedPaletteIndexQuad_to_signals[src2];
        auto v3 = packedPaletteIndexQuad_to_signals[src3];
        auto v4 = packedPaletteIndexQuad_to_signals[src4];

        *(dest + 0) = v1;
        *(dest + 1) = v2;
        *(dest + 2) = v3;
        *(dest + 3) = v4;

        dest += 4;
        src += 4;
      }

      ctrl->decorateScanLinePixels(decpix, scanLine);
}

template<>
void StockScanlineController<fabgl::VGA8Controller>::prepareStockRowQuiescent(
    int scanLine, std::uint8_t *signalRow) {
  auto ctrl = this;
  auto const width = this->m_viewPortWidth;
  std::uint8_t *lines[] = {signalRow};
  int lineIndex = 0;
  if (scanLine == 0) this->m_currentSignalItem = this->m_signalList;
      auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
      auto dest = (uint16_t*) lines[lineIndex];
      uint8_t* decpix = (uint8_t*) dest;
      auto const packedPaletteIndexPair_to_signals = (uint16_t *) ctrl->getSignalsForScanline(scanLine);

      // optimization warn: horizontal resolution must be a multiple of 16!
      for (int col = 0; col < width; col += 16) {

        auto w1 = *((uint16_t*)(src    ));  // hi A:23334445, lo A:55666777
        auto w2 = *((uint16_t*)(src + 2));  // hi B:55666777, lo A:00011122
        auto w3 = *((uint16_t*)(src + 4));  // hi B:00011122, lo B:23334445

        PSRAM_HACK;

        auto src1 = w1 | (w2 << 16);
        auto src2 = (w2 >> 8) | (w3 << 8);

        auto v1 = packedPaletteIndexPair_to_signals[(src1      ) & 0x3f];  // pixels 0, 1
        auto v2 = packedPaletteIndexPair_to_signals[(src1 >>  6) & 0x3f];  // pixels 2, 3
        auto v3 = packedPaletteIndexPair_to_signals[(src1 >> 12) & 0x3f];  // pixels 4, 5
        auto v4 = packedPaletteIndexPair_to_signals[(src1 >> 18) & 0x3f];  // pixels 6, 7
        auto v5 = packedPaletteIndexPair_to_signals[(src2      ) & 0x3f];  // pixels 8, 9
        auto v6 = packedPaletteIndexPair_to_signals[(src2 >>  6) & 0x3f];  // pixels 10, 11
        auto v7 = packedPaletteIndexPair_to_signals[(src2 >> 12) & 0x3f];  // pixels 12, 13
        auto v8 = packedPaletteIndexPair_to_signals[(src2 >> 18) & 0x3f];  // pixels 14, 15

        *(dest + 2) = v1;
        *(dest + 3) = v2;
        *(dest + 0) = v3;
        *(dest + 1) = v4;
        *(dest + 6) = v5;
        *(dest + 7) = v6;
        *(dest + 4) = v7;
        *(dest + 5) = v8;

        dest += 8;
        src += 6;

      }

      ctrl->decorateScanLinePixels(decpix, scanLine);
}

template<>
void StockScanlineController<fabgl::VGA16Controller>::prepareStockRowQuiescent(
    int scanLine, std::uint8_t *signalRow) {
  auto ctrl = this;
  auto const width = this->m_viewPortWidth;
  std::uint8_t *lines[] = {signalRow};
  int lineIndex = 0;
  if (scanLine == 0) this->m_currentSignalItem = this->m_signalList;
      auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
      auto dest = (uint16_t*) lines[lineIndex];
      uint8_t* decpix = (uint8_t*) dest;
      auto const packedPaletteIndexPair_to_signals = (uint16_t *) ctrl->getSignalsForScanline(scanLine);

      // optimization warn: horizontal resolution must be a multiple of 16!
      for (int col = 0; col < width; col += 16) {

        auto src1 = *(src + 0);
        auto src2 = *(src + 1);
        auto src3 = *(src + 2);
        auto src4 = *(src + 3);
        auto src5 = *(src + 4);
        auto src6 = *(src + 5);
        auto src7 = *(src + 6);
        auto src8 = *(src + 7);

        PSRAM_HACK;

        auto v1 = packedPaletteIndexPair_to_signals[src1];
        auto v2 = packedPaletteIndexPair_to_signals[src2];
        auto v3 = packedPaletteIndexPair_to_signals[src3];
        auto v4 = packedPaletteIndexPair_to_signals[src4];
        auto v5 = packedPaletteIndexPair_to_signals[src5];
        auto v6 = packedPaletteIndexPair_to_signals[src6];
        auto v7 = packedPaletteIndexPair_to_signals[src7];
        auto v8 = packedPaletteIndexPair_to_signals[src8];

        *(dest + 1) = v1;
        *(dest    ) = v2;
        *(dest + 3) = v3;
        *(dest + 2) = v4;
        *(dest + 5) = v5;
        *(dest + 4) = v6;
        *(dest + 7) = v7;
        *(dest + 6) = v8;

        dest += 8;
        src += 8;

      }

      ctrl->decorateScanLinePixels(decpix, scanLine);
}

template<>
void StockScanlineController<fabgl::VGA64Controller>::prepareStockRowQuiescent(
    int scanLine, std::uint8_t *signalRow) {
  auto ctrl = this;
  auto const width = this->m_viewPortWidth;
  std::uint8_t *lines[] = {signalRow};
  int lineIndex = 0;
      auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
      auto dest = (uint8_t*) lines[lineIndex];

      memcpy(dest, src, width);

      ctrl->decorateScanLinePixels(dest, scanLine);
}

} // namespace agon::extender::display
