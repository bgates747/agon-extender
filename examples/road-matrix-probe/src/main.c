/* PORT-003 local reduction of Rally's stock buffered-road protocol.
 * Select mode8 at the CLI/autoexec before running. No mode change here.
 * "compute" suppresses only the final call of the transformed PLOT buffer.
 * UART output may block if the VDP fails; the bench owns reset recovery. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "protocol_data.h"

static void word(uint8_t *p, unsigned value) {p[0]=value;p[1]=value>>8;}
int main(int argc,char **argv) {
    int draw=argc==2 && !strcmp(argv[1],"draw");
    if(argc!=2 || (!draw && strcmp(argv[1],"compute"))) {
        puts("Usage: matprobe compute|draw");return 1;
    }
    uint8_t setup[sizeof(Startup)];memcpy(setup,Startup,sizeof(setup));
    if(!draw) {
        const uint8_t call[]={23,0,160,55,117,1};unsigned replaced=0;
        for(unsigned i=0;i+sizeof(call)<=sizeof(setup);++i)
            if(!memcmp(setup+i,call,sizeof(call))) {memset(setup+i,0,sizeof(call));++replaced;}
        if(replaced!=2) {puts("Protocol reduction mismatch");return 2;}
    }
    printf("Matrix probe: %s\r\n",draw?"draw":"compute");
    const uint8_t pixel[]={23,0,192,0,23,1,0};mos_puts((const char*)pixel,sizeof(pixel),0);
    mos_puts((const char*)setup,sizeof(setup),0);
    uint32_t start=getsysvar_time();unsigned count=0;
    for(;count<80;++count) {
        uint8_t command[]={23,0,160,48,117,5,194,0,0,8,0,0,0,0,0,0,0,0,0,23,0,160,56,117,1};
        word(command+11,160);word(command+13,160);
        word(command+15,104+(count%40)*3);word(command+17,107+(count%40)*3);
        command[22]=(count&1)?56:57;
        mos_puts((const char*)command,sizeof(command),0);
        uint32_t due=start+(count+1)*12;
        while((int32_t)(getsysvar_time()-due)<0){}
    }
    char report[128];int n=snprintf(report,sizeof(report),"mode,submitted,elapsed_ticks\n%s,%u,%lu\n",draw?"draw":"compute",count,(unsigned long)(getsysvar_time()-start));
    uint8_t file=mos_fopen(draw?"MATDRAW.CSV":"MATCOMP.CSV",FA_WRITE|FA_CREATE_ALWAYS);
    int ok=file && mos_fwrite(file,report,n)==(unsigned)n;if(file)mos_fclose(file);
    const uint8_t restore[]={23,0,192,1,23,1,1,31,0,20};mos_puts((const char*)restore,sizeof(restore),0);
    puts(ok?"Matrix probe submitted 80 calls.":"Matrix probe receipt failed.");
    return ok?0:3;
}
