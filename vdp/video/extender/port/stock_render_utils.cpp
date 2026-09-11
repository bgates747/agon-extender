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

// Original vdp-gl all-the-plots utility bodies, extracted without rewriting.
// Whole fabutils.cpp also owns classic GPIO/ADC/RTC/storage implementations.
// R1 selects only the common-renderer/native-controller dependency closure.
// Source spans and hashes: docs/tasks/PORT-003/stock-backend-r1/utility-spans.json.
// R2 retains these bodies and adds only the same native-entry guard as
// original LightMemoryPool::alloc/free; never guard its caller retry loop.
#include "fabutils.h"
#include "fabglconf.h"
#include "esp_heap_caps.h"
#include "esp_wifi.h"
#include <cmath>

namespace fabgl {

// Upstream src/fabutils.cpp:85-104
int isqrt (int x)
{
  if (x < 1)
    return 0;
  int squaredbit = 0x40000000;
  int remainder = x;
  int root = 0;
  while (squaredbit > 0) {
    if (remainder >= (squaredbit | root)) {
      remainder -= (squaredbit | root);
      root >>= 1;
      root |= squaredbit;
    } else
      root >>= 1;
    squaredbit >>= 2;
  }
  return root;
}




// Upstream src/fabutils.cpp:143-146
uint32_t msToTicks(int ms)
{
  return ms < 0 ? portMAX_DELAY : pdMS_TO_TICKS(ms);
}


// Upstream src/fabutils.cpp:268-333

static int clipLine_code(int x, int y, Rect const & clipRect)
{
  int code = 0;
  if (x < clipRect.X1)
    code = 1;
  else if (x > clipRect.X2)
    code = 2;
  if (y < clipRect.Y1)
    code |= 4;
  else if (y > clipRect.Y2)
    code |= 8;
  return code;
}

// false = line is out of clipping rect
// true = line intersects or is inside the clipping rect (x1, y1, x2, y2 are changed if checkOnly=false)
bool clipLine(int & x1, int & y1, int & x2, int & y2, Rect const & clipRect, bool checkOnly)
{
  int newX1 = x1;
  int newY1 = y1;
  int newX2 = x2;
  int newY2 = y2;
  int topLeftCode     = clipLine_code(newX1, newY1, clipRect);
  int bottomRightCode = clipLine_code(newX2, newY2, clipRect);
  while (true) {
    if ((topLeftCode == 0) && (bottomRightCode == 0)) {
      if (!checkOnly) {
        x1 = newX1;
        y1 = newY1;
        x2 = newX2;
        y2 = newY2;
      }
      return true;
    } else if (topLeftCode & bottomRightCode) {
      break;
    } else {
      int x = 0, y = 0;
      int ncode = topLeftCode != 0 ? topLeftCode : bottomRightCode;
      if (ncode & 8) {
        x = newX1 + (newX2 - newX1) * (clipRect.Y2 - newY1) / (newY2 - newY1);
        y = clipRect.Y2;
      } else if (ncode & 4) {
        x = newX1 + (newX2 - newX1) * (clipRect.Y1 - newY1) / (newY2 - newY1);
        y = clipRect.Y1;
      } else if (ncode & 2) {
        y = newY1 + (newY2 - newY1) * (clipRect.X2 - newX1) / (newX2 - newX1);
        x = clipRect.X2;
      } else if (ncode & 1) {
        y = newY1 + (newY2 - newY1) * (clipRect.X1 - newX1) / (newX2 - newX1);
        x = clipRect.X1;
      }
      if (ncode == topLeftCode) {
        newX1 = x;
        newY1 = y;
        topLeftCode = clipLine_code(newX1, newY1, clipRect);
      } else {
        newX2 = x;
        newY2 = y;
        bottomRightCode = clipLine_code(newX2, newY2, clipRect);
      }
    }
  }
  return false;
}



// Upstream src/fabutils.cpp:365-381
Rect IRAM_ATTR Rect::merge(Rect const & rect) const
{
  return Rect(imin(rect.X1, X1), imin(rect.Y1, Y1), imax(rect.X2, X2), imax(rect.Y2, Y2));
}


Rect IRAM_ATTR Rect::intersection(Rect const & rect) const
{
  return Rect(tmax(X1, rect.X1), tmax(Y1, rect.Y1), tmin(X2, rect.X2), tmin(Y2, rect.Y2));
}


bool getBit(uint8_t* array, size_t bitIndex) {
    size_t byteIndex = bitIndex / 8;
    int bitPosition = 7 - (bitIndex % 8);
    return (array[byteIndex] >> bitPosition) & 1;
}


// Upstream src/fabutils.cpp:384-438
uint8_t getCircleQuadrant(int x, int y) {
  if (x < 0) {
    if (y > 0) {
      return 2;
    }
    return 1;
  }
  if (y <= 0) {
    return 0;
  }
  return 3;
}


bool quadrantContainsArcPixel(QuadrantInfo & quadrant, LineInfo & start, LineInfo & end, int16_t x, int16_t y) {
  // Work out whether our arc circumference pixel should be shown in this quadrant
  bool drawing = false;
  if (quadrant.showAll) {
    return true;
  } else if (!quadrant.noArc) {
    if (quadrant.containsStart) {
      auto slopeTest = start.absDeltaY * abs(x);
      if (quadrant.isEven) {
        drawing = slopeTest <= (start.absDeltaX * abs(y));
      } else {
        drawing = slopeTest >= (start.absDeltaX * abs(y));
      }
      if (quadrant.containsEnd) {
        slopeTest = end.absDeltaY * abs(x);
        bool drawingEnd = false;
        if (quadrant.isEven) {
          drawingEnd = (slopeTest >= (end.absDeltaX * abs(y)));
        } else {
          drawingEnd = (slopeTest <= (end.absDeltaX * abs(y)));
        }
        if (quadrant.containsStart && quadrant.containsEnd) {
          if (quadrant.startCloserToHorizontal ^ quadrant.isEven) {
            return drawing || drawingEnd;
          } else {
            return drawing && drawingEnd;
          }
        }
      }
    } else if (quadrant.containsEnd) {
      auto slopeTest = end.absDeltaY * abs(x);
      if (quadrant.isEven) {
        return slopeTest >= (end.absDeltaX * abs(y));
      } else {
        return slopeTest <= (end.absDeltaX * abs(y));
      }
    }
  }
  return drawing;
}



// Upstream src/fabutils.cpp:443-461
void rgb222_to_hsv(int R, int G, int B, double * h, double * s, double * v)
{
  double r = R / 3.0;
  double g = G / 3.0;
  double b = B / 3.0;
  double cmax = tmax<double>(tmax<double>(r, g), b);
  double cmin = tmin<double>(tmin<double>(r, g), b);
  double diff = cmax - cmin;
  if (cmax == cmin)
    *h = 0;
  else if (cmax == r)
    *h = fmod((60.0 * ((g - b) / diff) + 360.0), 360.0);
  else if (cmax == g)
    *h = fmod((60.0 * ((b - r) / diff) + 120.0), 360.0);
  else if (cmax == b)
    *h = fmod((60.0 * ((r - g) / diff) + 240.0), 360.0);
  *s = cmax == 0 ? 0 : (diff / cmax) * 100.0;
  *v = cmax * 100.0;
}


// Upstream src/fabutils.cpp:1416-1536
void LightMemoryPool::mark(int pos, int16_t size, bool allocated)
{
  m_mem[pos]     = size & 0xff;
  m_mem[pos + 1] = ((size >> 8) & 0x7f) | (allocated ? 0x80 : 0);
}


int16_t LightMemoryPool::getSize(int pos)
{
  return m_mem[pos] | ((m_mem[pos + 1] & 0x7f) << 8);
}


bool LightMemoryPool::isFree(int pos)
{
  return (m_mem[pos + 1] & 0x80) == 0;
}


LightMemoryPool::LightMemoryPool(int poolSize)
{
  m_poolSize = poolSize + 2;
  m_mem = (uint8_t*) heap_caps_malloc(m_poolSize, MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL);
  mark(0, m_poolSize - 2, false);
}


LightMemoryPool::~LightMemoryPool()
{
  heap_caps_free(m_mem);
}


void * LightMemoryPool::alloc(int size)
{
  AGON_STOCK_NATIVE_GUARD;
  for (int pos = 0; pos < m_poolSize; ) {
    int16_t blockSize = getSize(pos);
    if (isFree(pos)) {
      if (blockSize == size) {
        // found a block having the same size
        mark(pos, size, true);
        return m_mem + pos + 2;
      } else if (blockSize > size) {
        // found a block having larger size
        int remainingSize = blockSize - size - 2;
        if (remainingSize > 0)
          mark(pos + 2 + size, remainingSize, false);  // create new free block at the end of this block
        else
          size = blockSize; // to avoid to waste last block
        mark(pos, size, true);  // reduce size of this block and mark as allocated
        return m_mem + pos + 2;
      } else {
        // this block hasn't enough space
        // can merge with next block?
        int nextBlockPos = pos + 2 + blockSize;
        if (nextBlockPos < m_poolSize && isFree(nextBlockPos)) {
          // join blocks and stay at this pos
          mark(pos, blockSize + getSize(nextBlockPos) + 2, false);
        } else {
          // move to the next block
          pos += blockSize + 2;
        }
      }
    } else {
      // move to the next block
      pos += blockSize + 2;
    }
  }
  return nullptr;
}


bool LightMemoryPool::memCheck()
{
  int pos = 0;
  while (pos < m_poolSize) {
    int16_t blockSize = getSize(pos);
    pos += blockSize + 2;
  }
  return pos == m_poolSize;
}


int LightMemoryPool::totFree()
{
  int r = 0;
  for (int pos = 0; pos < m_poolSize; ) {
    int16_t blockSize = getSize(pos);
    if (isFree(pos))
      r += blockSize;
    pos += blockSize + 2;
  }
  return r;
}


int LightMemoryPool::totAllocated()
{
  int r = 0;
  for (int pos = 0; pos < m_poolSize; ) {
    int16_t blockSize = getSize(pos);
    if (!isFree(pos))
      r += blockSize;
    pos += blockSize + 2;
  }
  return r;
}


int LightMemoryPool::largestFree()
{
  int r = 0;
  for (int pos = 0; pos < m_poolSize; ) {
    int16_t blockSize = getSize(pos);
    if (isFree(pos) && blockSize > r)
      r = blockSize;
    pos += blockSize + 2;
  }
  return r;
}



// Upstream src/fabutils.cpp:1547-1547
int CoreUsage::s_busiestCore = FABGLIB_VIDEO_CPUINTENSIVE_TASKS_CORE;


// Upstream src/fabutils.cpp:1559-1559
VideoMode CurrentVideoMode::s_videoMode = VideoMode::None;


} // namespace fabgl
