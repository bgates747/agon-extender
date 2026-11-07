// COMMS-002 benchmark-only corpus and timer arithmetic. No CRC/retry engine.
#pragma once
#include <stdint.h>
namespace comms_performance {
enum Workload:uint8_t {sink=0,short_vdu=1,medium_vdu=2,buffer_vdu=3};
inline uint32_t bytes(Workload kind,uint32_t amount){
    if(kind==sink)return amount<=1048576UL?amount:0;
    if(kind==short_vdu)return amount&&amount<=32767?amount*2:0;
    if(kind==medium_vdu)return amount&&amount<=4096?amount*15:0;
    if(kind==buffer_vdu)return amount&&amount<=65535?amount+14:0;
    return 0;
}
inline bool byte_at(Workload kind,uint32_t amount,uint16_t buffer_id,uint32_t at,uint8_t&out){
    uint32_t n=bytes(kind,amount);if(!n||at>=n)return false;
    if(kind==sink){out=uint8_t(at*37+11);return true;}
    if(kind==short_vdu){out=(at&1)?uint8_t((at/2)%16):17;return true;}
    if(kind==medium_vdu){
        uint32_t i=at/15;uint8_t y=uint8_t((i*7)%192);
        const uint8_t p[]={18,0,uint8_t(i%16),25,4,16,0,y,0,25,5,240,0,y,0};
        out=p[at%15];return true;
    }
    // Standard buffer clear2 then write0. Caller must own the chosen buffer.
    // The corpus cannot allocate/reserve that resource or prove execution.
    if(!buffer_id||buffer_id==65535)return false;
    const uint8_t prefix[]={23,0,0xa0,uint8_t(buffer_id),uint8_t(buffer_id>>8),2,
        23,0,0xa0,uint8_t(buffer_id),uint8_t(buffer_id>>8),0,uint8_t(amount),uint8_t(amount>>8)};
    out=at<14?prefix[at]:uint8_t((at-14)*37+11);return true;
}
// The observer supplies an independently established upper interval bound.
// Without it equal/modulo counters cannot disambiguate multiple wraps.
inline bool interval(uint32_t start,uint32_t end,unsigned bits,uint32_t confirmed_upper,uint32_t&counts){
    if(bits<8||bits>32||!confirmed_upper)return false;
    uint32_t mask=bits==32?uint32_t(0xffffffffUL):(uint32_t(1)<<bits)-1;
    if(start>mask||end>mask||confirmed_upper>(mask>>1))return false;
    uint32_t result=(end-start)&mask;
    if(!result||result>confirmed_upper)return false;
    counts=result;return true;
}
}
