/* QUAL-003 finite graphics diagnostic. Autoexec alone selects mode 20.
 * Every output byte and route switch uses public MOS calls owned by EMOS.
 * Preload entire stage into RAM; no file reads, writes or status printing in a
 * measured interval. Resource-upload traffic is retained and identified.
 * Drawing/SoftwareSprites counters overlap; never add them as exclusive costs.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"
#include "cases.h"
extern uint24_t bench_clock(const volatile uint8_t *);
extern uint24_t bench_count(const uint8_t *,uint24_t);
extern void graphics_callback(void);
static volatile uint8_t *sv;
static uint8_t data[MAX_CASE_BYTES];
static FIL file;
static char filename[32],line[640],command[64];
static unsigned review,unattended;
static uint24_t suite_start;
static unsigned saved,route,repeat,case_index,detail,mismatches;
static uint16_t token;
static volatile uint8_t expected_source,armed,received[9],bad;
static volatile uint16_t expected_token;
static volatile uint32_t values[9],counts[9];
static uint8_t review_keycount;
static uint24_t send_ticks,reply_ticks,receive_start,receive_done;
static const char *phase="start";
volatile unsigned graphics_exit_status=1;
__attribute__((noinline)) void graphics_done(void) { __asm__ volatile("nop"); }
/* RST18's documented count is BC, not BCU. Preserve the byte stream while
 * splitting RAM stages larger than 65535 bytes into bounded public API calls. */
static unsigned send_bytes(const uint8_t *p,unsigned n) {
    while(n) {
        unsigned chunk=n>32768?32768:n;
        unsigned status=bench_count(p,chunk);if(status)return status;
        p+=chunk;n-=chunk;
    }
    return 0;
}
static uint32_t u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1]<<8) | ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}
/* Called with IRQs masked. Token/source checks and fixed nine-slot mailbox.
 * A1 in byte3 cannot be a valid ordinary keyboard down byte (only 0 or 1).
 * Stale/unrelated events are ignored; duplicate correlated metrics fail. */
