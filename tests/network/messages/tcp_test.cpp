#include "extender/network/messages/tcp_client.hpp"
#include <arpa/inet.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <thread>
using namespace agon::extender::network::messages;
int main() {
    // Only loopback, ephemeral port, finite process. This is NOT LAN/P4/EMOS proof.
    const int server=socket(AF_INET,SOCK_STREAM,0);assert(server>=0);
    sockaddr_in a{};a.sin_family=AF_INET;a.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    assert(bind(server,reinterpret_cast<sockaddr*>(&a),sizeof a)==0&&listen(server,1)==0);
    socklen_t length=sizeof a;assert(getsockname(server,reinterpret_cast<sockaddr*>(&a),&length)==0);
    assert(fcntl(server,F_SETFL,O_NONBLOCK)==0);
    TcpClient client;assert(client.start("bad-address",80)==Result::Invalid);
    assert(client.start("127.0.0.1",0)==Result::Invalid);
    assert(client.start("127.0.0.1",ntohs(a.sin_port))==Result::Ok);
    assert(client.start("127.0.0.1",ntohs(a.sin_port))==Result::Busy);
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(3);
    int peer=-1;
    while(peer<0||client.pollConnect()!=Connect::Connected) {
        if(peer<0)peer=accept(server,nullptr,nullptr);
        assert(std::chrono::steady_clock::now()<deadline);std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    assert(fcntl(peer,F_SETFL,O_NONBLOCK)==0);
    const std::uint8_t incoming[]={3,0,0,0,0,17,255};
    assert(::send(peer,incoming,sizeof incoming,0)==sizeof incoming);
    Channel<16,2> channel;std::uint32_t token;assert(channel.open(token)==Result::Ok);
    const std::uint8_t outgoing[]={10,13};assert(channel.send(token,outgoing,sizeof outgoing)==Result::Ok);
    PumpCursor cursor;std::uint8_t seen[6]{};std::size_t received=0;
    while(channel.pendingReceives()!=1||channel.pendingSends()!=0||received<sizeof seen) {
        assert(pump(channel,token,client,cursor,4,16).result==Result::Ok);
        if(received<sizeof seen){const auto n=recv(peer,seen+received,sizeof seen-received,0);if(n>0)received+=n;}
        assert(std::chrono::steady_clock::now()<deadline);std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    const std::uint8_t expected[]={2,0,0,0,10,13};assert(std::equal(std::begin(seen),std::end(seen),std::begin(expected)));
    std::uint8_t output[3];std::size_t n;assert(channel.receive(token,output,3,n)==Result::Ok&&n==3&&output[0]==0&&output[1]==17&&output[2]==255);
    ::close(peer);::close(server);
    while(channel.state()==State::Open){pump(channel,token,client,cursor,4,16);assert(std::chrono::steady_clock::now()<deadline);}
    assert(channel.fault()==Fault::PeerClosed);client.close();client.close();assert(client.state()==Connect::Closed);
    // The closed listener's still-unreused port gives a finite refusal case.
    assert(client.start("127.0.0.1",ntohs(a.sin_port))==Result::Ok||client.state()==Connect::Failed);
    while(client.pollConnect()==Connect::Connecting){assert(std::chrono::steady_clock::now()<deadline);}
    assert(client.state()==Connect::Failed&&client.error()!=0);client.close();
    std::puts("TCP loopback: connection, bidirectional frames, EOF and refusal passed");
}
