// NET-004 isolated async echo case; deliberately separate from frozen repeat.cpp.
// Same deterministic matrix and mode lifecycle. UART0/SD only after positive
// source+tail/reply/close boundaries. This is correctness, not overlap or speed.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"
#include "mode_lifecycle.hpp"
#include "endpoint.hpp"
#include "async_carrier.hpp"
extern "C" uint24_t bench_clock(const volatile uint8_t*);
extern "C" uint24_t bench_count(const uint8_t*,uint24_t);
static volatile uint8_t*sysvars;
static uint24_t ticks(){return bench_clock(sysvars);}
static bool write_bytes(const uint8_t*p,unsigned n){return bench_count(p,n)==0;}
struct ModeIO {
    int expected_mode=-1;
    bool query(test_appliance::Mode &out){
        sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_mode);
        const uint8_t p[]={23,0,0x86};if(!write_bytes(p,sizeof(p)))return false;
        auto start=ticks();uint32_t fuse=8000000;
        // Stock VDP v2.16.0 vdu_fonts.h emits unsolicited mode information
        // when selecting/deleting fonts. Cleanup can leave a mode20 reply
        // ahead of the selected entry-mode reply. A shared completion flag
        // cannot identify which request produced it. Keep the one query
        // outstanding and consume replies until the selected mode arrives;
        // never mistake that earlier font reply for failed restoration.
        while(uint24_t(ticks()-start)<600&&--fuse){
            if(!(sysvars[sysvar_vdp_pflags]&vdp_pflag_mode))continue;
            out={sysvars[sysvar_scrMode],uint16_t(getsysvar_scrwidth()),uint16_t(getsysvar_scrheight()),sysvars[sysvar_scrColours]};
            if(out.width&&out.height&&out.colours&&
               (expected_mode<0||out.number==expected_mode)){
                expected_mode=-1;return true;
            }
            sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_mode);
        }
        expected_mode=-1;return false;
    }
    bool cli_supported(const test_appliance::Mode&s){return s.number<128;}
    bool select(uint8_t mode){
        const uint8_t p[]={22,mode};
        if(!write_bytes(p,sizeof(p)))return false;
        expected_mode=mode;return true;
    }
    bool settle(){
        // Nominal sysvar clock advances twice per60/70Hz VBlank.160ticks
        // exceeds one second on either, with an independent stopped-clock fuse.
        auto start=ticks();uint32_t fuse=10000000;
        while(uint24_t(ticks()-start)<160&&--fuse){}
        return fuse!=0;
    }
    bool prepare_cli(){
        const uint8_t p[]={4,23,1,1,23,1,3};return write_bytes(p,sizeof(p));
    }
};

