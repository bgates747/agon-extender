// COMMS-002 independent measurement engine. No accuracy CRC/retry dependency.
#pragma once
#include "core.hpp"
namespace comms_performance {
struct Corpus {
    Workload kind=sink;uint32_t amount=0;uint16_t buffer_id=0;
    uint32_t size()const{return bytes(kind,amount);}
    bool at(uint32_t index,uint8_t&value)const{return byte_at(kind,amount,buffer_id,index,value);}
};
struct Witness {bool completed=false,retired=false;};
enum Admission {submit_refused,submit_accepted,submit_uncertain};
enum Outcome {measured,refused,invalid_sample,unsafe_owner};
struct Measurement {
    Outcome outcome=refused;uint32_t source_counts=0,complete_counts=0;
    bool checked=false,cleaned=false;
};
// One endpoint-local timer. P4 execution timing belongs to a separate observer.
// prepare/validate/cleanup are outside both intervals. wait_source() must be a
// source-release witness, wait_complete() the actual required receiver fence.
template<class IO> Measurement measure(const Corpus&corpus,unsigned bits,uint32_t upper,IO&io){
    Measurement m;uint8_t byte=0;
    if(!corpus.size()||!corpus.at(0,byte)||!io.prepare(corpus))return m;
    uint32_t started=io.clock();
    Admission admission=io.submit(corpus);
    if(admission==submit_uncertain){m.outcome=unsafe_owner;return m;}
    if(admission==submit_refused){
        // Refusal contract must guarantee no accepted source reference.
        m.cleaned=io.cleanup();return m;
    }
    Witness source=io.wait_source();
    if(!source.retired){m.outcome=unsafe_owner;return m;}
    uint32_t released=io.clock();
    if(!source.completed){m.outcome=invalid_sample;m.cleaned=io.cleanup();return m;}
    Witness done=io.wait_complete();
    if(!done.retired){m.outcome=unsafe_owner;return m;}
    uint32_t completed=io.clock();
    m.checked=done.completed&&io.validate(corpus);
    m.cleaned=io.cleanup();
    m.outcome=m.checked&&m.cleaned&&interval(started,released,bits,upper,m.source_counts)&&
        interval(started,completed,bits,upper,m.complete_counts)?measured:invalid_sample;
    return m;
}
}
