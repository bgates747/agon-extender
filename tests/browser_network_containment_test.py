"""Fault-inject the actual target adapter's send/start/stop method bodies.

Platform calls alone are fakes. This checks F003 complete sends/bounded timeout and F012 handle
retention; it does not qualify physical link loss or ESP-IDF task destruction.
"""
from pathlib import Path
import subprocess
import tempfile
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'vdp/video/extender/network/wired_network_service.cpp'

def main():
    source=SOURCE.read_text()
    parts=[function(source,s) for s in ('int completeSend(', 'bool WiredNetworkService::startHttp(', 'void WiredNetworkService::stopHttp(')]
    fake=r'''
#include <cassert>
#include <atomic>
#include <cstdint>
#include <cstddef>
#include <cerrno>
#include <algorithm>
#include <cstdio>
#include <string>
#include <cstring>
template<typename... T> void trace(T...) {}
using httpd_handle_t=void *; using esp_err_t=int;
constexpr int ESP_OK=0, HTTP_GET=0, HTTPD_SOCK_ERR_TIMEOUT=-2, HTTPD_SOCK_ERR_FAIL=-1;
constexpr int HTTP_POST=1;
#if defined(AGON_EXTENDER_SD_SERVICE)
static int sdStatusHandler(void*) { return 0; }
static int sdRpcHandler(void*) { return 0; }
constexpr int route_count=8;
#else
constexpr int route_count=6;
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
static int keyboardStatusHandler(void*) { return 0; }
static int keyboardRpcHandler(void*) { return 0; }
namespace input {
struct RemoteKeyboard { enum { disconnected }; void cancel(int) {} };
template<class F> auto remoteLocked(F fn) { RemoteKeyboard r;return fn(r); }
}
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
static int telemetryHandler(void*) { return 0; }
#endif
#if defined(AGON_EXTENDER_VIDEO_TIMING)
static int videoTimingHandler(void*) { return 0; }
#endif
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
constexpr int kVideoSendWaitSeconds=5;
static int sends,send_limit=3,send_error,starts,stops,registrations,fail_at,stop_error;
static int64_t clock_us,clock_step=100;
int64_t esp_timer_get_time(){ clock_us+=clock_step; return clock_us; }
int send(int,const char *,size_t n,int){ ++sends; if(send_error) return send_error; return int(std::min(n,size_t(send_limit))); }
struct httpd_config_t { int max_uri_handlers; bool lru_purge_enable; void *global_user_ctx; void(*global_user_ctx_free_fn)(void*); int(*open_fn)(void*,int); void(*close_fn)(void*,int); int send_wait_timeout,recv_wait_timeout; };
#define HTTPD_DEFAULT_CONFIG() httpd_config_t{}
struct httpd_uri_t { const char *uri; int method; int(*handler)(void*); void *user_ctx; bool is_websocket; int(*ws_post_handshake_cb)(void*);  };
int httpd_start(void **p,httpd_config_t*) { ++starts; *p=(void*)123; return 0; }
int httpd_stop(void*) { ++stops; return stop_error; }
int httpd_register_uri_handler(void*,httpd_uri_t*) { return ++registrations==fail_at ? -1:0; }
namespace web { struct EmbeddedAsset { const char *route; }; EmbeddedAsset assets[5]={{"a"},{"b"},{"c"},{"d"},{"e"}}; auto &embeddedBrowserAssets(){return assets;} }
class WiredNetworkService {
 public:
 std::atomic<void*> server_{}; bool http_fault_{};
 std::atomic<unsigned> http_starts_{},http_stops_{},http_start_failures_{};
 void increment(std::atomic<unsigned>&n){++n;}
 static int socketOpened(void*,int){return 0;} static void socketClosed(void*,int){}
 static int assetHandler(void*){return 0;} static int videoHandler(void*){return 0;}
 static int videoPostHandshake(void*){return 0;}
 bool startHttp() noexcept; void stopHttp() noexcept;
};
'''
    checks=r'''
int main() {
 char data[12]{};
 assert(completeSend(nullptr,1,data,12,0)==12 && sends==4);
 send_error=-1; assert(completeSend(nullptr,1,data,12,0)<0);
 send_error=0;send_limit=3;clock_step=2000000;
 assert(completeSend(nullptr,1,data,12,0)==HTTPD_SOCK_ERR_TIMEOUT);
 clock_step=100;send_error=0;
 // Each registration position: five assets and the video endpoint.
 const int total_routes=route_count
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
 +2
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
 +1
#endif
#if defined(AGON_EXTENDER_VIDEO_TIMING)
 +1
#endif
 ;
 for(int failure=1;failure<=total_routes;++failure) {
  starts=stops=registrations=0;fail_at=failure;stop_error=-1;
  WiredNetworkService s;
  assert(!s.startHttp()); assert(starts==1&&stops==1&&s.server_!=nullptr&&s.http_fault_);
  assert(!s.startHttp()); assert(starts==1); // no duplicate after failed rollback
  s.stopHttp();assert(s.server_!=nullptr);
  stop_error=0;s.stopHttp();assert(s.server_==nullptr);
  fail_at=0;registrations=0;assert(s.startHttp());assert(starts==2);
  assert(s.startHttp()&&starts==2);s.stopHttp();assert(s.server_==nullptr);
 }
 printf("PASS: positive short writes complete; all %d registration failures retain live handles across failed stop/retry\n",total_routes);
}
'''
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);(p/'test.cpp').write_text(fake+'\n'.join(parts)+checks)
        for sd_service in (False,True):
            flags=['-DAGON_EXTENDER_SD_SERVICE=1'] if sd_service else []
            for remote in (False,True):
                for telemetry in (False,True):
                    selected=flags+(['-DAGON_EXTENDER_REMOTE_KEYBOARD=1'] if remote else [])
                    selected+=['-DAGON_EXTENDER_TELEMETRY=1'] if telemetry else []
                    for video_timing in (False,True):
                        diagnostic=selected+(['-DAGON_EXTENDER_VIDEO_TIMING=1'] if video_timing else [])
                        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*diagnostic,str(p/'test.cpp'),'-o',str(p/'test')],check=True)
                        subprocess.run([str(p/'test')],check=True)
if __name__=='__main__':main()
