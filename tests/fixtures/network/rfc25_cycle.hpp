// Fixture-only guarded RFC25 control. No raw UART, hidden drain or game ABI.
// A callback releases SOURCE storage; the trailing point reply witnesses the
// mainboard parser. Neither event alone is reported as wire-empty or optical proof.
#pragma once
#include <stdint.h>

struct ProbeRfc25Cycle {
    static constexpr unsigned packet_size=67;
    uint8_t packet[packet_size]{};
    volatile uint8_t source_done=0;
    uint8_t admission=0;
    bool borrowed=false,uncertain=false,receiver_seen=false,cancelled=false;
    unsigned releases=0,replies=0;
    uint32_t elapsed=0;

    void prepare(unsigned index){
        unsigned at=0;
        for(unsigned line=0;line<4;++line){
            const unsigned y=48+index*64+line*16;
            const uint8_t draw[]={18,0,uint8_t(1+index+line),
                25,4,32,0,uint8_t(y),uint8_t(y>>8),
                25,5,224,0,uint8_t(y+8),uint8_t((y+8)>>8)};
            for(auto value:draw)packet[at++]=value;
        }
        const unsigned y=48+index*64;
        const uint8_t query[]={23,0,0x84,32,0,uint8_t(y),uint8_t(y>>8)};
        for(auto value:query)packet[at++]=value;
    }

    template<class IO> uint8_t run(unsigned index,IO &io){
        // An uncertain prior submission is never reused, even if its callback
        // subsequently appears. The owner must retire the original invocation.
        if(borrowed||uncertain||index>=4)return 134;
        if(io.escaped())return 130;
        auto context=io.context();if(context)return context;
        prepare(index);source_done=0;receiver_seen=false;cancelled=false;elapsed=0;
        io.clear_point();
        const auto began=io.ticks();
        borrowed=true; // Publish lifetime BEFORE submit: callback may be immediate.
        admission=io.submit(packet,packet_size,&source_done);
        if(admission){
            const bool refused=admission==19||admission==31||admission==32||admission==35;
            uncertain=!refused||source_done;
            borrowed=uncertain;
            return admission;
        }
        uint32_t fuse=8000000;
        while(io.elapsed(began)<300&&--fuse){
            io.poll(); // Native adapter is empty; isolated tests deliver IRQ events.
            if(io.escaped())cancelled=true;
            if(source_done&&borrowed){borrowed=false;++releases;}
            if(io.point_ready()&&!receiver_seen){receiver_seen=true;++replies;}
            if(!borrowed&&receiver_seen){
                elapsed=io.elapsed(began);
                return cancelled?130:0;
            }
        }
        // Timeout or Escape cannot revoke an ISR borrow. The native caller
        // halts with EI and no more MOS/output/network calls if this is true.
        uncertain=borrowed;
        elapsed=io.elapsed(began);
        return cancelled?130:131;
    }
};
