#!/usr/bin/env python3
"""Prepare an isolated, provisional SD-service headless profile; never touch hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import struct
import zlib

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','runtime','fab-root','firmware','firmware-map','application','mcopy','emos-root'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--quick',action='store_true',help='Focused recovery refinement; large-file baseline is separate')
    a=p.parse_args();output=a.output.absolute()
    if not output.is_relative_to(ROOT/'.emulator'):raise ValueError('Output must be in project .emulator')
    output.mkdir(parents=True,exist_ok=False)
    runtime=a.runtime.resolve();manifest=json.loads((runtime/'runtime-inputs.json').read_text())
    for name,digest in manifest['files'].items():
        if sha(runtime/name)!=digest:raise ValueError('Changed UART test runtime: '+name)
    media=output/'sdcard';(media/'extender/sdtest').mkdir(parents=True)
    shutil.copyfile(a.application,media/'extender/sdserve.bin')
    journal=b'SDT1'+struct.pack('<III',1,4,zlib.crc32(b'data'))
    (media/'extender/sdtest/orphan.bin.p17meta').write_bytes(journal+struct.pack('<I',zlib.crc32(journal)))
    (media/'extender/sdtest/orphan.bin.p17part').write_bytes(b'da')
    (media/'autoexec.txt').write_bytes(b'VDU 22 3\r\nSET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\n'
        b'LOAD /extender/sdserve.bin\r\nRUN . /extender/sdtest\r\n')
    seed=media/'seed.img'
    with seed.open('wb') as f:f.truncate(32*1024*1024)
    subprocess.run(['mkfs.fat','-F','16',str(seed)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run([str(a.mcopy),'-i',str(seed),'-s',str(media/'autoexec.txt'),str(media/'extender'),'::/'],check=True)
    subprocess.run(['c++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror',
                    '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/sd_peer.cpp'),'-o',str(media/'sd-peer.so')],check=True)
    for name in ('qualify_sd_headless.py','sdcard.py'):shutil.copyfile(ROOT/'scripts'/name,media/name)
    shutil.copyfile(a.firmware,output/'MOS.bin');shutil.copyfile(a.firmware_map,output/'MOS.map')
    (media/'fixture.json').write_text(json.dumps({
        'status':'provisional, unqualified, no deployment',
        'sizes':[0,213] if a.quick else [0,1,212,213,65537,131731],
        'runtime_manifest_sha256':sha(runtime/'runtime-inputs.json'),
        'seed_sha256':sha(seed),'application_sha256':sha(a.application),'firmware_sha256':sha(a.firmware),
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
    },indent=2)+'\n')
    sys.path.insert(0,str(a.emos_root.resolve()/'scripts'))
    from review_boot import make_profile
    make_profile(output/'profile',output/'MOS.bin',output/'MOS.map',media,a.fab_root.resolve(),
                 runtime=runtime,peer=media/'qualify_sd_headless.py',
                 mutable_names=('working.img','client-state.json','client-state.json.tmp','client-state.json.lock'))
    print(output/'profile')
if __name__=='__main__':main()
