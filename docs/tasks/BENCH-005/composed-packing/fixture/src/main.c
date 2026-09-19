/* W08 deterministic fixture. Mode only selected by startup; no mode changes.
 * Reuses QUAL-004 immutable VDU scene loading and BENCH-005 moving rectangles.
 * ESC exits. A toggles static/animated. Commands go through public MOS routing.
 */
#include <agon/mos.h>
#include <agon/vdp.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
static uint8_t scene[131072];
static FIL file;
int main(int argc,char**argv){
 if(argc<6)return 19;
 unsigned w=atoi(argv[2]),h=atoi(argv[3]),colours=atoi(argv[4]),dbl=atoi(argv[5]);
 if(!w||!h||w>1024||h>768||!colours)return 19;
 if(ffs_fopen(&file,argv[1],FA_READ))return 1;
 unsigned n=ffs_fread(&file,(char*)scene,sizeof(scene));ffs_fclose(&file);
 mos_puts((char*)scene,n,0);
 vdp_cursor_enable(0);
 if(dbl){const char swap[]={23,0,195};mos_puts(swap,3,0);}
 uint8_t last=getsysvar_vkeycount();unsigned anim=0,frame=0;
 clock_t start=clock(),prev=start;
 while((uint32_t)(clock()-start)<72000UL){
  uint8_t k=getsysvar_vkeycount();
  if(k!=last){last=k;if(getsysvar_vkeydown()){k=getsysvar_keyascii();if(k==27)break;if(k=='a'||k=='A')anim=!anim;}}
  if(!anim||clock()==prev)continue;
  prev=clock();
  /* Same deterministic full-surface tiles for every encoding; geometry scales.
   * Each frame redraws all tiles, so double buffering has no stale-page history. */
  for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++){
   vdp_gcol(0,(x+y+frame)%colours);
   vdp_filled_rectangle(x*w/8,y*h/8,(x+1)*w/8-1,(y+1)*h/8-1);
  }
  ++frame;const char sync[]={23,0,195};mos_puts(sync,3,0);
 }
 vdp_cursor_enable(1);return 0;
}
