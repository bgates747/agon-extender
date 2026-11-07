// Actual query helper, MOS/transport substituted at its documented boundaries.
#include "uart0_cursor.hpp"
#include <assert.h>
#include <stdint.h>
#include <vector>
struct IO {
    unsigned writes=0,clears=0,polls=0,ready_after=2;
    bool flag=true,drop=false,cancel=false,wrong=false,stopped=false;
    unsigned refuse=0;
    uint8_t current_x=0,current_y=0,requested_x=0,requested_y=0;
    uint32_t clock=0;
    std::vector<std::vector<uint8_t>> bytes;
    bool write(const uint8_t*p,unsigned n){
        ++writes;bytes.emplace_back(p,p+n);
        if(refuse==writes)return false;
        if(p[0]==31){requested_x=p[1];requested_y=p[2];}
        else {assert(n==3&&p[0]==23&&p[1]==0&&p[2]==0x82);}
        return true;
    }
    void clear_cursor(){++clears;flag=false;}
    uint32_t tick(){uint32_t r=clock;if(!stopped)clock=(clock+1)&0xffffff;return r;}
    bool cancelled(){return cancel;}
    bool cursor_ready(){
        ++polls;
        if(!drop&&polls>=ready_after){flag=true;current_x=wrong?uint8_t(requested_x+1):requested_x;current_y=requested_y;}
        return flag;
    }
    uint8_t x(){return current_x;}
    uint8_t y(){return current_y;}
};
int main(){
    for(auto xy:std::vector<std::vector<uint8_t>>{{0,0},{7,5},{0,5},{7,0}}){
        IO io;assert(uart0_cursor::query(io,xy[0],xy[1]));
        assert(io.clears==1&&io.writes==2&&io.bytes[0]==std::vector<uint8_t>({31,xy[0],xy[1]})&&io.bytes[1]==std::vector<uint8_t>({23,0,0x82}));
    }
    IO stale;stale.drop=true;assert(!uart0_cursor::query(stale,0,0));assert(stale.clears==1&&stale.writes==2);
    IO wrong;wrong.wrong=true;assert(!uart0_cursor::query(wrong,7,5));assert(wrong.writes==2);
    IO position;position.refuse=1;assert(!uart0_cursor::query(position,0,0));assert(position.writes==1&&position.clears==0);
    IO request;request.refuse=2;assert(!uart0_cursor::query(request,0,0));assert(request.writes==2&&request.clears==1);
    IO cancelled;cancelled.cancel=true;assert(!uart0_cursor::query(cancelled,0,0));assert(cancelled.writes==2&&cancelled.polls==0);
    IO wrap;wrap.clock=0xfffffe;assert(uart0_cursor::query(wrap,0,0));
    IO timeout;timeout.clock=0xfffffe;timeout.drop=true;assert(!uart0_cursor::query(timeout,0,0));assert(timeout.writes==2&&timeout.polls<=60);
    IO stopped;stopped.stopped=true;stopped.drop=true;assert(!uart0_cursor::query(stopped,0,0));assert(stopped.polls==1000000&&stopped.writes==2);
}
