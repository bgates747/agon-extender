// PORT-008 STREAM-TIMING-R01. Timing candidate only, exact ROM-bound fixture.
// All transport operations belong to EMOS. No GPIO/UART registers here.
// PRT1 is the only application-owned peripheral; source/PRT0/IRQs unchanged.
#include <agon/mos.h>
#include <agon/timer.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "binding.hpp"
extern "C" uint24_t bench_count(const uint8_t *,uint24_t),bench_clock(const volatile uint8_t *);
extern "C" uint24_t gt_prt_init(void),gt_prt_read(void);
extern "C" void gt_prt_begin(void),gt_prt_close(void);
extern "C" uint24_t st_wire_read(void);
extern "C" uint24_t st_flush(void);
// entries.asm has an unused private graphics callback; never installed here.
extern "C" void graphics_receive(const uint8_t *) {}

static volatile uint8_t *sv;
static uint8_t bytes[8192];
static const unsigned lengths[]={256,4096,4097,8192};
struct Row {unsigned bytes,repeat,submit,wire,receipt,reply,mos_ticks,flags;};
static Row rows[24];
static unsigned used;
static bool parallel;
enum {OutputFault=1,DrainFault=2,ReplyFault=4,Overflow=8,MissingStamp=16};
static uint24_t now(){return bench_clock(sv);}
static bool sent(const uint8_t *p,unsigned n){return bench_count(p,n)==0;}
static bool drain(){
 if(parallel) return st_flush()==0;
 const auto begin=now();
 do {
  const uint24_t result=((uint24_t(*)(void))ST_UART)();
  if(result==1)return true;
  if(result>1)return false;
 } while(uint24_t(now()-begin)<240);
 return false;
}
static bool fence(uint24_t timeout_ticks=240){
 // Buffer adjustment is synchronous in EDP. This ordinary query's reply
 // confirms parser progression, not scanout or arbitrary drawing completion.
 static const uint8_t query[]={23,0,0x84,0,0,0,0};
 sv[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_point);
 if(!sent(query,sizeof query)||!drain())return false;
 const auto begin=now();
 while(!(sv[sysvar_vdp_pflags]&vdp_pflag_point))
  if(uint24_t(now()-begin)>=timeout_ticks)return false;
 return true;
}
static bool prepare(){
 // Allocate just once outside all measured intervals. Command 0 appends a
 // block, so clear first; do not pretend it overwrites an existing block.
 static const uint8_t clear[]={23,0,0xA0,0,0xE1,2};
 static const uint8_t upload[]={23,0,0xA0,0,0xE1,0,0,32};
 // Reuse the payload workspace during setup rather than consume another 8KiB
 // of MOSlet RAM just to upload zeroes once.
 memset(bytes,0,sizeof bytes);
 return sent(clear,sizeof clear)&&sent(upload,sizeof upload)&&sent(bytes,sizeof bytes)&&drain()&&fence();
}
static bool poison(){
 static const uint8_t set[]={23,0,0xA0,0,0xE1,5,0x42,0,0,0,32,0xAA};
 return sent(set,sizeof set)&&drain()&&fence();
}
static void payload(unsigned n){
 const uint8_t header[]={23,0,0xA0,0,0xE1,5,0xC2,0,0,uint8_t(n-11),uint8_t((n-11)>>8)};
 memcpy(bytes,header,sizeof header);
 for(unsigned i=11;i<n;++i)bytes[i]=uint8_t((i-11)*73+19);
}
static bool dump(){
 // Existing EDP serial debug output, outside timing. A host must retain and
 // compare every byte; a successful query alone does not verify buffer data.
 static const uint8_t command[]={23,0,0xA0,0,0xE1,0x80};
 // Thousands of individually formatted USB log lines may drain slowly. This
 // separate 7200-MOS-unit bound is outside measurement. MOS increments by two
 // per VBlank: at 60Hz this is ~60s; ordinary 240-unit fences are ~2s. The
 // frozen r09 artifact used these same constants with inaccurate comments.
 return sent(command,sizeof command)&&drain()&&fence(7200);
}
static bool rom_matches(){
 uint32_t hash=2166136261UL;
 const volatile uint8_t *rom=(const volatile uint8_t *)0;
 for(uint24_t i=0;i<131072;++i)hash=(hash^rom[i])*16777619UL;
 return hash==ST_ROM_FNV;
}
int main(int argc,char **argv){
 if((argc!=3&&argc!=4)||(strcmp(argv[1],"excom")&&strcmp(argv[1],"exext"))){
  printf("Usage: stream excom|exext results.csv [wire-bytes]\n");return 1;
 }
 const unsigned selected=argc==4?strtoul(argv[3],nullptr,10):0;
 if(argc==4&&selected!=256&&selected!=4096&&selected!=4097&&selected!=8192){
  printf("Timing refused: choose 256, 4096, 4097 or 8192 bytes\n");return 1;
 }
 const unsigned expected=selected?6:24;
 parallel=!strcmp(argv[1],"exext");sv=mos_sysvars();
 if(!rom_matches()||*(volatile uint8_t*)ST_BACKEND!=(parallel?2:1)||
    *(volatile uint8_t*)ST_FAULT||(parallel&&!*(volatile uint8_t*)ST_OWNED)){
  printf("Timing refused: ROM or route does not match binding\n");return 2;
 }
 if(!gt_prt_init()){printf("Timing refused: PRT1 unavailable\n");return 3;}
 const auto run_begin=now();
 gt_prt_begin();const unsigned read_overhead=gt_prt_read();
 bool ok=prepare();
 gt_prt_begin();if(ok&&!drain())ok=false;
 const unsigned empty_drain=gt_prt_read();
 waitvblank();const auto cal_begin=now();gt_prt_begin();waitvblank();
 const unsigned vblank_prt=gt_prt_read();const auto vblank_mos=uint24_t(now()-cal_begin);
 if(vblank_prt==65535)ok=false;
 for(unsigned length:lengths){
  if(selected&&selected!=length)continue;
  if(!ok)break;
  payload(length);
  for(unsigned repeat=0;repeat<6;++repeat){
   if(!poison()){ok=false;break;}
   *(volatile uint16_t*)ST_LAST_RAW=65535;
   Row r={length,repeat,0,0,0,0,0,0};
   const auto begin=now();gt_prt_begin();
   if(!sent(bytes,length))r.flags|=OutputFault;
   r.submit=gt_prt_read();
   if(!r.flags&&!drain())r.flags|=DrainFault;
   r.receipt=gt_prt_read();
   if(parallel){
    // Explicit 24-bit assembly subtraction avoids AgonDev's unavailable
    // compiler-generated 16-bit complement helper (__snot).
    r.wire=st_wire_read();if(r.wire==0)r.flags|=MissingStamp;
   } else r.wire=r.receipt;
   if(!r.flags&&!fence())r.flags|=ReplyFault;
   r.reply=gt_prt_read();r.mos_ticks=uint24_t(now()-begin);
   if(r.submit==65535||r.wire==65535||r.receipt==65535||r.reply==65535)r.flags|=Overflow;
   rows[used++]=r;
   if(r.flags){ok=false;break;}
   // Repeat0 is retained as an unmeasured-analysis warm-up; its PRT values
   // remain visible but never enter the five-sample performance summaries.
   if(!dump()){ok=false;break;}
  }
 }
 const auto run_ticks=uint24_t(now()-run_begin);gt_prt_close();
 FILE *f=fopen(argv[2],"w");if(!f){printf("Timing failed: cannot save\n");return 4;}
 bool saved=fprintf(f,"route,wire_bytes,repeat,submit_prt,wire_prt,receipt_prt,reply_prt,mos_ticks,flags,read_overhead,empty_drain_prt,vblank_prt,vblank_mos,divider,run_ticks\n")>0;
 for(unsigned i=0;i<used;++i){const auto &r=rows[i];
  if(fprintf(f,"%s,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,256,%u\n",argv[1],r.bytes,r.repeat,r.submit,r.wire,r.receipt,r.reply,r.mos_ticks,r.flags,read_overhead,empty_drain,vblank_prt,vblank_mos,run_ticks)<0)saved=false;
 }
 if(fclose(f))saved=false;
 printf("Timing %s: %u/%u rows; buffer-byte validation requires retained USB dumps\n",ok&&saved?"captured":"incomplete",used,expected);
 printf("%s\n",ST_BUILD_ID);
 return ok&&saved&&used==expected?0:5;
}
