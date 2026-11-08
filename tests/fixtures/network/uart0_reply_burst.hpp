// Owner overlap diagnostic: ordinary EMOS-routed MODE/cursor only; no GP.
// Each completion has its own documented flag and value oracle. The native
// replies total14 logical bytes (MODE10+cursor4), not measured FIFO occupancy.
#pragma once
#include <stdint.h>
namespace uart0_reply_burst {
template<class IO> bool query(IO &io,uint8_t x,uint8_t y) {
    io.clear_replies();
    const uint8_t request[]={31,x,y,23,0,0x86,23,0,0x82};
    if(!io.write(request,sizeof(request)))return false;
    const uint32_t began=io.tick();
    unsigned long fuse=1000000;
    bool mode=false,cursor=false;
    do {
        if(io.cancelled())return false;
        if(!mode&&io.mode_ready()){
            if(!io.mode_matches())return false;
            mode=true;
        }
        if(!cursor&&io.cursor_ready()){
            if(io.x()!=x||io.y()!=y)return false;
            cursor=true;
        }
        if(mode&&cursor)return true;
    } while(((io.tick()-began)&0xffffffUL)<60UL&&--fuse);
    return false;
}
}
