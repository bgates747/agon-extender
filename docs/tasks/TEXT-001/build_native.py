#!/usr/bin/env python3
"""Build only a bespoke VDP module from a COPY of the installed Fab source.
Leaves upstream sources, libraries and emulator executable untouched.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--fab',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
src=a.fab.resolve()/'src/vdp';out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
for name in ['vdp-console8.cpp','vdp-console8.h','vdp.h','rust_glue.cpp']:shutil.copy2(src/name,out/name)
shutil.copytree(src/'vdp-console8/video',out/'vdp-console8/video')
(out/'userspace-vdp-gl').symlink_to(src/'userspace-vdp-gl')
subprocess.run(['python3',str(Path(__file__).with_name('apply-native-prototype.py')),str(out/'vdp-console8/video')],check=True)
flags=['g++','-O2','-std=c++17','-DUSERSPACE','-fPIC','-g','-I.','-Iuserspace-vdp-gl/src','-Iuserspace-vdp-gl/src/userspace-platform','-Iuserspace-vdp-gl/src/userspace-platform/matrix','-Iuserspace-vdp-gl/src/dispdrivers','-Ivdp-console8/video']
for name in ['vdp-console8','rust_glue']:subprocess.run(flags+['-c',name+'.cpp','-o',name+'.o'],cwd=out,check=True)
subprocess.run(['g++','-shared','rust_glue.o','vdp-console8.o','userspace-vdp-gl/src/vdp-gl.a','-o','vdp_text001.so'],cwd=out,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'native_vdp_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src/'vdp-console8',text=True).strip(),'gl_archive_sha256':sha(src/'userspace-vdp-gl/src/vdp-gl.a'),'module_sha256':sha(out/'vdp_text001.so'),'scope':'TEXT-001 native prototype; not hardware qualification'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
