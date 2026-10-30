// Application-owned normalized controller input. No allocation, device report
// decoding, application ISR, UART/GPIO access or MOSlet is involved.
// Keep Client in ordinary application RAM (normally a static object): EMOS
// rejects gateway/buffers on the MOS-owned stack or at/above 0xB0000.
// Call with interrupts enabled at a complete VDU command boundary. EMOS alone
// admits and owns the P4 transport; this include never changes that admission.
#pragma once
#include <stdint.h>
#include <string.h>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
// BEGIN mechanically copied appliance_wire.h
/* Developmental EMOS/application controller carrier. Mirrored by the EMOS
 * candidate; no MOS API slot, SD lease or keyboard payload is repurposed.
 * CI requests use the existing F7/16 Extender control envelope; replies use
 * Extender-local UART1 type8E. Version2 removes the agent-added CRCs under
 * the Author's2026-10-25 instruction. The fixed carrier's last two bytes are
 * reserved zero; the result has no checksum trailer. See INPUT-001. */
#ifndef EXT_CONTROLLER_APPLIANCE_WIRE_H
#define EXT_CONTROLLER_APPLIANCE_WIRE_H
#define CONTROLLER_REPLY 0x8E
#define CONTROLLER_CARRIER_VERSION 2
#define CONTROLLER_RESULT_MAGIC "CIS2"
#define CONTROLLER_RESULT_SIZE 96
#define CONTROLLER_BATCH 8
/* Application-owned controller interpretation: distinct gateway operations
 * reject the older resident-semantic ABI. CI2/CIS2 UART bytes are unchanged. */
#define CONTROLLER_GATEWAY_OPEN 4
#define CONTROLLER_GATEWAY_RECEIVE 5
#define CONTROLLER_GATEWAY_SEND 6
#define CONTROLLER_GATEWAY_CLOSE 7
#define CONTROLLER_GATEWAY_RESULT_SIZE 98
#define CONTROLLER_GATEWAY_SEND_SIZE 20
static unsigned short controller_u16(const unsigned char*p){return p[0]|((unsigned short)p[1]<<8);}
static unsigned long controller_u32(const unsigned char*p){return (unsigned long)controller_u16(p)|((unsigned long)controller_u16(p+2)<<16);}
static void controller_put16(unsigned char*p,unsigned short v){p[0]=v;p[1]=v>>8;}
static void controller_put32(unsigned char*p,unsigned long v){controller_put16(p,v);controller_put16(p+2,v>>16);}
#endif
// END mechanically copied appliance_wire.h
#pragma GCC diagnostic pop

#if defined(_EZ80)
#include <agon/mos.h>
// Checked against maintained EMOS mos_api.inc by the application builder.
#define AGON_CONTROLLER_MOS_GETFUNCTION 0x50
#define AGON_CONTROLLER_EMOS_GATEWAY 0x51
#define AGON_CONTROLLER_EMOS_FUNCTION_GATEWAY 0x20
#define AGON_CONTROLLER_STRINGIFY_INNER(value) #value
#define AGON_CONTROLLER_STRINGIFY(value) AGON_CONTROLLER_STRINGIFY_INNER(value)
#endif

