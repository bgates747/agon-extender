/* Independent ordinary stock pixel queries, after the static image is captured.
 * No video mode selection, private VDP command, direct UART, or graphics changes. */
#include <agon/mos.h>
#include <stdint.h>
static FIL file;
int main(void) {
 const unsigned xy[5][2]={{80,40},{144,40},{208,40},{336,40},{16,200}};
 uint8_t out[48]={'Q','4','P','R',1,5,0,0};
 volatile uint8_t *sv=mos_sysvars();
 for(unsigned i=0;i<5;i++) {
  unsigned x=xy[i][0],y=xy[i][1];uint8_t q[]={23,0,132,x,x>>8,y,y>>8};
  mos_clearvdpflags(4);mos_puts((const char *)q,sizeof(q),0);
  unsigned e=mos_waitforvdpflags(4);uint8_t *r=out+8+i*8;
  r[0]=x;r[1]=x>>8;r[2]=y;r[3]=y>>8;r[4]=e;
  for(unsigned j=0;j<3;j++)r[5+j]=sv[sysvar_scrpixel+j];
 }
 unsigned e=ffs_fopen(&file,"/test/qual004/probe.bin",FA_WRITE|FA_CREATE_ALWAYS);if(e)return e;
 unsigned n=ffs_fwrite(&file,(const char *)out,sizeof(out));ffs_fclose(&file);
 return n==sizeof(out)?0:1;
}
