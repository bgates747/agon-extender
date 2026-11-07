#include "../fixtures/comms_accuracy/core.hpp"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "engine_model.hpp"
using namespace comms_accuracy;
static Frame sample(){
    Frame f;f.run=0x12345678;f.case_id=7;f.sequence=1;f.total=84;f.length=84;f.pattern=5;f.seed=0xfedcba98;
    for(unsigned i=0;i<f.length;++i)f.payload[i]=pattern_byte(f.pattern,f.seed,i);
    return f;
}
int main(int argc,char**argv){
    uint8_t wire[max_wire],again[max_wire];Frame f=sample(),got;
    if(argc==2&&!strcmp(argv[1],"--dump")){
        const unsigned sizes[]={0,1,17,84};
        for(unsigned p=0;p<6;++p)for(unsigned tx=1;tx<=2;++tx)for(unsigned rx=1;rx<=2;++rx)for(auto length:sizes){
            f=sample();f.pattern=uint8_t(p);f.tx=uint8_t(tx);f.rx=uint8_t(rx);f.total=f.length=uint16_t(length);
            for(unsigned i=0;i<length;++i)f.payload[i]=pattern_byte(f.pattern,f.seed,i);
            size_t n=encode(f,wire,sizeof(wire));assert(n);put32(again,uint32_t(n));
            assert(fwrite(again,1,4,stdout)==4);assert(fwrite(wire,1,n,stdout)==n);
        }
        return 0;
    }
    const uint8_t vector[]="123456789";assert(crc32(vector,9)==0xcbf43926UL);
    assert(crc32(vector,0)==0);
    size_t n=encode(f,wire,sizeof(wire));assert(n==128);
    for(unsigned bit=0;bit<n*8;++bit){
        memcpy(again,wire,n);again[bit/8]^=uint8_t(1u<<(bit%8));got.run=999;
        assert(decode(again,n,got)==crc_error&&got.run==999);
    }
    for(size_t size=0;size<n;++size)assert(decode(wire,size,got)!=decoded);
    assert(decode(wire,n,got)==decoded&&correct_pattern(got));
    got.payload[83]^=1;uint32_t first=0;assert(!correct_pattern(got,&first)&&first==83);
    assert(!encode(f,wire,127));f.attempt=6;assert(!encode(f,wire,sizeof(wire)));f=sample();
    n=encode(f,wire,sizeof(wire));wire[38]=1;put32(wire+n-4,crc32(wire,n-4));assert(decode(wire,n,got)==invalid);
    f.offset=max_logical;f.total=max_logical;f.length=1;assert(!valid(f));f=sample();
    Attempts a;assert(a.begin(f));assert(!a.begin(f));
    for(unsigned attempt=1;attempt<=5;++attempt){
        assert(a.attempt()==attempt&&a.state()==Attempts::active);
        Frame control=f;control.kind=retry;control.direction=1;control.length=0;control.flags=1;control.attempt=uint8_t(attempt);
        n=encode(control,wire,sizeof(wire));assert(n);
        assert(a.control(wire,n)==Attempts::refused); // No retirement/report yet.
        assert(a.complete(false,true,1));assert(a.state()==Attempts::need_uart_report);
        assert(a.control(wire,n)==Attempts::refused);
        assert(a.report(true));
        if(attempt==5){assert(a.state()==Attempts::exhausted);assert(a.control(wire,n)==Attempts::refused);}
        else{
            Frame wrong=control;wrong.tx=2;n=encode(wrong,again,sizeof(again));assert(a.control(again,n)==Attempts::refused);
            n=encode(control,wire,sizeof(wire));assert(a.control(wire,n)==Attempts::accepted);
            assert(a.control(wire,n)==Attempts::duplicate&&a.attempt()==attempt+1);
        }
    }
    assert(a.failures()==5);assert(!a.begin(f));f.case_id=8;assert(a.begin(f));
    assert(a.complete(true,true,0)&&a.state()==Attempts::passed&&a.failures()==0);
    f.case_id=9;assert(a.begin(f));assert(!a.complete(false,false,1)&&a.state()==Attempts::halted);
    assert(!a.begin(sample()));
    Attempts b;f=sample();assert(b.begin(f));assert(b.complete(false,true,1));assert(!b.report(false));
    assert(b.state()==Attempts::halted);b.infrastructure_fault();assert(b.state()==Attempts::halted);
    f=sample();f.total=169;
    AccuracyModel clean;auto result=run_case(f,clean);
    assert(result.outcome==case_passed&&result.verified_bytes==169&&clean.exchanges==3&&clean.reports==0);
    assert(result.expected_stream_crc==result.received_stream_crc&&result.failed_attempts==0);
    AccuracyModel recovered;recovered.fail_through=1;result=run_case(f,recovered);
    assert(result.outcome==case_passed&&result.attempts==2&&result.failed_attempts==1&&result.first_error==bad_crc);
    assert(recovered.reports==1&&recovered.retries==1&&recovered.exchanges==4);
    AccuracyModel five;five.fail_through=5;result=run_case(f,five);
    assert(result.outcome==case_failed&&result.attempts==5&&five.exchanges==5&&five.reports==5&&five.retries==4);
    AccuracyModel unknown;unknown.unsafe=true;result=run_case(f,unknown);
    assert(result.outcome==ownership_unknown&&unknown.checkpoints==1&&unknown.reports==0&&unknown.retries==0);
    AccuracyModel log;log.fail_log_at=1;result=run_case(f,log);
    assert(result.outcome==log_failed&&log.exchanges==0&&log.attempts==0);
    AccuracyModel uart;uart.fail_through=1;uart.report_ok=false;result=run_case(f,uart);
    assert(result.outcome==infrastructure_failed&&uart.exchanges==1&&uart.retries==0);
    AccuracyModel stale;stale.wrong_case=true;result=run_case(f,stale);
    assert(result.outcome==case_failed&&result.first_error==bad_sequence&&stale.reports==5);
    AccuracyModel peer;peer.peer_nack=true;result=run_case(f,peer);
    assert(result.outcome==case_failed&&result.first_error==bad_pattern&&peer.reports==5);
    AccuracyModel cancel;cancel.keep_running=false;result=run_case(f,cancel);
    assert(result.outcome==cancelled&&cancel.checkpoints==0&&cancel.exchanges==0);
    puts("Accuracy core: corruption, spans, source-safe refusal, five attempts and controls PASS");
}
