// COMMS-001 test-payload protocol only. No MOS/VDP API, peripheral or retry I/O.
#pragma once
#include <stdint.h>
#include <stddef.h>
namespace comms_accuracy {
constexpr size_t header_bytes=40, max_payload=84, max_wire=128;
constexpr uint32_t max_logical=16UL*1024*1024;
enum Kind:uint8_t {data=1,ack=2,nack=3,retry=4};
enum Status:uint8_t {ok=0,bad_crc=1,bad_pattern=2,bad_sequence=3,timeout=4,owner_fault=5};
inline uint16_t get16(const uint8_t*p){return uint16_t(p[0])|(uint16_t(p[1])<<8);}
inline uint32_t get32(const uint8_t*p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
inline void put16(uint8_t*p,uint16_t v){p[0]=uint8_t(v);p[1]=uint8_t(v>>8);}
inline void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=uint8_t(v>>(8*i));}
inline uint32_t crc32(const uint8_t*p,size_t n){
    uint32_t v=0xffffffffUL;
    for(size_t i=0;i<n;++i){v^=p[i];for(unsigned b=0;b<8;++b)v=(v>>1)^((v&1)?0xedb88320UL:0);}
    return v^0xffffffffUL;
}
inline uint8_t pattern_byte(uint8_t pattern,uint32_t seed,uint32_t at){
    switch(pattern){
    case 0:return 0;case 1:return 255;case 2:return (at&1)?255:0;
    case 3:return uint8_t(1u<<((at+seed)&7));case 4:return uint8_t(at+seed);
    default:{uint32_t v=seed^at^0x9e3779b9UL;v^=v>>16;v*=0x7feb352dUL;v^=v>>15;v*=0x846ca68bUL;v^=v>>16;return uint8_t(v);}
    }
}
struct Frame {
    uint8_t kind=data,tx=1,rx=1,pattern=0,attempt=1,direction=0,status=ok,flags=0;
    uint32_t run=0,case_id=0,sequence=0,seed=0,total=0,offset=0;
    uint16_t length=0;
    uint8_t payload[max_payload]{};
};
inline bool valid(const Frame&f){
    if(f.kind<data||f.kind>retry||f.tx<1||f.tx>2||f.rx<1||f.rx>2||f.pattern>5||
       !f.run||!f.case_id||!f.sequence||!f.attempt||f.attempt>5||f.direction>1||
       f.status>owner_fault||(f.flags&~1)||f.length>max_payload||f.total>max_logical||f.offset>f.total)return false;
    if(f.kind==data||f.kind==ack)return f.status==ok&&f.length<=f.total-f.offset;
    if(f.kind==nack)return f.status!=ok&&f.length==8;
    return f.status==ok&&f.length==0&&f.flags==1;
}
inline size_t encode(const Frame&f,uint8_t*out,size_t capacity){
    size_t n=header_bytes+f.length+4;if(!valid(f)||!out||capacity<n)return 0;
    for(size_t i=0;i<header_bytes;++i)out[i]=0;
    out[0]='C';out[1]='A';out[2]='0';out[3]='1';out[4]=f.kind;out[5]=f.tx;out[6]=f.rx;out[7]=f.pattern;
    put32(out+8,f.run);put32(out+12,f.case_id);put32(out+16,f.sequence);put32(out+20,f.seed);
    put32(out+24,f.total);put32(out+28,f.offset);out[32]=f.attempt;out[33]=f.direction;
    put16(out+34,f.length);out[36]=f.status;out[37]=f.flags;
    for(unsigned i=0;i<f.length;++i)out[header_bytes+i]=f.payload[i];
    put32(out+n-4,crc32(out,n-4));return n;
}
enum Decode {decoded=0,invalid=1,crc_error=2};
inline Decode decode(const uint8_t*p,size_t n,Frame&out){
    if(!p||n<header_bytes+4||n>max_wire)return invalid;
    if(crc32(p,n-4)!=get32(p+n-4))return crc_error;
    if(p[0]!='C'||p[1]!='A'||p[2]!='0'||p[3]!='1'||p[38]||p[39]||size_t(get16(p+34))+header_bytes+4!=n)return invalid;
    Frame f;f.kind=p[4];f.tx=p[5];f.rx=p[6];f.pattern=p[7];f.run=get32(p+8);f.case_id=get32(p+12);
    f.sequence=get32(p+16);f.seed=get32(p+20);f.total=get32(p+24);f.offset=get32(p+28);
    f.attempt=p[32];f.direction=p[33];f.length=get16(p+34);f.status=p[36];f.flags=p[37];
    if(!valid(f))return invalid;
    for(unsigned i=0;i<f.length;++i)f.payload[i]=p[header_bytes+i];
    out=f;return decoded; // Never publish a partial or bad-CRC header.
}
inline bool correct_pattern(const Frame&f,uint32_t*first=nullptr){
    if(f.kind!=data&&f.kind!=ack)return false;
    for(unsigned i=0;i<f.length;++i)if(f.payload[i]!=pattern_byte(f.pattern,f.seed,f.offset+i)){
        if(first)*first=f.offset+i;
        return false;
    }
    return true;
}
// Positive retirement and verified UART report are independent prerequisites.
// This pure state machine sends no bytes and can never reset/replay hardware.
class Attempts {
 public:
    enum State {idle,active,need_uart_report,need_retry,passed,exhausted,halted};
    enum Control {accepted,duplicate,refused};
    bool begin(const Frame&f){
        if(!valid(f)||f.kind!=data||f.sequence!=1||f.offset||f.attempt!=1||f.direction||
           (state_!=idle&&state_!=passed&&state_!=exhausted))return false;
        if(f.run==run_&&f.case_id<=case_)return false;
        run_=f.run;case_=f.case_id;tx_=f.tx;rx_=f.rx;pattern_=f.pattern;seed_=f.seed;total_=f.total;
        attempt_=1;failures_=0;failed_sequence_=0;state_=active;return true;
    }
    bool complete(bool success,bool retired,uint32_t failed_sequence){
        if(state_!=active)return false;
        if(!retired||(!success&&!failed_sequence)){state_=halted;return false;}
        if(success){state_=passed;return true;}
        ++failures_;failed_sequence_=failed_sequence;state_=need_uart_report;return true;
    }
    bool report(bool verified_uart){
        if(state_!=need_uart_report)return false;
        if(!verified_uart){state_=halted;return false;}
        state_=(attempt_==5)?exhausted:need_retry;return true;
    }
    Control control(const uint8_t*p,size_t n){
        Frame f;if(decode(p,n,f)!=decoded||f.kind!=retry||f.run!=run_||f.case_id!=case_||f.sequence!=failed_sequence_||
            f.tx!=tx_||f.rx!=rx_||f.pattern!=pattern_||f.seed!=seed_||f.total!=total_||f.offset||f.direction!=1)return refused;
        if(state_==active&&attempt_>1&&f.attempt==attempt_-1)return duplicate;
        if(state_!=need_retry||f.attempt!=attempt_)return refused;
        ++attempt_;state_=active;return accepted;
    }
    void infrastructure_fault(){state_=halted;}
    State state()const{return state_;}
    unsigned attempt()const{return attempt_;}
    unsigned failures()const{return failures_;}
 private:
    State state_=idle;uint32_t run_=0,case_=0,failed_sequence_=0,seed_=0,total_=0;
    uint8_t attempt_=0,failures_=0,tx_=0,rx_=0,pattern_=0;
};
}
