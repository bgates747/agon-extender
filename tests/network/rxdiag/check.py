#!/usr/bin/env python3
"""Actual-C lifecycle/linked-marker source controls, no CPU emulation/device."""
from pathlib import Path
import argparse,json,subprocess
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[3];a.output.mkdir(exist_ok=False)
exe=a.output/'lifecycle'
cmd=['cc','-std=c11','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-D__ez80__=1','-I'+str(r/'include/agon/rxdiag'),str(r/'include/agon/rxdiag/observer.c'),str(Path(__file__).with_name('lifecycle.c')),'-o',str(exe)]
subprocess.run(cmd,check=True)
for case in range(6):subprocess.run([str(exe),str(case)],check=True,timeout=10)
s=(r/'include/agon/rxdiag/observer.s').read_text()
# Actual source negative controls: these checks must reject the draft defects,
# not mistake compile success for correct active/nested event dispatch.
def dispatch(text):
 head=text[text.index(' call sample\n'):text.index('cap_point:')]
 assert head.index('cp 0x20')<head.index('cp 0x10')
 assert 'jr z,first_read_point' in head
 inner=text[text.index('inner_begin:'):text.index('outer_end:')]
 assert inner.count('ld a,(active)')==2
 assert 'cp (hl)' in inner and 'jp nz,partial' in inner
 assert 'cp 8' in inner and 'inner_stack' in inner
 assert 'ld a,(_agon_rxdiag_record+64)' not in inner
 return True
assert dispatch(s)
for bad in [s.replace(' cp 0x20\n jr z,first_read_point',''),s.replace('inner_begin:\n ld a,(active)','inner_begin:\n ld a,(_agon_rxdiag_record+64)'),s.replace(' cp (hl)',' nop')]:
 try:dispatch(bad)
 except (AssertionError,ValueError):pass
 else:raise AssertionError('Draft marker regression escaped source checker')
marker=s[s.index('_agon_rxdiag_entry:'):s.index('sample:')]
assert not any(x in marker.lower() for x in ['\n ei','\n reti','(0xd5)','(0xd0)','call _'])
for instruction in ['push af','push bc','push de','push hl','push ix','push iy','ex af,af\'','exx','pop iy','pop ix']:
 assert instruction in marker,instruction
out=dict(actual_C_lifecycle_cases=6,source_dispatch_negative_controls=3,passed=True,limits='No executed native IRQ/register/timer or physical acceptance; static checks are bounded source controls')
(a.output/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
