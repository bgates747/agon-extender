"""Run the actual fixture control flow against bounded fake MOS/file/VDP APIs.
Not an emulator or hardware timing test. Exercise success and durable-write failure.
"""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
header='''#include <stdint.h>
typedef unsigned uint24_t;
typedef struct { int unused; } FIL;
enum {FA_READ=1,FA_WRITE=2,FA_OPEN_APPEND=4,FA_CREATE_NEW=8,FR_DISK_ERR=1,FR_EXIST=8,FR_TIMEOUT=15,FR_INT_ERR=2,FR_NO_FILE=4,FR_INVALID_PARAMETER=19};
enum {sysvar_vkeycount=0,sysvar_scrMode=1,sysvar_scrpixel=2};
unsigned ffs_fwrite(FIL*,const char*,unsigned);unsigned ffs_fsync(FIL*);unsigned ffs_fclose(FIL*);unsigned ffs_fopen(FIL*,const char*,unsigned);
uint8_t mos_fopen(const char*,unsigned);unsigned mos_fread(uint8_t,char*,unsigned);void mos_fclose(uint8_t);
unsigned mos_oscli(char*,void*,unsigned);void mos_clearvdpflags(unsigned);unsigned mos_waitforvdpflags(unsigned);void *mos_sysvars(void);void mos_setkbvector(void(*)(void),unsigned);
'''
harness='''#include <assert.h>
#include <stdlib.h>
#define main fixture_main
#include "SOURCE"
#undef main
static char journal[50000],screen[50000];static unsigned jlen,slen,opens,closes,syncs,active,measuring,fail;
static uint8_t vars[20]={0,20};
unsigned ffs_fopen(FIL*f,const char*p,unsigned flags){(void)f;(void)p;(void)flags;assert(!measuring);++opens;return 0;}
unsigned ffs_fwrite(FIL*f,const char*p,unsigned n){(void)f;assert(!measuring);if(fail==1 && strstr(p,"next=output"))return 0;memcpy(journal+jlen,p,n);jlen+=n;journal[jlen]=0;return n;}
unsigned ffs_fsync(FIL*f){(void)f;++syncs;return 0;}
unsigned ffs_fclose(FIL*f){(void)f;++closes;return 0;}
uint8_t mos_fopen(const char*p,unsigned f){(void)p;(void)f;assert(!measuring);return 1;}
unsigned mos_fread(uint8_t f,char*p,unsigned n){(void)f;(void)p;(void)n;return 0;}
void mos_fclose(uint8_t f){(void)f;}
unsigned mos_oscli(char*p,void*x,unsigned n){(void)x;(void)n;assert(!measuring);active=strstr(p,"excom")!=0;return 0;}
void mos_clearvdpflags(unsigned n){(void)n;}
unsigned mos_waitforvdpflags(unsigned n){(void)n;return 0;}
void *mos_sysvars(void){return vars;}
void mos_setkbvector(void(*f)(void),unsigned n){(void)f;(void)n;}
void graphics_callback(void){}
uint24_t bench_clock(const volatile uint8_t*p){static unsigned t;(void)p;return ++t;}
uint24_t bench_count(const uint8_t*p,uint24_t n){
 if(n==7 && p[0]==23 && p[2]==0xEF){
  assert(active==route);
  if(p[3]==1){assert(!measuring);measuring=1;received[0]=1;}
  else if(p[3]==2 || p[3]==3){assert(measuring);measuring=0;if(fail==2)return FR_TIMEOUT;received[1]=1;receive_done=clock_now();}
  else {assert(p[3]==4);received[p[6]]=1;}
 }else if(n && p[0]=='P'){
  assert(!active && !measuring);memcpy(screen+slen,p,n);slen+=n;screen[slen]=0;
 }else if(n==7 && p[0]==26){assert(!measuring);for(unsigned i=0;i<n;++i)assert(p[i]!=12 && p[i]!=30 && p[i]!=31);}
 return 0;
}
int main(int argc,char**argv){fail=argc>1?atoi(argv[1]):0;char *args[]={"test","unattended"};assert(fixture_main(2,args)==0);
 assert(strstr(journal,"# timing,start_tick=") && strstr(journal,",nominal_hz=120"));
 assert(opens==closes && opens==syncs);assert(!active && !measuring);
 if(fail==2){assert(graphics_exit_status==FR_TIMEOUT && saved==1);assert(strstr(journal,"# terminal,status=15,saved=1"));}
 else if(fail){assert(graphics_exit_status==FR_DISK_ERR);assert(saved==1);assert(strstr(journal,"# terminal,status=1,saved=1"));}
 else {assert(!graphics_exit_status && saved==16);assert(strstr(journal,"# terminal,status=0,saved=16"));assert(strstr(screen,"P4 test 4/4 ONLY probe [16/16]"));}
 assert(strstr(journal,"next=draw") && strstr(journal,"next=setup"));
 return 0;
}
'''.replace('SOURCE',str(ROOT/'fixture/src/main.c'))
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'agon').mkdir();(p/'agon/mos.h').write_text(header)
 (p/'build_identity.h').write_text('#define GRAPHICS_BUILD_ID "host-control-flow-test"\n')
 (p/'cases.h').write_text('typedef struct {const char*name;unsigned group,setup,bytes,probes,uploads;} Case;\nstatic const Case cases[]={{"ONLY",0,0,0,0,0}};\n#define CASE_COUNT 1\n#define MAX_CASE_BYTES 1\n')
 (p/'test.c').write_text(harness)
 subprocess.run(['cc','-std=c17','-I'+tmp,str(p/'test.c'),'-o',str(p/'test')],check=True)
 for fault in ('0','1','2'):subprocess.run([str(p/'test'),fault],check=True)
print('PASS: complete run; SD-write failure; VDP failure; synced journal; no status IO inside measurements; batch continuation; Legacy return')
