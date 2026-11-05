// Actual P4 peer + EMOS C endpoint + public C codec; physical transport is fake.
#include <sys/mman.h>
#include <new>
#include <cassert>
#include <vector>
#include <cstdio>
#include "extender/network/messages/peer.hpp"
using namespace agon::extender::network::messages;
extern "C" uint32_t emos_net_gateway(void*);
extern "C" void emos_net_packet(const uint8_t*,uint8_t);
static uint32_t now_ms;
#define AGON_NET_CLOCK() uint8_t(now_ms*120/1000)
static uint8_t gateway(uint8_t*p){return uint8_t(emos_net_gateway(p));}
#define AGON_NET_CALL(request) gateway(request)
#include <agon/net.h>
struct Socket:Io {
    Connect state_=Connect::Closed;
    std::vector<uint8_t> incoming,outgoing;
    Result start(const char*,uint16_t){state_=Connect::Connected;return Result::Ok;}
    void close(){state_=Connect::Closed;}
    Connect state(){return state_;} Connect pollConnect(){return state_;}
    IoResult read(uint8_t*p,size_t n) noexcept override{
        if(incoming.empty())return {IoState::WouldBlock,0};
        n=std::min(n,incoming.size());memcpy(p,incoming.data(),n);incoming.erase(incoming.begin(),incoming.begin()+n);
        return {IoState::Progress,n};
    }
    IoResult write(const uint8_t*p,size_t n) noexcept override{outgoing.insert(outgoing.end(),p,p+n);return {IoState::Progress,n};}
} socket;
static Peer peer;static uint8_t irq=1,pending[AGON_NET_BODY];static unsigned pendingSize;
static agon_net_client*active;
static bool immediate;
extern "C" {
uint32_t user_kbvector=0x123456;
void emos_reply_callback(const uint8_t*p){assert(!irq);agon_net_receive(active,p);}
volatile uint8_t emos_key_source=2,emos_key_faulted=0,uart1_keyboard_owned=1;
uint8_t emos_keyboard_lock(){auto old=irq;irq=0;return old;}
void emos_keyboard_unlock(uint8_t v){irq=v;}
uint8_t emos_keyboard_clock(){return uint8_t(now_ms*120/1000);}
uint8_t emos_application_context(){return 1;}
uint8_t emos_get_mode(){return 0;}
uint32_t emos_read24(const uint8_t*p){return p[0]|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16);}
uint8_t emos_keyboard_send(const uint8_t*p,uint16_t n){
    assert(irq&&n==unsigned(4+p[3])&&p[0]==23&&p[1]==0&&p[2]==AGON_NET_VDU);
    pendingSize=peer.request(p+4,p[3],pending,socket,now_ms,true);assert(pendingSize);
    if(immediate){irq=0;emos_net_packet(pending,pendingSize);irq=1;pendingSize=0;}return 0;
}
}
static void deliver(){assert(pendingSize);irq=0;emos_net_packet(pending,pendingSize);irq=1;pendingSize=0;}
static void exchange(agon_net_client*c,uint8_t kind,const void*p=nullptr,uint8_t n=0){
    assert(agon_net_submit(c,kind,p,n)==0);assert(agon_net_take(c)==31);deliver();assert(agon_net_take(c)==0);
}
int main(){
    void*ram=mmap((void*)0x40000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(ram==(void*)0x40000);auto*c=new(ram)agon_net_client{};
    active=c;assert(agon_net_begin(c)==0);assert(agon_net_previous(c)==0x123456);uint8_t address[]={127,0,0,1,0xf6,0x1d};
    exchange(c,AGON_NET_CONNECT,address,6);assert(agon_net_status(c)==AGON_NET_CONNECTED);
    uint8_t bytes[128];for(unsigned i=0;i<128;++i)bytes[i]=i;
    exchange(c,AGON_NET_SEND,bytes,128);assert(agon_net_status(c)==AGON_NET_ACCEPTED);
    exchange(c,AGON_NET_SEND,bytes,128);assert(agon_net_status(c)==AGON_NET_ACCEPTED);
    exchange(c,AGON_NET_SEND,bytes,128);assert(agon_net_status(c)==AGON_NET_BUSY);
    peer.tick(socket,now_ms,true);assert(socket.outgoing.size()==264);
    socket.incoming={128,0,0,0};socket.incoming.insert(socket.incoming.end(),bytes,bytes+128);
    peer.tick(socket,now_ms,true);exchange(c,AGON_NET_POLL);
    assert(agon_net_status(c)==AGON_NET_RECEIVED&&agon_net_size(c)==128&&!memcmp(agon_net_data(c),bytes,128));
    socket.incoming={0,0,0,0};peer.tick(socket,now_ms,true);exchange(c,AGON_NET_POLL);
    assert(agon_net_status(c)==AGON_NET_RECEIVED&&agon_net_size(c)==0);
    assert(agon_net_submit(c,AGON_NET_POLL,nullptr,0)==0);pending[8]^=1;deliver();assert(agon_net_take(c)==31);
    now_ms=251;assert(agon_net_take(c)==35);assert(agon_net_release(c)==0);
    assert(agon_net_begin(c)==0);exchange(c,AGON_NET_CONNECT,address,6);
    c->query=65535;exchange(c,AGON_NET_POLL);assert(c->query==65536);
    irq=0;assert(agon_net_submit(c,AGON_NET_POLL,nullptr,0)==31);irq=1;
    exchange(c,AGON_NET_POLL);now_ms+=2001;peer.tick(socket,now_ms,true);exchange(c,AGON_NET_POLL);
    assert(agon_net_status(c)==AGON_NET_FAULT&&agon_net_data(c)[0]==AGON_NET_LEASE_EXPIRED);
    assert(agon_net_release(c)==0);assert(emos_net_gateway((void*)1)==32);
    assert(agon_net_begin(c)==0);immediate=true;
    assert(agon_net_submit(c,AGON_NET_CONNECT,address,6)==0);assert(agon_net_take(c)==0);
    immediate=false;assert(agon_net_release(c)==0);
    auto*unsafe=(agon_net_client*)((uint8_t*)ram+0x10000);*unsafe={};
    assert(agon_net_begin(unsafe)==0);unsafe->query=UINT32_MAX;
    assert(agon_net_submit(unsafe,AGON_NET_POLL,nullptr,0)==AGON_NET_QUERY_EXHAUSTED);
    assert(agon_net_release(unsafe)==0);peer.stop(socket);
    puts("actual peer/EMOS/public C pipeline passed");
}
