// Private foreground appliance peer. Caller holds the receiver mutex. Only
// EMOS on the wired console requests state; the network worker never writes UART.
#pragma once
#include "receiver.hpp"
#include "appliance_wire.h"
#include <cstring>
namespace agon::extender::controller {
class Appliance {
    std::array<std::uint8_t,16> request_{};
    bool ready_=false;
    std::uint32_t owner_{};
    std::uint64_t reply_session_{};
 public:
    bool request(const std::uint8_t*p,Receiver&core,std::uint64_t now){
        if(p[0]!='C'||p[1]!='I')return false;
        if(p[2]!=CONTROLLER_CARRIER_VERSION||(p[3]!=1&&p[3]!=2)||
           !controller_u32(p+4)||!controller_u16(p+12)||p[14]||p[15])return true;
        const auto token=controller_u32(p+4);
        if(p[3]==2){if(token==owner_)ready_=false;return true;}
        const auto s=core.snapshot(now);
        if(token==owner_&&reply_session_==s.session&&s.valid) {
            if(!core.retire(controller_u32(p+8)))return true;
        }
        owner_=token;std::memcpy(request_.data(),p,16);ready_=true;return true;
    }
    bool take(std::uint8_t*out,Receiver&core,std::uint64_t now){
        if(!ready_)return false;
        // Snapshot when the console owner can actually enqueue the reply;
        // network/keyboard backpressure must not make an old reply look fresh.
        const auto s=core.snapshot(now);reply_session_=s.session;
        std::memset(out,0,CONTROLLER_RESULT_SIZE);std::memcpy(out,CONTROLLER_RESULT_MAGIC,4);
        controller_put32(out+4,owner_);controller_put16(out+8,controller_u16(request_.data()+12));
        out[10]=(s.active?1:0)|(s.valid?2:0);
        put64(out+12,s.instance);put64(out+20,s.session);put32(out+28,s.sequence);
        const auto age=s.valid?now-s.last_state:0;
        put16(out+32,std::uint16_t(age>65535?65535:age));put16(out+34,s.state.held);
        for(unsigned i=0;i<4;++i)put16(out+36+i*2,std::uint16_t(s.state.sticks[i]));
        out[44]=s.state.triggers[0];out[45]=s.state.triggers[1];
        for(unsigned i=0;i<CONTROLLER_BATCH;++i){
            Edge edge;if(!core.peek(i,edge))break;
            auto*e=out+48+i*6;put32(e,edge.sequence);e[4]=edge.control;e[5]=edge.down;++out[11];
        }
        ready_=false;return true;
    }
};
bool applianceRequest(const std::uint8_t*p);
bool applianceTake(std::uint8_t*out);
}
