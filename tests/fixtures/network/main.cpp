// Generic finite hardware echo appliance; no game records or startup changes.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"
#include "mode_lifecycle.hpp"
#include "endpoint.hpp"
#include "carrier.hpp"
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
#if defined(NETPROBE_GRAPHICS_CYCLE) || defined(NETPROBE_RFC25_CYCLE)
static uint24_t graphics_ticks[4];
#endif
#ifdef NETPROBE_RFC25_CYCLE
#include "rfc25_cycle.hpp"
extern "C" uint8_t netprobe_rfc_context();
extern "C" uint8_t netprobe_rfc_submit(const uint8_t*,uint24_t,volatile uint8_t*);
static ProbeRfc25Cycle rfc_cycle;
struct RfcIO {
    bool escaped(){return ::escaped();}
    uint8_t context(){return netprobe_rfc_context();}
    uint24_t ticks(){return ::ticks();}
    uint24_t elapsed(uint24_t start){return uint24_t(::ticks()-start);}
    void clear_point(){sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_point);}
    bool point_ready(){return sysvars[sysvar_vdp_pflags]&vdp_pflag_point;}
    void poll(){} // Native interrupts update the flags, never a polling syscall.
    uint8_t submit(const uint8_t*p,unsigned n,volatile uint8_t*done){
        return netprobe_rfc_submit(p,n,done);
    }
};
static uint8_t graphics_cycle(unsigned index){
    RfcIO io;const auto error=rfc_cycle.run(index,io);
    graphics_ticks[index]=uint24_t(rfc_cycle.elapsed);
    if(rfc_cycle.uncertain){
        // Preserve the first fault/static packet/callback in application RAM.
        // No output, SD/MOS call, network RELEASE or return while ownership is
        // uncertain. Host recovery preserves RAM before any subsequent LOAD.
        for(;;)__asm__ volatile("ei\n\thalt" ::: "memory");
    }
    return error;
}
#elif defined(NETPROBE_GRAPHICS_CYCLE)
// Independent owner control: ordinary UART0 VDU, not a game/module/RFC25 test.
// Each query follows its draw in the same stream; no network request is pending.
// A mode response establishes a bounded ordering witness, not optical timing.
static uint8_t graphics_cycle(unsigned index){
    if(escaped())return 130;
    const uint8_t y=uint8_t(32+index*32);
    const uint8_t packet[]={18,0,uint8_t(1+index),25,4,32,0,y,0,
        25,5,224,0,uint8_t(y+32),0,23,0,0x86};
    sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_mode);
    const auto began=ticks();
    if(!write_bytes(packet,sizeof(packet)))return 132;
    uint32_t fuse=8000000;
    while(uint24_t(ticks()-began)<300&&--fuse){
        if(escaped())return 130;
        if(sysvars[sysvar_vdp_pflags]&vdp_pflag_mode){
            graphics_ticks[index]=uint24_t(ticks()-began);
            return sysvars[sysvar_scrMode]==20?0:133;
        }
    }
    return 131; // One outstanding query, no resubmission on timeout.
}
#endif
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
int main(int argc,char**argv){
    puts(NETPROBE_BUILD_ID " [experimental]");
    if(argc!=3){puts("Usage: netprobe IPv4:port /agents/extender/results/FRESH.txt");return 19;}
    uint8_t address[6];if(!parse_endpoint(argv[1],address)){puts("Invalid numeric IPv4:port");return 19;}
    // Restrict result writes to the reserved evidence subtree, never card root.
    if(strncmp(argv[2],"/agents/extender/results/",25)||strstr(argv[2],".."))return 19;
    FILE*prior=fopen(argv[2],"rb");if(prior){fclose(prior);puts("Result already exists");return 19;}
    FILE*result=fopen(argv[2],"wb");if(!result){puts("Cannot create result");return 1;}
    sysvars=mos_sysvars();ModeIO io;test_appliance::ModeSession<ModeIO> mode(io);
    bool ok=mode.begin({20,512,384,64});uint8_t error=0;unsigned passed=0;bool opened=false;
    const auto start=ticks();
    if(ok){const uint8_t text[]={4,17,15,17,128,12};ok=write_bytes(text,sizeof(text));}
    printf("Network echo probe - mainboard mode20; carrier=%s\r\n",probe_carrier);
    puts("Four binary lengths; Escape cancels. No automatic replay.");
#if defined(NETPROBE_GRAPHICS_CYCLE) || defined(NETPROBE_RFC25_CYCLE)
#ifdef NETPROBE_RFC25_CYCLE
    puts("Independent guarded RFC25 draw/point reply after each echo; no raw UART or module.");
#else
    puts("Independent ordinary mainboard draw/query after each echo; no game or module.");
#endif
    unsigned graphics_passed=0;
#endif
    if(ok){error=probe_begin();ok=!error;opened=ok;}
    if(ok){error=request(AGON_NET_CONNECT,address,6);ok=!error;}
    auto connecting=ticks();uint32_t connect_fuse=10000000;
    while(ok&&probe_status()==AGON_NET_CONNECTING&&
          uint24_t(ticks()-connecting)<240&&--connect_fuse){error=request(AGON_NET_POLL);ok=!error;}
    ok=ok&&connect_fuse&&probe_status()==AGON_NET_CONNECTED;
#if defined(NETPROBE_PARALLEL) || defined(NETPROBE_GRAPHICS_CYCLE) || defined(NETPROBE_RFC25_CYCLE)
    const unsigned sizes[]={0,1,127,128};
#else
    const unsigned sizes[]={0,1,56,128};
#endif
    for(unsigned i=0;ok&&i<4;++i){
        uint8_t payload[128];for(unsigned j=0;j<128;++j)payload[j]=uint8_t(j*37+i);
        printf("Case%u: %u bytes\r\n",i+1,sizes[i]);
        error=request(AGON_NET_SEND,payload,sizes[i]);ok=!error&&probe_status()==AGON_NET_ACCEPTED;
        const auto sent=ticks();uint32_t receive_fuse=10000000;
        bool received=false;
        while(ok&&!received&&uint24_t(ticks()-sent)<240&&--receive_fuse){
            error=request(AGON_NET_POLL);ok=!error;
            if(ok&&probe_status()==AGON_NET_RECEIVED){
                ok=probe_size()==sizes[i]&&!memcmp(probe_data(),payload,sizes[i]);received=true;
            }else if(ok)ok=probe_status()==AGON_NET_CONNECTED;
        }
        ok=ok&&received&&receive_fuse;
#if defined(NETPROBE_GRAPHICS_CYCLE) || defined(NETPROBE_RFC25_CYCLE)
        if(ok){error=graphics_cycle(i);ok=!error;if(ok)++graphics_passed;}
#endif
        if(ok)++passed;
    }
    const auto elapsed=uint24_t(ticks()-start);
    auto released=probe_release();
#ifdef NETPROBE_PARALLEL
    // Positive close follows the P4 worker's socket close; BUSY is a
    // non-admission/poll result, not permission to resubmit any payload.
    const auto closing=ticks();uint32_t close_fuse=10000000;
    while(released==31&&uint24_t(ticks()-closing)<240&&--close_fuse)
        released=probe_release();
#endif
    ok=!released&&ok;
    if(released&&opened){
        // Refused close retains carrier ownership. UART may still own a live
        // callback; parallel may have an uncertain physical epoch. Preserve
        // application storage for admitted owner recovery, no reset or replay.
        fprintf(result,"%s close refused release=%u passed=%u/4 terminal_wait=1\n",
                NETPROBE_BUILD_ID,unsigned(released),passed);
        fclose(result);
        puts("Network echo probe: close refused; owner recovery required.");
        for(;;)__asm__ volatile("ei\n\thalt" ::: "memory");
    }
    if(opened)probe_restore_callback();
    bool restored=mode.restore();
    fprintf(result,"%s passed=%u/4 result=%s error=%u release=%u restore=%u elapsed_ticks=%lu tick_hz_nominal=120 carrier=%s size_checks=%u\n",
            NETPROBE_BUILD_ID,passed,ok&&restored?"PASS":"FAIL",unsigned(error),unsigned(released),unsigned(restored),(unsigned long)elapsed,probe_carrier,probe_size_checks);
#ifdef NETPROBE_RFC25_CYCLE
    fprintf(result,"rfc25_cycles=%u/4 source_releases=%u/4 point_replies=%u/4 query_ticks=%lu,%lu,%lu,%lu calibrated=0 ordinary_graphics_test=0\n",
        graphics_passed,rfc_cycle.releases,rfc_cycle.replies,(unsigned long)graphics_ticks[0],
        (unsigned long)graphics_ticks[1],(unsigned long)graphics_ticks[2],(unsigned long)graphics_ticks[3]);
#elif defined(NETPROBE_GRAPHICS_CYCLE)
    fprintf(result,"ordinary_graphics_cycles=%u/4 query_ticks=%lu,%lu,%lu,%lu calibrated=0 rfc25_test=0\n",
        graphics_passed,(unsigned long)graphics_ticks[0],(unsigned long)graphics_ticks[1],
        (unsigned long)graphics_ticks[2],(unsigned long)graphics_ticks[3]);
#endif
    const bool saved=fclose(result)==0;
    puts(ok&&restored&&saved?"Network echo probe PASS":"Network echo probe FAIL");
    printf("Result: %s; %lu nominal120Hz ticks\r\n",argv[2],(unsigned long)elapsed);
    return ok&&restored&&saved?0:1;
}
