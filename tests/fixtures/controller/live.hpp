// Candidate application client: existing EMOS gateway only. EMOS owns request
// serialization, UART RX and expiry. There is no application ISR or raw I/O.
#pragma once
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#include "controller_wire.h"
#pragma GCC diagnostic pop
#include "view.hpp"
extern "C" uint24_t controller_gateway_available(void);
extern "C" uint24_t controller_gateway_call(uint8_t*);
namespace controller_view {
class Live {
    // Static-lifetime object is required: gateway pointers must be ordinary
    // application RAM, not the MOS-owned call stack.
    uint8_t request[66]{},input[1]{},output[CONTROLLER_RESULT_SIZE]{};
    uint8_t source[16]{};uint32_t edge=0;bool opened=false,have_source=false;
    uint24_t call(uint8_t operation){
        error_operation=operation;
        memset(request,0,sizeof(request));input[0]=operation;
        request[0]=66;request[2]=1;request[4]=3;request[5]=10;request[6]=2;
        pointer(request+10,uint24_t(input));request[13]=1;
        if(operation==1){pointer(request+16,uint24_t(output));request[19]=sizeof(output);}
        memcpy(request+25,"ext",3);memcpy(request+41,"controller",10);
        return controller_gateway_call(request);
    }
    static void pointer(uint8_t*p,uint24_t value){p[0]=value;p[1]=value>>8;p[2]=value>>16;}
 public:
    uint24_t error=0;
    uint8_t error_operation=0;
    bool open(){
        if(!controller_gateway_available()){error=35;return false;}
        error=call(0);opened=error==0;return opened;
    }
    bool update(Sample&s){
        if(!opened)return false;
        const auto result=call(1);
        if(!result){
            if(request[22]!=sizeof(output)||request[23]||request[24]||memcmp(output,CONTROLLER_RESULT_MAGIC,4)||output[11]>8){error=19;return false;}
            if(!have_source||memcmp(source,output+12,16)){
                memcpy(source,output+12,16);have_source=true;edge=0;
                ++s.generation;memset(s.presses,0,sizeof(s.presses));
            }
            s.sequence=controller_u32(output+28);s.age_ms=controller_u16(output+32);
            s.connected=output[10]&1;s.valid=output[10]&2;s.replay=false;
            s.held=controller_u16(output+34);
            for(unsigned i=0;i<4;++i)s.stick[i]=int16_t(controller_u16(output+36+i*2));
            memcpy(s.trigger,output+44,2);
            for(unsigned i=0;i<output[11];++i){
                const auto*p=output+48+i*6;const uint32_t sequence=controller_u32(p);
                if(p[4]>=15||p[5]>1){error=19;return false;}
                if(sequence>edge){
                    if(p[5]&&s.presses[p[4]]!=65535)++s.presses[p[4]];
                    edge=sequence;
                }
            }
            // Renew a healthy wire lease before its16-bit query counter is
            // exhausted. Preserve source/edge identity across this transport
            // renewal; faults still require an explicit application restart.
            if(controller_u16(output+8)>=65000)return close()&&open();
        }else if(result!=31){error=result;return false;}
        error=call(2);return error==0||error==31;
    }
    bool close(){if(!opened)return true;opened=false;error=call(3);return error==0;}
};
}
