#include <cassert>
#include "vdp/video/extender/network/screen_text.hpp"
struct Font {int width=8,height=8;};
struct Context {Font f;Font*screenTextFont(){return &f;} unsigned char getScreenChar(unsigned x,unsigned y){return x==0&&y==0?'X':' ';}};
int main(){
 using namespace agon::extender::screen_text;
 Context c;httpd_req_t r;handle(&r);assert(r.status=="202 Accepted");
 while(state!=3)poll(&c,640,480);
 r={};handle(&r);assert(r.status=="200 OK");assert(r.body.find("\nX ")!=std::string::npos);assert(state==0);
 r={};handle(&r);poll(&c,640,480);poll(&c,320,240);r={};handle(&r);assert(r.status=="409 Conflict");
 r={};handle(&r);poll(&c,4096,4096);r={};handle(&r);assert(r.status=="409 Conflict");
 r={};handle(&r);while(state!=3)poll(&c,2040,256);assert(length<sizeof(text));r={};handle(&r);assert(r.status=="200 OK");
}
