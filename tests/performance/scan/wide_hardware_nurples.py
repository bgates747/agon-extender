#!/usr/bin/env python3
"""HDMI02-F: mode-96 admission companion of retained hardware Nurples r03.

Reproduce r03 before changing its startup-mode check, error text and identity.
Gameplay, assets, PRT instrumentation and deterministic input remain identical.
Neither this fixture nor its builder selects a mode; SD startup owns that.
"""
import argparse,datetime,difflib,hashlib,json,shutil,subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build(source,assembler,output):
    old=json.loads((source/'manifest.json').read_text())
    assert old['build_id'].startswith('scan-scroll-suite-r03-b')
    assert sha(assembler)==old['assembler_sha256']
    output.mkdir(parents=True,exist_ok=False)
    asm=output/'asm';shutil.copytree(source/'asm',asm)
    def assemble(label):
        result=subprocess.run([str(assembler.resolve()),'nurples.asm','scan.bin','-l','-s'],
                              cwd=asm,capture_output=True,text=True)
        (output/(label+'.log')).write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stderr
    assemble('reproduction')
    assert sha(asm/'scan.bin')==old['binary_sha256']
    before=(asm/'runner.inc').read_text()
    check='sc_mode_ready:\n    ld a,(ix+27h)\n    cp 20\n'
    assert before.count(check)==1
    after=before.replace(check,check.replace('cp 20','cp 96'))
    after=after.replace('SCAN: mode 20/VDP reply/clock required.','SCAN: mode 96/VDP reply/clock required.')
    (asm/'runner.inc').write_text(after)
    identity='scan-scroll-suite-r04-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    (asm/'identity.inc').write_text('db '+json.dumps(identity)+'\n')
    (output/'mode-only.diff').write_text(''.join(difflib.unified_diff(
        before.splitlines(True),after.splitlines(True),fromfile='r03/runner.inc',tofile='r04/runner.inc')))
    for name,expected in old['sources'].items():
        if name not in ('runner.inc','identity.inc'): assert sha(asm/name)==expected,name
    assemble('wide')
    binary=output/'hardware-wide-r04.bin';shutil.copyfile(asm/'scan.bin',binary)
    manifest=dict(build_id=identity,status='experimental',mode=96,prior_build=old['build_id'],
        prior_binary_sha256=old['binary_sha256'],prior_reproduction='pass',
        assembler_sha256=sha(assembler),binary=binary.name,binary_sha256=sha(binary),
        changes=['Require startup mode96 instead of20','Corresponding error text','Fixture identity'],
        limits='Identical deterministic gameplay and timing; not a full-screen workload or input-delivery test',
        sources={p.name:sha(p) for p in asm.iterdir() if p.suffix in ('.asm','.inc')},
        builder_sha256=sha(Path(__file__)))
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(identity,manifest['binary_sha256'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','assembler','output'): parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();build(a.source,a.assembler,a.output)
