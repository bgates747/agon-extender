// Actual P4 receiver + actual EMOS C service + actual Agon application client.
// Only the physical UART, clock, IRQ lock and gateway entry are fake.
#include <sys/mman.h>
#include <new>
#include <cstdint>
#include <cstring>
#include <cassert>
using uint24_t=std::uintptr_t;
#include "../fixtures/controller/live.hpp"
#include "extender/input/controller/appliance.hpp"
using namespace agon::extender::controller;
static Receiver core;
static Appliance peer;
static std::uint32_t now_ms=0;
static std::uint8_t irq=1;
static unsigned closes=0;
extern "C" {
volatile std::uint8_t emos_key_source=2,emos_key_faulted=0,uart1_keyboard_owned=1;
std::uint32_t emos_controller_gateway(void*);
void emos_controller_packet(const std::uint8_t*,std::uint8_t);
void emos_controller_tick();
std::uint8_t emos_keyboard_lock(){auto old=irq;irq=0;return old;}
void emos_keyboard_unlock(std::uint8_t value){irq=value;}
std::uint8_t emos_keyboard_clock(){return std::uint8_t(now_ms*120/1000);}
std::uint8_t emos_application_context(){return 1;}
std::uint8_t emos_get_mode(){return 0;}
std::uint32_t emos_read24(const std::uint8_t*p){return p[0]|(std::uint32_t(p[1])<<8)|(std::uint32_t(p[2])<<16);}
std::uint8_t emos_keyboard_send(const std::uint8_t*p,std::uint16_t length){
    assert(irq&&length==19&&p[0]==23&&p[1]==0&&p[2]==0xf7);
    if(p[6]==2)++closes;
    assert(peer.request(p+3,core,now_ms));return 0;
}
uint24_t controller_gateway_available(){return 1;}
uint24_t controller_gateway_call(std::uint8_t*r){
    assert(r[0]==66&&r[2]==1&&r[4]==3&&r[5]==10&&r[6]==2);
    assert(!std::memcmp(r+25,"ext",3)&&!std::memcmp(r+41,"controller",10));
    return emos_controller_gateway(r);
}
}
static void deliver(){
    std::uint8_t p[CONTROLLER_RESULT_SIZE];assert(peer.take(p,core,now_ms));
    irq=0;emos_controller_packet(p,sizeof(p));irq=1;
}
int main(){
    void*ram=mmap(reinterpret_cast<void*>(0x40000),0x10000,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(ram==reinterpret_cast<void*>(0x40000));
    auto*client=new(ram)controller_view::Live;
    controller_view::Sample sample{};
    core.begin(100);assert(core.open(100,1,{1,2},250,200,0)==200);
    Packet state{};state.instance=100;state.session=200;state.sequence=1;
    state.state.sticks[0]=32767;state.state.triggers[0]=255;state.count=2;
    state.edges[0]={1,0,1};state.edges[1]={2,0,0};std::array<std::uint8_t,40>ack;
    assert(core.receive(state,{1,2},0,ack));
    assert(client->open()&&client->update(sample));
    deliver();assert(client->update(sample));
    assert(sample.valid&&sample.stick[0]==32767&&sample.trigger[0]==255);
    assert(sample.presses[0]==1&&sample.held==0&&core.snapshot(0).queued==0);
    assert(client->update(sample)&&sample.presses[0]==1); // Cached read: no duplicate tap.
    for(const unsigned time:{60u,120u,180u,240u,260u}){
        now_ms=time;deliver();assert(client->update(sample));
    }
    assert(!sample.valid&&!sample.connected&&!sample.held);
    assert(core.open(100,2,{1,2},250,300,261)==200);
    state.session=300;state.sequence=1;state.count=1;state.edges[0]={1,5,1};
    now_ms=261;assert(core.receive(state,{1,2},now_ms,ack));
    deliver();assert(client->update(sample));
    assert(sample.valid&&sample.presses[0]==0&&sample.presses[5]==1);
    assert(core.snapshot(now_ms).queued==0);
    // Exercise the actual client's healthy lease renewal without advancing
    // the fake clock. This is a sequence-boundary check, not a latency run.
    for(unsigned i=0;i<65004;++i){
        assert(client->update(sample));
        std::uint8_t body[CONTROLLER_RESULT_SIZE];
        if(peer.take(body,core,now_ms)){irq=0;emos_controller_packet(body,sizeof(body));irq=1;}
    }
    assert(closes==1&&sample.presses[5]==1&&sample.presses[0]==0);
    assert(client->close());
    assert(closes==2);
    // Preserve the actual failed operation/status for the on-screen diagnosis.
    assert(client->open()&&client->update(sample));
    now_ms+=300;emos_controller_tick();
    assert(!client->update(sample));
    assert(client->error==35&&client->error_operation==1);
    assert(client->close());
}
