// Standalone diagnostic fixture, not Extender firmware or upstream benchmark.
// Uses Espressif Ethernet and HTTP server APIs; no Agon pins/protocols.
#include <Arduino.h>
#include <ETH.h>
#include <esp_http_server.h>
#include <esp_timer.h>
#include <esp_heap_caps.h>
#include <esp_ota_ops.h>
#include <atomic>
#include <algorithm>
#include "pattern.h"
static constexpr char ID[]="research003-reference-r01";
static constexpr unsigned MAX=1800;
struct Sample {uint32_t id,us;uint64_t done;};
struct Slot {uint8_t *p;Sample s;};
static Slot slots[3];
static uint8_t *precomputed;
static QueueHandle_t freeq,readyq;
static std::atomic<bool> busy{false},finished{false},cancelled{false};
static TaskHandle_t producer;
static unsigned mode,fps,count,produced,dropped,sent;
static uint64_t start_us,end_us;
static Sample samples[MAX];
static uint32_t sends[MAX];
static char result[2048]="{\"state\":\"idle\"}";
static portMUX_TYPE result_lock=portMUX_INITIALIZER_UNLOCKED;
static void put_result(const char *s) {portENTER_CRITICAL(&result_lock);strlcpy(result,s,sizeof(result));portEXIT_CRITICAL(&result_lock);}
static uint32_t percentile(uint32_t *p,unsigned n,unsigned percent) {
 if(!n)return 0;std::sort(p,p+n);return p[((n-1)*percent)/100];
}
static void produce(void*) {
 for(;;){ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
  produced=dropped=0;start_us=esp_timer_get_time();
  for(unsigned id=0;id<count&&!cancelled.load();++id){
   int64_t target=start_us+(uint64_t)id*1000000/fps;
   while(!cancelled.load()&&esp_timer_get_time()<target) vTaskDelay(1);
   if(cancelled.load())break;
   if(esp_timer_get_time()-target >= 1000000/fps){++dropped;continue;}
   int idx=0;
   if(xQueueReceive(freeq,&idx,0)!=pdTRUE){++dropped;continue;}
   auto t=esp_timer_get_time();
   if(mode!=1)pattern(slots[idx].p,id);
   auto done=esp_timer_get_time();
   slots[idx].s={id,(uint32_t)(done-t),(uint64_t)done};
   samples[produced++]=slots[idx].s;
   if(mode==0)xQueueSend(freeq,&idx,portMAX_DELAY);
   else if(xQueueSend(readyq,&idx,pdMS_TO_TICKS(2000))!=pdTRUE){cancelled=true;break;}
  }
  while(!cancelled.load() && esp_timer_get_time() < (int64_t)(start_us+(uint64_t)count*1000000/fps))vTaskDelay(1);
  end_us=esp_timer_get_time();finished=true;
 }
}
static esp_err_t status_handler(httpd_req_t *r){
 char copy[2048];portENTER_CRITICAL(&result_lock);memcpy(copy,result,sizeof(copy));portEXIT_CRITICAL(&result_lock);
 httpd_resp_set_type(r,"application/json");return httpd_resp_sendstr(r,copy);
}
static esp_err_t run_handler(httpd_req_t *r){
 char q[128],v[24];
 if(httpd_req_get_url_query_str(r,q,sizeof(q))!=ESP_OK)return httpd_resp_send_err(r,HTTPD_400_BAD_REQUEST,"query");
 if(busy.exchange(true))return httpd_resp_send_err(r,HTTPD_400_BAD_REQUEST,"busy");
 unsigned m=99,f=0,c=0;
 if(httpd_query_key_value(q,"mode",v,sizeof(v))==ESP_OK)m=strcmp(v,"render")==0?0:strcmp(v,"send")==0?1:strcmp(v,"combined")==0?2:99;
 if(httpd_query_key_value(q,"fps",v,sizeof(v))==ESP_OK)f=atoi(v);
 if(httpd_query_key_value(q,"frames",v,sizeof(v))==ESP_OK)c=atoi(v);
 if(m>2||(f!=30&&f!=60)||c<120||c>MAX){busy=false;return httpd_resp_send_err(r,HTTPD_400_BAD_REQUEST,"parameters");}
 mode=m;fps=f;count=c;sent=0;cancelled=false;finished=false;
 xQueueReset(freeq);xQueueReset(readyq);for(int i=0;i<3;++i)xQueueSend(freeq,&i,0);
 put_result("{\"state\":\"running\"}");
 httpd_resp_set_type(r,"application/octet-stream");
 xTaskNotifyGive(producer);
 esp_err_t rc=ESP_OK;
 uint64_t send_end=0;
 while(!finished.load()||uxQueueMessagesWaiting(readyq)){
  int idx;if(xQueueReceive(readyq,&idx,pdMS_TO_TICKS(50))!=pdTRUE)continue;
  const auto &s=slots[idx].s;
  // Native little endian words: magic R3F1, sequence, bytes, render us, done us.
  uint32_t header[6]={0x31463352,s.id,N,s.us,(uint32_t)s.done,(uint32_t)(s.done>>32)};
  uint64_t t=esp_timer_get_time();
  rc=httpd_resp_send_chunk(r,(char*)header,sizeof(header));
  if(rc==ESP_OK)rc=httpd_resp_send_chunk(r,(char*)(mode==1?precomputed+(s.id&63)*N:slots[idx].p),N);
  send_end=esp_timer_get_time();sends[sent++]=send_end-t;
  xQueueSend(freeq,&idx,portMAX_DELAY);
  if(rc!=ESP_OK){cancelled=true;break;}
 }
 while(!finished.load())vTaskDelay(1);
 uint64_t elapsed=std::max(end_us,send_end)-start_us;
 static uint32_t work[MAX],interval[MAX];uint64_t sum=0;unsigned ni=0;
 for(unsigned i=0;i<produced;++i){work[i]=samples[i].us;sum+=work[i];if(i>60)interval[ni++]=samples[i].done-samples[i-1].done;}
 auto p95=percentile(work,produced,95),mx=produced?work[produced-1]:0;
 auto i50=percentile(interval,ni,50),i95=percentile(interval,ni,95),im=ni?interval[ni-1]:0;
 uint64_t ssum=0;for(unsigned i=0;i<sent;++i)ssum+=sends[i];auto sp95=percentile(sends,sent,95);
 char out[2048];snprintf(out,sizeof(out),"{\"state\":\"done\",\"identity\":\"%s\",\"mode\":%u,\"fps_target\":%u,\"requested\":%u,\"produced\":%u,\"dropped\":%u,\"sent\":%u,\"send_error\":%d,\"elapsed_us\":%llu,\"render_mean_us\":%.3f,\"render_p95_us\":%u,\"render_max_us\":%u,\"interval_p50_us\":%u,\"interval_p95_us\":%u,\"interval_max_us\":%u,\"send_mean_us\":%.3f,\"send_p95_us\":%u,\"cpu_mhz\":%u,\"psram_bytes\":%u}",ID,mode,fps,count,produced,dropped,sent,(int)rc,(unsigned long long)elapsed,produced?(double)sum/produced:0,p95,mx,i50,i95,im,sent?(double)ssum/sent:0,sp95,getCpuFrequencyMhz(),ESP.getPsramSize());
 put_result(out);
 if(rc==ESP_OK){uint32_t h[6]={0x314a3352,0,(uint32_t)strlen(out),0,0,0};rc=httpd_resp_send_chunk(r,(char*)h,sizeof(h));if(rc==ESP_OK)rc=httpd_resp_send_chunk(r,out,strlen(out));if(rc==ESP_OK)rc=httpd_resp_send_chunk(r,nullptr,0);}
 busy=false;return rc;
}
void setup(){
 Serial.begin(115200);Serial.printf("Standalone %s\n",ID);
 esp_ota_mark_app_valid_cancel_rollback();
 for(auto &s:slots){s.p=(uint8_t*)heap_caps_malloc(N,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);assert(s.p);}
 precomputed=(uint8_t*)heap_caps_malloc(64*N,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);assert(precomputed);
 for(unsigned i=0;i<64;++i)pattern(precomputed+i*N,i);
 freeq=xQueueCreate(3,sizeof(int));readyq=xQueueCreate(3,sizeof(int));assert(freeq&&readyq);
 assert(xTaskCreatePinnedToCore(produce,"producer",4096,nullptr,5,&producer,0)==pdPASS);
 assert(ETH.begin(ETH_PHY_IP101,1,31,52,51,EMAC_CLK_EXT_IN));
 httpd_config_t cfg=HTTPD_DEFAULT_CONFIG();cfg.core_id=1;cfg.task_priority=5;cfg.stack_size=8192;cfg.send_wait_timeout=5;
 httpd_handle_t h;ESP_ERROR_CHECK(httpd_start(&h,&cfg));
 httpd_uri_t run={};run.uri="/run";run.method=HTTP_GET;run.handler=run_handler;ESP_ERROR_CHECK(httpd_register_uri_handler(h,&run));
 httpd_uri_t status={};status.uri="/status";status.method=HTTP_GET;status.handler=status_handler;ESP_ERROR_CHECK(httpd_register_uri_handler(h,&status));
 cfg.server_port=8080;cfg.ctrl_port+=1;ESP_ERROR_CHECK(httpd_start(&h,&cfg));ESP_ERROR_CHECK(httpd_register_uri_handler(h,&status));
}
void loop(){delay(1000);}
