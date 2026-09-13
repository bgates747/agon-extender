/* Bounded stock-VDP text readback for REMOTE-002 command diagnostics.
 * Never selects a mode or draws before capturing. The host runs this from a
 * finite MOS batch followed by sdserve and downloads the resulting text. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include "identity.h"
static char text[80*61];
int main(void) {
    volatile uint8_t *sv=mos_sysvars();
    unsigned columns=sv[sysvar_scrCols],rows=sv[sysvar_scrRows],used=0;
    uint32_t started=getsysvar_time();
    if(!columns || columns>80 || !rows || rows>60)return 1;
    for(unsigned y=0;y<rows;++y) {
        for(unsigned x=0;x<columns;++x) {
            uint8_t query[]={23,0,0x83,x,0,y,0};
            sv[sysvar_vdp_pflags]&=(uint8_t)~vdp_pflag_scrchar;
            mos_puts((const char *)query,sizeof(query),0);
            uint32_t at=getsysvar_time();
            while(!(sv[sysvar_vdp_pflags]&vdp_pflag_scrchar)) {
                if((uint32_t)(getsysvar_time()-at)>120 ||
                   (uint32_t)(getsysvar_time()-started)>120*60)return 2;
            }
            uint8_t c=sv[sysvar_scrchar];text[used++]=c>=32 && c<127?c:' ';
        }
        text[used++]='\n';
    }
    uint8_t f=mos_fopen("/extender/key-screen.txt",FA_WRITE|FA_CREATE_ALWAYS);
    int ok=f && mos_fwrite(f,text,used)==used;
    if(f)mos_fclose(f);
    puts(KEYSCREEN_BUILD_ID);puts(ok?"Screen text saved.":"Screen text save failed.");
    return ok?0:3;
}
