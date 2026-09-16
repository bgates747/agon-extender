#pragma once
#include <stdint.h>
#include <string.h>
// Project-authored full-frame workload. Six-bit colours, all background pixels
// change phase each frame; moving solid rectangles add predictable overdraw.
static constexpr unsigned W=512,H=384,N=W*H;
static inline void pattern(uint8_t *p,unsigned id) {
  unsigned phase=id&63;
  for(unsigned y=0;y<H;++y)
    for(unsigned x=0;x<W;++x) p[y*W+x]=((x>>2)^(y>>2)^phase)&63;
  for(unsigned i=0;i<16;++i) {
    unsigned x=(phase*7+i*29)%(W-24),y=(phase*3+i*19)%(H-24);
    for(unsigned dy=0;dy<24;++dy) memset(p+(y+dy)*W+x,(i*3+phase)&63,24);
  }
}
