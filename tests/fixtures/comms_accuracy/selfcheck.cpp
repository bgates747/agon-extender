// Stopped core self-check, not a transport appliance. Never deploy as one.
#include "core.hpp"
#include <stdio.h>
int main(){
    using namespace comms_accuracy;
    const uint8_t vector[]="123456789";
    if(crc32(vector,9)!=0xcbf43926UL)return 1;
    Frame f;f.run=1;f.case_id=1;f.sequence=1;f.total=84;f.length=84;f.pattern=5;f.seed=0x12345678;
    for(unsigned i=0;i<f.length;++i)f.payload[i]=pattern_byte(f.pattern,f.seed,i);
    uint8_t bytes[max_wire];Frame got;
    size_t n=encode(f,bytes,sizeof(bytes));
    if(n!=128||decode(bytes,n,got)!=decoded||!correct_pattern(got))return 2;
    Attempts a;if(!a.begin(f)||!a.complete(false,true,1)||!a.report(true))return 3;
    f.kind=retry;f.direction=1;f.length=0;f.flags=1;n=encode(f,bytes,sizeof(bytes));
    if(a.control(bytes,n)!=Attempts::accepted||a.attempt()!=2)return 4;
    puts("COMMS-001 core self-check; no transport or hardware qualification");return 0;
}
