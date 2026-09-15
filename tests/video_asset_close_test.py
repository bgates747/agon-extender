"""Finite assets free HTTP admission slots without touching the video socket."""
from pathlib import Path
import subprocess,tempfile
from processed_keyboard_test import function
root=Path(__file__).resolve().parents[1]
body=function((root/'vdp/video/extender/network/wired_network_service.cpp').read_text(),'esp_err_t WiredNetworkService::assetHandler(')
fake=r'''
#include <cassert>
#include <cstring>
#include <cstdint>
#include <cstdio>
#include <sys/types.h>
using esp_err_t=int;constexpr int ESP_OK=0;
struct httpd_req_t{void *user_ctx;void *handle;int socket;};
namespace web {struct EmbeddedAsset {const uint8_t *data;size_t size;const char *media_type;};}
int sent=0,closed=0,send_result=0,close_result=0;bool close_header=false;
int httpd_resp_send_500(httpd_req_t*){return -500;}
int httpd_resp_set_type(httpd_req_t*,const char*){return 0;}
int httpd_resp_set_hdr(httpd_req_t*,const char *name,const char *value){if(!strcmp(name,"Connection"))close_header=!strcmp(value,"close");return 0;}
int httpd_resp_send(httpd_req_t*,const char *data,ssize_t size){assert(size==3&&!memcmp(data,"abc",3));++sent;return send_result;}
int httpd_req_to_sockfd(httpd_req_t*r){return r->socket;}
int httpd_sess_trigger_close(void*,int fd){assert(fd==7);++closed;return close_result;}
class WiredNetworkService {public:static int assetHandler(httpd_req_t*) noexcept;};
'''
checks=r'''
int main(){web::EmbeddedAsset asset{(const uint8_t*)"abc",3,"text/plain"};httpd_req_t r{&asset,(void*)1,7};
assert(WiredNetworkService::assetHandler(&r)==0&&sent==1&&closed==1&&close_header);
send_result=-1;assert(WiredNetworkService::assetHandler(&r)==-1&&closed==1);
send_result=0;close_result=-2;assert(WiredNetworkService::assetHandler(&r)==-2&&closed==2);
r.user_ctx=nullptr;assert(WiredNetworkService::assetHandler(&r)==-500&&closed==2);
puts("PASS: exact asset response, connection close, send/close failure propagation, invalid asset");}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'test.cpp').write_text(fake+body+checks)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
