// Execute the actual C caller, EMOS endpoint, P4 mailbox and Peer together.
// Only physical pad/clock transfer and TCP IO are injected; no hardware claim.
#include <sys/mman.h>
#include <new>
#include <vector>
#include <cassert>
#include <cstdio>
#include "extender/network/messages/mailbox.hpp"
#include "extender/network/messages/peer.hpp"
using namespace agon::extender::network::messages;
extern "C" uint32_t emos_netp_gateway(void*);
static uint8_t gateway(uint8_t*p){return uint8_t(emos_netp_gateway(p));}
#define AGON_NET_CALL(request) gateway(request)
#include <agon/net_parallel.h>
static Mailbox mailbox;
static Peer peer;
static uint8_t mode=0;
static uint32_t now;
static bool physicalFail=false;
extern "C" { uint32_t emos_netp_token; }
#define carrierToken emos_netp_token
struct Socket:Io {
    Connect status=Connect::Closed;
    std::vector<uint8_t> in,out;
    Result start(const char*,uint16_t){status=Connect::Connected;return Result::Ok;}
    void close(){status=Connect::Closed;}
    Connect state(){return status;}Connect pollConnect(){return status;}
    IoResult read(uint8_t*p,size_t n)noexcept override{
        if(in.empty())return {IoState::WouldBlock,0};
        n=std::min(n,in.size());memcpy(p,in.data(),n);in.erase(in.begin(),in.begin()+n);return {IoState::Progress,n};
    }
    IoResult write(const uint8_t*p,size_t n)noexcept override{out.insert(out.end(),p,p+n);return {IoState::Progress,n};}
} socket_;
static uint8_t status(MailboxResult r){
    switch(r){case MailboxResult::ok:return 0;case MailboxResult::busy:return 31;
    case MailboxResult::empty:return 131;case MailboxResult::tooSmall:return 130;
    case MailboxResult::invalid:return 19;case MailboxResult::stale:return 35;
    default:return 132;}
}
static void worker(){
    if(mailbox.takeCloseRequest()){peer.stop(socket_);mailbox.completeClose();}
    uint8_t input[142],output[142];unsigned n;uint32_t gen;
    if(mailbox.beginWork(input,n,gen)){
        auto got=peer.request(input,n,output,socket_,now,true);
        mailbox.completeWork(gen,output,got);
    }
    peer.tick(socket_,now,true);
}
extern "C" {
volatile uint8_t emosVduBackend=0;
uint8_t emos_application_context(){return 1;}
uint8_t emos_get_mode(){return mode;}
uint32_t emos_read24(const uint8_t*p){return p[0]|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16);}
uint8_t emos_netp_link_open(){return status(mailbox.openParallel(emos_netp_token));}
uint8_t emos_netp_link_submit(const uint8_t*p,uint16_t n){return status(mailbox.submitParallel(carrierToken,p,n));}
uint8_t emos_netp_link_take(uint8_t*out,uint16_t cap,uint16_t*length){
    auto t=carrierToken;
    const uint8_t*p;unsigned n;auto r=mailbox.offerParallel(t,cap,p,n);*length=n;
    if(r!=MailboxResult::ok)return status(r);
    if(!physicalFail)memcpy(out,p,n);
    return status(mailbox.finishParallel(t,!physicalFail,true));
}
uint8_t emos_netp_link_release(){auto r=mailbox.releaseParallel(carrierToken);if(r==MailboxResult::ok)emos_netp_token=0;return status(r);}
}
static void request(agon_netp_client*c,uint8_t*buffer,uint8_t op,const uint8_t*data,unsigned size){
    memcpy(buffer,"NM\001",3);buffer[3]=op;agon_net_put32(buffer+4,c->token);
    agon_net_put32(buffer+8,c->query+1);buffer[12]=size;buffer[13]=0;
    if(size)memcpy(buffer+14,data,size);
}
int main(){
    void*ram=mmap((void*)0x40000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(ram==(void*)0x40000);auto*c=new(ram)agon_netp_client{};
    auto*packet=(uint8_t*)ram+0x1000;auto*out=packet+256;unsigned n;
    assert(agon_netp_open(c)==0&&c->token);
    assert(agon_netp_open(c)==31);
    assert(agon_netp_take(c,out,142,&n)==131);
    uint8_t ip[]={127,0,0,1,0xf6,0x1d};request(c,packet,1,ip,6);
    assert(agon_netp_submit(c,packet,20)==0);
    assert(agon_netp_take(c,out,142,&n)==31);
    worker();assert(agon_netp_take(c,out,13,&n)==130&&n==14&&c->pending);
    assert(agon_netp_take(c,out,142,&n)==0&&n==14&&out[13]==AGON_NET_CONNECTED);
    for(unsigned size:{0U,1U,127U,128U}){
        uint8_t bytes[128];for(unsigned i=0;i<size;++i)bytes[i]=uint8_t(i*53);
        request(c,packet,3,bytes,size);assert(agon_netp_submit(c,packet,14+size)==0);
        assert(agon_netp_submit(c,packet,14+size)==31);
        worker();assert(agon_netp_take(c,out,142,&n)==0&&out[13]==AGON_NET_ACCEPTED);
        worker();assert(socket_.out.size()>=size+4);
        // Remote binary reply is assembled by the real stream pump.
        socket_.in={uint8_t(size),0,0,0};socket_.in.insert(socket_.in.end(),bytes,bytes+size);
        worker();request(c,packet,2,nullptr,0);assert(agon_netp_submit(c,packet,14)==0);
        worker();assert(agon_netp_take(c,out,142,&n)==0&&n==size+14&&out[13]==AGON_NET_RECEIVED);
        assert(!memcmp(out+14,bytes,size));
    }
    request(c,packet,2,nullptr,0);packet[8]=uint8_t(c->query);
    assert(agon_netp_submit(c,packet,14)==19); // No wrapping or duplicate query.
    request(c,packet,2,nullptr,0);assert(agon_netp_submit(c,packet,14)==0);
    worker();physicalFail=true;assert(agon_netp_take(c,out,142,&n)==132&&c->pending);
    assert(agon_netp_take(c,out,142,&n)==132);physicalFail=false;
    mode=1; // RELEASE remains available for cleanup after ordinary route loss.
    assert(agon_netp_release(c)==31&&c->token);worker();
    assert(agon_netp_release(c)==0&&!c->token);
    assert(agon_netp_open(c)==35);mode=0;emosVduBackend=1;
    assert(agon_netp_open(c)==35);emosVduBackend=0;
    assert(agon_netp_open(c)==0);c->query=65535;
    request(c,packet,1,ip,6);assert(agon_netp_submit(c,packet,20)==0&&c->query==65536);
    worker();assert(agon_netp_take(c,out,142,&n)==0);
    assert(agon_netp_release(c)==31);worker();assert(agon_netp_release(c)==0);
    assert(emos_netp_gateway((void*)1)==32);
    munmap(ram,0x20000);
    puts("Actual netp C caller/EMOS/P4 mailbox/Peer pipeline: binary limits, busy, required-size, fault, close, route and32-bit query PASS");
}
