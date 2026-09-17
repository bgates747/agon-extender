// Task-only bounded codec RPC. Does not inject VDU commands or draw pixels.
#pragma once
#include "extender/diagnostics/srle2/srle2.hpp"
#include <esp_http_server.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <cstdio>
#include <cstring>
namespace srle2probe {
struct Buffer {
  uint8_t *p;
  explicit Buffer(size_t n):p(static_cast<uint8_t*>(heap_caps_malloc(n,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT))){}
  ~Buffer(){heap_caps_free(p);}
  Buffer(const Buffer&)=delete;
  Buffer& operator=(const Buffer&)=delete;
};
inline esp_err_t handler(httpd_req_t *req) {
  constexpr size_t maximum=1048590, capacity=2097152;
  char query[64]{};
  if (!req->content_len || req->content_len>maximum ||
      httpd_req_get_url_query_str(req,query,sizeof query)!=ESP_OK)
    return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid bounded codec request");
  const bool enc=std::strcmp(query,"op=encode")==0;
  const bool dec=std::strcmp(query,"op=decode")==0;
  const bool unpack=std::strcmp(query,"op=unpack")==0;
  if(!enc&&!dec&&!unpack)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Unknown codec operation");
  Buffer input(req->content_len),output(capacity);
  if(!input.p||!output.p)return httpd_resp_send_500(req);
  size_t at=0;unsigned timeouts=0;
  while(at<req->content_len){
    int n=httpd_req_recv(req,reinterpret_cast<char*>(input.p+at),req->content_len-at);
    if(n==HTTPD_SOCK_ERR_TIMEOUT && ++timeouts<3)continue;
    if(n<=0)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Incomplete body");
    at+=size_t(n);
  }
  size_t written=0;
  const size_t before=heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  auto start=esp_timer_get_time();
  int status=unpack?srle2::decode(input.p,at,output.p,capacity,&written):p4_szip(dec?1:0,input.p,at,output.p,capacity,&written);
  auto elapsed=esp_timer_get_time()-start;
  const size_t after=heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  char duration[32],stack[32],free_before[32],free_after[32],code[16];
  snprintf(duration,sizeof duration,"%lld",static_cast<long long>(elapsed));
  snprintf(stack,sizeof stack,"%u",unsigned(uxTaskGetStackHighWaterMark(nullptr)));
  snprintf(free_before,sizeof free_before,"%u",unsigned(before));
  snprintf(free_after,sizeof free_after,"%u",unsigned(after));
  snprintf(code,sizeof code,"%d",status);
  httpd_resp_set_hdr(req,"X-Codec-Us",duration);
  httpd_resp_set_hdr(req,"X-Stack-Min-Bytes",stack);
  httpd_resp_set_hdr(req,"X-Psram-Free-Before",free_before);
  httpd_resp_set_hdr(req,"X-Psram-Free-After",free_after);
  httpd_resp_set_hdr(req,"X-Codec-Status",code);
  if(status)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Codec rejected input");
  httpd_resp_set_type(req,"application/octet-stream");
  return httpd_resp_send(req,reinterpret_cast<char*>(output.p),written);
}
}
