// NET-004 sole console-owner adapter to the existing bounded block coordinator.
// OPEN does not activate a display mode. The caller must already hold the
// Legacy service admission and physically recovered UART boundary. Existing
// EX format4 capability3 names the private block engine (also used by Legacy
// diagnostic probes), not permission to commit an ExExt display route.
#pragma once
#include "mailbox.hpp"
#include "parallel_control.h"
#include "extender/transport/parallel_control.hpp"
#include <array>

namespace agon::extender::network::messages {
template<class Endpoint> class ParallelService final {
    transport::ParallelControl& pipe_;
    Endpoint& endpoint_;
    std::array<uint8_t,AGON_NET_BODY> payload_{};
    uint32_t token_{};
    bool waiting_{},reverse_{},replyBorrowed_{};
    static uint8_t code(MailboxResult r){
        switch(r){case MailboxResult::ok:return 0;case MailboxResult::busy:return 31;
        case MailboxResult::empty:return 131;case MailboxResult::tooSmall:return 130;
        case MailboxResult::invalid:return 19;case MailboxResult::stale:return 35;
        default:return 132;}
    }
public:
    ParallelService(transport::ParallelControl&p,Endpoint&e):pipe_(p),endpoint_(e){}
    bool active()const{return token_!=0;}
    bool ownsControl(const uint8_t*p)const{return p[0]=='N'&&p[1]=='P'&&p[2]==NETP_CONTROL_VERSION;}
    // Return a complete control response even on normal refusal. No ignored
    // BUSY request may become a sender timeout or silently consume a record.
    bool request(const uint8_t*p,uint8_t*reply,bool legacy,uint32_t now){
        if(!ownsControl(p))return false;
        std::memcpy(reply,p,16);reply[3]|=0x80;reply[13]=19;reply[14]=reply[15]=0;
        const auto token=agon_net_u32(p+4);
        const auto length=unsigned(p[10])|(unsigned(p[11])<<8);
        const auto seq=unsigned(p[8])|(unsigned(p[9])<<8);
        if(p[13]||p[3]<NETP_CONTROL_OPEN||p[3]>NETP_CONTROL_RELEASE)return true;
        if(p[3]==NETP_CONTROL_OPEN){
            if(token||seq||length||p[12])return true;
            if(!legacy||!pipe_.uartTransitionAllowed()||pipe_.session.phase!=PARALLEL_SESSION_ACTIVE){reply[13]=35;return true;}
            if(token_){reply[13]=31;return true;}
            if(!pipe_.provide(payload_.data(),payload_.size())){reply[13]=31;return true;}
            reply[13]=code(endpoint_.openParallel(token_));
            if(!reply[13])agon_net_put32(reply+4,token_);
            return true;
        }
        if(!token_||token!=token_){reply[13]=35;return true;}
        if(waiting_||!pipe_.uartTransitionAllowed()){reply[13]=31;return true;}
        if(p[3]==NETP_CONTROL_RELEASE){
            if(seq||length||p[12])return true;
            reply[13]=code(endpoint_.releaseParallel(token_));
            if(!reply[13]){token_=0;pipe_.revokeUartCapability();}
            return true;
        }
        if(!legacy){reply[13]=35;return true;}
        const bool reverse=p[3]==NETP_CONTROL_TAKE;
        if(p[12]!=(reverse?1:0)||!length||length>AGON_NET_BODY||(!reverse&&length<AGON_NET_HEADER))return true;
        const unsigned next=(unsigned(pipe_.session.bytes[4])|(unsigned(pipe_.session.bytes[5])<<8))+1;
        if(!next||next>65535||seq!=next){reply[13]=35;return true;}
        unsigned actual=length;const uint8_t*source=nullptr;
        auto status=reverse?endpoint_.offerParallel(token_,length,source,actual):endpoint_.canSubmitParallel(token_);
        reply[13]=code(status);reply[10]=uint8_t(actual);reply[11]=uint8_t(actual>>8);
        if(status!=MailboxResult::ok)return true;
        replyBorrowed_=reverse;
        if(reverse)std::memcpy(payload_.data(),source,actual);
        uint8_t offer[16]{},ack[16]{};
        std::memcpy(offer,"EX",2);offer[2]=PARALLEL_WIRE_VERSION;offer[3]=PARALLEL_OFFER;
        std::memcpy(offer+4,pipe_.session.bytes,4);offer[8]=uint8_t(seq);offer[9]=uint8_t(seq>>8);
        offer[10]=uint8_t(actual);offer[11]=uint8_t(actual>>8);offer[12]=reverse;
        if(!pipe_.request(offer,now,0,ack)){
            if(replyBorrowed_)endpoint_.finishParallel(token_,false,true);
            replyBorrowed_=false;reply[13]=132;return true;
        }
        waiting_=true;reverse_=reverse;return true;
    }
    bool retire(){
        if(!waiting_)return true;
        uint8_t*p=nullptr,direction=0;size_t length=0;
        if(!pipe_.takeCompleted(p,length,direction))return !pipe_.handover.failed();
        if(p!=payload_.data()||length<AGON_NET_HEADER||length>payload_.size()||direction!=reverse_)return false;
        waiting_=false;
        const auto r=reverse_?endpoint_.finishParallel(token_,true,true):endpoint_.submitParallel(token_,p,unsigned(length));
        replyBorrowed_=false;return r==MailboxResult::ok;
    }
    // Call only after the physical coordinator actually stops DMA/releases pads.
    // A timeout alone is insufficient. The session is terminal, never replayed.
    void physicalStopped(){
        if(replyBorrowed_)endpoint_.finishParallel(token_,false,true);
        waiting_=replyBorrowed_=false;
    }
};
}
