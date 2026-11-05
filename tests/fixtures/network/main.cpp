// Generic finite hardware echo appliance; no game records or startup changes.
#include <agon/mos.h>
#include <agon/net.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "mode_lifecycle.hpp"
extern "C" uint24_t bench_clock(const volatile uint8_t*);
extern "C" uint24_t bench_count(const uint8_t*,uint24_t);
static volatile uint8_t*sysvars;
static agon_net_client client;
extern "C" {
void (*agon_net_callback_previous)(void);
void agon_net_callback(void);
unsigned agon_net_callback_packet(const uint8_t*p){
    if(!agon_net_is_reply(p))return 0;
    agon_net_receive(&client,p);return 1;
}
}
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
        auto r=agon_net_take(&client);if(r!=AGON_NET_LOCAL_BUSY)return r;
    }
    return 131;
}
static uint8_t request(uint8_t kind,const uint8_t*p=nullptr,uint8_t n=0){
    auto r=agon_net_submit(&client,kind,p,n);return r?r:wait_reply();
}
static bool parse(const char*s,uint8_t*address){
    unsigned a,b,c,d,port;char tail;
    if(sscanf(s,"%u.%u.%u.%u:%u%c",&a,&b,&c,&d,&port,&tail)!=5||
       a>255||b>255||c>255||d>255||!port||port>65535)return false;
    address[0]=a;address[1]=b;address[2]=c;address[3]=d;address[4]=port;address[5]=port>>8;return true;
}
int main(int argc,char**argv){
    if(argc!=3){puts("Usage: netprobe IPv4:port /agents/extender/results/FRESH.txt");return 19;}
    uint8_t address[6];if(!parse(argv[1],address)){puts("Invalid numeric IPv4:port");return 19;}
    // Restrict result writes to the reserved evidence subtree, never card root.
    if(strncmp(argv[2],"/agents/extender/results/",25)||strstr(argv[2],".."))return 19;
    FILE*prior=fopen(argv[2],"rb");if(prior){fclose(prior);puts("Result already exists");return 19;}
    FILE*result=fopen(argv[2],"wb");if(!result){puts("Cannot create result");return 1;}
    sysvars=mos_sysvars();ModeIO io;test_appliance::ModeSession<ModeIO> mode(io);
    bool ok=mode.begin({20,512,384,64});uint8_t error=0;unsigned passed=0;bool callback=false;
    const auto start=ticks();
    if(ok){const uint8_t text[]={4,17,15,17,128,12};ok=write_bytes(text,sizeof(text));}
    puts("Network echo probe r01 - mainboard mode20");
    puts("Four binary lengths; Escape cancels. No automatic replay.");
    if(ok){
        error=agon_net_begin(&client);ok=!error;
        if(ok){agon_net_callback_previous=reinterpret_cast<void(*)(void)>(agon_net_previous(&client));
            mos_setkbvector(agon_net_callback,0);callback=true;}
    }
    if(ok){error=request(AGON_NET_CONNECT,address,6);ok=!error;}
    auto connecting=ticks();uint32_t connect_fuse=10000000;
    while(ok&&agon_net_status(&client)==AGON_NET_CONNECTING&&
          uint24_t(ticks()-connecting)<240&&--connect_fuse){error=request(AGON_NET_POLL);ok=!error;}
    ok=ok&&connect_fuse&&agon_net_status(&client)==AGON_NET_CONNECTED;
    const unsigned sizes[]={0,1,56,128};
    for(unsigned i=0;ok&&i<4;++i){
        uint8_t payload[128];for(unsigned j=0;j<128;++j)payload[j]=uint8_t(j*37+i);
        printf("Case%u: %u bytes\r\n",i+1,sizes[i]);
        error=request(AGON_NET_SEND,payload,sizes[i]);ok=!error&&agon_net_status(&client)==AGON_NET_ACCEPTED;
        const auto sent=ticks();uint32_t receive_fuse=10000000;
        bool received=false;
        while(ok&&!received&&uint24_t(ticks()-sent)<240&&--receive_fuse){
            error=request(AGON_NET_POLL);ok=!error;
            if(ok&&agon_net_status(&client)==AGON_NET_RECEIVED){
                ok=agon_net_size(&client)==sizes[i]&&!memcmp(agon_net_data(&client),payload,sizes[i]);received=true;
            }else if(ok)ok=agon_net_status(&client)==AGON_NET_CONNECTED;
        }
        ok=ok&&received&&receive_fuse;if(ok)++passed;
    }
    const auto elapsed=uint24_t(ticks()-start);
    auto released=agon_net_release(&client);ok=!released&&ok;
    if(callback)mos_setkbvector(agon_net_callback_previous,0);
    bool restored=mode.restore();
    fprintf(result,"netprobe-r01 passed=%u/4 result=%s error=%u release=%u restore=%u elapsed_ticks=%lu tick_hz_nominal=120\n",
            passed,ok&&restored?"PASS":"FAIL",unsigned(error),unsigned(released),unsigned(restored),(unsigned long)elapsed);
    const bool saved=fclose(result)==0;
    puts(ok&&restored&&saved?"Network echo probe PASS":"Network echo probe FAIL");
    printf("Result: %s; %lu nominal120Hz ticks\r\n",argv[2],(unsigned long)elapsed);
    return ok&&restored&&saved?0:1;
}
