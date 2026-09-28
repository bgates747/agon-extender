#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>
namespace agon::extender::display::lcd {
// Preserve aspect ratio, nearest-neighbor; output is little-endian RGB888 (B,G,R).
// This is output conversion only, never the native renderer's storage format.
inline bool expand(const std::uint8_t *src, unsigned w, unsigned h,
                   unsigned stride, std::uint8_t *dst) {
  if (!src || !dst || !w || !h || stride<w) return false;
  unsigned dw=640, dh=unsigned(std::uint64_t(h)*640/w);
  if (dh>480) { dh=480; dw=unsigned(std::uint64_t(w)*480/h); }
  if (!dw || !dh) return false;
  std::memset(dst,0,640*480*3);
  unsigned ox=(640-dw)/2, oy=(480-dh)/2;
  for (unsigned y=0;y<dh;++y) {
    auto row=src+(std::size_t(y)*h/dh)*stride;
    auto out=dst+((y+oy)*640+ox)*3;
    for (unsigned x=0;x<dw;++x) {
      auto v=row[std::size_t(x)*w/dw];
      *out++=((v>>4)&3)*85; *out++=((v>>2)&3)*85; *out++=(v&3)*85;
    }
  }
  return true;
}
}
