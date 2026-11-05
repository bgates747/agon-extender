// Compile-only target probe: no firmware composition, flash or execution.
#include "extender/network/messages/tcp_client.hpp"
#include "extender/network/messages/runtime.hpp"
#include "extender/network/messages/parallel_service.hpp"
using namespace agon::extender::network::messages;
extern "C" {
unsigned char net003_small_size[sizeof(Channel<256,2>)];
unsigned char net003_large_size[sizeof(Channel<1024,4>)];
unsigned char net004_mailbox_size[sizeof(Mailbox)];
}
bool net004_compile_probe(agon::extender::transport::ParallelControl&pipe,const uint8_t*p,uint8_t*out){
    ParallelService<Runtime> service(pipe,runtime);
    return service.request(p,out,true,0)&&service.retire();
}
void net003_compile_probe(Io& io) {
    Channel<256,2> channel;std::uint32_t token;
    if(channel.open(token)!=Result::Ok)return;
    const std::uint8_t input[]={1,2};std::uint8_t output[2];std::size_t n;
    channel.send(token,input,2);channel.feed(token,input,2);
    PumpCursor cursor;pump(channel,token,io,cursor,2,16);
    channel.receive(token,output,2,n);channel.close(token);
}
