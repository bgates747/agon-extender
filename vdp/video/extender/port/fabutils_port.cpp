// PORT-003 narrow vdp-gl utility closure for ESP32-P4.
//
// The retained common renderer needs only a bounded subset of vdp-gl's broad
// fabutils.cpp. Compiling that entire upstream file would also select
// classic-ESP32 GPIO/ADC/RTC and storage code already classified for
// replacement or omission. These routines preserve the all-the-plots
// implementations at their existing ABI. Provenance: vdp-gl tag
// all-the-plots, ac2dd5986daf496c43ae8e7fe41836274aec54a0,
// src/fabutils.cpp lines 85-104, 141-146, 273-325, 365-381, 384-394,
// 398-440, and 1416-1485.
#include "fabutils.h"

#include <cstdlib>

#include "esp_heap_caps.h"

[[noreturn]] std::uintptr_t agon_extender_removed_frc_timer_register() {
  std::abort();
}

namespace fabgl {

// Upstream fabutils.cpp normally owns this common scheduling hint, but the P4
// closure deliberately selects only the reviewed utility subset in this file.
int CoreUsage::s_busiestCore = 0;

uint32_t msToTicks(int milliseconds) {
  return milliseconds < 0 ? portMAX_DELAY : pdMS_TO_TICKS(milliseconds);
}

int isqrt(int x) {
  if (x < 1) return 0;
  int squaredbit = 0x40000000;
  int remainder = x;
  int root = 0;
  while (squaredbit > 0) {
    if (remainder >= (squaredbit | root)) {
      remainder -= (squaredbit | root);
      root >>= 1;
      root |= squaredbit;
    } else {
      root >>= 1;
    }
    squaredbit >>= 2;
  }
  return root;
}

namespace {

int clipLineCode(int x, int y, Rect const &clip) {
  int code = 0;
  if (x < clip.X1)
    code = 1;
  else if (x > clip.X2)
    code = 2;
  if (y < clip.Y1)
    code |= 4;
  else if (y > clip.Y2)
    code |= 8;
  return code;
}

}  // namespace

bool clipLine(int &x1, int &y1, int &x2, int &y2, Rect const &clip,
              bool check_only) {
  int new_x1 = x1;
  int new_y1 = y1;
  int new_x2 = x2;
  int new_y2 = y2;
  int first = clipLineCode(new_x1, new_y1, clip);
  int second = clipLineCode(new_x2, new_y2, clip);
  while (true) {
    if (first == 0 && second == 0) {
      if (!check_only) {
        x1 = new_x1;
        y1 = new_y1;
        x2 = new_x2;
        y2 = new_y2;
      }
      return true;
    }
    if (first & second) return false;
    int x = 0;
    int y = 0;
    int code = first != 0 ? first : second;
    if (code & 8) {
      x = new_x1 + (new_x2 - new_x1) * (clip.Y2 - new_y1) /
                       (new_y2 - new_y1);
      y = clip.Y2;
    } else if (code & 4) {
      x = new_x1 + (new_x2 - new_x1) * (clip.Y1 - new_y1) /
                       (new_y2 - new_y1);
      y = clip.Y1;
    } else if (code & 2) {
      y = new_y1 + (new_y2 - new_y1) * (clip.X2 - new_x1) /
                       (new_x2 - new_x1);
      x = clip.X2;
    } else {
      y = new_y1 + (new_y2 - new_y1) * (clip.X1 - new_x1) /
                       (new_x2 - new_x1);
      x = clip.X1;
    }
    if (code == first) {
      new_x1 = x;
      new_y1 = y;
      first = clipLineCode(new_x1, new_y1, clip);
    } else {
      new_x2 = x;
      new_y2 = y;
      second = clipLineCode(new_x2, new_y2, clip);
    }
  }
}

Rect IRAM_ATTR Rect::merge(Rect const &rect) const {
  return Rect(imin(rect.X1, X1), imin(rect.Y1, Y1), imax(rect.X2, X2),
              imax(rect.Y2, Y2));
}

Rect IRAM_ATTR Rect::intersection(Rect const &rect) const {
  return Rect(tmax(X1, rect.X1), tmax(Y1, rect.Y1), tmin(X2, rect.X2),
              tmin(Y2, rect.Y2));
}

bool getBit(uint8_t *array, size_t bitIndex) {
  size_t byteIndex = bitIndex / 8;
  int bitPosition = 7 - (bitIndex % 8);
  return (array[byteIndex] >> bitPosition) & 1;
}

uint8_t getCircleQuadrant(int x, int y) {
  if (x < 0) {
    if (y > 0) return 2;
    return 1;
  }
  if (y <= 0) return 0;
  return 3;
}

bool quadrantContainsArcPixel(QuadrantInfo &quadrant, LineInfo &start,
                              LineInfo &end, int16_t x, int16_t y) {
  bool drawing = false;
  if (quadrant.showAll) {
    return true;
  } else if (!quadrant.noArc) {
    if (quadrant.containsStart) {
      auto slopeTest = start.absDeltaY * std::abs(x);
      if (quadrant.isEven) {
        drawing = slopeTest <= (start.absDeltaX * std::abs(y));
      } else {
        drawing = slopeTest >= (start.absDeltaX * std::abs(y));
      }
      if (quadrant.containsEnd) {
        slopeTest = end.absDeltaY * std::abs(x);
        bool drawingEnd = false;
        if (quadrant.isEven) {
          drawingEnd = slopeTest >= (end.absDeltaX * std::abs(y));
        } else {
          drawingEnd = slopeTest <= (end.absDeltaX * std::abs(y));
        }
        if (quadrant.startCloserToHorizontal ^ quadrant.isEven) {
          return drawing || drawingEnd;
        }
        return drawing && drawingEnd;
      }
    } else if (quadrant.containsEnd) {
      auto slopeTest = end.absDeltaY * std::abs(x);
      if (quadrant.isEven) {
        return slopeTest >= (end.absDeltaX * std::abs(y));
      }
      return slopeTest <= (end.absDeltaX * std::abs(y));
    }
  }
  return drawing;
}

void LightMemoryPool::mark(int position, int16_t size, bool allocated) {
  m_mem[position] = size & 0xff;
  m_mem[position + 1] = ((size >> 8) & 0x7f) | (allocated ? 0x80 : 0);
}

int16_t LightMemoryPool::getSize(int position) {
  return m_mem[position] | ((m_mem[position + 1] & 0x7f) << 8);
}

bool LightMemoryPool::isFree(int position) {
  return (m_mem[position + 1] & 0x80) == 0;
}

LightMemoryPool::LightMemoryPool(int pool_size) {
  m_poolSize = pool_size + 2;
  m_mem = static_cast<uint8_t *>(
      heap_caps_malloc(m_poolSize, MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL));
  mark(0, m_poolSize - 2, false);
}

LightMemoryPool::~LightMemoryPool() { heap_caps_free(m_mem); }

void *LightMemoryPool::alloc(int size) {
  for (int position = 0; position < m_poolSize;) {
    int16_t block_size = getSize(position);
    if (isFree(position)) {
      if (block_size == size) {
        mark(position, size, true);
        return m_mem + position + 2;
      }
      if (block_size > size) {
        int remaining = block_size - size - 2;
        if (remaining > 0)
          mark(position + 2 + size, remaining, false);
        else
          size = block_size;
        mark(position, size, true);
        return m_mem + position + 2;
      }
      int next = position + 2 + block_size;
      if (next < m_poolSize && isFree(next))
        mark(position, block_size + getSize(next) + 2, false);
      else
        position += block_size + 2;
    } else {
      position += block_size + 2;
    }
  }
  return nullptr;
}

}  // namespace fabgl
