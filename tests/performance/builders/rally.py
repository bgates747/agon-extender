#!/usr/bin/env python3
"""Build isolated game timing derivative; source checkout is never modified."""
import argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--prt-divider',type=int,choices=[16,64],default=16)
args=parser.parse_args()
if args.output.exists():parser.error('output must be a fresh directory')
args.output.parent.mkdir(parents=True,exist_ok=True)
from pathlib import Path
import shutil,subprocess
r=Path(__file__).resolve().parents[3];orig=args.source.resolve();out=args.output.resolve()
out.mkdir(exist_ok=True)
for d in ['src','include']:shutil.copytree(orig/'rally-game'/d,out/d,dirs_exist_ok=True)
shutil.copytree(orig/'rally-production/include',out/'shared',dirs_exist_ok=True)
for name in ['game_timing.hpp','entries.asm','prt.asm']:shutil.copy2(r/'tests/performance/ez80'/name,out/('include' if name.endswith('hpp') else 'src')/name)
if args.prt_divider==64:
 p=out/'src/prt.asm';p.write_text(p.read_text().replace('ld a,007h','ld a,00bh').replace('Single-pass /16','Single-pass /64').replace('1,152,000','288,000').replace('~56.89 ms','~227.55 ms'))
s=(out/'src/main.cpp').read_text();s='#include "game_timing.hpp"\n'+s
s=s.replace('if(!readRecords("rally.sav",records))readRecords("rally.bak",records);','// Isolated test: no production high scores read or written.')
s=s.replace('if(vdp_mode(136)<0)return 1;','// Startup selects mode 136.')
s=s.replace('uint32_t previous=rawClock(),next=previous;','if(!gt::init()) return 2;\n    uint32_t previous=rawClock(),next=previous;')
s=s.replace('const uint32_t now=rawClock();if(!rally::tickDue(now,next))continue;next=now+4;','gt::loop_begin();\n        const uint32_t now=rawClock();next=now+4;')
s=s.replace('input();if(quit)break;','// Poll the entire real map above; deterministic attract driver owns controls.\n        if(false) input();')
s=s.replace('drawScenery();road.emit', 'gt::drawing_begin();\n        drawScenery();road.emit')
s=s.replace('vdp_swap();sceneryHistory.swapped();','vdp_swap();sceneryHistory.swapped();\n        gt::drawing_end();\n        while(!rally::tickDue(rawClock(),next)) {}\n        if(gt::loop_end()) break;')
s=s.replace('(void)saveRecords(records);savePending=false;','savePending=false;')
s=s.replace('engine.stop(send);font(65535);','bool timingOK=gt::save("rally.csv");\n    printf("Timing %s: rally.csv\\n",timingOK?"complete":"failed");\n    engine.stop(send);font(65535);')
s=s.replace('vdp_mode(0);','')
(out/'src/main.cpp').write_text(s)
(out/'Makefile').write_text('NAME=rtiming\nLDHAS_ARG_PROCESSING=0\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nOBJS := $(filter-out obj/emos_gateway.o,$(OBJS))\nCFLAGS += -Ishared\nCXXFLAGS += -std=c++17 -Wall -Wextra -Werror -fno-exceptions -fno-rtti\n')
subprocess.run(['make','-C',str(out)],check=True)

from provenance import record
record(args.source,args.output,prt_divider=args.prt_divider)
