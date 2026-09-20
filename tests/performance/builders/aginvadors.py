#!/usr/bin/env python3
"""Build isolated game timing derivative; source checkout is never modified."""
import argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
if args.output.exists():parser.error('output must be a fresh directory')
args.output.parent.mkdir(parents=True,exist_ok=True)
from pathlib import Path
import shutil,subprocess
root=Path(__file__).resolve().parents[3];src=args.source.resolve();out=args.output.resolve()
out.mkdir(exist_ok=True)
for d in ['include','src']:shutil.copytree(src/d,out/d,dirs_exist_ok=True)
for name in ['game_timing.hpp','entries.asm','prt.asm']:shutil.copy2(root/'tests/performance/ez80'/name,out/('include' if name.endswith('hpp') else 'src')/name)
s=(out/'src/main.cpp').read_text().replace('#include "game.hpp"','#include "game.hpp"\n#include "game_timing.hpp"')
s=s.replace('saved_best = load_best();','saved_best = 0;')
s=s.replace('game.init(static_cast<uint32_t>(clock()) + 1, saved_best);','game.init(12345, saved_best);')
s=s.replace('if (vdp_mode(8) < 0) { printf("Aginvadors requires VDP mode 8.\\n"); return 1; }','// Test startup selects mode 8.')
s=s.replace('if (demo) game.reset();','game.reset();\n    render(); waitvblank();\n    if (!gt::init()) { printf("Timing handshake failed\\n"); return 2; }')
s=s.replace('uint8_t keys = input();','gt::loop_begin();\n        (void)input(); // Retain real held-map traffic; scripted input owns replay.\n        uint8_t keys = Fire | ((game.frame / 60) & 1 ? Left : Right);\n        game.invulnerable = 100;')
s=s.replace('sound(); render();','gt::drawing_begin(); sound(); render(); gt::drawing_end();')
s=s.replace('if (!demo && old != game.state && (game.state == GameOver || game.state == WaveClear)) save_best();','(void)old;')
s=s.replace('waitvblank();\n    }','waitvblank();\n        if (gt::loop_end()) break;\n    }')
s=s.replace('if (!demo) save_best();','bool ok = gt::save("inv.csv");')
s=s.replace('vdp_mode(0);','')
s=s.replace('printf("Aginvadors: sector disengaged.\\n");','printf("Timing %s: inv.csv\\n",ok?"complete":"failed");')
# Existing local save helpers remain unused in this test-only translation unit.
s=s.replace('uint32_t load_best()', '[[maybe_unused]] uint32_t load_best()').replace('void save_best()', '[[maybe_unused]] void save_best()')
(out/'src/main.cpp').write_text(s)
(out/'Makefile').write_text((src/'Makefile').read_text().split('.PHONY')[0].replace('NAME=aginvadors','NAME=inv'))
subprocess.run(['make','-C',str(out)],check=True)

from provenance import record
record(args.source,args.output)
