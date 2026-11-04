// Compile-only target probe: no firmware composition, flash or execution.
#include "extender/network/messages/tcp_client.hpp"
using namespace agon::extender::network::messages;
extern "C" {
unsigned char net003_small_size[sizeof(Channel<256,2>)];
unsigned char net003_large_size[sizeof(Channel<1024,4>)];
}
void net003_compile_probe(Io& io) {
    Channel<256,2> channel;std::uint32_t token;
    if(channel.open(token)!=Result::Ok)return;
    const std::uint8_t input[]={1,2};std::uint8_t output[2];std::size_t n;
    channel.send(token,input,2);channel.feed(token,input,2);
    PumpCursor cursor;pump(channel,token,io,cursor,2,16);
    channel.receive(token,output,2,n);channel.close(token);
}
