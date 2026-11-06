/* SPDX-License-Identifier: GPL-3.0-only: actual main adapter with host MOS double. */
#include <agon/mos.h>
#include "setup.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
struct test_file {FILE *f;};
static struct test_file files[3];
static int fault,uart_calls,reads;
int ws_native_main(int,char **);
uint32_t getsysvar_time(void) {static uint32_t t;return t++;}
uint8_t getsysvar_keyascii(void) {return fault==4&&reads>4?27:0;}
uint8_t getsysvar_vkeydown(void) {return 1;}
int mos_ugetc_nb(void) {return -1;}
int wifi_try_put(int c) {(void)c;abort();}
uint8_t mos_uopen(UART *u) {assert(u->baudRate==115200&&u->flowcontrol==0&&u->eir==0);uart_calls++;return 1;}
uint8_t mos_uclose(void) {abort();}
uint8_t mos_fopen(const char *s,uint8_t m) {
 unsigned i=m==FA_READ?2:1;assert(!files[i].f);files[i].f=fopen(s,m==FA_READ?"rb":"r+b");
 if(!files[i].f&&m!=FA_READ)files[i].f=fopen(s,"w+b");
 return files[i].f?i:0;
}
uint8_t mos_fclose(uint8_t h) {assert(files[h].f);fclose(files[h].f);files[h].f=NULL;return 0;}
uint8_t mos_feof(uint8_t h) {return feof(files[h].f)!=0;}
size_t mos_fread(uint8_t h,char *b,size_t n) {reads++;if(fault==5)return 0;return fread(b,1,n,files[h].f);}
size_t mos_fwrite(uint8_t h,char *b,size_t n) {if(fault==1)return n?n-1:0;return fwrite(b,1,n,files[h].f);}
FIL *mos_getfil(uint8_t h) {return &files[h];}
uint8_t mos_flseek(uint8_t h,uint32_t n) {return fseek(files[h].f,n,SEEK_SET)!=0;}
uint8_t ffs_fsize(FIL *p,uint32_t *n) {if(fault==3)return 1;fseek(p->f,0,SEEK_END);*n=(uint32_t)ftell(p->f);return 0;}
uint8_t ffs_fsync(FIL *p) {return fault==2?1:fflush(p->f)!=0;}
int main(int argc,char **argv) {
 char cfg[400],log[400];char *args[]={"wifi-setup",cfg,log,NULL};
 assert(argc==2);snprintf(cfg,sizeof(cfg),"%s/private.cfg",argv[1]);snprintf(log,sizeof(log),"%s/progress.log",argv[1]);
 for(fault=0;fault<=5;fault++) {
  int expected=128+(fault==0?4:fault<=3?7:fault==4?3:2);FILE *f=fopen(cfg,"wb");
  assert(f);fputs("ssid=private-network\npassword=never-log-this\nbbs_host=example.invalid\n",f);fclose(f);
  f=fopen(log,"wb");assert(f);fputs("PREVIOUS SESSION\n",f);fclose(f);
  uart_calls=reads=0;int got=ws_native_main(3,args);
  if(got!=expected)fprintf(stderr,"fault%d expected%d actual%d\n",fault,expected,got);
  assert(got==expected&&uart_calls==(fault==0));assert(!files[1].f&&!files[2].f);
  char buffer[4000];f=fopen(log,"rb");size_t n=fread(buffer,1,sizeof(buffer)-1,f);buffer[n]=0;fclose(f);
  assert(!strncmp(buffer,"PREVIOUS SESSION\n",17));assert(!strstr(buffer,"never-log-this")&&!strstr(buffer,"private-network"));
 }
 for(int code=0;code<=8;code++)assert(ws_mos_exit(code)==(code?128+code:0));
 puts("PASS: native adapter log append, partial write, sync/seek failures, config Escape/read failure, no premature UART open.");return 0;
}
