// Executes the actual fixture state/packet leaf with isolated interrupt events.
// Host tests do not qualify eZ80 ABI, hardware timing, VDP execution or optics.
#include <cassert>
#include <cstring>
#include <initializer_list>
#include "../../fixtures/network/rfc25_cycle.hpp"

struct IO {
    uint32_t now=0;
    unsigned submits=0,polls=0,release_at=1,reply_at=2,cancel_at=0;
    uint8_t result=0,context_result=0;
    volatile uint8_t*done=nullptr;
    bool point=true,cleared=false,immediate=false,cancel_before=false;
    const uint8_t*source=nullptr;
    uint8_t original[ProbeRfc25Cycle::packet_size]{};
    bool escaped(){return cancel_before||(cancel_at&&polls>=cancel_at);}
    uint8_t context(){return context_result;}
    uint32_t ticks(){return now;}
    uint32_t elapsed(uint32_t start){return (now++-start)&0xffffff;}
    void clear_point(){point=false;cleared=true;}
    bool point_ready(){return point;}
    uint8_t submit(const uint8_t*p,unsigned n,volatile uint8_t*flag){
        assert(cleared&&!point&&*flag==0&&n==ProbeRfc25Cycle::packet_size);
        ++submits;source=p;done=flag;memcpy(original,p,n);
        if(immediate){*done=1;point=true;}
        return result;
    }
    void poll(){
        ++polls;assert(!memcmp(source,original,sizeof(original)));
        if(release_at&&polls==release_at)*done=1;
        if(reply_at&&polls==reply_at)point=true;
    }
};

int main(){
    {
        ProbeRfc25Cycle p;IO io;io.immediate=true;
        assert(p.run(0,io)==0&&io.submits==1&&!p.borrowed&&!p.uncertain);
        assert(p.releases==1&&p.replies==1&&p.receiver_seen);
        const uint8_t first[]={18,0,1,25,4,32,0,48,0,25,5,224,0,56,0};
        const uint8_t query[]={23,0,132,32,0,48,0};
        assert(!memcmp(p.packet,first,sizeof(first)));
        assert(!memcmp(p.packet+60,query,sizeof(query)));
        IO last;assert(p.run(3,last)==0&&p.releases==2&&p.replies==2);
        assert(p.packet[2]==4&&p.packet[7]==240&&p.packet[8]==0);
        assert(p.packet[45+7]==32&&p.packet[45+8]==1);
        assert(p.packet[65]==240&&p.packet[66]==0);
    }
    for(bool reply_first:{false,true}){
        ProbeRfc25Cycle p;IO io;
        io.release_at=reply_first?3:1;io.reply_at=reply_first?1:3;
        assert(p.run(0,io)==0&&io.polls==3&&p.releases==1&&p.replies==1);
    }
    for(uint8_t refusal:{19,31,32,35}){
        ProbeRfc25Cycle p;IO io;io.result=refusal;
        assert(p.run(0,io)==refusal&&io.submits==1&&!p.borrowed&&!p.uncertain);
        assert(io.polls==0&&p.releases==0&&p.replies==0);
    }
    {
        ProbeRfc25Cycle p;IO io;io.result=77;
        assert(p.run(0,io)==77&&p.uncertain&&p.borrowed&&io.submits==1);
        assert(p.run(1,io)==134&&io.submits==1); // No replay or mutation.
        assert(!memcmp(p.packet,io.original,sizeof(io.original)));
    }
    {
        ProbeRfc25Cycle p;IO io;io.result=31;io.immediate=true;
        assert(p.run(0,io)==31&&p.uncertain&&p.borrowed); // Contradictory refusal.
    }
    {
        ProbeRfc25Cycle p;IO io;io.release_at=0;
        assert(p.run(0,io)==131&&p.uncertain&&p.borrowed&&p.receiver_seen);
        assert(p.run(1,io)==134&&io.submits==1);
    }
    {
        ProbeRfc25Cycle p;IO io;io.reply_at=0;
        assert(p.run(0,io)==131&&!p.uncertain&&!p.borrowed&&!p.receiver_seen);
        assert(p.releases==1&&p.replies==0&&io.submits==1);
    }
    {
        ProbeRfc25Cycle p;IO io;io.cancel_at=1;io.release_at=3;io.reply_at=4;
        assert(p.run(0,io)==130&&io.polls==4&&!p.borrowed&&!p.uncertain);
    }
    {
        ProbeRfc25Cycle p;IO io;io.cancel_at=1;io.release_at=0;
        assert(p.run(0,io)==130&&p.uncertain&&p.borrowed&&io.submits==1);
    }
    {
        ProbeRfc25Cycle p;IO io;io.cancel_before=true;
        assert(p.run(0,io)==130&&io.submits==0&&!p.borrowed);
        io.cancel_before=false;io.context_result=32;
        assert(p.run(0,io)==32&&io.submits==0&&!p.borrowed);
    }
    {
        ProbeRfc25Cycle p;IO io;io.now=0xfffffe;
        assert(p.run(0,io)==0); // Application elapsed policy wraps at24 bits.
    }
}