void graphics_receive(const uint8_t *p) {
    if (!armed || p[0]!='Q' || p[1]!='T' || p[2]!='G' || p[3]!=0xA1 ||
        p[7]!=expected_source || (uint16_t)(p[4]|((uint16_t)p[5]<<8))!=expected_token) return;
    unsigned m=p[6];
    if(m>8 || received[m]) {bad=1;return;}
    values[m]=u32(p+8);counts[m]=u32(p+12);
    if(m==1) receive_done=bench_clock(sv);
    received[m]=1; /* publish last */
}
static uint24_t clock_now(void) {return bench_clock(sv);}
static unsigned wait_metric(unsigned m) {
    uint24_t t=clock_now();uint32_t budget=8000000UL;
    while(!received[m] && !bad && clock_now()-t<1200 && --budget) {}
    if(!received[m] || bad)return FR_TIMEOUT;
    return 0;
}
static unsigned request(unsigned op,unsigned flag) {
    uint8_t p[]={23,0,0xEF,op,token,token>>8,flag};
    return send_bytes(p,sizeof p);
}
static unsigned begin(void) {
    review_keycount=sv[sysvar_vkeycount];
    armed=0;++token;if(!token)++token;
    memset((void*)received,0,sizeof received);
    memset((void*)values,0,sizeof values);memset((void*)counts,0,sizeof counts);bad=0;
    expected_token=token;expected_source=route;armed=1;
    unsigned s=request(1,detail);
    return s?s:wait_metric(0);
}
static unsigned end(unsigned op) {
    receive_start=clock_now();unsigned s=request(op,detail);
    if(!s)s=wait_metric(1);
    reply_ticks=(received[1]?receive_done:clock_now())-receive_start;
    for(unsigned m=2;m<=8 && !s;++m) {
        s=request(4,m);if(!s)s=wait_metric(m);
    }
    armed=0;
    for(unsigned i=0;!s && i<9;++i)if(!received[i])s=FR_INT_ERR;
    /* No emulator keys are injected. Diagnostic records must never publish
     * keyboard events, including a count wrap hidden across the whole suite. */
    if(!s && review && sv[sysvar_vkeycount]!=review_keycount)s=FR_INT_ERR;
    return s;
}
static unsigned write_close(const char *s) {
    unsigned n=strlen(s);unsigned status=ffs_fwrite(&file,s,n)==n?0:FR_DISK_ERR;
    unsigned sync=ffs_fsync(&file),close=ffs_fclose(&file);
    return status?status:(sync?sync:close);
}
static unsigned append(const char *s) {
    unsigned status=ffs_fopen(&file,filename,FA_WRITE|FA_OPEN_APPEND);
    return status?status:write_close(s);
}
static unsigned create(void) {
    for(unsigned n=1;n<1000;++n) {
        snprintf(filename,sizeof filename,"GQT%03u.CSV",n);
        unsigned status=ffs_fopen(&file,filename,FA_WRITE|FA_CREATE_NEW);
        if(status==FR_EXIST)continue;
        if(status)return status;
        snprintf(line,sizeof line,"# %s\r\n# MOS ticks are raw; local us never subtracted across processors.\r\nrepeat,route,detail,case,phase,metric,value,count,send_ticks,reply_ticks,bytes,upload_bytes,status\r\n",GRAPHICS_BUILD_ID);
        return write_close(line);
    }
    return FR_EXIST;
}
static unsigned save(unsigned status) {
    for(unsigned i=1;i<9;++i) {
        snprintf(line,sizeof line,"%u,%u,%u,%s,%s,%u,%lu,%lu,%u,%u,%u,%u,%u\r\n",
          repeat,route,detail,cases[case_index].name,phase,i,
          (unsigned long)values[i],(unsigned long)counts[i],send_ticks,reply_ticks,
          cases[case_index].bytes,cases[case_index].uploads,status);
        unsigned s=append(line);if(s)return s;
    }
    ++saved;return status;
}
static unsigned load_case(const Case *c) {
    char path[20];snprintf(path,sizeof path,"%s.DAT",c->name);
    unsigned size=c->setup+c->bytes+c->probes*7;
    uint8_t fd=mos_fopen(path,FA_READ);if(!fd)return FR_NO_FILE;
    unsigned actual=mos_fread(fd,(char*)data,size+1);mos_fclose(fd);
    return actual==size?0:FR_INVALID_PARAMETER;
}
static unsigned switch_route(void) {
    strcpy(command,route?"emos excom --keep-display":"emos legacy --keep-display");
    unsigned s=mos_oscli(command,NULL,0);if(s)return s;
    const uint8_t q[]={23,0,0x86};mos_clearvdpflags(16);
    s=send_bytes(q,sizeof q);if(s)return s;
    s=mos_waitforvdpflags(16);if(s)return s;
    return sv[sysvar_scrMode]==20?0:FR_INVALID_PARAMETER;
}
/* Unattended checkpoints are synced and closed before the named operation.
 * The mainboard text log is updated only while P4 owns the graphics test;
 * public EMOS routing returns to P4 before any measured interval. Never clear
 * or home the text cursor: normal scrolling preserves the visible history.
 * Mainboard graphics cases necessarily overwrite their own screen. */
