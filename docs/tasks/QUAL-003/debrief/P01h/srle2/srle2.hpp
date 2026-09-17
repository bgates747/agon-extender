#pragma once
#include "szip_p4.h"
#include "../rle2/rle2.hpp"
#include "esp_heap_caps.h"
namespace srle2 {
// Caller supplies distinct bounded destination. Temporary bytes are never published.
inline int encode(const uint8_t*src,size_t n,uint8_t*dst,size_t cap,size_t*written){
 if(!n||n>1048576||!written)return 1;*written=0;
 auto tmp=static_cast<uint8_t*>(heap_caps_malloc(n+14,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
 if(!tmp)return 3;
 auto r=rle2::encode_auto(src,n,tmp,n+14);
 int status=r?p4_szip(0,tmp,r.bytes,dst,cap,written):1;
 heap_caps_free(tmp);return status;
}
inline int decode(const uint8_t*src,size_t n,uint8_t*dst,size_t cap,size_t*written){
 if(n<14||!written)return 1;*written=0;
 uint32_t mid=uint32_t(src[4])|uint32_t(src[5])<<8|uint32_t(src[6])<<16|uint32_t(src[7])<<24;
 if(mid<14||mid>1048590)return 1;
 auto tmp=static_cast<uint8_t*>(heap_caps_malloc(mid,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
 if(!tmp)return 3;size_t actual=0;int status=p4_szip(1,src,n,tmp,mid,&actual);
 if(!status){auto r=rle2::decode_words(tmp,actual,dst,cap);if(r)*written=r.bytes;else status=1;}
 heap_caps_free(tmp);return status;
}
}
