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
inline size_t encode(const uint8_t*src,size_t n,uint8_t*dst,size_t cap,size_t smaller_than,bool sixbit=false) {
 if(!n || n>max_pixels)return 0;
 // Even a single-colour 1-bit image cannot beat this bound.
 if(5+(n+7)/8>=smaller_than)return 0;
 uint8_t map[64],palette[16];std::memset(map,255,sizeof(map));unsigned colours=0;
 for(size_t i=0;i<n;++i){unsigned p=src[i];if(p>63)return 0;
  if(map[p]==255){if(colours==16){
   if(!sixbit)return 0;
   const size_t bytes=4+(n*6+7)/8;
   if(bytes>cap || bytes>=smaller_than)return 0;
   dst[0]=6;dst[1]=dst[2]=dst[3]=0;auto out=dst+4;
   size_t j=0;
   // Four complete RGB222 pixels become three bytes, MSB first.
   for(;j+4<=n;j+=4){
    const unsigned a=src[j],b=src[j+1],c=src[j+2],d=src[j+3];
    if((a|b|c|d)>63)return 0;
    *out++=(a<<2)|(b>>4);*out++=(b<<4)|(c>>2);*out++=(c<<6)|d;
   }
   unsigned acc=0,used=0;
   for(;j<n;++j){if(src[j]>63)return 0;acc=(acc<<6)|src[j];used+=6;
    if(used>=8){used-=8;*out++=acc>>used;}}
   if(used)*out=acc<<(8-used);
   return bytes;
  }map[p]=colours;palette[colours++]=p;}}
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
