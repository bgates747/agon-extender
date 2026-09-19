/* BENCH-005 textread r01. Read-only screen query, no mode/font/cursor change.
 * Queries stock VDU 23,0,0x83. Recognition depends on current font/text colour.
 * Collect before opening output so screen is stable throughout queries.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
static uint8_t cells[8192];
int main(int argc,char**argv){
 unsigned cols=getsysvar_scrCols(),rows=getsysvar_scrRows(),x,y,n=0,unknown=0,timeouts=0;
 unsigned cx=getsysvar_cursorX(),cy=getsysvar_cursorY();
 const char*name=argc>1?argv[1]:"/test/bench005/screen.txt";
 if(!cols||!rows||cols*rows>sizeof(cells))return 19;
 for(y=0;y<rows;y++)for(x=0;x<cols;x++){
  clock_t start;mos_clearvdpflags(vdp_pflag_scrchar);
  putch(23);putch(0);putch(0x83);putch(x);putch(x>>8);putch(y);putch(y>>8);
  start=clock();while(!(getsysvar_vdp_pflags()&vdp_pflag_scrchar))if((uint32_t)(clock()-start)>120)break;
  if(!(getsysvar_vdp_pflags()&vdp_pflag_scrchar)){cells[n++]='?';timeouts++;goto finish;}
  cells[n]=getsysvar_scrchar();if(!cells[n]){cells[n]='?';unknown++;}n++;
 }
 finish:;
 FILE*f=fopen(name,"w");if(!f)return 4;
 fprintf(f,"cols=%u rows=%u cursor=%u,%u unknown=%u timeouts=%u captured=%u\n",cols,rows,cx,cy,unknown,timeouts,n);
 for(x=0;x<n;x++){fputc(cells[x],f);if((x+1)%cols==0)fputc('\n',f);}
 if(fclose(f))return 1;return timeouts?1:0;
}
