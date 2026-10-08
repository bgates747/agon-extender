#!/usr/bin/env python3
"""SPRITE-001: hardware companion of the frozen SCAN r02 Nurples fixture.

Accept a retained r02 build, reproduce its original binary first, then change
only explicit sprite type/admission plus the fixture identity. No game tree or
ordinary SD binary is edited. Startup continues to own the video mode.
"""
import argparse,datetime,hashlib,json,shutil,subprocess,difflib
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(source,assembler,output):
    previous=json.loads((source/'manifest.json').read_text())
    assert previous['build_id'].startswith('scan-scroll-suite-r02-b')
    assert sha(assembler)==previous['assembler_sha256']
    output.mkdir(parents=True,exist_ok=False)
    asm=output/'asm';shutil.copytree(source/'nurples-source/asm',asm)
    def assemble(label):
        p=subprocess.run([str(assembler.resolve()),'nurples.asm','scan.bin','-l','-s'],cwd=asm,capture_output=True,text=True)
        (output/(label+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0,p.stderr+p.stdout[-1000:]
    assemble('reproduction')
    assert sha(asm/'scan.bin')==previous['cases'][8]['binary_sha256'],'Frozen r02 reproduction differs'
    before=(asm/'game.inc').read_text()
    assert before.count('    call game_init')==1
    after=before.replace('    call game_init','    ld hl,sc_hw_enable\n    ld bc,7\n    rst.lil 18h\n    call game_init')
    after=after.replace('sc_sw_packet: db 23,27,18,0,23,27,20','sc_sw_packet: db 23,27,18,0,23,27,19\nsc_hw_enable: db 23,0,248,2,0,0,0')
    assert before!=after
    (asm/'game.inc').write_text(after)
    identity='scan-scroll-suite-r03-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    (asm/'identity.inc').write_text('db '+json.dumps(identity)+'\n')
    (output/'hardware-only.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='r02/game.inc',tofile='r03/game.inc')))
    assemble('hardware')
    shutil.copyfile(asm/'scan.bin',output/'hardware-r03.bin')
    m={'build_id':identity,'status':'experimental','prior_build':previous['build_id'],
       'source_head':previous['source_head'],'assembler_sha256':sha(assembler),
       'prior_binary_sha256':previous['cases'][8]['binary_sha256'],'prior_reproduction':'pass',
       'binary':'hardware-r03.bin','binary_sha256':sha(output/'hardware-r03.bin'),
       'changes':['Enable VDP hardware-sprite API variable 2 before game initialization','Choose hardware type after every bitmap frame attachment','New fixture identity'],
       'limits':'Same deterministic map, script, invulnerability, PRT and MOS polling as r02; not input delivery evidence',
       'sources':{p.name:sha(p) for p in asm.iterdir() if p.is_file() and p.suffix in ('.asm','.inc')},
       'builder_sha256':sha(Path(__file__))}
    (output/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps({k:m[k] for k in ('build_id','binary_sha256','prior_reproduction')}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('source','assembler','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();build(a.source,a.assembler,a.output)
