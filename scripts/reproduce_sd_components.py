#!/usr/bin/env python3
"""Reproduce pinned EMOS and SD MOSlet in isolated clones; never deploy.

Recorded timestamps may be reused only with expected hashes: mismatch is failure.
Use the original checkout's toolchain and Python environment, not old objects.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('emos-source','builder-source','toolchain','builder-python','output'):
        p.add_argument('--'+name,type=Path,required=True)
    for name in ('emos-build-id','listener-build-id','emos-sha256','listener-sha256'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args();out=a.output.absolute();out.mkdir(parents=True,exist_ok=False)
    pins={}
    for name,src in [('agon-emos',a.emos_source.resolve()),('mos-agondev',a.builder_source.resolve())]:
        if subprocess.check_output(['git','status','--porcelain'],cwd=src).strip():
            raise SystemExit('dirty source: '+str(src))
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()
        subprocess.run(['git','clone','--no-hardlinks','--no-checkout',str(src),str(out/name)],check=True)
        subprocess.run(['git','checkout','--detach',commit],cwd=out/name,check=True)
        pins[name]=commit
    source=out/'agon-emos';builder=out/'mos-agondev';tool=a.toolchain.absolute()
    # The existing builder resolves these conventional roots for provenance.
    (builder/'toolchains').mkdir()
    (builder/'toolchains/agondev').symlink_to(tool)
    (builder/'.venv').symlink_to(a.builder_python.absolute().parent.parent)
    work=builder/'projects/mos-port/worktree'
    with (out/'emos-build.log').open('w') as log:
        subprocess.run([str(a.builder_python.absolute()),'scripts/prepare_mos_worktree.py',
            '--upstream',str(source),'--destination',str(work)],cwd=builder,
            stdout=log,stderr=subprocess.STDOUT,check=True)
        cmd=['make','firmware-check','PYTHON='+str(a.builder_python.absolute()),
            'MOS_AGONDEV_ROOT='+str(builder),'MOS_AGONDEV_PYTHON='+str(a.builder_python.absolute()),
            'MOS_SOURCE='+str(source),'MOS_WORKTREE='+str(work),'AGONDEV_TOOLCHAIN='+str(tool),
            'PROVENANCE_DIR='+str(out/'provenance'),'EMOS_BUILD_ID='+a.emos_build_id]
        subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT,check=True)
    app=source/'projects/sdserve';(app/'build').mkdir(exist_ok=True)
    (app/'build/build_identity.h').write_text(f'#define SDSERVE_BUILD_ID {json.dumps(a.listener_build_id)}\n#define SDSERVE_STATUS "draft"\n')
    with (out/'listener-build.log').open('w') as log:
        subprocess.run(['make','AGONDEV_TOOLCHAIN='+str(tool),'SDSERVE_IDENTIFIED_BUILD=1',
            'RAM_START=0xB0000','RAM_SIZE=0x8000'],cwd=app,
            env=dict(os.environ,PATH=str(tool/'bin')+':'+os.environ['PATH']),
            stdout=log,stderr=subprocess.STDOUT,check=True)
    outputs={}
    for role,path,identity,expected in [
        ('emos',builder/'projects/mos-port/bin/MOS.bin',a.emos_build_id,a.emos_sha256),
        ('listener',app/'bin/sdserve.bin',a.listener_build_id,a.listener_sha256)]:
        digest=sha(path)
        outputs[role]={'build_id':identity,'sha256':digest,'size_bytes':path.stat().st_size,
            'expected_sha256':expected,'identical':digest==expected}
    report={'source_commits':pins,'outputs':outputs,
        'compiler_sha256':sha(tool/'bin/ez80-none-elf-clang'),
        'scope':'Byte reproduction and existing link checks; no deployment or new hardware acceptance'}
    (out/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
    if not all(row['identical'] for row in outputs.values()):
        raise SystemExit('Reproduction differs: do not reuse these historical identities for deployment')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
