#include "extender/input/controller/appliance.hpp"
#include <cassert>
using namespace agon::extender::controller;
static std::array<std::uint8_t,16> query(unsigned sequence,unsigned ack=0){
    std::array<std::uint8_t,16>p{};p[0]='C';p[1]='I';p[2]=CONTROLLER_CARRIER_VERSION;p[3]=1;
    controller_put32(p.data()+4,9);controller_put32(p.data()+8,ack);
    controller_put16(p.data()+12,sequence);return p;
}
int main(){
    Receiver core;core.begin(100);assert(core.open(100,1,{1,2},250,200,0)==200);
    Packet p{};p.instance=100;p.session=200;p.sequence=1;p.count=2;
    p.edges[0]={1,0,1};p.edges[1]={2,0,0};std::array<std::uint8_t,40>ack;
    assert(core.receive(p,{1,2},0,ack));assert(core.snapshot(0).queued==2);
    Appliance peer;auto q=query(1);assert(peer.request(q.data(),core,0));
    p.sequence=2;p.count=0;p.state.sticks[0]=32767;assert(core.receive(p,{1,2},10,ack));
    std::uint8_t response[CONTROLLER_RESULT_SIZE];assert(peer.take(response,core,10));
    assert(controller_u16(response+36)==32767&&controller_u32(response+28)==2);
    assert(response[11]==2&&!std::memcmp(response,CONTROLLER_RESULT_MAGIC,4));
    // A reply being enqueued does not consume transitions. Consumption is an
    // explicit later acknowledgement after EMOS copied them to its caller.
    assert(core.snapshot(10).queued==2);q=query(2,2);peer.request(q.data(),core,11);
    assert(peer.take(response,core,11)&&response[11]==0&&core.snapshot(11).queued==0);
    q=query(3);peer.request(q.data(),core,12);assert(peer.take(response,core,260));
    assert(!response[10]&&!response[11]&&!controller_u16(response+36));
    assert(core.open(100,2,{1,2},250,300,260)==200);
    p.session=300;p.sequence=1;p.count=1;p.edges[0]={1,0,1};
    assert(core.receive(p,{1,2},261,ack));q=query(4,2);peer.request(q.data(),core,262);
    assert(peer.take(response,core,262)&&response[11]==1&&core.snapshot(262).queued==1);
    q=query(5,99);peer.request(q.data(),core,263);assert(!peer.take(response,core,263));
    q=query(6);q[14]=1;peer.request(q.data(),core,264);assert(!peer.take(response,core,264));
    q=query(7);q[2]=1;assert(peer.request(q.data(),core,265));
    assert(!peer.take(response,core,265)); // Old carrier stays in CI, never EX.
}
