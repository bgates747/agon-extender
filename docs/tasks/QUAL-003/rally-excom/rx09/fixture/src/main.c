#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint8_t *sv;
static char line[180];
static const char *output;
static unsigned failures,probes;
static uint32_t started;
static void send(const void *p,unsigned n){mos_puts((const char*)p,n,0);}
static int append(const char *s){
    uint8_t f=mos_fopen(output,FA_WRITE|FA_OPEN_APPEND);if(!f)return 0;
    unsigned n=strlen(s),got=mos_fwrite(f,(char*)s,n);mos_fclose(f);return got==n;
}
static void plot(uint8_t op,int x,int y){
    uint8_t p[]={25,op,x,x>>8,y,y>>8};send(p,sizeof p);
}
static void viewport(int left,int top,int right,int bottom){
    uint8_t p[]={24,left,left>>8,bottom,bottom>>8,right,right>>8,top,top>>8};
    send(p,sizeof p);plot(4,left,top); /* Same clip activation as current hud.hpp. */
}
static void colour(unsigned c){uint8_t p[]={18,0,c};send(p,sizeof p);}
static void rect(int x1,int y1,int x2,int y2,unsigned c){colour(c);plot(4,x1,y1);plot(101,x2,y2);}
static int probe(unsigned frame,int x,int y,unsigned r,unsigned g,unsigned b){
    uint8_t q[]={23,0,0x84,x,x>>8,y,y>>8};mos_clearvdpflags(4);send(q,sizeof q);
    unsigned status=mos_waitforvdpflags(4);if(status)return 0;
    /* Stock ABI is R,G,B in the three wire bytes, despite legacy field names. */
    unsigned a=sv[sysvar_scrpixel],c=sv[sysvar_scrpixel+1],d=sv[sysvar_scrpixel+2];
    unsigned match=r==999 || (a==r&&c==g&&d==b);++probes;failures+=!match;
    snprintf(line,sizeof line,"probe,%u,%d,%d,%u,%u,%u,%u,%u,%u,%u\r\n",frame,x,y,r,g,b,a,c,d,match);
    return append(line);
}
/* numeric-guard-probe-r02: stock receives valid cases only; rejection mode is P4 only.
 * Caller selects mode136/route in autoexec. Counts are correctness probes;
 * raw120Hz elapsed includes serial queries and SD writes, not renderer FPS. */
