"""Bench-free configurable codec build; inherited original algorithms unchanged."""
from pathlib import Path
import argparse,subprocess,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--emcc',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent.parent;old=root.parent/'srle2';a.out.mkdir(exist_ok=False);src=a.out/'c'
subprocess.run(['.venv/bin/python',str(old/'port.py'),str(src)],check=True)
f=src/'szip.c';s=f.read_text().replace('if(order!=3 || indexlast>=buflen)','if((order!=0 && order!=3 && order!=4 && order!=6) || indexlast>=buflen)').replace('if(recordsize!=1)sz_fail(1);','if(!(recordsize&127) || (recordsize&127)>8)sz_fail(1);')
s=s.replace('int p4_szip(int decode,','static unsigned chosen_order=3,chosen_record=1,chosen_block=4259840;\nint p4_szip(int decode,').replace('order=3;recordsize=1;verbosity=0;','order=chosen_order;recordsize=chosen_record;verbosity=0;')
a0=s.index('   /* -b41o3:');a1=s.index('\n  }\n  *written',a0)
s=s[:a0]+'''   writeglobalheader(length);
   for(size_t pos=0;pos<length;){size_t n=length-pos;if(n>chosen_block)n=chosen_block;
    unsigned char*buf=sz_alloc(n+order+1);memcpy(buf,src+pos,n);
    unsigned dir=writeblockdir(n);
    if(n<=order||n<=5)writestorblock(dir,n,buf);else writeszipblock(dir,n,buf);
    sz_free(buf);pos+=n;
   }'''+s[a1:]
s+='''
int bench_szip(int decode,const uint8_t*src,size_t n,uint8_t*dst,size_t cap,size_t*written,unsigned o,unsigned r,unsigned block){
 if((o!=0&&o!=3&&o!=4&&o!=6)||!(r&127)||(r&127)>8||r>255||!block||block>4259840)return 1;
 chosen_order=o;chosen_record=r;chosen_block=block;return p4_szip(decode,src,n,dst,cap,written);
}
'''
s=s.replace('static void *allocations[4096];','static void *allocations[4096];static size_t allocation_sizes[4096];').replace('allocations[i]=p;allocated+=n;','allocations[i]=p;allocation_sizes[i]=n;allocated+=n;').replace('heap_caps_free(p);allocations[i]=NULL;return;','allocated-=allocation_sizes[i];allocation_sizes[i]=0;heap_caps_free(p);allocations[i]=NULL;return;')
s=s.replace('int sz_get(void)', 'static void sz_release_block(void){for(unsigned i=0;i<4096;i++)if(allocations[i]){heap_caps_free(allocations[i]);allocations[i]=NULL;allocation_sizes[i]=0;}allocated=0;p4_szip_reset_sort();}\nint sz_get(void)').replace('sz_free(buf);pos+=n;', 'sz_free(buf);sz_release_block();pos+=n;').replace('    sz_free(buf);\n   }', '    sz_free(buf);sz_release_block();\n   }')
f.write_text(s)
(src/'esp_heap_caps.h').write_text('#pragma once\n#undef malloc\n#undef free\n#include <stdlib.h>\n#define MALLOC_CAP_SPIRAM 0\n#define MALLOC_CAP_8BIT 0\nstatic inline void*heap_caps_malloc(size_t n,int caps){(void)caps;return malloc(n);}\nstatic inline void heap_caps_free(void*p){free(p);}\n')
files=[str(x) for x in src.glob('*.c') if x.name!='qsort_u4.c']
subprocess.run(['cc','-O2','-shared','-fPIC',*files,'-I'+str(src),'-o',str(a.out/'codec.so')],check=True)
subprocess.run([str(a.emcc),'-O2',*files,'-I'+str(src),'-sMODULARIZE=1','-sEXPORT_ES6=1','-sENVIRONMENT=worker','-sINITIAL_MEMORY=67108864','-sSTACK_SIZE=2097152','-sALLOW_MEMORY_GROWTH=0','-sEXPORTED_FUNCTIONS=["_p4_szip","_bench_szip","_malloc","_free"]','-sEXPORTED_RUNTIME_METHODS=["HEAPU8","HEAPU32"]','-o',str(a.out/'szip.js')],check=True)
reference=a.out/'reference';shutil.copytree(old/'vendor',reference)
subprocess.run(['cc','-O2','-DGCC','szip.c','rangecod.c','qsmodel.c','bitmodel.c','sz_mod4.c','sz_srt.c','reorder.c','-o','szip'],cwd=reference,check=True)
(a.out/'manifest.json').write_text(json.dumps({'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'outputs':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in a.out.iterdir() if x.is_file()}},indent=2))
