// Experimental EVP1: lossless palette packing of final composed RGB222.
// No native framebuffer assumptions, allocation, or graphics locks.
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstring>
namespace packed_frame {
constexpr size_t max_pixels=1024u*768u;
// Payload: bit depth, palette count, two zero bytes, RGB222 palette,
// then MSB-first indices across the raster. Final low padding bits are zero.
inline size_t encode(const uint8_t*src,size_t n,uint8_t*dst,size_t cap,size_t smaller_than) {
 if(!n || n>max_pixels)return 0;
 uint8_t map[64],palette[16];std::memset(map,255,sizeof(map));unsigned colours=0;
 for(size_t i=0;i<n;++i){unsigned p=src[i];if(p>63)return 0;
  if(map[p]==255){if(colours==16)return 0;map[p]=colours;palette[colours++]=p;}}
 unsigned bits=colours<=2?1:colours<=4?2:4;
 size_t bytes=4+colours+(n*bits+7)/8;
 if(bytes>cap || bytes>=smaller_than)return 0;
 dst[0]=bits;dst[1]=colours;dst[2]=dst[3]=0;
 std::memcpy(dst+4,palette,colours);auto out=dst+4+colours;
 unsigned acc=0,used=0;
 for(size_t i=0;i<n;++i){acc=(acc<<bits)|map[src[i]];used+=bits;
  if(used==8){*out++=acc;used=0;acc=0;}}
 if(used)*out=acc<<(8-used);
 return bytes;
}
}
