#!/usr/bin/env python3
"""Isolated one-shot entry; retain the existing GPIO walk, never deploy here."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[3]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);src=ROOT/'docs/tasks/HW-002/pinwalk';dst=out/'fixture';(dst/'src').mkdir(parents=True)
for name in ('Makefile','LICENSE'):shutil.copy2(src/name,dst/name)
for name in ('main.c','pinwalk_wire.asm','pinwalk_wire.h'):shutil.copy2(src/'src'/name,dst/'src'/name)
f=dst/'src/main.c';s=f.read_text();old='    putch(22);\n    putch(3);\n';assert s.count(old)==1
s=s.replace(old,'''    /* External startup selected mode3 and P4 inputs were verified first. */
    if (ffs_unlink("/extender/gqt/pw-once") != FR_OK) {
        puts("Pinwalk not armed; no GPIO activity.");
        return 1;
    }
''')
s=s.replace('    return 0;','''    puts("Pinwalk complete; pins released. Awaiting bench reset.");
    for (;;) { /* Explicit reset only; do not resume UART1 while P4 is in ROM. */ }
''');f.write_text(s)
build='header-pinwalk-boot-r01'+datetime.now(timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ');(dst/'src/build_identity.h').write_text('#define BUILD_ID "'+build+' (experimental one-shot entry)"\n')
assert (dst/'src/pinwalk_wire.asm').read_bytes()==(src/'src/pinwalk_wire.asm').read_bytes()
with (out/'build.log').open('w') as log:subprocess.run(['make','-C',str(dst),'all'],stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(dst/'bin/PWBOOT.bin',out/'PWBOOT.bin')
meta=dict(build_id=build,status='experimental',variant='one-shot external-mode input-verified entry',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs={str(x.relative_to(dst)):hashlib.sha256(x.read_bytes()).hexdigest() for x in dst.rglob('*') if x.is_file()},binary_sha256=hashlib.sha256((out/'PWBOOT.bin').read_bytes()).hexdigest())
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(build)
