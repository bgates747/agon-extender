// NET-003 worker-owned endpoint; no UART, mutex, tasks or game code here.
#pragma once
#include "wire.h"
#include "tcp_client.hpp"
#include <cstdio>
namespace agon::extender::network::messages {
class Peer {
    Channel<AGON_NET_PAYLOAD,2> channel_;
    PumpCursor cursor_;
    std::uint32_t local_{},owner_{},touched_{},connectingAt_{};
    bool connecting_{};
    std::uint8_t fault_{};
    void retire() noexcept {if(local_)channel_.close(local_);local_=0;connecting_=false;}
public:
    static constexpr std::uint32_t ConnectDeadline=1500,IdleLease=2000;
    // Io/TCP lifecycle is injected so actual peer logic is testable without LAN.
    template<class Socket> void tick(Socket&socket,std::uint32_t now,bool link){
        if(!local_)return;
        if(!link){fault_=AGON_NET_IO_FAILED;socket.close();}
        if(std::uint32_t(now-touched_)>=IdleLease){fault_=AGON_NET_LEASE_EXPIRED;socket.close();}
        if(fault_)return;
        if(connecting_){
            const auto s=socket.pollConnect();
            if(s==Connect::Connected)connecting_=false;
            else if(s==Connect::Failed)fault_=AGON_NET_CONNECT_FAILED;
            else if(std::uint32_t(now-connectingAt_)>=ConnectDeadline)fault_=AGON_NET_CONNECT_TIMEOUT;
            if(fault_)socket.close();
        }
        if(!connecting_&&!fault_){
            const auto result=pump(channel_,local_,socket,cursor_,8,512);
            if(result.result==Result::Faulted){
                fault_=channel_.fault()==Fault::PeerClosed?AGON_NET_PEER_CLOSED:
                       channel_.fault()==Fault::InvalidLength?AGON_NET_BAD_FRAME:AGON_NET_IO_FAILED;
                socket.close();
            }
        }
    }
    template<class Socket> unsigned request(const std::uint8_t*p,unsigned n,std::uint8_t*out,
                                            Socket&socket,std::uint32_t now,bool link){
        if(n<AGON_NET_HEADER||n>AGON_NET_BODY||std::memcmp(p,"NM\001",3)||
           p[3]<1||p[3]>3||!agon_net_u32(p+4)||!agon_net_u32(p+8)||
           p[12]!=n-AGON_NET_HEADER||p[13]||
           (p[3]==1?p[12]!=6:p[3]==2?p[12]!=0:p[12]>AGON_NET_PAYLOAD))return 0;
        std::memcpy(out,p,AGON_NET_HEADER);out[3]|=0x80;out[12]=0;out[13]=AGON_NET_INVALID;
        auto finish=[&](std::uint8_t status){out[13]=status;return unsigned(AGON_NET_HEADER+out[12]);};
        if(p[3]==AGON_NET_CONNECT){
            // CONNECT is an explicit new incarnation, not automatic recovery.
            socket.close();retire();owner_=agon_net_u32(p+4);fault_=0;cursor_={};
            touched_=connectingAt_=now;
            const auto*ip=p+AGON_NET_HEADER;char host[16];
            std::snprintf(host,sizeof host,"%u.%u.%u.%u",ip[0],ip[1],ip[2],ip[3]);
            const auto port=std::uint16_t(ip[4]|(unsigned(ip[5])<<8));
            if(!link||!port||channel_.open(local_)!=Result::Ok||socket.start(host,port)!=Result::Ok){
                fault_=AGON_NET_CONNECT_FAILED;socket.close();
            }else connecting_=socket.state()!=Connect::Connected;
        }else if(agon_net_u32(p+4)!=owner_||!local_)return finish(AGON_NET_CLOSED);
        touched_=now;
        if(p[3]==AGON_NET_POLL){
            std::size_t got=0;
            if(channel_.receive(local_,out+AGON_NET_HEADER,AGON_NET_PAYLOAD,got)==Result::Ok){
                out[12]=std::uint8_t(got);return finish(AGON_NET_RECEIVED);
            }
        }
        if(fault_){out[12]=1;out[AGON_NET_HEADER]=fault_;return finish(AGON_NET_FAULT);}
        if(connecting_)return finish(AGON_NET_CONNECTING);
        if(p[3]==AGON_NET_SEND){
            const auto r=channel_.send(local_,p+AGON_NET_HEADER,p[12]);
            return finish(r==Result::Ok?AGON_NET_ACCEPTED:r==Result::Busy?AGON_NET_BUSY:AGON_NET_CLOSED);
        }
        return finish(AGON_NET_CONNECTED);
    }
    template<class Socket> void stop(Socket&socket){socket.close();retire();owner_=0;fault_=0;}
};
} // namespace agon::extender::network::messages
