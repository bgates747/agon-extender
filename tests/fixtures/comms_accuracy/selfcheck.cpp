// Stopped core self-check, not a transport appliance. Never deploy as one.
#include "engine.hpp"
#include "build_identity.h"
#include <stdio.h>
struct LocalModel {
    bool running(){return true;}
    bool checkpoint(comms_accuracy::Checkpoint,const comms_accuracy::Frame&,uint8_t){return true;}
    bool baseline(const comms_accuracy::Frame&){return true;}
    comms_accuracy::Exchange exchange(const uint8_t*p,size_t n,uint8_t,uint8_t rx,uint8_t*out,size_t capacity){
        comms_accuracy::Frame f;if(comms_accuracy::decode(p,n,f)!=comms_accuracy::decoded)return {};
        f.kind=comms_accuracy::ack;f.direction=1;
        return {comms_accuracy::encode(f,out,capacity),true,rx};
    }
    bool uart_report(const comms_accuracy::Frame&,uint8_t){return false;}
    size_t uart_retry(const comms_accuracy::Frame&,uint8_t*,size_t){return 0;}
};
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
    Frame first;first.run=1;first.case_id=1;first.sequence=1;first.total=169;
    LocalModel model;auto result=run_case(first,model);
    if(result.outcome!=case_passed||result.verified_bytes!=169)return 5;
    puts(COMMS_CORE_BUILD_ID " [stopped core check; no hardware qualification]");return 0;
}
