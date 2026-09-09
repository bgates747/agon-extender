"""Replay the selected IDF handshake dispatch branch with the actual key handler.

Transport parsing/sends are fakes. The dispatch branch is read from the installed
IDF source supplied by the caller; do not replace it with a second handshake
model. This specifically catches initialization hidden in a skipped GET handler.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--idf-root',type=Path,required=True)
    args=parser.parse_args()
    upstream=(args.idf_root/'components/esp_http_server/src/httpd_uri.c').read_text()
    a=upstream.index('    /* Attach user context data (passed during URI registration)')
    dispatch=upstream[a:upstream.index('\n}',a)]
    source=(ROOT/'vdp/video/extender/network/wired_network_service.cpp').read_text()
    a=source.index('struct KeyTraceContext')
    support=source[a:source.index('\n}\nesp_err_t WiredNetworkService::keyboardPostHandshake',a)]
    methods='\n'.join(function(source,s) for s in [
        'esp_err_t WiredNetworkService::keyboardPostHandshake(',
        'esp_err_t WiredNetworkService::keyboardHandler('])
    a=source.index('  httpd_uri_t keyboard{};')
    route=source[a:source.index('  if (httpd_register_uri_handler(server,&keyboard)',a)]
    fake=r'''
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cstdio>
#include "extender/input/browser_keyboard.hpp"
namespace input=agon::extender::input;
#define CONFIG_HTTPD_WS_SUPPORT 1
#define CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT 1
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1,ESP_ERR_NO_MEM=-2,HTTP_GET=1,HTTPD_WS_TYPE_BINARY=2;
struct httpd_req_t;
struct socket_db { int fd=42; bool ws_handshake_done{}; int(*ws_handler)(httpd_req_t*){}; bool ws_control_frames{}; void *ws_user_ctx{}; };
struct httpd_req_aux { bool ws_handshake_detect=true; socket_db *sd; };
struct httpd_req_t { int method=HTTP_GET; void *user_ctx{},*sess_ctx{}; void(*free_ctx)(void*){}; httpd_req_aux *aux{}; };
struct httpd_uri_t { const char *uri{};int method{};int(*handler)(httpd_req_t*){};void *user_ctx{};bool is_websocket{};
 int(*ws_pre_handshake_cb)(httpd_req_t*){};int(*ws_post_handshake_cb)(httpd_req_t*){};const char *supported_subprotocol{};bool handle_ws_control_frames{}; };
struct httpd_data { httpd_req_t hd_req; };
struct httpd_ws_frame_t { int type{};size_t len{};bool final{};uint8_t *payload{}; };
static unsigned opens,messages,missing,acks;
void trace(const char *event,uint64_t=0,int64_t=0,int64_t=0,int64_t=0){
 if(!strcmp(event,"keyboard_open"))++opens;
 if(!strcmp(event,"key_message"))++messages;
 if(!strcmp(event,"key_context_missing"))++missing;
}
int httpd_req_to_sockfd(httpd_req_t *r){return r->aux->sd->fd;}
int httpd_req_get_url_query_str(httpd_req_t*,char *p,size_t){strcpy(p,"sid=12345");return 0;}
int httpd_query_key_value(const char*,const char*,char *p,size_t){strcpy(p,"12345");return 0;}
int httpd_ws_respond_server_handshake(httpd_req_t*,const char*){return 0;}
static uint8_t packet[4]={'T'};static size_t packet_length=1;static int64_t now=1000;
int64_t esp_timer_get_time(){return now;}
int httpd_ws_recv_frame(httpd_req_t*,httpd_ws_frame_t *f,size_t n){
 if(!n){f->len=packet_length;f->type=HTTPD_WS_TYPE_BINARY;f->final=true;}
 else memcpy(f->payload,packet,packet_length);
 return 0;
}
int httpd_ws_send_frame(httpd_req_t*,httpd_ws_frame_t *f){assert(f->len==1&&*f->payload=='A');++acks;return 0;}
class WiredNetworkService {
 public:
 static int keyboardAdmission(httpd_req_t*){return 0;}
 static esp_err_t keyboardPostHandshake(httpd_req_t*) noexcept;
 static esp_err_t keyboardHandler(httpd_req_t*) noexcept;
 httpd_uri_t route();
};
'''
    checks=r'''
int main(){
 WiredNetworkService service;auto uri=service.route();
 socket_db socket;httpd_req_aux aux{true,&socket};httpd_data hd;hd.hd_req.aux=&aux;
 // With no post callback (the r03 registration), the actual IDF dispatch
 // skips the GET handler and the first frame fails because context is absent.
 auto old=uri;old.ws_post_handshake_cb=nullptr;
 assert(dispatch(&hd,&old,&hd.hd_req)==0);assert(opens==0&&!hd.hd_req.sess_ctx);
 hd.hd_req.method=-1;assert(socket.ws_handler(&hd.hd_req)==ESP_FAIL);assert(missing==1);
 // Correct callback initializes exactly once; normal frames retain that context.
 hd.hd_req.method=HTTP_GET;
 assert(uri.ws_post_handshake_cb!=nullptr);
 assert(dispatch(&hd,&uri,&hd.hd_req)==0);assert(opens==1&&hd.hd_req.sess_ctx);
 hd.hd_req.method=-1;input::browserKeyboard().ready(true);
 assert(socket.ws_handler(&hd.hd_req)==ESP_OK);assert(acks==1&&messages==1);
 packet[0]='H';assert(socket.ws_handler(&hd.hd_req)==ESP_OK);
 packet_length=4;packet[0]='K';packet[1]=4;packet[2]=0;packet[3]=1;
 assert(socket.ws_handler(&hd.hd_req)==ESP_OK);
 agon::extender::input::ProcessedKey key;
 assert(input::browserKeyboard().pop(key,1)&&key.keycode=='a'&&key.down);
 assert(acks==3&&messages==3&&opens==1);
 auto *ctx=static_cast<KeyTraceContext *>(hd.hd_req.sess_ctx);assert(ctx->session==12345&&ctx->ordinal==3);
 input::browserKeyboard().close(socket.fd);
 hd.hd_req.free_ctx(hd.hd_req.sess_ctx);hd.hd_req.sess_ctx=nullptr;
 puts("PASS: actual IDF handshake dispatch exposes old missing-context failure; registered post callback admits take/heartbeat/key, preserves context and releases it");
}
'''
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);code=fake+support+methods+'\nhttpd_uri_t WiredNetworkService::route(){\n'+route+'return keyboard;\n}\n'
        code+='int dispatch(httpd_data *hd,httpd_uri_t *uri,httpd_req_t *req){\n'+dispatch+'\n}\n'+checks
        (p/'test.cpp').write_text(code)
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
        subprocess.run([str(p/'test')],check=True)
if __name__=='__main__':main()
