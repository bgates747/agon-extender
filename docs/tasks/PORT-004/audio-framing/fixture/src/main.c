/* AFPROBE-r01: caller selects mode136 and route. Audio/pixel fences are
 * correctness checks, not renderer timing. Stock samples are silent. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint8_t *sv;
static char line[180];
static const char *output;
static unsigned failures,probes;
static void send(const uint8_t *p,unsigned n){mos_puts((const char*)p,n,0);}
static int append(const char *s){
    uint8_t f=mos_fopen(output,FA_WRITE|FA_OPEN_APPEND);if(!f)return 0;
    unsigned n=strlen(s),got=mos_fwrite(f,(char*)s,n);mos_fclose(f);return got==n;
}
static void plot(uint8_t op,int x,int y){
    uint8_t p[]={25,op,x,x>>8,y,y>>8};send(p,sizeof p);
}
static void viewport(int left,int top,int right,int bottom){
    uint8_t p[]={24,left,left>>8,bottom,bottom>>8,right,right>>8,top,top>>8};
    send(p,sizeof p);plot(4,left,top); /* Same clip activation as current hud.hpp. */
}
static void colour(unsigned c){uint8_t p[]={18,0,c};send(p,sizeof p);}
static void rect(int x1,int y1,int x2,int y2,unsigned c){colour(c);plot(4,x1,y1);plot(101,x2,y2);}
static int probe(unsigned frame,int x,int y,unsigned r,unsigned g,unsigned b){
    uint8_t q[]={23,0,0x84,x,x>>8,y,y>>8};mos_clearvdpflags(4);send(q,sizeof q);
    unsigned status=mos_waitforvdpflags(4);if(status)return 0;
    /* Stock ABI is R,G,B in the three wire bytes, despite legacy field names. */
    unsigned a=sv[sysvar_scrpixel],c=sv[sysvar_scrpixel+1],d=sv[sysvar_scrpixel+2];
    unsigned match=r==999 || (a==r&&c==g&&d==b);++probes;failures+=!match;
    snprintf(line,sizeof line,"probe,%u,%d,%d,%u,%u,%u,%u,%u,%u,%u\r\n",frame,x,y,r,g,b,a,c,d,match);
    return append(line);
}
static int audio(unsigned frame,const uint8_t *data,unsigned length,int unavailable){
    const uint8_t prefix[]={23,0,0x85};
    mos_clearvdpflags(vdp_pflag_audio);send(prefix,sizeof prefix);send(data,length);
    unsigned timeout=mos_waitforvdpflags(vdp_pflag_audio);
    unsigned expected=(data[1]==1 || data[1]==2)?255:0;
    unsigned channel=sv[sysvar_audioChannel],status=sv[syscar_audioSuccess];
    unsigned match=!timeout && channel==data[0] && (!unavailable || status==expected);
    failures+=!match;
    snprintf(line,sizeof line,"audio,%u,%u,%u,%u,%u,%u,%u,%u\r\n",frame,data[1],data[0],channel,status,expected,timeout,match);
    if(!append(line)||!match)return 0;
    return probe(frame,160,12,170,0,0)&&probe(frame,160,60,0,0,170)&&probe(frame,160,180,0,170,0);
}
int main(int argc,char **argv){
    if(argc!=3)return 2;output=argv[1];sv=mos_sysvars();const int unavailable=!strcmp(argv[2],"unavailable");
    if(!unavailable && strcmp(argv[2],"stock"))return 2;
    uint8_t existing=mos_fopen(output,FA_READ);if(existing){mos_fclose(existing);return 3;}
    uint8_t q[]={23,0,0x86};mos_clearvdpflags(16);send(q,sizeof q);if(mos_waitforvdpflags(16))return 4;
    if((sv[sysvar_scrMode]&127)!=8)return 5;
    if(!append("AFPROBE-r01,mode136-required,correctness-only\r\n"))return 6;
    const uint8_t init[]={23,0,0xC0,0,23,1,0};send(init,sizeof init);
    const uint8_t swap[]={23,0,0xC3};
    for(unsigned frame=0;frame<2;++frame){
        viewport(0,0,319,239);rect(0,0,319,23,1);rect(0,24,319,103,4);rect(0,104,319,239,2);
#define AUDIO(...) do{const uint8_t cmd[]={__VA_ARGS__};if(!audio(frame,cmd,sizeof cmd,unavailable))return 8;}while(0)
        AUDIO(0,8);AUDIO(0,10);AUDIO(0,4,3);AUDIO(0,2,0);AUDIO(0,1);
        /* Exact Rally frequency messages whose low bytes resemble CLS/CLG. */
        AUDIO(0,3,12,1);AUDIO(0,3,16,1);AUDIO(0,3,23,1);
        AUDIO(0,6,1,12,0,16,0,0,23,0);
        AUDIO(0,6,2,1,0,12,0,0,1,0,16,0);
        AUDIO(0,7,1,1,0,12,0,16,0,23,0);
        AUDIO(0,6,0);AUDIO(0,7,0);
        AUDIO(255,5,0,8,0,0,12,16,23,0,133,27,31,255);
        AUDIO(0,4,8,0,251);AUDIO(0,0,0,12,1,1,0);
        AUDIO(0,11,0,0,0);AUDIO(0,12,0,0,0);AUDIO(0,14,128,12,16);
        AUDIO(255,5,1);AUDIO(0,9);AUDIO(0,1);AUDIO(0,8);AUDIO(0,2,0);
#undef AUDIO
        send(swap,sizeof swap);
    }
    snprintf(line,sizeof line,"complete,probes=%u,failures=%u\r\n",probes,failures);if(!append(line))return 9;
    printf("\r\nAudio framing tests ended: %u pixel checks, %u failures\r\n",probes,failures);
    return failures?10:0;
}
