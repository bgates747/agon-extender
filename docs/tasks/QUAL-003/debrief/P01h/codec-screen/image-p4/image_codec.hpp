// Task-only image encoders. HTTP task is sole owner; snapshot lease is immutable.
// All persistent scratch is allocated once. No graphics lock or scheduler change.
#pragma once
#include <driver/jpeg_encode.h>
#include <esp_heap_caps.h>
#include <esp_timer.h>
#include <esp_http_server.h>
#include <new>
#include "PNGenc/PNGenc.h"
namespace imagecodec {
constexpr size_t pixels=512*384,capacity=pixels*4+4096;
static jpeg_encoder_handle_t engine=nullptr;
static uint8_t *rgb=nullptr,*output=nullptr,*input=nullptr;
static size_t rgbcap=0,outcap=0;
static PNGENC *png=nullptr;
static uint8_t palette[768]{};
static uint64_t convert_us=0,encode_us=0,attempts=0,failures=0,frames=0;
static int selected=0; // 80/90/95 JPEG, 1/3 PNG; 0 unchanged controls.
static bool init(){
 jpeg_encode_engine_cfg_t cfg{};cfg.timeout_ms=2000;
 if(jpeg_new_encoder_engine(&cfg,&engine)!=ESP_OK)return false;
 jpeg_encode_memory_alloc_cfg_t mem{};mem.buffer_direction=JPEG_ENC_ALLOC_INPUT_BUFFER;
 rgb=(uint8_t*)jpeg_alloc_encoder_mem(pixels*3,&mem,&rgbcap);
 mem.buffer_direction=JPEG_ENC_ALLOC_OUTPUT_BUFFER;
 output=(uint8_t*)jpeg_alloc_encoder_mem(capacity,&mem,&outcap);
 input=(uint8_t*)heap_caps_malloc(pixels,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 void *p=heap_caps_malloc(sizeof(PNGENC),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);if(p)png=new(p)PNGENC();
 for(unsigned i=0;i<64;i++){palette[i*3]=(i>>4)*85;palette[i*3+1]=((i>>2)&3)*85;palette[i*3+2]=(i&3)*85;}
 return rgb&&output&&input&&png;
}
// RGB888 driver expects BGR byte order. Future RGB888 buffers may call driver
// directly in that layout; indexed source expands exactly through this palette.
static bool encode(const uint8_t*src,unsigned w,unsigned h,int mode,size_t &n){
 n=0;if(!engine||!rgb||!output||!png||!src||!w||!h||w>512||h>384||w%8||h%8)return false;
 if(mode!=1&&mode!=3&&mode!=80&&mode!=90&&mode!=95)return false;
 ++attempts;auto start=esp_timer_get_time();
 for(size_t i=0;i<size_t(w)*h;i++){if(src[i]>63){++failures;return false;}if(mode>3){auto p=palette+src[i]*3;rgb[i*3]=p[0];rgb[i*3+1]=p[1];rgb[i*3+2]=p[2];}}
 convert_us+=esp_timer_get_time()-start;start=esp_timer_get_time();bool ok=false;
 if(mode>3){jpeg_encode_cfg_t cfg{};cfg.width=w;cfg.height=h;cfg.src_type=JPEG_ENCODE_IN_FORMAT_RGB888;cfg.sub_sample=JPEG_DOWN_SAMPLING_YUV444;cfg.image_quality=mode;uint32_t bytes=0;
 ok=jpeg_encoder_process(engine,&cfg,rgb,w*h*3,output,outcap,&bytes)==ESP_OK;n=bytes;
 }else{
 int rc=png->open(output,outcap);if(!rc)rc=png->encodeBegin(w,h,PNG_PIXEL_INDEXED,8,palette,mode);
 for(unsigned y=0;y<h&&!rc;y++)rc=png->addLine(const_cast<uint8_t*>(src+y*w));
 int bytes=png->close();ok=!rc&&!png->getLastError()&&bytes>0;n=bytes>0?size_t(bytes):0;
 }
 encode_us+=esp_timer_get_time()-start;if(!ok||!n||n>outcap){++failures;return false;}return true;
}
static esp_err_t handler(httpd_req_t *req){
 char query[80]{};unsigned w=0,h=0;int mode=0;char extra=0;
 if(httpd_req_get_url_query_str(req,query,sizeof query)!=ESP_OK||sscanf(query,"mode=%d&w=%u&h=%u%c",&mode,&w,&h,&extra)!=3||!w||!h||w>512||h>384||w%8||h%8||req->content_len!=w*h)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid image request");
 size_t at=0;while(at<req->content_len){int n=httpd_req_recv(req,(char*)input+at,req->content_len-at);if(n<=0)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Incomplete body");at+=n;}
 auto c=convert_us,e=encode_us;size_t n=0;if(!encode(input,w,h,mode,n))return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Image encode failed");
 char a[32],b[32];snprintf(a,sizeof a,"%llu",(unsigned long long)(convert_us-c));snprintf(b,sizeof b,"%llu",(unsigned long long)(encode_us-e));httpd_resp_set_hdr(req,"X-Convert-Us",a);httpd_resp_set_hdr(req,"X-Encode-Us",b);
 httpd_resp_set_type(req,mode>3?"image/jpeg":"image/png");return httpd_resp_send(req,(char*)output,n);
}
}
