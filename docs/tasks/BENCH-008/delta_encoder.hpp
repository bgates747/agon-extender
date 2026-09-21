// Ad hoc BENCH-008 transport adapter. Reuses RLE2; no renderer semantics.
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstring>
#include "extender/diagnostics/rle2/rle2.hpp"
namespace frame_delta {
constexpr size_t capacity=786432;
struct Encoder {
 uint8_t *previous=nullptr,*scratch=nullptr,*encoded=nullptr;
 uint32_t sequence=0,period=0;uint16_t width=0,height=0;unsigned age=0;bool valid=false;
 void reset(){valid=false;age=0;}
 bool supported(const uint8_t*h,size_t n)const{
  const size_t w=h[12]|size_t(h[13])<<8,hh=h[14]|size_t(h[15])<<8;
  return !std::memcmp(h,"EVF1",4)&&h[6]==2&&w&&hh&&w<=1024&&hh<=768&&n==w*hh&&n<=capacity&&rle2::get32(h+16)==w&&rle2::get32(h+20)==n;
 }
 size_t prepare(const uint8_t*h,const uint8_t*p,size_t n,size_t full_bytes){
  if(!previous||!scratch||!encoded||!supported(h,n))return 0;
  const unsigned w=h[12]|unsigned(h[13])<<8,hh=h[14]|unsigned(h[15])<<8;
  if(!valid||age>=119||w!=width||hh!=height||period!=rle2::get32(h+24))return 0;
  for(size_t i=0;i<n;++i)scratch[i]=p[i]==previous[i]?0:uint8_t(p[i]|192);
  auto result=rle2::encode_auto(scratch,n,encoded,capacity+14,false);
  return result&&result.bytes<full_bytes?result.bytes:0;
 }
 void commit(const uint8_t*h,const uint8_t*p,size_t n,bool delta){
  if(!previous||!supported(h,n)){reset();return;}
  std::memcpy(previous,p,n);sequence=rle2::get32(h+8);period=rle2::get32(h+24);
  width=h[12]|uint16_t(h[13])<<8;height=h[14]|uint16_t(h[15])<<8;valid=true;age=delta?age+1:0;
 }
};
}
