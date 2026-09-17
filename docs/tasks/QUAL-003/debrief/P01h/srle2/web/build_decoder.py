"""Build shared native/wasm codec from same generated P4 C; no bench access."""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--emcc',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];a.out.mkdir(exist_ok=False);src=a.out/'c'
subprocess.run(['.venv/bin/python',str(root/'port.py'),str(src)],check=True)
(src/'esp_heap_caps.h').write_text('#pragma once\n#undef malloc\n#undef free\n#include <stdlib.h>\n#define MALLOC_CAP_SPIRAM 0\n#define MALLOC_CAP_8BIT 0\nstatic inline void*heap_caps_malloc(size_t n,int caps){(void)caps;return malloc(n);}\nstatic inline void heap_caps_free(void*p){free(p);}\n')
files=[str(x) for x in src.glob('*.c') if x.name!='qsort_u4.c']
subprocess.run(['cc','-O2','-shared','-fPIC',*files,'-I'+str(src),'-o',str(a.out/'codec.so')],check=True)
args=[str(a.emcc),'-O2',*files,'-I'+str(src),'-sMODULARIZE=1','-sEXPORT_ES6=1','-sENVIRONMENT=worker','-sEXPORT_NAME=createSzip','-sINITIAL_MEMORY=67108864','-sSTACK_SIZE=2097152','-sALLOW_MEMORY_GROWTH=0','-sEXPORTED_FUNCTIONS=["_p4_szip","_malloc","_free"]','-sEXPORTED_RUNTIME_METHODS=["HEAPU8","HEAPU32"]','-o',str(a.out/'szip.js')]
subprocess.run(args,check=True)
(a.out/'build.json').write_text(json.dumps(dict(args=args,outputs={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.out.iterdir() if f.is_file()}),indent=2)+'\n')
