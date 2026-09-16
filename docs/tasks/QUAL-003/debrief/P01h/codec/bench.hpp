// Task-only synchronous microbenchmark. No graphics or UART command injection.
#pragma once
#include "rle2.hpp"
#include <esp_http_server.h>
#include <esp_heap_caps.h>
#include <esp_timer.h>
#include <cstdio>
#include <algorithm>
namespace rle2bench {
inline esp_err_t handler(httpd_req_t *req) {
 constexpr size_t n=512*384;
 auto a=(uint8_t*)heap_caps_malloc(n,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 auto b=(uint8_t*)heap_caps_malloc(n+14,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 auto c=(uint8_t*)heap_caps_malloc(n,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 if(!a||!b||!c){free(a);free(b);free(c);return httpd_resp_send_500(req);}
 auto reply=(char*)heap_caps_malloc(4200,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
 if(!reply){free(a);free(b);free(c);return httpd_resp_send_500(req);}
 size_t used=0;
 used+=snprintf(reply+used,4200-used,"{\"bytes\":%u,\"trials\":9,\"memory\":\"PSRAM\",\"rows\":[",unsigned(n));
 bool ok=true;
 for(unsigned pattern=0;pattern<4;++pattern){
  uint32_t rng=0x12345678;
  for(size_t i=0;i<n;++i){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;
   a[i]=pattern==0?0:pattern==1?uint8_t(rng&63):pattern==2?uint8_t(((i%512)+(i/512))&63):uint8_t(((i%512)/16+(i/512)/16)&63);}
  for(unsigned variant=0;variant<3;++variant){
   int64_t enc[9],dec[9];size_t bytes=0;
   for(unsigned trial=0;trial<10;++trial){
    auto t=esp_timer_get_time();auto e=variant==2?rle2::encode_words(a,n,b,n+14,true):variant?rle2::encode_fast(a,n,b,n+14,true):rle2::encode(a,n,b,n+14,true);auto t2=esp_timer_get_time();
    auto d=variant==2?rle2::decode_words(b,e.bytes,c,n):rle2::decode(b,e.bytes,c,n);auto t3=esp_timer_get_time();
    ok &= bool(e)&&bool(d)&&d.bytes==n;bytes=e.bytes;
    for(size_t i=0;i<n;++i)if(c[i]!=(a[i]|192)){ok=false;break;}
    if(trial){enc[trial-1]=t2-t;dec[trial-1]=t3-t2;}
   }
   std::sort(enc,enc+9);std::sort(dec,dec+9);
   used+=snprintf(reply+used,4200-used,"%s{\"pattern\":%u,\"variant\":%u,\"encoded\":%u,\"encode_us\":%lld,\"encode_max_us\":%lld,\"decode_us\":%lld,\"decode_max_us\":%lld}",pattern||variant?",":"",pattern,variant,unsigned(bytes),(long long)enc[4],(long long)enc[8],(long long)dec[4],(long long)dec[8]);
  }
 }
 used+=snprintf(reply+used,4200-used,"],\"exact\":%s}",ok?"true":"false");
 free(a);free(b);free(c);httpd_resp_set_type(req,"application/json");auto result=httpd_resp_send(req,reply,used);free(reply);return result;
}
}
