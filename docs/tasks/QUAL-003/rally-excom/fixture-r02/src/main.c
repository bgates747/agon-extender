/* RX r02: bounded current-Rally viewport/scroll/page reproduction.
 * Caller selects mode136 and route BEFORE launch. No mode switching, firmware
 * callback, browser dependency or Golem. Pixel queries are correctness fences,
 * not rendering-time instrumentation. Raw tick totals include queries and SD.
 */
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
int main(int argc,char **argv){
    if(argc!=2)return 2;output=argv[1];sv=mos_sysvars();
    uint8_t existing=mos_fopen(output,FA_READ);
    if(existing){mos_fclose(existing);return 3;} /* Never overwrite evidence. */
    uint8_t q[]={23,0,0x86};mos_clearvdpflags(16);send(q,sizeof q);
    if(mos_waitforvdpflags(16))return 4;
    if((sv[sysvar_scrMode]&127)!=8)return 5;
    if(!append("RXPROBE-r02,mode136-required,correctness-only\r\n"))return 6;
    const uint8_t init[]={23,0,0xC0,0,23,1,0};send(init,sizeof init);
    const uint8_t swap[]={23,0,0xC3};
    /* One solid RGBA8888 bitmap; direct draw matches current panorama path.
     * No transformed matrix is selected. Each row is128bytes, safely counted. */
    const uint8_t select[]={23,27,0,0},load[]={23,27,1,32,0,104,0};
    send(select,sizeof select);send(load,sizeof load);
    uint8_t pixels[128];for(unsigned i=0;i<32;++i){pixels[i*4]=0;pixels[i*4+1]=255;pixels[i*4+2]=0;pixels[i*4+3]=255;}
    for(unsigned y=0;y<104;++y)send(pixels,sizeof pixels);
    for(unsigned frame=0;frame<4;++frame){
        snprintf(line,sizeof line,"begin,%u\r\n",frame);if(!append(line))return 7;
        viewport(0,0,319,239);rect(0,0,319,239,0);rect(0,0,319,23,1);
        viewport(0,24,319,103);
        const uint8_t draw[]={23,27,3,244,255,0,0};send(draw,sizeof draw); /* x=-12 */
        viewport(0,0,319,239);
        if(!probe(frame,10,12,170,0,0)||!probe(frame,10,40,0,255,0)||
           !probe(frame,10,104,0,0,0)||!probe(frame,20,40,0,0,0))return 8;
        viewport(0,104,319,223);
        /* Same colour/MOVE/MOVE/filled-triangle/filled-triangle sequence as
         * Rally Stream::quad. Extrapolated left edge crosses screen boundary. */
        colour(15);plot(4,50,104);plot(4,100,104);plot(0x55,-100,223);plot(0x55,40,223);
        viewport(0,0,319,239);
        for(unsigned x=0;x<=120;x+=10)if(!probe(frame,x,210,999,999,999))return 8;
        send(swap,sizeof swap);
    }
    snprintf(line,sizeof line,"complete,probes=%u,failures=%u\r\n",probes,failures);
    if(!append(line))return 9;
    viewport(0,0,319,239);
    printf("\r\nRally probe complete: %u checks, %u mismatches\r\n",probes,failures);
    return failures?10:0;
}
