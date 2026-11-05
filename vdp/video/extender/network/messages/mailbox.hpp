// NET-004 console/worker mailboxes. Caller holds Runtime's short mutex.
// Parallel replies are borrowed until the physical owner proves pad release;
// neither a DMA offer nor a failed transfer is permission to emit them on UART.
// No socket, driver or application callback runs while this object is locked.
#pragma once
#include "wire.h"
#include <cstring>
#include <cstdint>

namespace agon::extender::network::messages {
enum class MailboxResult { ok, busy, empty, tooSmall, stale, invalid, fault, exhausted };
class Mailbox final {
    enum class Carrier { uart, parallel, closing, closed };
    Carrier carrier_{Carrier::uart};
    uint8_t command_[AGON_NET_BODY]{}, reply_[AGON_NET_BODY]{};
    unsigned commandLength_{}, replyLength_{};
    uint32_t generation_{}, sequence_{}, token_{};
    bool processing_{}, pending_{}, borrowed_{}, fault_{}, closeRequested_{};
    bool owns(uint32_t t) const { return t && t==token_; }
    static bool valid(const uint8_t*p,unsigned n) {
        return p && n>=AGON_NET_HEADER && n<=AGON_NET_BODY &&
               !std::memcmp(p,"NM\001",3) && p[12]==n-AGON_NET_HEADER;
    }
    void put(const uint8_t*p,unsigned n) {std::memcpy(command_,p,n);commandLength_=n;}
public:
    explicit Mailbox(uint32_t previousToken=0):sequence_(previousToken){}
    bool submitUart(const uint8_t*p,unsigned n) {
        if(carrier_!=Carrier::uart || !valid(p,n))return false;
        const bool replace=p[3]==AGON_NET_CONNECT;
        if(!replace && (commandLength_||replyLength_||processing_))return false;
        if(replace){++generation_;replyLength_=0;processing_=false;}
        put(p,n);return true;
    }
    unsigned takeUart(uint8_t*out) {
        if(carrier_!=Carrier::uart || !out)return 0;
        const auto n=replyLength_;if(n)std::memcpy(out,reply_,n);replyLength_=0;return n;
    }
    MailboxResult openParallel(uint32_t&token) {
        token=0;
        if(carrier_!=Carrier::uart || commandLength_||replyLength_||processing_)return MailboxResult::busy;
        if(sequence_==UINT32_MAX)return MailboxResult::exhausted;
        token_=++sequence_;token=token_;carrier_=Carrier::parallel;fault_=pending_=false;
        return MailboxResult::ok;
    }
    MailboxResult submitParallel(uint32_t token,const uint8_t*p,unsigned n) {
        if(!owns(token))return MailboxResult::stale;
        if(carrier_!=Carrier::parallel || fault_)return MailboxResult::fault;
        if(!valid(p,n))return MailboxResult::invalid;
        if(pending_)return MailboxResult::busy;
        put(p,n);pending_=true;return MailboxResult::ok;
    }
    MailboxResult canSubmitParallel(uint32_t token) const {
        if(!owns(token))return MailboxResult::stale;
        if(carrier_!=Carrier::parallel||fault_)return MailboxResult::fault;
        return pending_?MailboxResult::busy:MailboxResult::ok;
    }
    bool beginWork(uint8_t*out,unsigned&n,uint32_t&generation) {
        n=commandLength_;generation=generation_;
        if(!n)return false;
        std::memcpy(out,command_,n);commandLength_=0;processing_=true;return true;
    }
    void completeWork(uint32_t generation,const uint8_t*p,unsigned n) {
        if(generation!=generation_)return;
        processing_=false;
        if(!n){if(carrier_==Carrier::parallel)fault_=true;return;}
        if(!valid(p,n) || p[3]!=(command_[3]|0x80) || std::memcmp(p+4,command_+4,8)) {
            if(carrier_==Carrier::parallel)fault_=true;
            return;
        }
        std::memcpy(reply_,p,n);replyLength_=n;
    }
    // The returned pointer remains immutable while borrowed, even on fault.
    MailboxResult offerParallel(uint32_t token,unsigned capacity,
                                const uint8_t*&data,unsigned&required) {
        data=nullptr;required=0;
        if(!owns(token))return MailboxResult::stale;
        if(carrier_!=Carrier::parallel || fault_)return MailboxResult::fault;
        if(borrowed_)return MailboxResult::busy;
        if(!replyLength_)return pending_?MailboxResult::busy:MailboxResult::empty;
        required=replyLength_;
        if(capacity<required)return MailboxResult::tooSmall;
        data=reply_;borrowed_=true;return MailboxResult::ok;
    }
    MailboxResult finishParallel(uint32_t token,bool complete,bool padsReleased) {
        if(!owns(token))return MailboxResult::stale;
        if(!borrowed_)return MailboxResult::invalid;
        if(!padsReleased)return MailboxResult::busy;
        borrowed_=false;
        if(!complete){fault_=true;return MailboxResult::fault;}
        replyLength_=0;pending_=false;return MailboxResult::ok;
    }
    MailboxResult releaseParallel(uint32_t token) {
        if(!owns(token))return MailboxResult::stale;
        if(borrowed_)return MailboxResult::busy;
        if(carrier_==Carrier::closed){
            token_=0;carrier_=Carrier::uart;fault_=pending_=false;return MailboxResult::ok;
        }
        if(carrier_!=Carrier::closing){
            carrier_=Carrier::closing;++generation_;commandLength_=replyLength_=0;
            closeRequested_=true;
        }
        return MailboxResult::busy; // Worker must actually close its socket.
    }
    bool takeCloseRequest(){const bool result=closeRequested_;closeRequested_=false;return result;}
    void completeClose(){
        if(carrier_==Carrier::closing){processing_=false;carrier_=Carrier::closed;}
    }
    // A network shutdown does not prove DMA/pads stopped. Keep a borrowed reply
    // frozen, reject UART output, and require the physical owner's completion.
    void workerStopped(){
        ++generation_;commandLength_=0;processing_=false;closeRequested_=false;
        if(carrier_==Carrier::uart){replyLength_=0;return;}
        fault_=true;carrier_=borrowed_?Carrier::closing:Carrier::closed;
    }
    void completeStoppedClose(){
        if(carrier_==Carrier::closing && !borrowed_)carrier_=Carrier::closed;
    }
};
}
