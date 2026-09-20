#!/usr/bin/env python3
"""Build the paired timing protocol, drawing and precision controls."""
import argparse,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument("--prt-divider",type=int,choices=[16,64],default=16);a=p.parse_args()
if a.output.exists():p.error('output must be a fresh directory')
root=Path(__file__).resolve().parents[3];a.output.mkdir(parents=True)
for source in sorted((root/'tests/performance/controls').glob('*.cpp')):
 out=a.output/source.stem;(out/'src').mkdir(parents=True);(out/'include').mkdir()
 shutil.copy2(source,out/'src/main.cpp')
 for name in ['game_timing.hpp','entries.asm','prt.asm']:
  if source.stem=='prtcheck' and name!='prt.asm':continue
  shutil.copy2(root/'tests/performance/ez80'/name,out/('include' if name.endswith('hpp') else 'src')/name)
 if a.prt_divider==64:
  prt=out/'src/prt.asm';prt.write_text(prt.read_text().replace('ld a,007h','ld a,00bh'))
 (out/'Makefile').write_text('NAME='+source.stem+'\nLDHAS_ARG_PROCESSING=0\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nCXXFLAGS += -std=c++17\n')
 subprocess.run(['make','-C',str(out)],check=True)
