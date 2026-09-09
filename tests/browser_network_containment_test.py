"""Fault-inject the actual target adapter's send/start/stop method bodies.

Platform calls alone are fakes. This checks F003 complete sends and F012 handle
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
    parts=[function(source,s) for s in ('int completeSend(', 'bool WiredNetworkService::startHttp(', 'void WiredNetworkService::stopHttp(', 'esp_err_t WiredNetworkService::keyboardAdmission(')]
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
using httpd_handle_t=void *; using esp_err_t=int;
constexpr int ESP_OK=0, HTTP_GET=0, HTTPD_SOCK_ERR_TIMEOUT=-2, HTTPD_SOCK_ERR_FAIL=-1;
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define AGON_EXTENDER_BROWSER_TYPING 1
using String=std::string;
struct httpd_req_t { const char *host, *origin; };
struct Ip { String toString(){return "10.0.0.1";} }; struct Eth { Ip localIP(){return {};} } ETH;
int httpd_req_get_hdr_value_str(httpd_req_t *r,const char *name,char *out,size_t n) {
 const char *v=!strcmp(name,"Host")?r->host:r->origin;
 if(!v||strlen(v)>=n) return -1;
 strcpy(out,v); return 0;
}
static constexpr int ESP_FAIL=-1;
static int sends,send_limit=3,send_error,starts,stops,registrations,fail_at,stop_error;
static int64_t clock_us;
int64_t esp_timer_get_time(){ clock_us+=100; return clock_us; }
int send(int,const char *,size_t n,int){ ++sends; if(send_error) return send_error; return int(std::min(n,size_t(send_limit))); }
struct httpd_config_t { int max_uri_handlers; bool lru_purge_enable; void *global_user_ctx; void(*global_user_ctx_free_fn)(void*); int(*open_fn)(void*,int); void(*close_fn)(void*,int); int send_wait_timeout,recv_wait_timeout; };
#define HTTPD_DEFAULT_CONFIG() httpd_config_t{}
struct httpd_uri_t { const char *uri; int method; int(*handler)(void*); void *user_ctx; bool is_websocket; int(*ws_post_handshake_cb)(void*); int(*ws_pre_handshake_cb)(httpd_req_t*); };
int httpd_start(void **p,httpd_config_t*) { ++starts; *p=(void*)123; return 0; }
int httpd_stop(void*) { ++stops; return stop_error; }
int httpd_register_uri_handler(void*,httpd_uri_t*) { return ++registrations==fail_at ? -1:0; }
namespace web { struct EmbeddedAsset { const char *route; }; EmbeddedAsset assets[5]={{"a"},{"b"},{"c"},{"d"},{"e"}}; auto &embeddedBrowserAssets(){return assets;} }
namespace input { struct Keys { void ready(bool){} }; Keys &browserKeyboard(){static Keys keys;return keys;} }
class WiredNetworkService {
 public:
 std::atomic<void*> server_{}; bool http_fault_{};
 std::atomic<unsigned> http_starts_{},http_stops_{},http_start_failures_{};
 void increment(std::atomic<unsigned>&n){++n;}
 static int socketOpened(void*,int){return 0;} static void socketClosed(void*,int){}
 static int assetHandler(void*){return 0;} static int videoHandler(void*){return 0;}
 static int videoPostHandshake(void*){return 0;} static int keyboardHandler(void*){return 0;}
 static int keyboardAdmission(httpd_req_t*) noexcept;
 bool startHttp() noexcept; void stopHttp() noexcept;
};
'''
    checks=r'''
int main() {
 httpd_req_t origin{"10.0.0.1","http://10.0.0.1"};
 assert(WiredNetworkService::keyboardAdmission(&origin)==ESP_OK);
 origin.origin=nullptr; assert(WiredNetworkService::keyboardAdmission(&origin)==ESP_FAIL);
 origin.origin="http://attacker.test"; assert(WiredNetworkService::keyboardAdmission(&origin)==ESP_FAIL);
 origin.host="attacker.test"; assert(WiredNetworkService::keyboardAdmission(&origin)==ESP_FAIL);
 origin.host="10.0.0.1";origin.origin="null"; assert(WiredNetworkService::keyboardAdmission(&origin)==ESP_FAIL);
 char data[12]{};
 assert(completeSend(nullptr,1,data,12,0)==12 && sends==4);
 send_error=-1; assert(completeSend(nullptr,1,data,12,0)<0);
 // Each registration position, including the new writable endpoint.
 for(int failure=1;failure<=7;++failure) {
  starts=stops=registrations=0;fail_at=failure;stop_error=-1;
  WiredNetworkService s;
  assert(!s.startHttp()); assert(starts==1&&stops==1&&s.server_!=nullptr&&s.http_fault_);
  assert(!s.startHttp()); assert(starts==1); // no duplicate after failed rollback
  s.stopHttp();assert(s.server_!=nullptr);
  stop_error=0;s.stopHttp();assert(s.server_==nullptr);
  fail_at=0;registrations=0;assert(s.startHttp());assert(starts==2);
  assert(s.startHttp()&&starts==2);s.stopHttp();assert(s.server_==nullptr);
 }
 puts("PASS: positive short writes complete; all seven registration failures retain live handles across failed stop/retry");
}
'''
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);(p/'test.cpp').write_text(fake+'\n'.join(parts)+checks)
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
        subprocess.run([str(p/'test')],check=True)
if __name__=='__main__':main()
