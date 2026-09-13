/* Finite eZ80 receiver witness for REMOTE-002. Mode/admission are autoexec's
 * responsibility. No keyboard hook, UART access or emulator memory injection.
 * Poll MOS sysvars/keymap, retain events in RAM, write once after Enter-up or
 * a 90-second timeout. Return to a preinstalled service even on test failure. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>

struct Event { uint8_t ascii, mods, vk, down, held_bits; };
static struct Event events[96];
int main(void) {
    volatile uint8_t *sv=mos_sysvars();
    volatile uint8_t *map=mos_getkbmap();
    unsigned count=0;
    uint8_t previous=sv[sysvar_vkeycount];
    uint32_t start=getsysvar_time();
    int complete=0;
    puts("Remote keyboard receiver ready. Bounded automatic test.");
    while ((uint32_t)(getsysvar_time()-start)<90*120 && count<96) {
        uint8_t current=sv[sysvar_vkeycount];
        if(current==previous)continue;
        previous=current;
        struct Event *e=events+count++;
        e->ascii=sv[sysvar_keyascii];e->mods=sv[sysvar_keymods];
        e->vk=sv[sysvar_vkeycode];e->down=sv[sysvar_vkeydown];
        /* MOS uses BBC physical-key numbers, not FabGL virtual-key indexes.
         * Count all 128 physical bits to witness held-state and cleanup. */
        e->held_bits=0;
        for(unsigned j=0;j<16;++j) {
            uint8_t bits=map[j];
            while(bits) {e->held_bits+=bits&1;bits>>=1;}
        }
        if(e->ascii==13 && !e->down) {complete=1;break;}
    }
    uint8_t f=mos_fopen("/extender/key-seen.txt",FA_WRITE|FA_CREATE_ALWAYS);
    if(!f)return 1;
    char line[100];
    int n=snprintf(line,sizeof(line),"remote-keyboard receiver, complete=%u, events=%u\r\n",complete,count);
    int ok=mos_fwrite(f,line,n)==(unsigned)n;
    for(unsigned i=0;i<count && ok;++i) {
        const struct Event *e=events+i;
        n=snprintf(line,sizeof(line),"%u,%u,%u,%u,%u\r\n",e->ascii,e->mods,e->vk,e->down,e->held_bits);
        ok=mos_fwrite(f,line,n)==(unsigned)n;
    }
    mos_fclose(f);
    puts(complete && ok?"Receiver finished; receipt saved.":"Receiver incomplete; receipt saved.");
    return complete && ok?0:1;
}
