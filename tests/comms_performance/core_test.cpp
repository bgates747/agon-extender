#include "../fixtures/comms_performance/core.hpp"
#include <assert.h>
#include <stdio.h>
#include <string.h>
using namespace comms_performance;
int main(int argc,char**argv){
    uint8_t value=0;uint32_t count=0;
    if(argc==2&&!strcmp(argv[1],"--dump")){
        const uint32_t amounts[]={129,9,7,1024};
        for(unsigned k=0;k<4;++k){
            auto kind=Workload(k);uint32_t n=bytes(kind,amounts[k]);
            for(unsigned b=0;b<4;++b)assert(putchar(int(uint8_t(n>>(8*b))))!=EOF);
            for(uint32_t i=0;i<n;++i){assert(byte_at(kind,amounts[k],0x7800,i,value));assert(putchar(value)!=EOF);}
        }
        return 0;
    }
    assert(interval(250,5,8,30,count)&&count==11);
    assert(interval(0xfffffff0UL,16,32,100,count)&&count==32);
    assert(!interval(0,0,24,100,count));assert(!interval(0,90,8,30,count));
    assert(!interval(0,1,8,128,count));assert(!interval(256,1,8,30,count));assert(!interval(0,1,33,30,count));
    assert(bytes(short_vdu,1)==2&&bytes(medium_vdu,1)==15&&bytes(buffer_vdu,65535)==65549);
    assert(!bytes(buffer_vdu,65536)&&!bytes(short_vdu,0));
    assert(!byte_at(buffer_vdu,1,65535,0,value));assert(!byte_at(sink,1,0,1,value));
    puts("Performance core: corpus lengths/resources and bounded timer arithmetic PASS");
}
