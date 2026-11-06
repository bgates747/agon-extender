// PARALLEL-001 finite byte matrix. No hardware, CRC, retry or game semantics.
#pragma once
#include <stdint.h>
namespace probe_repeat {
constexpr unsigned sessions=4, rounds=4, lengths=11;
constexpr unsigned records_per_session=rounds*lengths;
constexpr unsigned records=sessions*records_per_session;
constexpr unsigned sizes[lengths]={0,1,2,17,63,64,65,75,79,127,128};
constexpr unsigned size(unsigned index){return sizes[index%lengths];}
constexpr uint8_t byte(unsigned session,unsigned index,unsigned offset){
    const unsigned seed=session*records_per_session+index;
    switch((session+index/lengths)%4){
    case 0:return uint8_t(offset*37+seed);
    case 1:return uint8_t(~(offset*37+seed));
    case 2:return (offset+seed)%2?0xff:0;
    default:return uint8_t(1u<<((offset+seed)%8));
    }
}
}
