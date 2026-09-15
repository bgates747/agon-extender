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

// Original scanline renderer with a caller-owned output row.
// The physical ISR is unavailable on P4; its portable inner body is retained
// verbatim in stock_scanline.cpp. Caller must hold native-state quiescence.
// Independent reader scheduling/lifetime is deliberately not implied here.
#pragma once
#if defined(AGON_EXTENDER_PACKED_ROW)
#include "extender/display/rgb222_row.hpp"
#endif
#include <cstdint>
#include "dispdrivers/vga2controller.h"
#include "dispdrivers/vga4controller.h"
#include "dispdrivers/vga8controller.h"
#include "dispdrivers/vga16controller.h"
#include "dispdrivers/vga64controller.h"

namespace agon::extender::display {
template<class DepthController>
class StockScanlineController : public DepthController {
 public:
  // Ascending rows, starting at zero, preserve the stock Copper cursor.
  // Signal storage must have at least viewport width bytes and 8-byte alignment.
  void prepareStockRowQuiescent(int scanLine, std::uint8_t *signalRow);

  // This is the output-device boundary: stock signal/lane bytes become the
  // existing EVF1 RGB222 bytes. Source and destination must not overlap.
  static void normalizeRow(std::uint8_t const *signalRow,
                           std::uint8_t *rgb222, int width) {
#if defined(AGON_EXTENDER_PACKED_ROW)
    normalizeRgb222Row(signalRow, rgb222, width);
#else
    for (int x = 0; x < width; ++x) rgb222[x] = signalRow[x ^ 2] & 63;
#endif
  }
};
} // namespace agon::extender::display