static bool escaped(){return sysvars[sysvar_vkeydown]&&sysvars[sysvar_keyascii]==27;}
static uint8_t wait_reply(){
    auto start=ticks();uint32_t fuse=12000000;
    while(uint24_t(ticks()-start)<60&&--fuse){
        if(escaped())return 130;
        auto r=probe_take();if(r!=AGON_NET_LOCAL_BUSY)return r;
    }
    return 131;
}
static uint8_t request(uint8_t kind,const uint8_t*p=nullptr,uint8_t n=0){
    auto r=probe_submit(kind,p,n);return r?r:wait_reply();
}
#include "repeat_matrix.hpp"
// Fixed-layout RAM witness survives quarantine; no logging/MOS under live borrow.
extern "C" {
volatile struct AsyncWitness {
    uint32_t magic,session,index,passed;
    uint8_t first_error,release,quarantine;
} async_witness={0x31585255,0,0,0,0,0,0};
}
static uint8_t release_positive(){
    auto r=probe_release();const auto began=ticks();uint32_t fuse=10000000;
    while(r==31&&uint24_t(ticks()-began)<240&&--fuse)r=probe_release();
    return r;
}
int main(int argc,char**argv){
    puts(NETPROBE_BUILD_ID " [experimental]");
    if(argc!=3){puts("Usage: netasync IPv4:port /agents/extender/results/FRESH.txt");return 19;}
    uint8_t address[6];if(!parse_endpoint(argv[1],address))return 19;
    if(strncmp(argv[2],"/agents/extender/results/",25)||strstr(argv[2],".."))return 19;
    FILE*prior=fopen(argv[2],"rb");if(prior){fclose(prior);return 19;}
    FILE*result=fopen(argv[2],"wb");if(!result)return 1;
    sysvars=mos_sysvars();ModeIO io;test_appliance::ModeSession<ModeIO> mode(io);
    bool ok=mode.begin({20,512,384,64});uint8_t error=0,released=0;
    unsigned passed=0,opened_sessions=0,closed_sessions=0;
    const auto began=ticks();
    if(ok){const uint8_t text[]={4,17,15,17,128,12};ok=write_bytes(text,sizeof(text));}
    puts("Async UART1 probe: 4 sessions, 176 exact records; Escape cancels.");
    for(unsigned session=0;ok&&session<probe_repeat::sessions;++session){
        printf("Session%u/4: 44 records, four bit patterns; no retry.\r\n",session+1);
        // Ordered mode reply drains preceding UART0 text before live NM.
        test_appliance::Mode observed;
        if(!io.query(observed)||observed.number!=20){error=133;ok=false;break;}
        async_witness.session=session;async_witness.index=0;
        // Flush all SD work before attaching the next live NM service.
        if(fflush(result)){error=1;ok=false;break;}
        error=probe_begin();ok=!error;
        if(!ok){
            released=release_positive();
            if(released){async_witness.first_error=error;async_witness.release=released;
                async_witness.quarantine=1;for(;;)__asm__ volatile("ei\n\thalt" ::: "memory");}
            probe_restore_callback();break;
        }
        ++opened_sessions;
        error=request(AGON_NET_CONNECT,address,6);ok=!error;
        auto start=ticks();uint32_t connect_fuse=10000000;
        while(ok&&probe_status()==AGON_NET_CONNECTING&&uint24_t(ticks()-start)<240&&--connect_fuse){
            error=request(AGON_NET_POLL);ok=!error;
        }
        ok=ok&&connect_fuse&&probe_status()==AGON_NET_CONNECTED;
        if(!ok&&!error)error=AGON_NET_PROTOCOL_ERROR;
        for(unsigned index=0;ok&&index<probe_repeat::records_per_session;++index){
            if(escaped()||uint24_t(ticks()-began)>=14400){error=130;ok=false;break;}
            async_witness.index=index;
            uint8_t payload[128];const unsigned n=probe_repeat::size(index);
            for(unsigned j=0;j<n;++j)payload[j]=probe_repeat::byte(session,index,j);
            error=request(AGON_NET_SEND,payload,n);ok=!error&&probe_status()==AGON_NET_ACCEPTED;
            start=ticks();uint32_t receive_fuse=10000000;bool received=false;
            while(ok&&!received&&uint24_t(ticks()-start)<240&&--receive_fuse){
                error=request(AGON_NET_POLL);ok=!error;
                if(ok&&probe_status()==AGON_NET_RECEIVED){
                    ok=probe_size()==n&&!memcmp(probe_data(),payload,n);received=true;
                }else if(ok)ok=probe_status()==AGON_NET_CONNECTED;
            }
            ok=ok&&received&&receive_fuse;
            if(!ok&&!error)error=AGON_NET_PROTOCOL_ERROR;
            if(ok){++passed;async_witness.passed=passed;}
        }
        // Each of the four sessions is declared, never a reconnect on failure.
        // Positive local close alone permits starting the next session.
        released=release_positive();
        if(released){
            async_witness.first_error=error;async_witness.release=released;
            async_witness.quarantine=1;
            for(;;)__asm__ volatile("ei\n\thalt" ::: "memory");
        }
        probe_restore_callback();++closed_sessions;
        fprintf(result,"session=%u records=%u first_error=%u source_phase=%u close=0\n",
                session,passed,unsigned(error),unsigned(client.tx.phase));
        if(fflush(result)){error=1;ok=false;}

    }
    // Every installed callback has already been restored after positive close.
    const auto elapsed=uint24_t(ticks()-began);const bool restored=mode.restore();
    fprintf(result,"%s result=%s first_error=%u records=%u/176 opened=%u/4 closed=%u/4 release=%u restore=%u elapsed_ticks=%lu tick_hz_nominal=120 carrier=uart1-async irq_complete=0\n",
        NETPROBE_BUILD_ID,ok&&restored?"PASS":"FAIL",unsigned(error),passed,opened_sessions,
        closed_sessions,unsigned(released),unsigned(restored),(unsigned long)elapsed);
    const bool saved=fclose(result)==0;
    puts(ok&&restored&&saved?"Async UART1 probe PASS":"Async UART1 probe FAIL");
    return ok&&restored&&saved?0:1;
}
