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
#pragma once
// Independent reference accessors copied verbatim from pinned upstream.
// These encode the expected logical test image; actual drawing uses Canvas.
namespace stock_oracle {
static inline __attribute__((always_inline)) void VGA2_SETPIXELINROW(uint8_t * row, int x, int value) {
  int brow = x >> 3;
  row[brow] ^= (-value ^ row[brow]) & (0x80 >> (x & 7));
}

static inline __attribute__((always_inline)) int VGA2_GETPIXELINROW(uint8_t * row, int x) {
  int brow = x >> 3;
  return (row[brow] & (0x80 >> (x & 7))) != 0;
}

static inline __attribute__((always_inline)) void VGA4_SETPIXELINROW(uint8_t * row, int x, int value) {
  int brow = x >> 2;
  int shift = 6 - (x & 3) * 2;
  row[brow] ^= ((value << shift) ^ row[brow]) & (3 << shift);
}

static inline __attribute__((always_inline)) int VGA4_GETPIXELINROW(uint8_t * row, int x) {
  int brow = x >> 2;
  int shift = 6 - (x & 3) * 2;
  return (row[brow] >> shift) & 3;
}

static inline __attribute__((always_inline)) void VGA8_SETPIXELINROW(uint8_t * row, int x, int value) {
  uint32_t * bits24 = (uint32_t*)(row + (x >> 3) * 3);  // x / 8 * 3
  int shift = 21 - (x & 7) * 3;
  *bits24 ^= ((value << shift) ^ *bits24) & (7 << shift);
}

static inline __attribute__((always_inline)) int VGA8_GETPIXELINROW(uint8_t * row, int x) {
  uint32_t * bits24 = (uint32_t*)(row + (x >> 3) * 3);  // x / 8 * 3
  int shift = 21 - (x & 7) * 3;
  return (*bits24 >> shift) & 7;
}

static inline __attribute__((always_inline)) void VGA16_SETPIXELINROW(uint8_t * row, int x, int value) {
  int brow = x >> 1;
  row[brow] = (x & 1) ? ((row[brow] & 0xf0) | value) : ((row[brow] & 0x0f) | (value << 4));
}

static inline __attribute__((always_inline)) int VGA16_GETPIXELINROW(uint8_t * row, int x) {
  int brow = x >> 1;
  return ((x & 1) ? (row[brow] & 0x0f) : ((row[brow] & 0xf0) >> 4));
}

} // namespace stock_oracle
