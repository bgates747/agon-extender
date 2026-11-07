// Owner-isolation cursor reply boundary. No raw registers/private IRQs or retry.
#pragma once
#include <stdint.h>
namespace uart0_cursor {
template<class IO> bool query(IO &io,uint8_t x,uint8_t y) {
    const uint8_t position[]={31,x,y};
    if(!io.write(position,sizeof(position)))return false;
    io.clear_cursor(); // only the supported cursor completion flag
    const uint8_t request[]={23,0,0x82};
    if(!io.write(request,sizeof(request)))return false;
    const uint32_t began=io.tick();
    unsigned long fuse=1000000;
    do {
        if(io.cancelled())return false;
        if(io.cursor_ready())return io.x()==x&&io.y()==y;
    } while(((io.tick()-began)&0xffffffUL)<60UL&&--fuse);
    return false;
}
}
