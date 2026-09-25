// Promoted deployed implementation: docs/tasks/QUAL-003/debrief/P01h/codec/rle2.hpp
// RELEASE-001 R01-03 maps the retained browser-reset-r02 composition.
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
// Iteration2: bypass run scanning for singleton-heavy frames. Same wire bytes.
inline Result encode_fast(const uint8_t*s,size_t n,uint8_t*d,size_t cap,bool opaque_rgb=false) {
 if(n>UINT32_MAX || n>std::numeric_limits<size_t>::max()-14)return {Status::length,0};
 if(cap<n+14)return {Status::capacity,0};
 std::memcpy(d,"Cmpr",4);put32(d+4,uint32_t(n));std::memcpy(d+8,"RLE2\1\0",6);
 size_t i=0,o=14;
 while(i<n){uint8_t v=s[i];
  if(opaque_rgb ? v>63 : ((v&192)!=0&&(v&192)!=192))return {Status::alpha,0};
  uint8_t pixel=opaque_rgb?uint8_t(v|192):v;
  if(n-i<3 || s[i+1]!=v || s[i+2]!=v){d[o++]=uint8_t(128|(pixel&63)|((pixel&192)==192?64:0));++i;continue;}
  size_t run=3;while(run<130 && run<n-i && s[i+run]==v)++run;
  d[o++]=uint8_t(run-3);d[o++]=pixel;i+=run;
 }
 return {Status::ok,o};
}

// Iteration3: four-token literals; memcpy avoids undefined unaligned accesses.
inline Result decode_words(const uint8_t*s,size_t n,uint8_t*d,size_t cap) {
 auto h=inspect(s,n);if(!h)return h;
 if(h.bytes>cap)return {Status::capacity,0};
 size_t i=14,o=0;
 while(i<n){
  if(n-i>=4 && h.bytes-o>=4){uint32_t word;std::memcpy(&word,s+i,4);
   if((word&0x80808080u)==0x80808080u){word=(word&0x7f7f7f7fu)|((word&0x40404040u)<<1);std::memcpy(d+o,&word,4);i+=4;o+=4;continue;}}

  uint8_t t=s[i++];
  if(t&128){if(o==h.bytes)return {Status::length,0};d[o++]=uint8_t((t&63)|((t&64)?192:0));}
  else {size_t count=size_t(t)+3;if(i==n)return {Status::truncated,0};
   if(count>h.bytes-o)return {Status::length,0};
   std::memset(d+o,s[i++],count);o+=count;}
 }
 return o==h.bytes?Result{Status::ok,o}:Result{Status::length,0};
}
inline Result encode_words(const uint8_t*s,size_t n,uint8_t*d,size_t cap,bool opaque_rgb=false) {
 if(n>UINT32_MAX || n>std::numeric_limits<size_t>::max()-14)return {Status::length,0};
 if(cap<n+14)return {Status::capacity,0};
 std::memcpy(d,"Cmpr",4);put32(d+4,uint32_t(n));std::memcpy(d+8,"RLE2\1\0",6);
 size_t i=0,o=14;
 while(i<n){
  if(opaque_rgb && n-i>=5 && s[i]!=s[i+1] && s[i+1]!=s[i+2] && s[i+2]!=s[i+3] && s[i+3]!=s[i+4]){
   uint32_t word;std::memcpy(&word,s+i,4);if(word&0xc0c0c0c0u)return {Status::alpha,0};word|=0xc0c0c0c0u;std::memcpy(d+o,&word,4);i+=4;o+=4;continue;}
  uint8_t v=s[i];
  if(opaque_rgb ? v>63 : ((v&192)!=0&&(v&192)!=192))return {Status::alpha,0};
  uint8_t pixel=opaque_rgb?uint8_t(v|192):v;
  if(n-i<3 || s[i+1]!=v || s[i+2]!=v){d[o++]=uint8_t(128|(pixel&63)|((pixel&192)==192?64:0));++i;continue;}
  size_t run=3;while(run<130 && run<n-i && s[i+run]==v)++run;
  d[o++]=uint8_t(run-3);d[o++]=pixel;i+=run;
 }
 return {Status::ok,o};
}

// Iteration4: bounded evenly spaced sample selects a measured implementation.
// Sampling affects CPU cost only: both choices emit identical complete streams.
inline Result encode_auto(const uint8_t*s,size_t n,uint8_t*d,size_t cap,bool opaque_rgb=false) {
 if(n>UINT32_MAX)return {Status::length,0};
 size_t repeated=0,checks=0;
 if(n>=32)for(size_t k=0;k<16;++k){size_t start=(n-32)*k/15;for(size_t j=1;j<32;++j){repeated+=s[start+j]==s[start+j-1];++checks;}}
 return repeated>checks/4?encode(s,n,d,cap,opaque_rgb):encode_words(s,n,d,cap,opaque_rgb);
}

}
