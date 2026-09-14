/* Pure-data diagnostic, public EMOS routing/output only. See PROCEDURE.md.
 * Timed sections contain no SD access or screen output. The private callback
 * never calls MOS; no firmware replacement or direct UART access here.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"
extern uint24_t bench_clock(const volatile uint8_t *);
extern uint24_t bench_count(const uint8_t *,uint24_t);
extern void graphics_callback(void);
static volatile uint8_t *sv;
#ifndef UART_BATCH_ROUNDS
#define UART_BATCH_ROUNDS 16
#endif
_Static_assert(UART_BATCH_ROUNDS == 16 || UART_BATCH_ROUNDS == 31 || UART_BATCH_ROUNDS == 128, "frozen batch scope");
#define UART_BATCH_BYTES (UART_BATCH_ROUNDS * 2048U)
_Static_assert(UART_BATCH_BYTES <= 262144U, "bounded application storage");
static uint8_t data[UART_BATCH_BYTES > 65535U ? UART_BATCH_BYTES : 65535U],returned[2048];
static volatile uint8_t armed,bad,seen[4],source;
static volatile uint16_t owner,packets;
static volatile uint32_t value[4],count[4];
static volatile uint24_t last_rx;
static unsigned route,repeat,pattern,length,saved;
static uint16_t token;
static FIL file;
static char filename[32],line[512],command[64];
static uint32_t rng,position;
static uint24_t ticks(void){return bench_clock(sv);}
static uint32_t u32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
void graphics_receive(const uint8_t *p) {
    if(!armed || p[0]!='Q' || p[1]!='T' || p[2]!='G' || p[3]!=0xA1 || p[7]!=source)return;
    unsigned id=(unsigned)p[4]|((unsigned)p[5]<<8),kind=p[6];
    if(kind==96) {
        if(id!=packets || packets>=256){bad=1;return;}
        memcpy(returned+packets*8,p+8,8);++packets;last_rx=ticks();return;
    }
    if(id!=owner || kind>3)return;
    if(seen[kind]){bad=1;return;}
    value[kind]=u32(p+8);count[kind]=u32(p+12);last_rx=ticks();seen[kind]=1;
}
static uint8_t next_byte(void) {
    uint32_t i=position++;
    if(pattern==0)return 0;
    if(pattern==1)return 255;
    if(pattern==2)return (i&1)?0xAA:0x55;
    rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return (uint8_t)rng;
}
static unsigned send(const uint8_t *p,unsigned n) {
    while(n){unsigned chunk=n>32768?32768:n;unsigned s=bench_count(p,chunk);if(s)return s;p+=chunk;n-=chunk;}return 0;
}
static unsigned wait_for(unsigned kind) {
    uint24_t t=ticks();uint32_t budget=16000000UL;
    while(!seen[kind] && !bad && ticks()-t<1800 && --budget){}
    return (!seen[kind] || bad)?FR_TIMEOUT:0;
}
static void arm(void) {
    armed=0;owner=++token;source=route;bad=0;packets=0;
    memset((void*)seen,0,sizeof seen);memset((void*)value,0,sizeof value);memset((void*)count,0,sizeof count);armed=1;
}
static unsigned request(unsigned op) {
    uint8_t p[]={23,0,0xEE,op,token,token>>8,length,length>>8,pattern};return send(p,sizeof p);
}
static unsigned close_write(const char *s) {
    unsigned n=strlen(s),status=ffs_fwrite(&file,s,n)==n?0:FR_DISK_ERR;
    unsigned sync=ffs_fsync(&file),close=ffs_fclose(&file);return status?status:(sync?sync:close);
}
static unsigned append(const char *s) {unsigned status=ffs_fopen(&file,filename,FA_WRITE|FA_OPEN_APPEND);return status?status:close_write(s);}
static unsigned create(void) {
    for(unsigned n=1;n<1000;++n){snprintf(filename,sizeof filename,"UDT%03u.CSV",n);unsigned s=ffs_fopen(&file,filename,FA_WRITE|FA_CREATE_NEW);if(s==FR_EXIST)continue;if(s)return s;
        snprintf(line,sizeof line,"# %s\r\nrepeat,route,direction,pattern,length,send_ticks,reply_ticks,elapsed_us,expected_bytes,actual_bytes,errors,status\r\n",UART_BUILD_ID);return close_write(line);}return FR_EXIST;
}
static unsigned row(const char *direction,uint24_t sent,uint24_t reply,uint32_t local,unsigned expected,unsigned actual,unsigned errors,unsigned status) {
    snprintf(line,sizeof line,"%u,%u,%s,%u,%u,%u,%u,%lu,%u,%u,%u,%u\r\n",repeat,route,direction,pattern,length,sent,reply,(unsigned long)local,expected,actual,errors,status);
    unsigned s=append(line);if(!s)++saved;return status?status:s;
}
static unsigned forward(void) {
    const uint8_t clear[]={23,0,160,10,250,2}; /* buffer64010 */
    unsigned s=send(clear,sizeof clear);if(s)return s;
    rng=0x12345678UL;position=0;for(unsigned i=0;i<length;++i)data[i]=next_byte();
    arm();s=request(1);if(!s)s=wait_for(0);if(s){armed=0;return row("forward",0,0,0,length,0,1,s);}
    if(value[0]!=length || count[0]!=pattern){armed=0;return FR_INT_ERR;}
    uint24_t start=ticks();
    if(length){uint8_t header[]={23,0,160,10,250,0,length,length>>8};s=send(header,sizeof header);if(!s)s=send(data,length);}
    uint24_t sent=ticks()-start,tail=ticks();
    if(!s)s=request(2);if(!s)s=wait_for(1);uint24_t reply=last_rx-tail;
    if(!s)s=request(3);if(!s)s=wait_for(2);armed=0;
    unsigned errors=s?1:(unsigned)value[2];if(!s && (count[1]!=length || errors))s=FR_INT_ERR;
    return row("forward",sent,reply,value[1],length,(unsigned)count[1],errors,s);
}
static unsigned reverse(void) {
    arm();uint24_t start=ticks();unsigned s=request(4);uint24_t sent=ticks()-start;
    if(!s)s=wait_for(3);uint24_t whole=last_rx-start;armed=0;
    unsigned errors=0;pattern=3;rng=0x12345678UL;position=0;
    for(unsigned i=0;i<packets*8;++i)if(returned[i]!=next_byte())++errors;
    if(packets!=length || count[3]!=length)++errors;if(!s && errors)s=FR_INT_ERR;
    return row("reverse",sent,whole,value[3],length*8,packets*8,errors,s);
}
/* E07P: one symmetric interval; preserve bytes, validate after timing. */
static unsigned reverse_batch(void) {
    unsigned s=0,rounds=0,errors=0;length=256;pattern=3;
    uint24_t start=ticks();
    for(;rounds<UART_BATCH_ROUNDS;++rounds) {
        arm();s=request(4);if(!s)s=wait_for(3);armed=0;
        if(s || bad || packets!=256 || count[3]!=256){++errors;break;}
        memcpy(data+rounds*2048,returned,2048);
    }
    uint24_t whole=ticks()-start;
    for(unsigned r=0;r<rounds;++r) {
        rng=0x12345678UL;position=0;
        for(unsigned i=0;i<2048;++i)if(data[r*2048+i]!=next_byte())++errors;
    }
    if(!s && (rounds!=UART_BATCH_ROUNDS || errors))s=FR_INT_ERR;
    return row("reverse-batch",0,whole,0,UART_BATCH_BYTES,rounds*2048,errors,s);
}
static unsigned duplex(void) {
    const uint8_t clear[]={23,0,160,10,250,2};
    unsigned n=length,s=send(clear,sizeof clear);if(s)return s;
    pattern=3;rng=0x12345678UL;position=0;for(unsigned i=0;i<n;++i)data[i]=next_byte();
    arm();s=request(1);if(!s)s=wait_for(0);if(s){armed=0;return s;}
    if(value[0]!=n || count[0]!=3){armed=0;return FR_INT_ERR;}
    uint24_t start=ticks();length=256;s=request(4);length=n;
    const uint8_t header[]={23,0,160,10,250,0,n,n>>8};
    if(!s)s=send(header,sizeof header);if(!s)s=send(data,n);
    uint24_t sent=ticks()-start;
    if(!s)s=wait_for(3);uint24_t reverse_ticks=last_rx-start;
    if(!s)s=request(2);if(!s)s=wait_for(1);
    if(!s)s=request(3);if(!s)s=wait_for(2);armed=0;
    unsigned reverse_errors=0;rng=0x12345678UL;position=0;
    for(unsigned i=0;i<packets*8;++i)if(returned[i]!=next_byte())++reverse_errors;
    if(packets!=256 || count[3]!=256)++reverse_errors;
    unsigned forward_errors=(unsigned)value[2];if(count[1]!=n)++forward_errors;
    if(!s && (reverse_errors || forward_errors || bad))s=FR_INT_ERR;
    unsigned a=row("duplex-forward",sent,reverse_ticks,value[1],n,(unsigned)count[1],forward_errors,s);
    length=256;unsigned b=row("duplex-reverse",sent,reverse_ticks,value[3],2048,packets*8,reverse_errors,s);length=n;
    return a?a:b;
}
int main(int argc,char **argv) {
    unsigned smoke=argc>1 && !strcmp(argv[1],"smoke"),status;sv=(volatile uint8_t*)mos_sysvars();status=create();if(status)return status;
    mos_setkbvector(graphics_callback,0);
    const unsigned lengths[]={0,1,63,64,65,255,256,257,4095,4096,4097,32768,65535};
    const unsigned returns[]={1,8,64,256};
    if(argc>1 && !strcmp(argv[1],"batch")) {
      for(repeat=0;repeat<6 && !status;++repeat)
        for(unsigned slot=0;slot<2 && !status;++slot) {
          route=(repeat+slot)&1;
          strcpy(command,route?"emos excom --keep-display":"emos legacy --keep-display");
          status=mos_oscli(command,NULL,0);if(!status)status=reverse_batch();
        }
    } else if(argc>1 && !strcmp(argv[1],"wire")) {
      /* Same transfer primitives; a bounded, uniquely tokened capture window. */
      repeat=0;pattern=3;
      for(unsigned direction=0;direction<2 && !status;++direction)
        for(route=0;route<2 && !status;++route) {
          strcpy(command,route?"emos excom --keep-display":"emos legacy --keep-display");status=mos_oscli(command,NULL,0);
          if(!status){length=direction?256:65535;status=direction?reverse():forward();}
        }
    } else if(argc>1 && !strcmp(argv[1],"duplex")) {
      const unsigned mixed_lengths[]={257,4096,65535};
      for(route=0;route<2 && !status;++route) {
        strcpy(command,route?"emos excom --keep-display":"emos legacy --keep-display");status=mos_oscli(command,NULL,0);
        for(repeat=0;repeat<3 && !status;++repeat)for(unsigned i=0;i<3 && !status;++i){length=mixed_lengths[i];status=duplex();}
      }
    } else for(unsigned direction=0;direction<2 && !status;++direction)
      for(route=0;route<2 && !status;++route){
        strcpy(command,route?"emos excom --keep-display":"emos legacy --keep-display");status=mos_oscli(command,NULL,0);if(status)break;
        for(repeat=0;repeat<(smoke?1:3) && !status;++repeat){
            if(!direction) {
                for(pattern=0;pattern<4 && !status;++pattern)for(unsigned i=0;i<sizeof lengths/sizeof *lengths && !status;++i){
                    length=lengths[i];if(smoke && length!=0 && length!=257 && length!=65535)continue;status=forward();}
            } else {
                pattern=3;for(unsigned i=0;i<sizeof returns/sizeof *returns && !status;++i){length=returns[i];status=reverse();}
            }
        }
      }
    armed=0;mos_setkbvector(NULL,0);strcpy(command,"emos legacy --keep-display");unsigned recovery=mos_oscli(command,NULL,0);
    snprintf(line,sizeof line,"# terminal,status=%u,saved=%u,recovery=%u\r\n",status,saved,recovery);unsigned persisted=append(line);
    printf("UART data test %s. %u cases saved to %s.\r\n",status||persisted||recovery?"incomplete":"complete",saved,filename);
    return 0; /* EXEC must resume SD recovery even after a saved failure. */
}
