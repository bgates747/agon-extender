#!/usr/bin/env python3
"""Build the paired timing protocol, drawing and precision controls."""
import argparse,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument("--prt-divider",type=int,choices=[16,64],default=16);p.add_argument('--no-markers',action='store_true',help='Build fixed pacing-only controls without timing.cfg');p.add_argument('--frames',type=int,default=120);a=p.parse_args()
if not 1<=a.frames<=10000:p.error('--frames must be in 1..10000')
if a.output.exists():p.error('output must be a fresh directory')
root=Path(__file__).resolve().parents[3];a.output.mkdir(parents=True)
for source in sorted((root/'tests/performance/controls').glob('*.cpp')):
 out=a.output/source.stem;(out/'src').mkdir(parents=True);(out/'include').mkdir()
 shutil.copy2(source,out/'src/main.cpp')
 for name in ['game_timing.hpp','entries.asm','prt.asm']:
  if source.stem=='prtcheck' and name!='prt.asm':continue
  shutil.copy2(root/'tests/performance/ez80'/name,out/('include' if name.endswith('hpp') else 'src')/name)
 if a.no_markers and source.stem!='prtcheck':
  header=out/'include/game_timing.hpp';text=header.read_text()
  old='FILE*cfg=fopen("timing.cfg","r");if(!cfg)return false;\n int selected=fgetc(cfg);fclose(cfg);if(selected!=\'0\'&&selected!=\'1\')return false;markers=selected==\'1\';'
  if text.count(old)!=1:raise RuntimeError('expected timing.cfg selection block')
  header.write_text(text.replace(old,'markers=false; // Fixed pacing-only qualification control'))
 if source.stem!='prtcheck':
  header=out/'include/game_timing.hpp';text=header.read_text()
  if text.count('constexpr unsigned Frames=120;')!=1:raise RuntimeError('expected frame-count declaration')
  header.write_text(text.replace('constexpr unsigned Frames=120;',f'constexpr unsigned Frames={a.frames};'))
 if a.prt_divider==64:
  prt=out/'src/prt.asm';prt.write_text(prt.read_text().replace('ld a,007h','ld a,00bh'))
 arguments=1 if source.stem=='empty' else 0
 (out/'Makefile').write_text('NAME='+source.stem+f'\nLDHAS_ARG_PROCESSING={arguments}\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nCXXFLAGS += -std=c++17\n')
 subprocess.run(['make','-C',str(out)],check=True)
