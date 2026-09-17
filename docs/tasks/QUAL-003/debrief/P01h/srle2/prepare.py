"""Prepare isolated candidate from retained RLE2 build cache; never use the bench."""
from pathlib import Path
import sys,subprocess,json,shutil,configparser
root=Path(__file__).resolve().parent;parent=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(exist_ok=False)
subprocess.run(['cp','-a','--reflink=auto',str(parent/'source'),str(out/'source')],check=True)
v=out/'source/vdp/video';dest=v/'extender/diagnostics/srle2'
subprocess.run([sys.executable,str(root/'port.py'),str(dest)],check=True)
shutil.copy2(root/'srle2.hpp',dest/'srle2.hpp')
f=v/'vdu_buffered.h';s=f.read_text();s='#include "extender/diagnostics/srle2/srle2.hpp"\n'+s
needle='if(prefix_n==4 && std::memcmp(prefix,"Cmpr",4)==0)';assert s.count(needle)==1;s=s.replace(needle,(root/'asset.inc').read_text()+'\n'+needle);f.write_text(s)
f=out/'source/vdp/pio/p4-console-source-selection.json';m=json.loads(f.read_text())
for p in dest.glob('*.c'):
 if p.name!='qsort_u4.c':m['project_translation_units'].append(str(p.relative_to(out/'source/vdp')))
f.write_text(json.dumps(m,indent=2)+'\n')
# Apply C++ standard only to C++; original codec remains C on RISC-V.
f=out/'source/vdp/pio/select_sources.py';s=f.read_text().replace('PRIVATE "-std=gnu++17"','PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>"');f.write_text(s)
shutil.copy2(parent/'sdkconfig',out/'sdkconfig');c=configparser.ConfigParser(interpolation=None);c.optionxform=str;c.read(parent/'platformio.ini');c['platformio']['build_dir']=str(out/'build');c['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(out/'sdkconfig')
with (out/'platformio.ini').open('w') as f:c.write(f)
