// Actual P4 admission/retirement adapter and existing handover state machine.
// Completed flags are injected; this test does not operate GPIO or claim timing.
#include "extender/network/messages/parallel_service.hpp"
#include <cassert>
#include <cstdio>
using namespace agon::extender::network::messages;
using H=agon::extender::transport::P4ParallelHandover;
using Control=agon::extender::transport::ParallelControl;
static void recover(H&h){
    for(uint8_t f:{uint8_t(H::released|H::validHigh),uint8_t(H::validHigh),uint8_t(0),uint8_t(H::validHigh),uint8_t(H::validHigh|H::uartUp)})h.step(f);
    assert(h.phase()==H::uart);
}
static void complete(Control&p,unsigned now){
    auto&h=p.handover;
    for(uint8_t f:{uint8_t(H::quiet),uint8_t(H::released|H::validHigh),uint8_t(0),uint8_t(H::validHigh),
                   uint8_t(H::validHigh|H::clockHigh),uint8_t(H::validHigh|H::clockHigh|H::armed),
                   uint8_t(H::done),uint8_t(H::validHigh),uint8_t(0),uint8_t(H::validHigh),uint8_t(H::validHigh|H::uartUp)})h.step(f);
    assert(h.phase()==H::uart&&p.payloadReturned(now));
}
int main(){
    Control pipe;Mailbox endpoint;ParallelService<Mailbox> service(pipe,endpoint);
    uint8_t request[16]{'N','P',4,NETP_CONTROL_OPEN},reply[16]{};
    assert(service.request(request,reply,true,1)&&reply[13]==35); // No boot/session proof.
    recover(pipe.handover);
    uint8_t transaction[4]{1,2,3,4},offer[16]{},ack[16]{};t_parallelSession client{};
    assert(parallel_session_begin(&client,transaction,offer));
    assert(pipe.request(offer,1,0x12345678,ack));
    assert(parallel_session_accept(&client,ack,offer));
    assert(pipe.request(offer,1,0,ack));
    assert(parallel_session_accept(&client,ack,offer)==PARALLEL_SESSION_ACTIVE);
    assert(service.request(request,reply,false,1)&&reply[13]==35); // No Legacy owner.
    assert(service.request(request,reply,true,1)&&!reply[13]);
    auto token=agon_net_u32(reply+4);assert(token&&service.active());
    request[3]=NETP_CONTROL_SUBMIT;agon_net_put32(request+4,token);
    request[8]=1;request[10]=142;
    assert(service.request(request,reply,true,2)&&!reply[13]&&pipe.pending());
    uint8_t*payload;size_t capacity;assert(pipe.payloadBuffer(payload,capacity)&&capacity==142);
    std::memset(payload,0xa5,142);std::memcpy(payload,"NM\001",3);payload[3]=AGON_NET_SEND;
    agon_net_put32(payload+4,token);agon_net_put32(payload+8,0x12345678);payload[12]=128;payload[13]=0;
    assert(service.request(request,reply,true,2)&&reply[13]==31); // No second epoch.
    complete(pipe,3);assert(service.retire());
    uint8_t work[142];unsigned n;uint32_t generation;
    assert(endpoint.beginWork(work,n,generation)&&n==142);work[3]|=0x80;
    endpoint.completeWork(generation,work,142);assert(endpoint.takeUart(work)==0);
    request[3]=NETP_CONTROL_TAKE;request[8]=2;request[12]=1;request[10]=13;
    assert(service.request(request,reply,true,4)&&reply[13]==130&&reply[10]==142&&!pipe.pending());
    request[10]=142;assert(service.request(request,reply,true,4)&&!reply[13]&&pipe.pending());
    assert(pipe.payloadBuffer(payload,capacity)&&!std::memcmp(payload,work,142));
    assert(endpoint.takeUart(work)==0);complete(pipe,5);assert(service.retire());
    request[3]=NETP_CONTROL_RELEASE;request[8]=request[10]=request[12]=0;
    assert(service.request(request,reply,true,6)&&reply[13]==31&&service.active());
    assert(endpoint.takeCloseRequest());endpoint.completeClose();
    assert(service.request(request,reply,true,7)&&!reply[13]&&!service.active());
    assert(pipe.session.phase==PARALLEL_SESSION_IDLE);
    puts("Parallel service: actual metadata admission/handover/whole-record retirement, no fallback, undersized retention and positive close PASS");
}