namespace agon { namespace controller {
enum class Control : uint8_t {
    A, B, Y, X, LeftShoulder, RightShoulder, Back, Start, Guide,
    LeftStick, RightStick, Left, Right, Up, Down
};
enum class Axis : uint8_t { LeftX, LeftY, RightX, RightY };
enum : unsigned { ControlCount=15, TransportResultSize=CONTROLLER_GATEWAY_RESULT_SIZE };
enum : uint8_t { Open=CONTROLLER_GATEWAY_OPEN, Receive=CONTROLLER_GATEWAY_RECEIVE,
                 Send=CONTROLLER_GATEWAY_SEND, Close=CONTROLLER_GATEWAY_CLOSE };
enum : uint32_t { Ok=0, Invalid=19, Busy=31, Unavailable=35 };
inline uint8_t axis8(int16_t value) { return uint8_t((int32_t(value)+32768)>>8); }
struct State {
    int16_t stick[4]{};
    uint8_t trigger[2]{};
    uint16_t held{}, presses[ControlCount]{};
    uint32_t sequence{}, age_ms{};
    uint16_t generation{};
    // Opaque P4 receiver and acquisition-session identities, not USB IDs.
    uint8_t source[16]{};
    bool connected{}, valid{};
    bool down(Control control) const { return valid&&(held&(uint16_t(1)<<unsigned(control))); }
    uint8_t stick8(Axis axis) const { return axis8(stick[unsigned(axis)]); }
};

#if defined(_EZ80)
// The SDK has no getfunction declaration. These register-preserving leaves
// reproduce the maintained MOS gateway bindings without a second file.
// They invoke MOS, never peripheral registers. No callback survives a call.
class Gateway {
    uint8_t request_[66]{};
    static __attribute__((naked,noinline)) uint24_t available_native() {
        __asm__ volatile(
            "push ix\n push iy\n"
            "ld b," AGON_CONTROLLER_STRINGIFY(AGON_CONTROLLER_EMOS_FUNCTION_GATEWAY) "\n"
            "ld c,0\n ld a," AGON_CONTROLLER_STRINGIFY(AGON_CONTROLLER_MOS_GETFUNCTION) "\n"
            "rst.lil 08h\n or a\n ld hl,0\n jr nz,1f\n inc hl\n"
            "1: pop iy\n pop ix\n ret\n");
    }
    static __attribute__((naked,noinline)) uint24_t call_native(uint8_t*) {
        __asm__ volatile(
            "push ix\n ld ix,0\n add ix,sp\n push iy\n ld hl,(ix+6)\n"
            "ld a," AGON_CONTROLLER_STRINGIFY(AGON_CONTROLLER_EMOS_GATEWAY) "\n"
            "rst.lil 08h\n ld hl,0\n ld l,a\n pop iy\n pop ix\n ret\n");
    }
    static void pointer(uint8_t*p,const void*address) {
        const uint24_t value=reinterpret_cast<uint24_t>(address);
        p[0]=value;p[1]=value>>8;p[2]=value>>16;
    }
 public:
    bool available() { return available_native()!=0; }
    uint32_t clock() { return getsysvar_time(); }
    uint32_t exchange(uint8_t*input,unsigned length,uint8_t*output,
                      unsigned capacity,unsigned&received) {
        memset(request_,0,sizeof(request_));
        request_[0]=66;request_[2]=1;request_[4]=3;request_[5]=10;request_[6]=2;
        pointer(request_+10,input);request_[13]=length;
        if(capacity){pointer(request_+16,output);request_[19]=capacity;}
        memcpy(request_+25,"ext",3);memcpy(request_+41,"controller",10);
        const uint32_t result=call_native(request_);
        received=unsigned(request_[22])|(unsigned(request_[23])<<8)|(unsigned(request_[24])<<16);
        return result;
    }
};
template<class Binding=Gateway>
#else
// Host models supply the same three Binding methods as Gateway. exchange()
// receives native pointers, so a model need not truncate them into 24 bits.
template<class Binding>
#endif
class Client {
    Binding binding_;
    uint8_t input_[CONTROLLER_GATEWAY_SEND_SIZE]{},output_[TransportResultSize]{};
    State state_{};
    uint32_t token_=0,edge_=0,sample_at_=0,sample_age_=0;
    uint16_t query_=0;
    bool opened_=false,failed_=false,waiting_=false,have_source_=false,have_sample_=false;
    void neutralize(bool disconnected=false) {
        state_.valid=false;state_.held=0;
        memset(state_.stick,0,sizeof(state_.stick));memset(state_.trigger,0,sizeof(state_.trigger));
        if(disconnected)state_.connected=false;
    }
    bool fail(uint32_t result) { error=result;failed_=true;neutralize(true);return false; }
    uint32_t call(uint8_t operation,unsigned length=1,unsigned capacity=0) {
        error_operation=operation;input_[0]=operation;
        unsigned received=0;
        const uint32_t result=binding_.exchange(input_,length,output_,capacity,received);
        if(result==Ok&&operation==Open)opened_=true;
        if(result==Ok&&received!=capacity)return Invalid;
        return result;
    }
    bool open_transport() {
        error=call(Open,1,4);
        if(error){
            const uint32_t saved=error;
            // A successful OPEN with malformed result length still allocated
            // a lease. A refused/busy OPEN never authorizes closing another.
            if(opened_){call(Close);opened_=false;}
            error_operation=Open;return fail(saved);
        }
        opened_=true;token_=controller_u32(output_);query_=0;waiting_=false;
        if(!token_||output_[3]){
            call(Close);opened_=false;error_operation=Open;return fail(Invalid);
        }
        return true;
    }
    uint32_t send(uint8_t operation) {
        if(query_==65535)return Unavailable;
        memset(input_,0,sizeof(input_));input_[1]=23;input_[3]=0xf7;
        auto*p=input_+4;p[0]='C';p[1]='I';p[2]=CONTROLLER_CARRIER_VERSION;p[3]=operation;
        controller_put32(p+4,token_);controller_put32(p+8,edge_);controller_put16(p+12,query_+1);
        const uint32_t result=call(Send,sizeof(input_));
        if(result==Ok){++query_;waiting_=operation==1;}
        return result;
    }
    bool decode() {
        const auto*p=output_;
        if(memcmp(p,CONTROLLER_RESULT_MAGIC,4)||controller_u32(p+4)!=token_||
           controller_u16(p+8)!=query_||p[10]>3||p[10]==2||p[11]>CONTROLLER_BATCH||p[46]||p[47]||
           output_[96]>=30||output_[97]>=30)return false;
        const uint16_t held=controller_u16(p+34);
        if((held&0x8000)||(held&0x1800)==0x1800||(held&0x6000)==0x6000)return false;
        for(unsigned i=0;i<p[11];++i){
            const auto*e=p+48+i*6;
            if(!controller_u32(e)||e[4]>=ControlCount||e[5]>1||
               (i&&controller_u32(e)!=controller_u32(e-6)+1))return false;
        }
        for(unsigned i=48+p[11]*6;i<CONTROLLER_RESULT_SIZE;++i)if(p[i])return false;
        if(!(p[10]&2)){
            if(p[11])return false;
            for(unsigned i=34;i<46;++i)if(p[i])return false;
        }
        const bool changed=!have_source_||memcmp(state_.source,p+12,16);
        // Validate the entire batch before changing source, counts or ACK.
        uint32_t next=changed?0:edge_;
        for(unsigned i=0;i<p[11];++i){
            const uint32_t id=controller_u32(p+48+i*6);
            if(id>next){if(next&&id!=next+1)return false;next=id;}
        }
        if(changed){
            memcpy(state_.source,p+12,16);have_source_=true;edge_=0;
            ++state_.generation;memset(state_.presses,0,sizeof(state_.presses));
        }
        state_.sequence=controller_u32(p+28);state_.connected=p[10]&1;
        // Nominal bounds, not calibrated physical milliseconds. Each local
        // delta has its own whole-tick phase allowance, as in the old service.
        sample_age_=uint32_t(controller_u16(p+32))+
                    (uint32_t(output_[96])+2+uint32_t(output_[97])+2)*9;
        sample_at_=binding_.clock();have_sample_=true;state_.age_ms=sample_age_;
        if(!(p[10]&2)||sample_age_>=250){neutralize();return true;}
        state_.valid=true;state_.held=held;
        for(unsigned i=0;i<4;++i)state_.stick[i]=int16_t(controller_u16(p+36+i*2));
        memcpy(state_.trigger,p+44,2);
        for(unsigned i=0;i<p[11];++i){
            const auto*e=p+48+i*6;const uint32_t id=controller_u32(e);
            if(id>edge_){
                if(e[5]&&state_.presses[e[4]]!=65535)++state_.presses[e[4]];
                edge_=id;
            }
        }
        return true;
    }
    void age() {
        if(!have_sample_)return;
        const uint32_t ticks=binding_.clock()-sample_at_;
        state_.age_ms=ticks>7281?65535:sample_age_+ticks*9;
        if(state_.age_ms>65535)state_.age_ms=65535;
        if(state_.age_ms>=250)neutralize();
    }
    bool close_transport() {
        if(!opened_)return true;
        const uint32_t wire=failed_?Ok:send(2);
        const uint8_t wire_operation=error_operation;
        const uint32_t local=call(Close);
        opened_=false;
        error=wire?wire:local;
        if(wire)error_operation=wire_operation;
        return error==Ok;
    }
 public:
    uint32_t error=0;
    uint8_t error_operation=0;
    explicit Client(const Binding&binding=Binding{}):binding_(binding) {}
    Client(const Client&)=delete;
    Client&operator=(const Client&)=delete;
    const State& state() const { return state_; }
    bool open() {
        if(opened_){error=Busy;error_operation=Open;return false;}
        error_operation=Open;
        if(!binding_.available())return fail(Unavailable);
        failed_=false;
        if(!open_transport())return false;
        state_=State{};edge_=0;have_source_=have_sample_=false;
        return true;
    }
    // RECEIVE never waits. A new request may encounter EMOS's existing bounded
    // serializer wait. False neutralizes state; only explicit close/open recovers.
    bool update() {
        if(!opened_||failed_)return false;
        error=call(Receive,1,TransportResultSize);
        if(error==Ok){
            waiting_=false;
            if(!decode())return fail(Invalid);
            if(query_>=65000){
                if(!close_transport())return fail(error);
                failed_=false;
                if(!open_transport())return false; // Preserve source/counts across healthy renewal.
                age(); // The wire CLOSE may have spent the sample's freshness budget.
                return true;
            }
        }else if(error!=Busy)return fail(error);
        age();
        if(waiting_)return true;
        error=send(1);
        age(); // The bounded serializer may have waited after the earlier age check.
        return error==Ok||error==Busy?true:fail(error);
    }
    bool close() {
        const bool ok=close_transport();neutralize(true);return ok;
    }
};
}} // namespace agon::controller
