#include "extender/network/messages/mailbox.hpp"
#include <array>
#include <cassert>
#include <cstdio>
using namespace agon::extender::network::messages;
using R=MailboxResult;
using Packet=std::array<uint8_t,AGON_NET_BODY>;
static Packet packet(uint32_t token,unsigned size,uint8_t op=AGON_NET_SEND){
    Packet p{};std::memcpy(p.data(),"NM\001",3);p[3]=op;
    agon_net_put32(p.data()+4,token);agon_net_put32(p.data()+8,1);
    p[12]=size-AGON_NET_HEADER;
    for(unsigned i=AGON_NET_HEADER;i<size;++i)p[i]=uint8_t(i*37);
    return p;
}
static void work(Mailbox&m,Packet&reply,unsigned expected){
    Packet command{};unsigned n=0;uint32_t generation=0;
    assert(m.beginWork(command.data(),n,generation)&&n==expected);
    reply=command;reply[3]|=0x80;reply[13]=AGON_NET_ACCEPTED;
    m.completeWork(generation,reply.data(),n);
}
int main(){
    for(unsigned payload: {0U,1U,127U,128U}){
        Mailbox m;uint32_t token=0;assert(m.openParallel(token)==R::ok&&token);
        Packet p=packet(token,AGON_NET_HEADER+payload),reply{},uart{};
        assert(m.submitParallel(token,p.data(),AGON_NET_HEADER+payload)==R::ok);
        assert(m.submitParallel(token,p.data(),AGON_NET_HEADER+payload)==R::busy);
        assert(!m.submitUart(p.data(),AGON_NET_HEADER+payload));
        const uint8_t*view=nullptr;unsigned needed=99;
        assert(m.offerParallel(token,AGON_NET_BODY,view,needed)==R::busy&&!view&&!needed);
        work(m,reply,AGON_NET_HEADER+payload);
        assert(m.takeUart(uart.data())==0); // No payload fallback, even after worker reply.
        assert(m.offerParallel(token,AGON_NET_HEADER+payload-1,view,needed)==R::tooSmall);
        assert(!view&&needed==AGON_NET_HEADER+payload);
        assert(m.offerParallel(token,AGON_NET_BODY,view,needed)==R::ok);
        assert(!std::memcmp(view,reply.data(),needed));
        assert(m.releaseParallel(token)==R::busy);
        assert(m.finishParallel(token,true,false)==R::busy);
        assert(!std::memcmp(view,reply.data(),needed)); // Still immutable during cleanup.
        assert(m.finishParallel(token+1,true,true)==R::stale);
        assert(m.finishParallel(token,true,true)==R::ok);
        assert(m.offerParallel(token,AGON_NET_BODY,view,needed)==R::empty);
        assert(m.releaseParallel(token)==R::busy&&m.takeCloseRequest());
        assert(m.releaseParallel(token)==R::busy); // Requested != actual socket close.
        m.completeClose();assert(m.releaseParallel(token)==R::ok);
        uint32_t next=0;assert(m.openParallel(next)==R::ok&&next>token);
        assert(m.submitParallel(token,p.data(),AGON_NET_HEADER+payload)==R::stale);
    }
    {
        Mailbox m;uint32_t token;assert(m.openParallel(token)==R::ok);
        Packet p=packet(token,142),reply{};assert(m.submitParallel(token,p.data(),142)==R::ok);
        work(m,reply,142);const uint8_t*view;unsigned n;
        assert(m.offerParallel(token,142,view,n)==R::ok);
        m.workerStopped();assert(!std::memcmp(view,reply.data(),142));
        assert(m.releaseParallel(token)==R::busy);
        assert(m.finishParallel(token,false,false)==R::busy);
        assert(m.finishParallel(token,false,true)==R::fault);
        assert(m.offerParallel(token,142,view,n)==R::fault); // Never replay uncertain reply.
        m.completeStoppedClose();assert(m.releaseParallel(token)==R::ok);
    }
    {
        Mailbox m;uint32_t token;assert(m.openParallel(token)==R::ok);
        Packet p=packet(token,14),reply{};unsigned n;uint32_t generation;
        assert(m.submitParallel(token,p.data(),14)==R::ok);
        assert(m.beginWork(reply.data(),n,generation));
        assert(m.releaseParallel(token)==R::busy);
        reply[3]|=0x80;m.completeWork(generation,reply.data(),14); // Late old completion.
        m.completeClose();assert(m.releaseParallel(token)==R::ok);
        assert(m.takeUart(reply.data())==0);
    }
    {
        Mailbox m;uint32_t token;assert(m.openParallel(token)==R::ok);
        Packet p=packet(token,14),reply{};unsigned n;uint32_t generation;
        assert(m.submitParallel(token,p.data(),13)==R::invalid);
        assert(m.submitParallel(token,p.data(),143)==R::invalid);
        assert(m.submitParallel(token,p.data(),14)==R::ok);
        assert(m.beginWork(reply.data(),n,generation));
        reply[3]|=0x80;reply[8]^=1;m.completeWork(generation,reply.data(),14);
        const uint8_t*view;assert(m.offerParallel(token,142,view,n)==R::fault);
    }
    {
        Mailbox m(UINT32_MAX);uint32_t token=99;
        assert(m.openParallel(token)==R::exhausted&&!token);
        Packet p=packet(1,14,AGON_NET_CONNECT),reply{};unsigned n;uint32_t generation;
        assert(m.submitUart(p.data(),14));assert(m.beginWork(reply.data(),n,generation));
        p[8]=2;assert(m.submitUart(p.data(),14));
        reply[3]|=0x80;m.completeWork(generation,reply.data(),14);
        assert(m.takeUart(reply.data())==0); // Existing UART CONNECT replacement still fenced.
        work(m,reply,14);assert(m.takeUart(reply.data())==14);
    }
    std::puts("Parallel mailbox: boundaries, ownership, no UART fallback, physical release, close, stale/fault and legacy replacement PASS");
}
