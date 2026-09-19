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
static void dense(unsigned w,unsigned h,unsigned colours,unsigned dbl){
 putch(20);if(colours!=64){const char reset[]={23,0,196,4};mos_puts(reset,4,0);}
 uint8_t pixels[1024];unsigned seed=817;
 uint8_t palette[16]={0,2,8,10,32,34,40,42,21,3,12,15,48,51,60,63};
 if(colours==2)palette[1]=63;
 if(colours==4){palette[1]=3;palette[2]=12;palette[3]=63;}
 if(colours!=64)for(unsigned i=0;i<colours;i++){unsigned c=palette[i];uint8_t set[]={19,i,255,(c&3)*85,((c>>2)&3)*85,((c>>4)&3)*85};mos_puts((char*)set,sizeof(set),0);}
 for(unsigned i=0;i<1024;i++){seed=(seed*109+89)&65535;unsigned c=(seed>>6)%colours;pixels[i]=192|(colours==64?c:palette[c]);}
 const uint8_t clear[]={23,0,160,32,203,2};mos_puts((char*)clear,sizeof(clear),0);
 const uint8_t prefix[]={23,0,160,32,203,0,0,4};mos_puts((char*)prefix,sizeof(prefix),0);mos_puts((char*)pixels,sizeof(pixels),0);
 const uint8_t bitmap[]={23,27,32,32,203,23,27,33,32,0,32,0,1};mos_puts((char*)bitmap,sizeof(bitmap),0);
 const uint8_t flush[]={23,0,202};mos_puts((char*)flush,sizeof(flush),0);
 for(unsigned y=0;y<h;y+=32)for(unsigned x=0;x<w;x+=32){uint8_t plot[]={25,237,x,x>>8,y,y>>8};mos_puts((char*)plot,sizeof(plot),0);}
 const char sync[]={23,0,195};if(dbl)mos_puts(sync,3,0);
}
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
  if(k!=last){last=k;if(getsysvar_vkeydown()){k=getsysvar_keyascii();if(k==27)break;if(k=='a'||k=='A')anim=!anim;if(k=='d'||k=='D')dense(w,h,colours,dbl);}}
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
