"""Execute the actual MOSlet's pattern, guard, stop and durable-report logic.

MOS gateway and SD I/O are modeled. This does not exercise physical GPIO or
AgonDev's target stdio; the target executable is compiled separately.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "agon-emos/projects/parprobe/src"
HARNESS = r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "pattern.h"
int fixture_main(int,char **);
static unsigned calls,scenario;
static char report[8192];
static uint32_t ticks;
uint32_t getsysvar_time(void){ticks+=2;return ticks;}
FILE *fixture_fopen(const char *path,const char *mode){
 assert(!strcmp(path,"/agents/extender/results/probe.csv"));
 if(!strcmp(mode,"r"))return scenario==6?tmpfile():NULL;
 assert(!strcmp(mode,"w"));return scenario==7?NULL:tmpfile();
}
int fixture_fclose(FILE *f){
 rewind(f);size_t n=fread(report,1,sizeof report-1,f);report[n]=0;return fclose(f);
}
static unsigned read24(const uint8_t *p){return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16);}
uint32_t emos_gateway_call(uint8_t *r){
 ++calls;assert(r[0]==66&&r[2]==1&&r[4]==3&&r[5]==8&&r[6]==2);
 assert(!memcmp(r+25,"ext",3)&&!memcmp(r+41,"uartdiag",8)&&read24(r+13)==2);
 uint8_t *input=(void*)(uintptr_t)read24(r+10),*out=(void*)(uintptr_t)read24(r+16);
 unsigned cap=read24(r+19),n=cap-16,reverse=input[1];assert(input[0]==6&&n&&n<=4096);
 assert(reverse==((calls-1)%10)/5);
 memset(out,0,16);memcpy(out,"EX\x03\x02",4);out[4]=calls;out[8]=1;
 out[10]=n;out[11]=n>>8;out[12]=reverse;
 if(reverse)for(unsigned i=0;i<n;++i)out[16+i]=parallel_probe_pattern(i,parallel_probe_seed(out));
 r[22]=cap;r[23]=cap>>8;
 if(calls==6){
  if(scenario==1)return 35;
  if(scenario==2)out[16]^=0x80;
  if(scenario==3)out[cap]=0;
  if(scenario==4)r[22]^=1;
  if(scenario==5)out[10]^=1;
 }
 return 0;
}
int main(void){
 char *args[]={"parprobe","/agents/extender/results/probe.csv"};
 char *version[]={"parprobe","--version"},*bad[]={"parprobe","bad"};
 assert(fixture_main(2,version)==0&&!calls);
 assert(fixture_main(1,args)==19&&!calls);assert(fixture_main(2,bad)==19&&!calls);
 for(scenario=0;scenario<8;++scenario){
  calls=0;report[0]=0;ticks=0;
  int status=fixture_main(2,args);
  if(scenario==0){assert(status==0&&calls==20&&strstr(report,"passed=20/20"));}
  else if(scenario<6){assert(status==15&&calls==6&&strstr(report,"passed=5/20"));}
  else {assert(status==(scenario==6?19:15)&&!calls);}
 }
 puts("PASS11 MOSlet invocation/complete/stop/report cases; modeled gateway/SD");
}
'''


class MosletTests(unittest.TestCase):
    def test_actual_moslet(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "agon").mkdir()
            (d / "agon/mos.h").write_text("#include <stdint.h>\ntypedef uint32_t uint24_t;\nuint32_t getsysvar_time(void);\n")
            (d / "test.c").write_text(HARNESS)
            flags = ["cc", "-std=c17", "-Wall", "-Wextra", "-Werror", "-Wno-pointer-to-int-cast",
                     "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-I" + str(d), "-I" + str(SOURCE)]
            subprocess.run(flags + ["-Dmain=fixture_main", "-Dfopen=fixture_fopen", "-Dfclose=fixture_fclose",
                                    "-c", str(SOURCE / "main.c"), "-o", str(d / "main.o")], check=True)
            subprocess.run(flags + ["-no-pie", str(d / "main.o"), str(d / "test.c"), "-o", str(d / "test")], check=True)
            subprocess.run([str(d / "test")], check=True, timeout=15)


if __name__ == "__main__":
    unittest.main()
