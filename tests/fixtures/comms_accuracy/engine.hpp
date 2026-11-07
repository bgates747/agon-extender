// COMMS-001 orchestration. The adapter owns real deadlines, MOS SD and pins.
// A false retirement witness forbids any further adapter call in this case.
#pragma once
#include "core.hpp"
namespace comms_accuracy {
struct Exchange {
    size_t length=0;
    bool retired=false;
    uint8_t actual_return_carrier=0;
};
enum Outcome {case_passed,case_failed,cancelled,infrastructure_failed,ownership_unknown,log_failed};
struct Result {
    Outcome outcome=infrastructure_failed;
    unsigned attempts=0,failed_attempts=0;
    uint32_t sequence=0,verified_bytes=0,expected_stream_crc=0,received_stream_crc=0;
    uint8_t first_error=ok;
};
enum Checkpoint {intent_checkpoint,outcome_checkpoint};

// Adapter contract:
// running(): bounded cancellation/deadline check at a known retired boundary.
// checkpoint(kind, frame, status): durable append; false forbids new dispatch.
// baseline(frame): restore only task-owned state; false means do not continue.
// exchange(out,n,tx,rx,in,capacity): bounded transfer, positive retirement proof.
// uart_report(frame,status): complete CRC-checked UART1 failure exchange.
// uart_retry(frame,out,capacity): fresh protected UART1 RETRY authorisation.
template<class IO> Result run_case(Frame first,IO&io){
    Result result;Attempts attempts;
    if(!attempts.begin(first))return result;
    uint8_t outbound[max_wire],incoming[max_wire];
    for(;;){
        first.attempt=uint8_t(attempts.attempt());result.attempts=attempts.attempt();
        if(!io.running()){result.outcome=cancelled;return result;}
        if(!io.checkpoint(intent_checkpoint,first,ok)){result.outcome=log_failed;return result;}
        if(!io.baseline(first)){attempts.infrastructure_fault();return result;}
        uint32_t offset=0,sequence=1;uint8_t error=ok;Frame failed=first;
        Crc32 expected_crc,received_crc;
        do {
            if(!io.running()){result.outcome=cancelled;return result;}
            Frame send=first;send.sequence=sequence;send.offset=offset;
            uint32_t left=send.total-offset;send.length=uint16_t(left>max_payload?max_payload:left);
            for(unsigned i=0;i<send.length;++i)send.payload[i]=pattern_byte(send.pattern,send.seed,offset+i);
            size_t n=encode(send,outbound,sizeof(outbound));
            if(!n)return result;
            Exchange x=io.exchange(outbound,n,send.tx,send.rx,incoming,sizeof(incoming));
            result.sequence=sequence;failed=send;
            if(!x.retired){
                result.outcome=ownership_unknown;
                if(!result.first_error)result.first_error=owner_fault;
                return result; // No logging/UART/MOS/cleanup after uncertain borrow.
            }
            Frame reply;Decode status=decode(incoming,x.length,reply);
            if(status!=decoded)error=status==crc_error?bad_crc:bad_sequence;
            else if(reply.kind==nack){
                // Peer failure messages must arrive on actual UART1, even when
                // this case selected parallel for successful data replies.
                if(x.actual_return_carrier!=1||reply.run!=send.run||reply.case_id!=send.case_id||
                   reply.sequence!=send.sequence||reply.attempt!=send.attempt)error=bad_sequence;
                else error=reply.status;
            }else{
                Frame expected=send;expected.kind=ack;expected.direction=1;
                size_t expected_n=encode(expected,outbound,sizeof(outbound));
                if(x.actual_return_carrier!=send.rx||x.length!=expected_n)error=bad_sequence;
                else {
                    for(size_t i=0;i<expected_n-4;++i)if(outbound[i]!=incoming[i]){
                        error=i<header_bytes?bad_sequence:bad_pattern;break;
                    }
                }
            }
            if(error)break;
            expected_crc.update(send.payload,send.length);received_crc.update(reply.payload,reply.length);
            offset+=send.length;++sequence;
        }while(offset<first.total);
        result.verified_bytes=offset;result.expected_stream_crc=expected_crc.value();result.received_stream_crc=received_crc.value();
        if(!error&&result.expected_stream_crc!=result.received_stream_crc)error=bad_crc;
        if(!attempts.complete(!error,true,error?failed.sequence:0))return result;
        if(error&&!result.first_error)result.first_error=error;
        result.failed_attempts=attempts.failures();
        if(!io.checkpoint(outcome_checkpoint,error?failed:first,error)){result.outcome=log_failed;return result;}
        if(!error){result.outcome=case_passed;return result;}
        bool reported=io.uart_report(failed,error);
        if(!attempts.report(reported)){result.outcome=infrastructure_failed;return result;}
        if(attempts.state()==Attempts::exhausted){result.outcome=case_failed;return result;}
        size_t n=io.uart_retry(failed,incoming,sizeof(incoming));
        if(attempts.control(incoming,n)!=Attempts::accepted)return result;
    }
}
}
