/* Task-local fixture: mode/route selected by startup batch, never here.
 * File consists only of immutable VDU bytes. Host releases checkpoint with ESC.
 * All bytes use public MOS transport, no GPIO/UART bypass. */
#include <agon/mos.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static FIL file;
static uint8_t data[131072];
static unsigned bench_count(const uint8_t *p,unsigned n) {
 mos_puts((const char *)p,n,0);return 0;
}
int main(int argc,char **argv) {
 if(argc<2)return 19;
 unsigned e=ffs_fopen(&file,argv[1],FA_READ);if(e)return e;
 unsigned n=ffs_fread(&file,(char *)data,sizeof(data));
 if(ffs_ferror(&file) || !ffs_feof(&file)){ffs_fclose(&file);return 1;}
 ffs_fclose(&file);
 // Preload first: SD latency must not split timing-sensitive path commands.
 for(unsigned offset=0;offset<n;) {
  unsigned chunk=n-offset;if(chunk>32768)chunk=32768;
  e=bench_count(data+offset,chunk);if(e)return e;offset+=chunk;
 }
 // Disable cursor blinking before capture; same command on both routes.
 const uint8_t hide[]={23,1,0};bench_count(hide,sizeof(hide));
 if(argc>2){unsigned token=atoi(argv[2]);uint8_t dump[]={23,0,0xEE,token,token>>8};bench_count(dump,sizeof(dump));}
 // No per-frame activity: leave the completed static scene available to host.
 // MOS input is through the already-qualified Extender keyboard pathway.
 while(getch()!=27){}
 return 0;
}
