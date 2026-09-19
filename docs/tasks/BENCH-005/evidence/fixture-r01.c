/* BENCH-005 r01. No mode switch. A-key rising edges change a sequence patch.
 * char=nonblocking MOS keycount/down/ascii; map=held A state; block=MOS getch.
 * Legacy telemetry reuses BENCH-001 v2 envelope ONLY for diagnostic markers.
 * No claim this synthetic payload describes a race. run identity is B005.
 */
#include <agon/mos.h>
#include <agon/vdp.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
extern unsigned emos_gateway_call(uint8_t*);
static uint8_t gateway[66],packet[141];
static void put24(uint8_t*p,unsigned v){p[0]=v;p[1]=v>>8;p[2]=v>>16;}
static void put32(uint8_t*p,uint32_t v){put24(p,(unsigned)v);p[3]=v>>24;}
static unsigned call(unsigned op){memset(gateway,0,66);packet[0]=op;gateway[0]=66;gateway[2]=1;gateway[4]=3;gateway[5]=9;gateway[6]=2;memcpy(gateway+25,"ext",3);memcpy(gateway+41,"telemetry",9);put24(gateway+10,(unsigned)packet);put24(gateway+13,op==1?141:1);return emos_gateway_call(gateway);}
static void report(unsigned seq,uint32_t run){
 uint32_t crc=0xffffffffUL;unsigned i,j;uint8_t*p=packet+1;
 memset(p,0,140);p[0]='R';p[1]='T';p[2]=2;p[3]=1;put32(p+4,run);put32(p+8,seq);put32(p+12,clock());
 for(i=0;i<136;i++){crc^=p[i];for(j=0;j<8;j++)crc=(crc>>1)^((crc&1)?0xedb88320UL:0);}
 put32(p+136,~crc);(void)call(1);
}
int main(int argc,char**argv){
 int map=argc>1&&!strcmp(argv[1],"map"),block=argc>1&&!strcmp(argv[1],"block");
 int busy=argc>2&&!strcmp(argv[2],"busy"),tele=argc>3&&!strcmp(argv[3],"tele");
 uint8_t last=getsysvar_vkeycount(),held=0;unsigned seq=0,anim=0;clock_t start=clock(),prev=start;uint32_t run=(uint32_t)start^0xb0050000UL;
 if(tele&&call(0))return 2;
 vdp_set_pixel_coordinates();vdp_cursor_enable(0);vdp_cls();
 printf("BENCH-005 %s %s\r\nA: marker  ESC: exit\r\n",map?"map":block?"block":"char",busy?"busy":"idle");
 vdp_gcol(0,0);vdp_filled_rectangle(0,40,95,135);
 while((uint32_t)(clock()-start)<21600UL){ /* raw ticks: safety cap, not stopwatch */
  int hit=0;uint8_t k;
  if(block){k=getch();if(k==27)break;hit=k=='a'||k=='A';}
  else if(map){k=vdp_getKeyMap(8)&2;hit=k&&!held;held=k;if(vdp_getKeyMap(14)&1)break;}
  else {k=getsysvar_vkeycount();if(k!=last){last=k;if(getsysvar_vkeydown()){k=getsysvar_keyascii();if(k==27)break;hit=k=='a'||k=='A';}}}
  if(hit){++seq;if(tele)report(seq,run);vdp_gcol(0,seq%2?15:0);vdp_filled_rectangle(0,40,95,135);putch(31);putch(0);putch(3);printf("%u ",seq);}
  if(busy&&clock()!=prev){prev=clock();vdp_gcol(0,++anim%16);vdp_filled_rectangle(160,80,300,200);}
 }
 if(tele)(void)call(2);vdp_cursor_enable(1);printf("\r\nBENCH-005 ended: %u events\r\n",seq);return 0;
}
