// EMOS-001 stopped UART fixture lifecycle adapter, not a new UART test.
// Reuses controller ModeIO, the existing ModeSession and MOS IO bridge.
// Original UART assertions/callback/buffer tests remain in uart_fixture_main.
// No routes, UART registers, firmware or startup files are changed here.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "mode_lifecycle.hpp"
#include "identity.h"
#include "adapter_identity.h"
extern "C" int uart_fixture_main(void);
extern "C" uint24_t bench_clock(const volatile uint8_t *);
extern "C" uint24_t bench_count(const uint8_t *,uint24_t);
static volatile uint8_t *sysvars;
static uint24_t ticks(){return bench_clock(sysvars);}
static bool write_bytes(const uint8_t *p,unsigned n){return bench_count(p,n)==0;}
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
    bool cli_supported(const test_appliance::Mode&s){return s.number==0; /* Native Legacy mode0 cohort. */}
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
        // Preserve the test result; restore ordinary visible/flashing CLI.
        const uint8_t p[]={4,23,1,1,23,1,3};
        return write_bytes(p,sizeof(p));
    }
};
int main(){
    char token[64]{};
    FILE *input=fopen("run-token.txt","rb");
    if(!input){puts("Missing per-run token; UART test not started");return 1;}
    size_t n=fread(token,1,sizeof(token),input);fclose(input);
    if(!n||n>=sizeof(token)){puts("Invalid run token; UART test not started");return 1;}
    for(size_t i=0;i<n;++i)if(!((token[i]>='a'&&token[i]<='z')||
        (token[i]>='0'&&token[i]<='9')||token[i]=='-'))return 1;
    // Reserve completion output before invoking any asynchronous work. A reused
    // result directory refuses entry instead of overwriting old evidence.
    uint8_t completion=mos_fopen("uart-complete.txt",FA_WRITE|FA_CREATE_NEW);
    if(!completion){puts("Completion path already exists or cannot be created");return 1;}
    sysvars=mos_sysvars();ModeIO io;test_appliance::Mode entry{};
    test_appliance::ModeSession<ModeIO> session(io);
    if(!io.query(entry)||!session.begin(entry)){
        puts("UART test requires queried native Legacy mode0; not started");
        mos_fclose(completion);return 1;
    }
    printf("EMOS UART %s: native Legacy mode%u, token %s\n",QUAL_KIND,entry.number,token);
    int result=uart_fixture_main(); // Retains uncertain source forever on timeout.
    bool cleaned=session.restore();
    char line[192];
    int length=snprintf(line,sizeof(line),"EMOS001 %s %s complete result=%d cleanup=%u mode=%u\r\n",
        QUAL_KIND,token,result,cleaned?1:0,entry.number);
    bool recorded=length>0&&length<int(sizeof(line))&&mos_fwrite(completion,line,length)==unsigned(length);
    mos_fclose(completion);
    // This marker is emitted only AFTER original finish/return and cleanup.
    // The coordinator still requires the later MOS prompt before listener entry.
    if(recorded)printf("%s",line);
    return result||!cleaned||!recorded;
}
