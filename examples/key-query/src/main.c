/* Finite MOS-API query witness. Host uses the admitted P4 input path for held
 * Shift/A phases. No mode change, direct UART access or keyboard callback hook.
 * Every wait is bounded; results survive return to MOS in /test/keyquery.csv. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include "identity.h"
struct Row { uint8_t vk, wanted, got_vk, down, ascii, mods, delta, pass; };
static struct Row rows[280];
static unsigned count;
static volatile uint8_t *sv;
static uint32_t started;
static int wait_event(uint8_t vk,uint8_t down) {
    uint32_t at=getsysvar_time();
    while (sv[sysvar_vkeycode]!=vk || sv[sysvar_vkeydown]!=down)
        if((uint32_t)(getsysvar_time()-at)>120*20)return 0;
    return 1;
}
static int query(uint8_t vk,uint8_t down,uint8_t mods) {
    struct Row *r=&rows[count++];r->vk=vk;r->wanted=down;
    uint8_t old=sv[sysvar_vkeycount];
    uint8_t bytes[]={23,0,0x99,vk};
    uint32_t at=getsysvar_time();
    mos_puts((const char *)bytes,sizeof(bytes),0);
    while(sv[sysvar_vkeycount]==old)
        if((uint32_t)(getsysvar_time()-at)>120*2)return 0;
    r->got_vk=sv[sysvar_vkeycode];r->down=sv[sysvar_vkeydown];
    r->ascii=sv[sysvar_keyascii];r->mods=sv[sysvar_keymods];
    r->delta=(uint8_t)(sv[sysvar_vkeycount]-old);
    r->pass=r->got_vk==vk && r->down==down && (r->mods&3)==mods;
    if(down && vk==22)r->pass=r->pass && r->ascii=='a';
    return r->pass;
}
int main(void) {
    sv=mos_sysvars();started=getsysvar_time();
    puts(KEYQUERY_BUILD_ID);
    /* Let the CLI Enter release arrive before requesting snapshots. */
    uint32_t at=getsysvar_time();while((uint32_t)(getsysvar_time()-at)<30){}
    int ok=query(22,0,0) && query(125,0,0) && query(117,0,0) && query(143,0,0);
    if(ok) {
        puts("Key query: hold Shift");
        ok=wait_event(117,1);
        for(unsigned i=0;i<260 && ok;++i)ok=query(117,1,2);
        if(ok)ok=query(22,0,2);
        puts("Key query: release Shift");
        if(ok)ok=wait_event(117,0) && query(117,0,0);
    }
    if(ok) {
        puts("Key query: hold a");
        ok=wait_event(22,1) && query(22,1,0);
        puts("Key query: release a");
        if(ok)ok=wait_event(22,0) && query(22,0,0) && query(125,0,0);
    }
    uint32_t elapsed=getsysvar_time()-started;
    uint8_t f=mos_fopen("/test/keyquery.csv",FA_WRITE|FA_CREATE_ALWAYS);
    int saved=f!=0;char line[256];
    int n=snprintf(line,sizeof(line),"%s,pass=%d,rows=%u,ticks=%lu,nominal_ticks_per_second=120\r\nvk,wanted,got_vk,down,keycode,modifiers,count_delta,pass\r\n",KEYQUERY_BUILD_ID,ok,count,(unsigned long)elapsed);
    if(saved)saved=mos_fwrite(f,line,n)==(unsigned)n;
    for(unsigned i=0;i<count && saved;++i) {
        const struct Row *r=&rows[i];
        n=snprintf(line,sizeof(line),"%u,%u,%u,%u,%u,%u,%u,%u\r\n",r->vk,r->wanted,r->got_vk,r->down,r->ascii,r->mods,r->delta,r->pass);
        saved=mos_fwrite(f,line,n)==(unsigned)n;
    }
    if(f)mos_fclose(f);
    puts(ok && saved?"Key query PASS; receipt saved; returning to MOS":"Key query FAIL; inspect receipt; returning to MOS");
    return ok && saved?0:1;
}
