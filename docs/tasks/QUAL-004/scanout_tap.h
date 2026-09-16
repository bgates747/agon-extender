// QUAL-004 diagnostic: one DRAM row copied from actual decorated VGA scanout.
// Static scenes only; capture spans refreshes. No ISR allocation or serial I/O.
#pragma once
#include <stdint.h>
#include <string.h>
#include "esp_attr.h"
namespace qual004 {
extern volatile int requested_row;
extern volatile int ready_width;
extern uint8_t row[1024];
inline void IRAM_ATTR tap(const uint8_t *pixels, int y, int width) {
  if (requested_row != y || width <= 0 || width > 1024) return;
  memcpy(row, pixels, width);
  __sync_synchronize();
  ready_width = width;
  requested_row = -1;
}
}
