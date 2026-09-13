/* PORT-003 bounded ordinary-VDU marker. Select mode8 before invocation.
 * No private callback, query, serial log or VDP mode change. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
static uint8_t output[256];
static unsigned used;
static void byte(uint8_t value) {output[used++]=value;}
static void word(unsigned value) {byte(value);byte(value>>8);}
static void rect(unsigned x,unsigned y,uint8_t colour) {
    byte(18);byte(0);byte(colour);
    byte(25);byte(4);word(x);word(y);
    byte(25);byte(101);word(x+11);word(y+11);
}
int main(void) {
    const uint8_t setup[]={23,0,192,0,23,1,0,18,0,0,16};
    mos_puts((const char*)setup,sizeof(setup),0);
    unsigned updates=0,maximum_gap=0;
    uint32_t bytes=sizeof(setup),start=getsysvar_time(),last=0xffffffffUL;
    uint8_t previous=0;
    for(;;) {
        uint32_t elapsed=getsysvar_time()-start;
        if(elapsed>=2400)break;
        uint32_t frame=elapsed/2;
        if(frame==last)continue;
        if(last!=0xffffffffUL && frame-last>maximum_gap)maximum_gap=frame-last;
        uint8_t target=(uint8_t)frame,gray=(uint8_t)(target^(target>>1));used=0;
        for(unsigned bit=0;bit<8;++bit)if(last==0xffffffffUL || ((gray^previous)&(1u<<bit))) {
            uint8_t colour=(gray&(1u<<bit))?15:0;
            rect(16+bit*16,32,colour);rect(16+bit*16,56,colour^15);
        }
        if(used)mos_puts((const char*)output,used,0);
        bytes+=used;previous=gray;last=frame;++updates;
    }
    char receipt[160];int length=snprintf(receipt,sizeof(receipt),
        "schema,elapsed_ticks,updates,max_frame_gap,vdu_bytes,last_frame\n1,%lu,%u,%u,%lu,%lu\n",
        (unsigned long)(getsysvar_time()-start),updates,maximum_gap,(unsigned long)bytes,(unsigned long)last);
    uint8_t file=mos_fopen("VIDMARK.CSV",FA_WRITE|FA_CREATE_ALWAYS);
    int ok=file && mos_fwrite(file,receipt,length)==(unsigned)length;
    if(file)mos_fclose(file);
    const uint8_t restore[]={23,0,192,1,23,1,1};mos_puts((const char*)restore,sizeof(restore),0);
    puts(ok?"Video marker complete.":"Video marker receipt failed.");return ok?0:1;
}
