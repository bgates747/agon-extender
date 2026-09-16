// Clean-sheet P4 codec. Wire format: Author's AGM RLE2 v1.0.
// No allocation, architecture intrinsics or unaligned integer access.
#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
namespace rle2 {
enum class Status { ok, header, version, truncated, length, capacity, alpha };
struct Result { Status status; size_t bytes; explicit operator bool() const { return status==Status::ok; } };
constexpr size_t header_size=14;
inline uint32_t get32(const uint8_t*p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
inline void put32(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;++i)p[i]=uint8_t(n>>(i*8));}
inline Result inspect(const uint8_t*s,size_t n) {
 if(n<14)return {Status::truncated,0};
 if(std::memcmp(s,"Cmpr",4)||std::memcmp(s+8,"RLE2",4))return {Status::header,0};
 if(s[12]!=1||s[13]!=0)return {Status::version,0};
 return {Status::ok,get32(s+4)};
}
// Source and destination must not overlap. Caller retains original asset until
// successful decode; invalid input may modify scratch but never published data.
inline Result decode(const uint8_t*s,size_t n,uint8_t*d,size_t cap) {
 auto h=inspect(s,n);if(!h)return h;
 if(h.bytes>cap)return {Status::capacity,0};
 size_t i=14,o=0;
 while(i<n){
  uint8_t t=s[i++];
  if(t&128){if(o==h.bytes)return {Status::length,0};d[o++]=uint8_t((t&63)|((t&64)?192:0));}
  else {size_t count=size_t(t)+3;if(i==n)return {Status::truncated,0};
   if(count>h.bytes-o)return {Status::length,0};
   std::memset(d+o,s[i++],count);o+=count;}
 }
 return o==h.bytes?Result{Status::ok,o}:Result{Status::length,0};
}
// opaque_rgb=true maps logical BBGGRR (0..63) snapshots to opaque RGBA2222.
// Asset encoding supports binary alpha only; partial alpha is rejected, not lost.
inline Result encode(const uint8_t*s,size_t n,uint8_t*d,size_t cap,bool opaque_rgb=false) {
 if(n>UINT32_MAX || n>std::numeric_limits<size_t>::max()-14)return {Status::length,0};
 if(cap<n+14)return {Status::capacity,0};
 std::memcpy(d,"Cmpr",4);put32(d+4,uint32_t(n));std::memcpy(d+8,"RLE2\1\0",6);
 size_t i=0,o=14;
 while(i<n){uint8_t v=s[i];
  if(opaque_rgb ? v>63 : ((v&192)!=0&&(v&192)!=192))return {Status::alpha,0};
  size_t run=1;while(run<130 && run<n-i && s[i+run]==v)++run;
  uint8_t pixel=opaque_rgb?uint8_t(v|192):v;
  if(run>=3){d[o++]=uint8_t(run-3);d[o++]=pixel;}
  else {uint8_t t=uint8_t(128|(pixel&63)|((pixel&192)==192?64:0));d[o++]=t;if(run==2)d[o++]=t;}
  i+=run;
 }
 return {Status::ok,o};
}
}
