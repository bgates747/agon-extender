// RESEARCH-007: call the exact frozen product CPU kernel, not an intentionally
// weak substitute. build.py copies its two hash-pinned headers unchanged.
#include "cpu.h"
#include "extender/display/hdmi_geometry.hpp"
#include <cstring>
using namespace agon::extender::display;
extern "C" void cpu_signal(const uint8_t *src, uint8_t *dst, unsigned w, unsigned h) {
  for (unsigned y=0; y<h; ++y)
    expandSignalRowToHdmi(src+y*w, dst+y*w*3, 0, w);
}
extern "C" void cpu_linear(const uint8_t *src, uint8_t *dst, unsigned w, unsigned h) {
  for (unsigned i=0; i<w*h; ++i) {
    const uint8_t c=src[i];
    *dst++=expandTwoBits(c>>4); *dst++=expandTwoBits(c>>2); *dst++=expandTwoBits(c);
  }
}
extern "C" void cpu_reorder(const uint8_t *src, uint8_t *dst, unsigned bytes) {
  // x^2 swaps the two 16-bit halves of each four-byte group. memcpy avoids
  // C++ aliasing UB and the target compiler can use ordinary word loads/stores.
  for (unsigned i=0; i<bytes; i+=4) {
    uint32_t word; std::memcpy(&word, src+i, 4);
    word=(word>>16)|(word<<16); std::memcpy(dst+i, &word, 4);
  }
}
