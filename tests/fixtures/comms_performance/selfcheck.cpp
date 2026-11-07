// Stopped target core self-check, not a benchmark or transport invocation.
#include "core.hpp"
#include <stdio.h>
int main(){
    using namespace comms_performance;
    uint8_t v=0;uint32_t ticks=0;
    if(bytes(buffer_vdu,1024)!=1038||!byte_at(buffer_vdu,1024,0x7800,13,v)||v!=4)return 1;
    if(!interval(250,5,8,30,ticks)||ticks!=11||interval(4,4,8,30,ticks))return 2;
    puts("COMMS-002 core self-check; no timing or hardware qualification");return 0;
}
