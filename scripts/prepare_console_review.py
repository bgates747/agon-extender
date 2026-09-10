#!/usr/bin/env python3
"""Prepare bounded real-EMOS/native-VDP console review; no physical deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','fab-root','runtime','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    bundle,fab,runtime=(x.resolve(strict=True) for x in (a.bundle,a.fab_root,a.runtime))
    manifest=yaml.safe_load((bundle/'build-manifest.yaml').read_text())
    for item in manifest['outputs']:
        if sha(bundle/item['filename'])!=item['sha256']:raise ValueError('Changed EMOS bundle')
    outputs={item['role']:bundle/item['filename'] for item in manifest['outputs']}
    runtime_manifest=json.loads((runtime/'runtime-inputs.json').read_text())
    for name,digest in runtime_manifest['files'].items():
        if sha(runtime/name)!=digest:raise ValueError('Changed UART1 emulator runtime')
    output=a.output.absolute();output.mkdir(parents=True,exist_ok=False)
    media=output/'sdcard';shutil.copytree(bundle/'emos-sdcard',media)
    media.joinpath('autoexec.txt').write_bytes(b'VDU 22 3\r\nLOAD /bin/EMBOOT.BIN\r\nRUN\r\n'
        b'ECHO Visual validation - screenshot requested\r\nSET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\n')
    subprocess.run(['c++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror',
                    '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/console_session_peer.cpp'),
                    '-o',str(media/'console-session.so')],check=True)
    shutil.copy2(fab/'firmware/vdp_platform.so',media/'vdp-reference.so')
    peer=output/'console_peer.py';shutil.copy2(ROOT/'scripts/console_peer.py',peer)
    inputs=[Path(__file__),ROOT/'scripts/console_peer.py',ROOT/'tests/console_session_peer.cpp',
            *sorted((ROOT/'vdp/video/extender/input').glob('*.hpp')),
            ROOT/'vdp/video/extender/transport/console_session.hpp',
            ROOT/'vdp/video/extender/transport/console_wire.h']
    (output/'review-inputs.json').write_text(json.dumps({
        'emos_build_id':manifest['build']['build_id'],'status':'draft',
        'scope':'real EMOS, native stock VDP and maintained P4 lease/key mapper; no P4/browser/electrical proof',
        'source_sha256':{str(x.relative_to(ROOT)):sha(x) for x in inputs},
        'session_library_sha256':sha(media/'console-session.so'),
        'runtime_manifest_sha256':sha(runtime/'runtime-inputs.json')},indent=2)+'\n')
    for absent in (False,True):
        result=output/('absent.json' if absent else 'paired.json')
        command=[sys.executable,str(peer),'--emulator',str(runtime/'target/release/agon-cli-emulator'),
                 '--firmware',str(outputs['firmware']),'--sdcard',str(media),'--output',str(result)]
        if absent:command+=['--withhold-activation']
        with result.with_suffix('.runner.log').open('w') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=85)
        print(('Absent' if absent else 'Paired')+' console control/stream checks passed; pixels require review',flush=True)
    sys.path.insert(0,str(ROOT.parent/'agon-emos/scripts'))
    from review_boot import make_profile
    make_profile(output/'profile',outputs['firmware'],outputs['firmware_map'],media,fab,
                 runtime=runtime,peer=peer,mutable_names=())
    print('Graphical review ready: '+str(output/'profile'))


if __name__=='__main__':main()
