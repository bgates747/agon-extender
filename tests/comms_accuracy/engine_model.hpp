// Host/stopped-link contract model only; does not model pin or IRQ timing.
#pragma once
#include "../fixtures/comms_accuracy/engine.hpp"
struct AccuracyModel {
    unsigned attempts=0,exchanges=0,reports=0,retries=0,checkpoints=0;
    unsigned fail_through=0,fail_log_at=0;
    bool keep_running=true,unsafe=false,report_ok=true,wrong_case=false,peer_nack=false;
    bool running(){return keep_running;}
    bool checkpoint(comms_accuracy::Checkpoint,const comms_accuracy::Frame&,uint8_t){
        ++checkpoints;return checkpoints!=fail_log_at;
    }
    bool baseline(const comms_accuracy::Frame&){++attempts;return true;}
    comms_accuracy::Exchange exchange(const uint8_t*p,size_t n,uint8_t,uint8_t rx,uint8_t*out,size_t capacity){
        using namespace comms_accuracy;
        ++exchanges;Frame f;if(decode(p,n,f)!=decoded)return {};
        if(unsafe)return {};
        f.kind=ack;f.direction=1;
        if(wrong_case)++f.case_id;
        if(peer_nack){f.kind=nack;f.status=bad_pattern;f.length=8;f.flags=0;rx=1;}
        size_t used=encode(f,out,capacity);
        if(attempts<=fail_through&&used)out[used-1]^=1;
        return {used,true,rx};
    }
    bool uart_report(const comms_accuracy::Frame&,uint8_t){++reports;return report_ok;}
    size_t uart_retry(comms_accuracy::Frame f,uint8_t*out,size_t capacity){
        ++retries;f.kind=comms_accuracy::retry;f.offset=0;f.direction=1;f.flags=1;f.length=0;
        return comms_accuracy::encode(f,out,capacity);
    }
};
