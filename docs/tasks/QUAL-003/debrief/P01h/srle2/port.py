"""Generate P4 C sources from pinned vendor bytes; compilation only, no execution."""
from pathlib import Path
import shutil,sys
root=Path(__file__).resolve().parent;out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
for p in (root/'vendor').glob('*'):
 if p.suffix in ('.c','.h'):shutil.copy2(p,out/p.name)
for name in ['io.h','szip_p4.h']:shutil.copy2(root/name,out/name)
(out/'port.h').write_text('#pragma once\n#include <stdint.h>\ntypedef unsigned int uint;\ntypedef uint16_t uint2;\ntypedef uint32_t uint4;\n#define Inline inline\n_Static_assert(sizeof(uint4)==4,"szip requires 32-bit words");\n')
for p in out.glob('*.c'):
 if p.name=='qsort_u4.c':continue
 s=p.read_text()
 # Include redirects after all standard declarations, before first function.
 s='#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <ctype.h>\n#include <sys/stat.h>\n#include "io.h"\n'+s
 if p.name=='szip.c':
  s=s[:s.index('static void compressit()')]
  # Original local codec kept the model on stack and omitted output for r1.
  s=s.replace('sz_model m;','sz_model *model = (sz_model*) sz_alloc(sizeof(sz_model));\n#define m (*model)')
  s=s.replace('deletemodel(&m);','deletemodel(&m);\n    sz_free(model);\n#undef m')
  # sz_unsrt(NULL) already emits via putc; do not append its work buffer.
  s=s.replace('order = getchar();','order = getchar();\n    if(order!=3 || indexlast>=buflen)sz_fail(1);')
  s=s.replace('initmodel(&m, -1, &recordsize);','initmodel(&m, -1, &recordsize);\n    if(recordsize!=1)sz_fail(1);')
  s=s.replace('if (runlength>bytesleft)','if (!runlength || ch>255 || runlength>bytesleft)')
  s+='\n'+(root/'entry.inc').read_text()
 if p.name=='sz_srt.c':
  # Legacy function-local caches cannot survive invocation-owned cleanup.
  s=s.replace('static uint4 *table;','uint4 *table=NULL;')
  for decl in ['uint4 *counters=NULL','uint2 *context=NULL','unsigned char *symbols=NULL','unsigned char *flags1=NULL','unsigned char *flags2=NULL']:
   s=s.replace('static '+decl,decl)
  s+='\nvoid p4_szip_reset_sort(void){globalinit=0;memset(&globalptr,0,sizeof globalptr); }\n'

 p.write_text(s)