static unsigned checkpoint(const char *next) {
    phase=next;
    if(!unattended)return 0;
    snprintf(line,sizeof line,"# progress,tick=%lu,rep=%u,route=%u,case=%s,next=%s,saved=%u/%u\r\n",
        (unsigned long)clock_now(),repeat,route,cases[case_index].name,next,saved,CASE_COUNT*16);
    unsigned s=append(line);if(s)return s;
    if(route) {
        strcpy(command,"emos legacy --keep-display");
        s=mos_oscli(command,NULL,0);if(s)return s;
        const uint8_t text[]={26,4,15,17,63,17,128};
        s=send_bytes(text,sizeof text);
        if(!s) {
            snprintf(line,sizeof line,"P4 test %u/4 %s %s [%u/%u]\r\n",
                repeat+1,cases[case_index].name,next,saved,CASE_COUNT*16);
            s=send_bytes((const uint8_t*)line,strlen(line));
        }
        strcpy(command,"emos excom --keep-display");
        unsigned back=mos_oscli(command,NULL,0);
        if(!s)s=back;
    }
    return s;
}
static unsigned settle(void) {
    uint24_t start=clock_now();uint32_t budget=8000000UL;
    while(clock_now()-start<(review?6:120) && --budget) {} /* raw MOS ticks; local us recorded */
    return budget?0:FR_TIMEOUT;
}
static unsigned probes(const Case *c) {
    uint8_t *p=data+c->setup+c->bytes;
    for(unsigned i=0;i<c->probes;++i,p+=7) {
        uint8_t q[]={23,0,0x84,p[0],p[1],p[2],p[3]};mos_clearvdpflags(4);
        unsigned s=send_bytes(q,sizeof q);if(s)return s;
        s=mos_waitforvdpflags(4);if(s)return s;
        uint8_t actual[3]={sv[sysvar_scrpixel],sv[sysvar_scrpixel+1],sv[sysvar_scrpixel+2]};
        unsigned match=!memcmp(actual,p+4,3);mismatches+=!match;
        snprintf(line,sizeof line,"# probe,rep=%u,route=%u,case=%s,index=%u,expected=%u/%u/%u,actual=%u/%u/%u,match=%u\r\n",
            repeat,route,c->name,i,p[4],p[5],p[6],actual[0],actual[1],actual[2],match);
        s=append(line);if(s)return s;
    }
    return 0;
}
int main(int argc,char **argv) {
    review=argc==2 && !strcmp(argv[1],"review");
    unattended=argc==2 && !strcmp(argv[1],"unattended");sv=(volatile uint8_t*)mos_sysvars();
    suite_start=clock_now();
    unsigned status=create();if(status)goto done;
    mos_setkbvector(graphics_callback,0);
    /* One complete off pair followed by three on pairs: identical traffic/order. */
    for(repeat=0;repeat<(review?1:4) && !status;++repeat) {
        detail=review || repeat!=0;
        for(route=0;route<2 && !status;++route) {
            phase="route";status=switch_route();if(status)break;
            for(case_index=0;case_index<CASE_COUNT && !status;++case_index) {
                const Case *c=&cases[case_index];status=checkpoint("preload");if(status)break;
                status=load_case(c);if(status)break;
                status=checkpoint("setup");if(status)break;
                status=c->setup?send_bytes(data,c->setup):0;if(status)break;
                /* Do not emit a zero-sized RST18: MOS interprets zero as string mode. */
                status=checkpoint("draw");if(status)break;
                status=begin();if(status)break;
                uint24_t t=clock_now();if(c->bytes)status=send_bytes(data+c->setup,c->bytes);
                send_ticks=clock_now()-t;
                if(!status)status=end(2);
                status=save(status);if(status)break;
                /* Recurring output window: no VDU refresh, queries or SD traffic. */
                status=checkpoint("output");if(status)break;
                status=begin();if(status)break;
                status=settle();send_ticks=0;
                if(!status)status=end(3);
                status=save(status);if(status)break;
                status=checkpoint("probe");if(status)break;
                status=probes(c);
            }
        }
    }
    armed=0;mos_setkbvector(NULL,0);
    if(unattended) {
        /* MOS increments by two per VBLANK: 120 ticks/s is nominal in mode20.
         * Report raw time too; this is not a calibrated host wall clock.
         * Modulo subtraction supports one low-24-bit wrap (<38.8h at 60Hz).
         * Excludes final timing/terminal writes and the separate voice player. */
        uint24_t finish=clock_now();
        snprintf(line,sizeof line,"# timing,start_tick=%lu,end_tick=%lu,elapsed_ticks=%lu,nominal_hz=120\r\n",
            (unsigned long)suite_start,(unsigned long)finish,
            (unsigned long)((finish-suite_start)&0xFFFFFFUL));
        unsigned s=append(line);if(!status)status=s;
    }
    snprintf(line,sizeof line,"# terminal,status=%u,saved=%u,probe_mismatches=%u,phase=%s\r\n",status,saved,mismatches,phase);
    {unsigned s=append(line);if(!status)status=s;}
done:
    if(unattended) {
        strcpy(command,"emos legacy --keep-display");
        unsigned returned=mos_oscli(command,NULL,0);
        if(!status)status=returned;
        const uint8_t text[]={26,4,15,17,63,17,128};
        (void)send_bytes(text,sizeof text);
    }
    graphics_exit_status=status;
    if(review) {
        strcpy(command,"emos legacy --keep-display");
        unsigned returned=mos_oscli(command,NULL,0);
        if(returned && !graphics_exit_status)graphics_exit_status=returned;
        const uint8_t clear[]={26,17,15,17,128,12};
        (void)send_bytes(clear,sizeof clear);
        printf("Visual validation - screenshot requested\r\n\r\n");
    }
    printf("Graphics timing %s; %u intervals saved to %s; %u probe differences.\r\n",
        status?"incomplete":"complete",saved,filename,mismatches);
    if(review) printf("64 cases per route; mainboard then EDP peer.\r\n"
                      "Native times are functional evidence only.\r\n"
                      "Hardware performance remains unmeasured.\r\n");
    graphics_done();
    /* The launcher plays audio on both complete and failed runs. CSV owns verdict. */
    return unattended?0:status;
}
