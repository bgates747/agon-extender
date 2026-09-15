"""NET-001: real adapter methods/core, fake IDF scheduling and opaque provider."""
from pathlib import Path
import subprocess,tempfile
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'vdp/video/extender/network/wired_network_service.cpp').read_text()
parts=[function(src,s) for s in ('esp_err_t WiredNetworkService::videoPostHandshake(', 'void WiredNetworkService::attemptVideoSend(', 'void WiredNetworkService::queuedSend(', 'void WiredNetworkService::performQueuedSend(')]
fake=r'''
#include <cassert>
#include <atomic>
#include <array>
#include <cstdio>
#include <vector>
#include <thread>
#include <condition_variable>
#include "extender/network/browser_video_service_core.hpp"
using namespace agon::extender::network;
using esp_err_t=int;using httpd_handle_t=void*;
constexpr int ESP_OK=0,ESP_FAIL=-1,HTTPD_WS_TYPE_CLOSE=8,HTTPD_WS_TYPE_BINARY=2,HTTPD_WS_TYPE_CONTINUE=0,HTTPD_WS_CLIENT_WEBSOCKET=1;
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
constexpr char kTag[]="test";
struct httpd_req_t {void *user_ctx;void *handle;int socket;};
struct httpd_ws_frame_t {int type{};bool fragmented{},final{};uint8_t *payload{};size_t len{};};
int httpd_req_to_sockfd(httpd_req_t *r){return r->socket;}
std::vector<int> closed,sent;void (*pending)(void*);void *pending_context;bool queue_fail=false;
int httpd_ws_send_frame_async(void*,int fd,httpd_ws_frame_t *f){if(f->type==8){assert(f->payload[0]==3&&f->payload[1]==232);closed.push_back(fd);}else sent.push_back(fd);return 0;}
int httpd_sess_trigger_close(void*,int){return 0;}
int httpd_ws_get_fd_info(void*,int){return HTTPD_WS_CLIENT_WEBSOCKET;}
int httpd_queue_work(void*,void (*fn)(void*),void *ctx){if(queue_fail)return -1;assert(!pending);pending=fn;pending_context=ctx;return 0;}
void drain(){auto fn=pending;auto ctx=pending_context;pending=nullptr;assert(fn);fn(ctx);}
namespace diagnostics {enum class VideoPhase{SocketSend};struct VideoTimingScope {VideoTimingScope(VideoPhase,unsigned){} void finish(size_t){}};}
class WiredNetworkService {
public:
 explicit WiredNetworkService(OpaqueMessageProvider &p):provider_(p){}
 OpaqueMessageProvider &provider_;BrowserVideoServiceCore video_;
 std::mutex video_dispatch_mutex_;bool video_send_queued_{};VideoClientId queued_video_client_{-1};
 std::atomic<void*> server_{(void*)1};std::atomic<unsigned> queued_sends_{},queue_failures_{},socket_send_failures_{};
 void increment(std::atomic<unsigned>&x){++x;}
 void closeVideo(httpd_req_t*,uint16_t,const char*){assert(false);}
 static esp_err_t videoPostHandshake(httpd_req_t*) noexcept;
 void attemptVideoSend() noexcept;static void queuedSend(void*) noexcept;void performQueuedSend() noexcept;
};
struct Provider:OpaqueMessageProvider {
 unsigned acquired=0,released=0;uint8_t data[1]={42};
 std::mutex gate;std::condition_variable cv;bool block=false,entered=false,proceed=false;
 static void release(void *p,uint64_t,OpaqueReleaseDisposition) noexcept {++static_cast<Provider*>(p)->released;}
 OpaqueAcquireResult tryAcquireAfter(uint64_t,OpaqueMessageLease &lease) noexcept override {
  {std::unique_lock<std::mutex> l(gate);entered=true;cv.notify_all();if(block)cv.wait(l,[&]{return proceed;});}
  OpaqueMessageSegment seg{data,1};++acquired;assert(lease.assign(acquired,&seg,1,this,release));return OpaqueAcquireResult::Acquired;
 }
};
'''
checks=r'''
void connect(WiredNetworkService &s,int fd){httpd_req_t r{&s,(void*)1,fd};assert(s.videoPostHandshake(&r)==0);assert(s.video_.client()==fd);}
void credit(WiredNetworkService &s,int fd){assert(s.video_.requestFrame(fd)==VideoCreditResult::Accepted);}
int main(){
 for(int stage=0;stage<3;++stage){Provider p;WiredNetworkService s(p);connect(s,10);
  if(stage>0)credit(s,10);if(stage>1)s.attemptVideoSend();
  connect(s,11);assert(closed.back()==10);assert(!s.video_.disconnect(10));
  assert(s.video_.requestFrame(10)==VideoCreditResult::InvalidClient);
  credit(s,11);s.attemptVideoSend();
  if(stage>1){assert(p.acquired==1);drain();assert(sent.empty()||sent.back()!=10);s.attemptVideoSend();}
  drain();assert(sent.back()==11);assert(p.acquired==p.released);
  // Reconnect the original browser, with old socket close arriving late.
  connect(s,12);assert(!s.video_.disconnect(11));credit(s,12);s.attemptVideoSend();drain();assert(sent.back()==12);
 }
 {Provider p;WiredNetworkService s(p);connect(s,20);credit(s,20);p.block=true;
  std::thread worker([&]{s.attemptVideoSend();});
  {std::unique_lock<std::mutex> l(p.gate);p.cv.wait(l,[&]{return p.entered;});}
  std::atomic<bool> started=false,done=false;
  std::thread http([&]{started=true;connect(s,21);done=true;});
  while(!started)std::this_thread::yield();assert(!done);
  {std::lock_guard<std::mutex> l(p.gate);p.proceed=true;p.cv.notify_all();}
  worker.join();http.join();assert(p.released==1);drain();credit(s,21);s.attemptVideoSend();drain();assert(sent.back()==21&&p.acquired==p.released);
 }
 {Provider p;WiredNetworkService s(p);connect(s,30);credit(s,30);queue_fail=true;s.attemptVideoSend();queue_fail=false;assert(p.acquired==p.released&&!s.video_send_queued_);connect(s,31);credit(s,31);s.attemptVideoSend();drain();assert(sent.back()==31);}
 puts("PASS: idle/credit/queued takeover, old cleanup, acquisition race, reconnect and queue failure");
}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'test.cpp').write_text(fake+'\n'.join(parts)+checks)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-pthread','-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),str(ROOT/'vdp/video/extender/network/browser_video_service_core.cpp'),str(ROOT/'vdp/video/extender/network/opaque_message.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
