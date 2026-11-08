// Execute actual header against independent documented MOS response boundaries.
#include "uart0_reply_burst.hpp"
#include <assert.h>
#include <vector>
struct IO {
    unsigned writes=0,clears=0,polls=0,mode_after=2,cursor_after=3;
    bool mode_flag=true,cursor_flag=true,drop_mode=false,drop_cursor=false;
    bool wrong_mode=false,wrong_cursor=false,refuse=false,cancel=false,stopped=false;
    uint8_t xx=0,yy=0;uint32_t clock=0;
    std::vector<uint8_t> bytes;
    void clear_replies(){++clears;mode_flag=false;cursor_flag=false;}
    bool write(const uint8_t*p,unsigned n){
        ++writes;assert(clears==1);bytes.assign(p,p+n);
        assert(n==9&&p[0]==31&&p[3]==23&&p[4]==0&&p[5]==0x86&&p[6]==23&&p[7]==0&&p[8]==0x82);
        xx=p[1];yy=p[2];return !refuse;
    }
    uint32_t tick(){auto r=clock;if(!stopped)clock=(clock+1)&0xffffff;return r;}
    bool cancelled(){++polls;return cancel;}
    bool mode_ready(){if(!drop_mode&&polls>=mode_after)mode_flag=true;return mode_flag;}
    bool cursor_ready(){if(!drop_cursor&&polls>=cursor_after)cursor_flag=true;return cursor_flag;}
    bool mode_matches(){return !wrong_mode;}
    uint8_t x(){return wrong_cursor?uint8_t(xx+1):xx;}
    uint8_t y(){return yy;}
};
int main(){
    for(auto xy:std::vector<std::vector<uint8_t>>{{0,0},{7,5},{0,5},{7,0}}){
        for(unsigned order=0;order<2;++order){IO io;if(order){io.mode_after=4;io.cursor_after=1;}
            assert(uart0_reply_burst::query(io,xy[0],xy[1]));assert(io.writes==1&&io.clears==1);
            assert(io.bytes==std::vector<uint8_t>({31,xy[0],xy[1],23,0,0x86,23,0,0x82}));}
    }
    IO stale;stale.drop_mode=stale.drop_cursor=true;assert(!uart0_reply_burst::query(stale,0,0));
    IO missing_mode;missing_mode.drop_mode=true;assert(!uart0_reply_burst::query(missing_mode,0,0));
    IO missing_cursor;missing_cursor.drop_cursor=true;assert(!uart0_reply_burst::query(missing_cursor,0,0));
    IO wrong_mode;wrong_mode.wrong_mode=true;assert(!uart0_reply_burst::query(wrong_mode,7,5));
    IO wrong_cursor;wrong_cursor.wrong_cursor=true;assert(!uart0_reply_burst::query(wrong_cursor,7,5));
    IO refused;refused.refuse=true;assert(!uart0_reply_burst::query(refused,0,0));assert(refused.writes==1&&refused.polls==0);
    IO cancelled;cancelled.cancel=true;assert(!uart0_reply_burst::query(cancelled,0,0));assert(cancelled.polls==1);
    IO wrap;wrap.clock=0xfffffe;assert(uart0_reply_burst::query(wrap,0,0));
    IO timeout;timeout.clock=0xfffffe;timeout.drop_mode=true;assert(!uart0_reply_burst::query(timeout,0,0));assert(timeout.polls<=60);
    IO stopped;stopped.stopped=true;stopped.drop_cursor=true;assert(!uart0_reply_burst::query(stopped,0,0));assert(stopped.polls==1000000&&stopped.writes==1);
}
