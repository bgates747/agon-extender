// BENCH-006: HTTP requests; only the VDU owner reads Context/font/canvas.
// Polling never claims video ownership. Text is sampled over time, not atomic.
#pragma once
#include <atomic>
#include <cstdio>
#include <esp_http_server.h>
namespace agon::extender::screen_text {
inline std::atomic<unsigned> state{0}; // idle, requested, collecting, ready
inline char text[9000];
inline size_t length=0;
inline unsigned cols=0,rows=0,index=0,unknown=0;
inline const void *owner=nullptr,*font=nullptr;
inline int width=0,height=0,fw=0,fh=0;
inline bool changed=false;
inline esp_err_t handle(httpd_req_t *req) {
 unsigned s=state.load(std::memory_order_acquire);
 httpd_resp_set_hdr(req,"Cache-Control","no-store");
 httpd_resp_set_type(req,"text/plain; charset=utf-8");
 if(s==3){
  if(changed)httpd_resp_set_status(req,"409 Conflict");
  auto result=httpd_resp_send(req,text,length);
  state.store(0,std::memory_order_release);return result;
 }
 if(s==0)state.store(1,std::memory_order_release);
 httpd_resp_set_status(req,"202 Accepted");
 httpd_resp_set_hdr(req,"Retry-After","1");
 return httpd_resp_sendstr(req,"Screen capture pending\n");
}
template<class C> void poll(C *ctx,int w,int h) {
 unsigned s=state.load(std::memory_order_acquire);
 if(s!=1 && s!=2)return;
 auto f=ctx->screenTextFont();
 if(s==1){
  width=w;height=h;fw=f->width;fh=f->height;owner=ctx;font=f;
  cols=fw?w/fw:0;rows=fh?h/fh:0;index=unknown=0;changed=false;
  if(!cols||!rows||cols>255||rows>255||cols*rows>8192){
   length=snprintf(text,sizeof(text),"Unsupported screen/font dimensions\n");
   changed=true;state.store(3,std::memory_order_release);return;
  }
  length=snprintf(text,sizeof(text),"cols=%u rows=%u; sampled text; unknown=?; edge cells may be unreadable\n",cols,rows);
  state.store(2,std::memory_order_release);
 }
 if(owner!=ctx||font!=f||w!=width||h!=height||f->width!=fw||f->height!=fh){
  changed=true;length=snprintf(text,sizeof(text),"Display context changed; request a fresh capture\n");
  state.store(3,std::memory_order_release);return;
 }
 // Eight cells per parser iteration keep input/parser progress between batches.
 for(unsigned n=0;n<8 && index<cols*rows;++n,++index){
  unsigned char c=ctx->getScreenChar(index%cols,index/cols);
  if(c<32||c>126){c='?';++unknown;}
  text[length++]=c;
  if(index%cols==cols-1)text[length++]='\n';
 }
 if(index==cols*rows)state.store(3,std::memory_order_release);
}
}
