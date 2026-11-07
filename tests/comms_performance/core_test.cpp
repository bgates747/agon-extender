#include "../fixtures/comms_performance/core.hpp"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "engine_model.hpp"
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
    Corpus c{sink,84,0};PerformanceModel clean;auto m=measure(c,24,100,clean);
    assert(m.outcome==measured&&m.source_counts==5&&m.complete_counts==12&&m.checked&&m.cleaned);
    assert(clean.tick==222&&clean.clock_reads==3); // Validation/cleanup outside measured interval.
    PerformanceModel uncertain;uncertain.admission=submit_uncertain;m=measure(c,24,100,uncertain);
    assert(m.outcome==unsafe_owner&&uncertain.cleaned==0&&uncertain.validated==0&&uncertain.clock_reads==1);
    PerformanceModel release;release.source={false,false};m=measure(c,24,100,release);
    assert(m.outcome==unsafe_owner&&release.cleaned==0&&release.validated==0);
    PerformanceModel done;done.done={false,false};m=measure(c,24,100,done);
    assert(m.outcome==unsafe_owner&&done.cleaned==0&&done.validated==0);
    PerformanceModel corrupt;corrupt.validation_ok=false;m=measure(c,24,100,corrupt);
    assert(m.outcome==invalid_sample&&m.cleaned&&corrupt.validated==1);
    PerformanceModel refused;refused.admission=submit_refused;m=measure(c,24,100,refused);
    assert(m.outcome==comms_performance::refused&&refused.cleaned==1&&refused.clock_reads==1);
    PerformanceModel prepare;prepare.prepare_ok=false;m=measure(c,24,100,prepare);
    assert(m.outcome==comms_performance::refused&&prepare.submitted==0&&prepare.clock_reads==0);
    puts("Performance core: corpus lengths/resources and bounded timer arithmetic PASS");
}
