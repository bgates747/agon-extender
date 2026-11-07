// Stopped target core self-check, not a benchmark or transport invocation.
#include "engine.hpp"
#include "build_identity.h"
#include <stdio.h>
struct LocalModel {
    uint32_t ticks=10;
    bool prepare(const comms_performance::Corpus&){return true;}
    uint32_t clock(){return ticks++;}
    comms_performance::Admission submit(const comms_performance::Corpus&){return comms_performance::submit_accepted;}
    comms_performance::Witness wait_source(){return {true,true};}
    comms_performance::Witness wait_complete(){return {true,true};}
    bool validate(const comms_performance::Corpus&){return true;}
    bool cleanup(){return true;}
};
int main(){
    using namespace comms_performance;
    uint8_t v=0;uint32_t ticks=0;
    if(bytes(buffer_vdu,1024)!=1038||!byte_at(buffer_vdu,1024,0x7800,13,v)||v!=4)return 1;
    if(!interval(250,5,8,30,ticks)||ticks!=11||interval(4,4,8,30,ticks))return 2;
    LocalModel model;Corpus c{sink,84,0};
    if(measure(c,24,100,model).outcome!=measured)return 3;
    puts(COMMS_CORE_BUILD_ID " [stopped core check; no timing qualification]");return 0;
}
