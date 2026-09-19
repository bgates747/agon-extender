#pragma once
#include <cstdint>
#include <cstddef>
namespace pair_rle {
// EVQ1: little-endian [repeat-1:4, first:6, second:6]. Odd tail is one byte.
// Returns zero on invalid data or if output cannot beat smaller_than.
inline size_t encode(const uint8_t*s,size_t n,uint8_t*d,size_t cap,size_t smaller_than){
 if(!n||n>1024u*768u)return 0;
 size_t i=0,o=0;
 while(i+1<n){
  unsigned a=s[i],b=s[i+1];if((a|b)>63)return 0;
  unsigned count=1;i+=2;
  while(count<16&&i+1<n&&s[i]==a&&s[i+1]==b){++count;i+=2;}
  if(o+2>cap||o+2>=smaller_than)return 0;
  unsigned word=((count-1)<<12)|(a<<6)|b;d[o++]=word;d[o++]=word>>8;
 }
 if(i<n){if(s[i]>63||o+1>cap||o+1>=smaller_than)return 0;d[o++]=s[i];}
 return o;
}
}
