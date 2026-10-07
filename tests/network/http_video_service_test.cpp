// Compile the entire shared adapter with only the ESP-IDF/socket boundary faked.
#include "extender/network/http_video_service.hpp"
#include "extender/network/display_status.hpp"
#include <cassert>
#include <algorithm>
#include <cstring>
#include <cerrno>
#include <vector>
#include <string>
#include <thread>
#include <condition_variable>
using namespace agon::extender::network;
static httpd_config_t config;
static std::vector<httpd_uri_t> routes;
static void(*queued)(void*);static void *queued_ctx;
static int reg_fail,reg_count,stop_fail,start_fail,queue_fail,send_fail,sends,send_limit=3,send_errno;
static int64_t clock_us,clock_step=100;
static int (*send_override)(httpd_handle_t,int,const char*,size_t,int);
static std::vector<int> closed,sent;
static std::vector<std::vector<uint8_t>> payloads;
static std::vector<int> types;static std::vector<bool> finals,fragmented;
static std::string response;
int httpd_start(httpd_handle_t *s,httpd_config_t *c){if(start_fail)return -1;config=*c;*s=&config;routes.clear();reg_count=0;return 0;}
int httpd_stop(httpd_handle_t){if(stop_fail)return -1;queued=nullptr;return 0;}
int httpd_register_uri_handler(httpd_handle_t,httpd_uri_t *r){if(++reg_count==reg_fail)return -1;routes.push_back(*r);return 0;}
int httpd_sess_set_send_override(httpd_handle_t,int,int(*f)(httpd_handle_t,int,const char*,size_t,int)){send_override=f;return 0;}
int httpd_resp_send_500(httpd_req_t*){return -500;}
int httpd_resp_set_type(httpd_req_t*,const char*){return 0;}
int httpd_resp_set_hdr(httpd_req_t*,const char*,const char*){return 0;}
int httpd_resp_set_status(httpd_req_t*,const char*){return 0;}
int httpd_resp_sendstr(httpd_req_t*,const char*body){response=body;return send_fail;}
int httpd_resp_send(httpd_req_t*,const char*body,ssize_t length){response.assign(body,size_t(length));return send_fail;}
int httpd_sess_trigger_close(httpd_handle_t,int fd){closed.push_back(fd);return 0;}
int httpd_req_to_sockfd(httpd_req_t*r){return r->socket;}
int httpd_ws_send_frame_async(httpd_handle_t,int fd,httpd_ws_frame_t *f){
 if(f->type!=HTTPD_WS_TYPE_CLOSE){sent.push_back(fd);payloads.emplace_back(f->payload,f->payload+f->len);types.push_back(f->type);finals.push_back(f->final);fragmented.push_back(f->fragmented);}
 return send_fail;
}
int httpd_ws_send_frame(httpd_req_t*r,httpd_ws_frame_t*f){return httpd_ws_send_frame_async(r->handle,r->socket,f);}
static std::string incoming="frame";static int incoming_type=HTTPD_WS_TYPE_TEXT;
int httpd_ws_recv_frame(httpd_req_t*,httpd_ws_frame_t*f,size_t n){if(!n){f->len=incoming.size();f->type=incoming_type;}else memcpy(f->payload,incoming.data(),n);return 0;}
int httpd_ws_get_fd_info(httpd_handle_t,int){return HTTPD_WS_CLIENT_WEBSOCKET;}
int httpd_queue_work(httpd_handle_t,void(*f)(void*),void*c){if(queue_fail)return -1;assert(!queued);queued=f;queued_ctx=c;return 0;}
void*httpd_get_global_user_ctx(httpd_handle_t){return config.global_user_ctx;}
int fake_send(int,const char*,size_t n,int){++sends;if(send_errno){errno=send_errno;send_errno=0;return -1;}if(send_fail)return -1;return int(std::min(n,size_t(send_limit)));}
int lwip_close(int){return 0;}
int64_t esp_timer_get_time(){return clock_us+=clock_step;}
[[maybe_unused]] static void drain(){auto f=queued;auto c=queued_ctx;queued=nullptr;assert(f);f(c);}
struct Provider:OpaqueMessageProvider {
 int acquired=0,released=0;OpaqueReleaseDisposition disposition{};uint8_t a[2]={1,2},b[3]={3,4,5};
 bool unavailable=false,block=false,entered=false,proceed=false;
 std::mutex gate;std::condition_variable cv;
 static void release(void*c,uint64_t,OpaqueReleaseDisposition d) noexcept {auto*p=static_cast<Provider*>(c);++p->released;p->disposition=d;}
 OpaqueAcquireResult tryAcquireAfter(uint64_t,OpaqueMessageLease&l) noexcept override {
  {std::unique_lock<std::mutex> lock(gate);entered=true;cv.notify_all();if(block)cv.wait(lock,[&]{return proceed;});}
  if(unavailable)return OpaqueAcquireResult::Unavailable;
  OpaqueMessageSegment s[]={{a,2},{b,3}};assert(l.assign(++acquired,s,2,this,release));return OpaqueAcquireResult::Acquired;
 }
};
[[maybe_unused]] static httpd_req_t connect(int fd){auto&r=routes.back();httpd_req_t q{r.user_ctx,&config,fd};assert(r.ws_post_handshake_cb(&q)==0);return q;}
[[maybe_unused]] static void credit(httpd_req_t&q){assert(routes.back().handler(&q)==0);}
int main(){
 // Mode metadata remains nominal even when the physical HDMI clock is fixed.
 agon::extender::display::modeStatus.publish({140,320,200,64,70,true});
 httpd_req_t metadata{};assert(agon::extender::display_status::handle(&metadata)==0);
 assert(response.find("\"width\":320")!=std::string::npos);
 assert(response.find("\"refresh_hz\":70")!=std::string::npos);
 assert(response.find("\"double_buffered\":true")!=std::string::npos);
#if defined(AGON_EXTENDER_HDMI)
 assert(response.find("\"output\":\"hdmi\"")!=std::string::npos);
 assert(response.find("\"output_width\":1280")!=std::string::npos);
 assert(response.find("\"output_height\":720")!=std::string::npos);
 assert(response.find("\"output_nominal_refresh_hz\":60")!=std::string::npos);
 assert(response.find("\"frame_clock\":\"dma-frame-complete\"")!=std::string::npos);
#else
 assert(response.find("\"output\"")==std::string::npos);
#endif
 Provider p;HttpVideoService service(p);uint8_t assetdata[]={42};
 agon::extender::web::EmbeddedAsset assets[]={{"/","text/plain",assetdata,1}};
#if defined(AGON_EXTENDER_HDMI)
 // HDMI selection removes video transport while preserving the asset server
 // on which independent input/control routes are subsequently registered.
 reg_fail=1;assert(!service.startServer(assets,1));assert(!service.running());reg_fail=0;
 assert(service.startServer(assets,1));
 assert(routes.size()==1 && std::strcmp(routes[0].uri,"/")==0);
 for(auto const &route:routes)assert(std::strcmp(route.uri,"/video")!=0);
 httpd_req_t request{routes[0].user_ctx,&config,7};
 assert(routes[0].handler(&request)==0);
 for(int i=0;i<10;++i)service.poll();
 assert(p.acquired==0 && p.released==0 && queued==nullptr);
 assert(service.stopServer());
#else
 start_fail=1;assert(!service.startServer(assets,1));start_fail=0;
 for(int fail=1;fail<=2;++fail){reg_fail=fail;assert(!service.startServer(assets,1));assert(!service.running());}reg_fail=0;
 // Failed rollback retains context, refuses replacement startup, allows stop retry.
 reg_fail=1;stop_fail=1;assert(!service.startServer(assets,1));assert(!service.startServer(assets,1));assert(!service.stopServer());stop_fail=0;assert(service.stopServer());reg_fail=0;
 assert(service.startServer(assets,1));assert(config.server_port==80&&config.ctrl_port==32768&&config.max_open_sockets==7);
 config.open_fn(&config,7);char data[12]{};assert(send_override(&config,7,data,12,0)==12&&sends==4);
 send_errno=EINTR;assert(send_override(&config,7,data,12,0)==12);
 send_fail=1;assert(send_override(&config,7,data,12,0)<0);send_fail=0;
 clock_step=2000000;assert(send_override(&config,7,data,12,0)==HTTPD_SOCK_ERR_TIMEOUT);clock_step=100;
 auto q=connect(7);service.poll();assert(!queued);credit(q);service.poll();assert(queued&&p.released==0);drain();assert(p.released==1&&p.disposition==OpaqueReleaseDisposition::Sent);
 assert(payloads[0]==std::vector<uint8_t>({1,2})&&payloads[1]==std::vector<uint8_t>({3,4,5}));
 assert(types[0]==HTTPD_WS_TYPE_BINARY&&types[1]==HTTPD_WS_TYPE_CONTINUE&&fragmented[0]&&!finals[0]&&finals[1]);
 // Old queued work cannot send to a replacement viewer.
 credit(q);service.poll();auto q2=connect(8);assert(p.released==2);credit(q2);auto n=sent.size();drain();assert(sent.size()==n);service.poll();drain();assert(sent.back()==8);
 // A delayed close for the old fd must not disconnect its replacement.
 config.close_fn(&config,7);credit(q2);service.poll();drain();assert(sent.back()==8);
 // Disconnect with queued work releases once, including fd reuse.
 credit(q2);service.poll();auto before=p.released;config.close_fn(&config,8);assert(p.released==before+1);q2=connect(8);credit(q2);drain();assert(p.released==before+1);service.poll();drain();
 queue_fail=1;credit(q2);service.poll();assert(!queued&&p.disposition==OpaqueReleaseDisposition::Failed);queue_fail=0;
 q2=connect(9);send_fail=1;credit(q2);service.poll();drain();assert(p.disposition==OpaqueReleaseDisposition::Failed);send_fail=0;
 q2=connect(10);credit(q2);credit(q2);assert(!closed.empty()&&closed.back()==10);service.poll();assert(!queued);
 q2=connect(11);incoming="wrong";credit(q2);incoming="frame";assert(closed.back()==11);
 q2=connect(12);p.unavailable=true;credit(q2);service.poll();assert(!queued&&closed.back()==12);p.unavailable=false;
 // Worker acquisition and HTTP takeover serialize around held provider state.
 q2=connect(13);credit(q2);p.block=true;p.entered=false;
 std::thread worker([&]{service.poll();});
 {std::unique_lock<std::mutex> lock(p.gate);p.cv.wait(lock,[&]{return p.entered;});}
 std::thread http([&]{connect(14);});
 {std::lock_guard<std::mutex> lock(p.gate);p.proceed=true;p.cv.notify_all();}
 worker.join();http.join();p.block=false;drain();
 q2=connect(15);credit(q2);service.poll();before=p.released;stop_fail=1;assert(!service.stopServer());assert(p.released==before);stop_fail=0;assert(service.stopServer());assert(p.released==before+1&&!queued);
 assert(service.startServer(assets,1));assert(service.stopServer());assert(p.acquired==p.released);
#endif
}