#define SRC 1200
#define MAT 1201
#define DST 1202
static void clearbuf(unsigned id){uint8_t p[]={23,0,160,id,id>>8,2};send(p,sizeof p);}
static void block(unsigned id,const void *data,unsigned n){uint8_t p[]={23,0,160,id,id>>8,0,n,n>>8};send(p,sizeof p);send(data,n);}
static void matrix(const uint32_t *bits,const uint32_t *inverse){clearbuf(MAT);block(MAT,bits,36);if(inverse)block(MAT,inverse,36);}
static void selectbm(unsigned id){uint8_t p[]={23,27,32,id,id>>8};send(p,sizeof p);}
static void create(unsigned id,unsigned w,unsigned h,unsigned fmt){selectbm(id);uint8_t p[]={23,27,33,w,w>>8,h,h>>8,fmt};send(p,sizeof p);}
static void transform(unsigned id){uint8_t p[]={23,0,150,1,id,id>>8};send(p,sizeof p);}
static void source(unsigned fmt){uint8_t bytes[64];memset(bytes,255,sizeof bytes);clearbuf(SRC);block(SRC,bytes,fmt==0?64:fmt==1?16:4);create(SRC,4,4,fmt);}
static void copied(void){uint8_t p[]={23,0,160,(uint8_t)DST,DST>>8,40,5,(uint8_t)MAT,MAT>>8,(uint8_t)SRC,SRC>>8};send(p,sizeof p);}
static const uint32_t identity[9]={0x3f800000,0,0,0,0x3f800000,0,0,0,0x3f800000};
static void logical(uint32_t x,uint32_t y){uint8_t p[]={23,0,160,(uint8_t)MAT,MAT>>8,32,0,23,0,160,(uint8_t)MAT,MAT>>8,32,7,0};clearbuf(MAT);send(p,sizeof p);send(&x,4);send(&y,4);}
static int sample(unsigned id){
 transform(65535);viewport(0,0,319,239);rect(20,180,24,184,4);
 if(!probe(id,160,12,170,0,0)||!probe(id,22,182,0,0,170))return 0;
 for(int y=99;y<=108;y+=3)for(int x=77;x<=86;x+=3)if(!probe(id,x,y,999,999,999))return 0;
 return 1;
}
int main(int argc,char **argv){
 if(argc!=3)return 2;output=argv[1];sv=mos_sysvars();int reject=!strcmp(argv[2],"reject");if(!reject&&strcmp(argv[2],"valid"))return 2;
 uint8_t existing=mos_fopen(output,FA_READ);if(existing){mos_fclose(existing);return 3;}
 uint8_t q[]={23,0,134};mos_clearvdpflags(16);send(q,sizeof q);if(mos_waitforvdpflags(16))return 4;if((sv[sysvar_scrMode]&127)!=8)return 5;
 started=getsysvar_time();if(!append("numeric-guard-probe-r02,correctness-only,raw-ticks-120Hz\r\n"))return 6;
 const uint8_t init[]={23,0,192,0,23,1,0,23,0,248,1,0,1,0};send(init,sizeof init);
 const uint8_t swap[]={23,0,195};unsigned id=0;
 for(unsigned page=0;page<2;page++)for(unsigned fmt=0;fmt<3;fmt++)for(unsigned kind=0;kind<(reject?5u:3u);kind++){
  transform(65535);viewport(0,0,319,239);rect(0,0,319,239,0);rect(0,0,319,23,1);colour(15);source(fmt); /* default palette15 is white;63 is pale yellow */
  uint32_t mat[9];memcpy(mat,identity,sizeof mat);matrix(mat,0);selectbm(SRC);
  snprintf(line,sizeof line,"begin,%u,page=%u,format=%u,kind=%u\r\n",id,page,fmt,kind);if(!append(line))return 7;
  if(!reject){
   if(kind==0)logical(0xbfe00000,0x40200000); /* -1.75 and2.5; truncation before scale */
   if(kind==1){mat[0]=0xbf800000;mat[2]=0x40800000;matrix(mat,0);} /* mirror with positive translated bounds */
   if(kind==2){mat[2]=0xc0000000;mat[5]=0x3f800000;matrix(mat,0);copied();selectbm(DST);}
   transform(kind==2?65535:MAT);plot(0xed,80,100);
  }else{
   if(kind==0){logical(0x7fc00000,0);transform(MAT);plot(0xed,80,100);} /* invalid logical translate leaves identity */
   if(kind==1){copied();mat[0]=0x7fc00000;matrix(mat,identity);copied();selectbm(DST);plot(0xed,80,100);} /* retained destination */
   if(kind==2){mat[0]=0x7fc00000;matrix(mat,identity);transform(MAT);plot(0xed,80,100);} /* invalid plot bounds */
   if(kind==3){uint32_t inv[9];memcpy(inv,identity,sizeof inv);inv[0]=0x7fc00000;matrix(identity,inv);transform(MAT);plot(0xed,80,100);} /* invalid inverse source samples */
   if(kind==4){create(SRC,65535,65535,0);plot(0xed,80,100);} /* no bitmap after oversized count */
  }
  if(!sample(id))return 8;
  if(!probe(id,81,103,reject&&kind>=2?0:255,reject&&kind>=2?0:255,reject&&kind>=2?0:255))return 8;
  ++id;send(swap,sizeof swap);
 }
 transform(65535);viewport(0,0,319,239);
 snprintf(line,sizeof line,"complete,cases=%u,probes=%u,failures=%u,elapsed_ticks=%lu\r\n",id,probes,failures,(unsigned long)(getsysvar_time()-started));if(!append(line))return 9;
 printf("\r\nNumeric tests ended: %u cases, %u checks, %u failures\r\n",id,probes,failures);return failures?10:0;
}
