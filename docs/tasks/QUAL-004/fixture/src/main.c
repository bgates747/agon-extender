/* Task-local fixture: mode/route selected by startup batch, never here.
 * File consists only of immutable VDU bytes. Host releases checkpoint with ESC.
 * All bytes use public MOS transport, no GPIO/UART bypass. */
#include <agon/mos.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static FIL file;
static uint8_t data[131072],bars[4096];
static char barpath[128];
static unsigned bench_count(const uint8_t *p,unsigned n) {
 mos_puts((const char *)p,n,0);return 0;
}
int main(int argc,char **argv) {
 if(argc<2)return 19;
 unsigned e=ffs_fopen(&file,argv[1],FA_READ);if(e)return e;
 unsigned n=ffs_fread(&file,(char *)data,sizeof(data));
 if(ffs_ferror(&file) || !ffs_feof(&file)){ffs_fclose(&file);return 1;}
 ffs_fclose(&file);
 // Sidecars are test-only barriers at validated resource-mutation boundaries.
 if(snprintf(barpath,sizeof(barpath),"%s.bar",argv[1]) >= (int)sizeof(barpath))return 19;
 e=ffs_fopen(&file,barpath,FA_READ);if(e)return e;
 unsigned size=ffs_fread(&file,(char *)bars,sizeof(bars));
 if(ffs_ferror(&file) || !ffs_feof(&file)){ffs_fclose(&file);return 1;}
 ffs_fclose(&file);
 if(size<9 || memcmp(bars,"Q4B1",4))return 19;
 unsigned declared=bars[4]|((unsigned)bars[5]<<8)|((unsigned)bars[6]<<16);
 unsigned count=bars[7]|((unsigned)bars[8]<<8);
 if(declared!=n || size!=9+count*3)return 19;
 unsigned previous=0;
 for(unsigned i=0;i<count;i++) {
  const uint8_t *b=bars+9+i*3;unsigned offset=b[0]|((unsigned)b[1]<<8)|((unsigned)b[2]<<16);
  if(offset+6>n || (i && offset<=previous) || data[offset]!=23 || data[offset+1]!=0 || data[offset+2]!=160 || data[offset+5]!=2)return 19;
  previous=offset;
 }
 unsigned pos=0;
 for(unsigned i=0;i<=count;i++) {
  const uint8_t *b=bars+9+i*3;unsigned end=i==count?n:(b[0]|((unsigned)b[1]<<8)|((unsigned)b[2]<<16));
  while(pos<end){unsigned chunk=end-pos;if(chunk>32768)chunk=32768;bench_count(data+pos,chunk);pos+=chunk;}
  if(i<count){const uint8_t flush[]={23,0,202};bench_count(flush,sizeof(flush));}
 }
 // Disable cursor blinking before capture; same command on both routes.
 const uint8_t hide[]={23,1,0};bench_count(hide,sizeof(hide));
 if(argc>2){unsigned token=atoi(argv[2]);uint8_t dump[]={23,0,0xEE,token,token>>8};bench_count(dump,sizeof(dump));}
 // No per-frame activity: leave the completed static scene available to host.
 // MOS input is through the already-qualified Extender keyboard pathway.
 while(getch()!=27){}
 return 0;
}
