#!/usr/bin/env python3
"""Freeze a paired graphics emulator profile; no launch, SD deployment or flash."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import yaml

TASK=Path(__file__).resolve().parents[1]
ROOT=TASK.parents[2]
SUITE=TASK/'suite'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','fab-root','runtime','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--app',choices=('shapes','bitmaps'),required=True)
    p.add_argument('--page',type=int)
    p.add_argument('--stages',type=int)
    p.add_argument('--human',action='store_true')
    p.add_argument('--asset-fault',choices=('missing','truncated'))
    a=p.parse_args()
    bundle,fab,runtime=(x.resolve(strict=True) for x in (a.bundle,a.fab_root,a.runtime))
    output=a.output.resolve()
    if not output.is_relative_to(ROOT/'.emulator'):p.error('Profiles belong under project .emulator')
    manifest=yaml.safe_load((bundle/'build-manifest.yaml').read_text())
    for item in manifest['outputs']:
        if sha(bundle/item['filename'])!=item['sha256']:raise ValueError('Changed EMOS bundle')
    outputs={item['role']:bundle/item['filename'] for item in manifest['outputs']}
    for name,digest in json.loads((runtime/'runtime-inputs.json').read_text())['files'].items():
        if sha(runtime/name)!=digest:raise ValueError('Changed emulator runtime')
    subprocess.run(['make','all','check'],cwd=SUITE,check=True)
    if a.app=='shapes':total=1 if a.page else 24
    else:
        pages=json.loads((SUITE/'build/bitmaps-catalog.json').read_text())['pages']
        total=sum(len(p['stages']) for p in pages if a.page is None or p['page']==a.page)
    if a.page and not 1<=a.page<=(24 if a.app=='shapes' else 32):p.error('Invalid page')
    stages=a.stages or total
    if not 1<=stages<=total:p.error('Invalid stage count')
    if a.asset_fault and (a.app!='bitmaps' or a.page!=1 or a.human):
        p.error('Asset recovery uses automatic Bitmaps page 1')
    output.mkdir(parents=True,exist_ok=False)
    media=output/'sdcard';shutil.copytree(bundle/'emos-sdcard',media)
    shutil.copytree(SUITE/'tgt',media/'extender')
    (media/'extender/hello.bin').unlink(missing_ok=True)
    # Both modes are selected explicitly by autoexec, never by a test program.
    startup='VDU 22 3\r\nLOAD /bin/EMBOOT.BIN\r\nRUN\r\nSET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\n'
    startup+='VDU 22 20\r\nEMOS EXCOM\r\nVDU 22 20\r\nCD /extender\r\n'
    startup+=f'LOAD {a.app}.bin\r\n'+(f'RUN . {a.page}' if a.page else 'RUN')+'\r\n'
    (media/'autoexec.txt').write_bytes(startup.encode())
    if a.asset_fault:
        asset=media/'extender/assets/bitmaps/axes2.rgba2'
        if a.asset_fault=='missing':asset.unlink()
        else:asset.write_bytes(asset.read_bytes()[:-1])
    config=dict(app=a.app,page=a.page,stages=stages,escape=stages<total,human=a.human,asset_fault=a.asset_fault)
    (media/'review.json').write_text(json.dumps(config,indent=2)+'\n')
    symbols={k:int(v,16) for k,v in re.findall(r'^(\S+) \$([0-9a-fA-F]+)',
                    (SUITE/'build'/f'{a.app}.symbols').read_text(),re.M)}
    (media/'symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
    for source in (TASK/'scripts/graphics_peer.py',TASK/'scripts/vdu_framer.py',ROOT/'scripts/console_peer.py'):
        shutil.copyfile(source,media/source.name)
    subprocess.run(['c++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror',
                    '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/console_session_peer.cpp'),
                    '-o',str(media/'console-session.so')],check=True)
    subprocess.run(['gcc','-Wall','-Werror','-shared','-fPIC','-I',str(Path.home()/'.local/include'),
                    str(SUITE/'tests/sdl_review.c'),'-ldl','-o',str(media/'sdl-review.so')],check=True)
    identity=json.loads((SUITE/'build/paired-identity.json').read_text())
    for app in ('shapes','bitmaps'):
        if identity['build_id'].encode() not in (media/'extender'/f'{app}.bin').read_bytes():
            raise ValueError('Fixture build identity missing')
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(TASK.rglob('*')) if p.is_file()
             and not any(x in p.parts for x in ('build','tgt','__pycache__'))}
    (output/'review-inputs.json').write_text(json.dumps(dict(
        prepared_at=datetime.now(timezone.utc).isoformat(),
        fixture=identity,emos=manifest['build'],config=config,source_sha256=sources,
        outputs_sha256={str(p.relative_to(media)):sha(p) for p in media.rglob('*') if p.is_file()}),indent=2)+'\n')
    sys.path.insert(0,str(ROOT.parent/'agon-emos/scripts'))
    from review_boot import make_profile
    make_profile(output/'profile',outputs['firmware'],outputs['firmware_map'],media,fab,
                 runtime=runtime,peer=media/'graphics_peer.py',mutable_names=())
    print('Prepared '+str(output/'profile'))

if __name__=='__main__':main()
