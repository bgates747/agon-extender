#!/usr/bin/env python3
"""Prepare or execute isolated Fab host-directory/raw-image reproductions.

No emulator modification, UART peer, API stub or hardware operation. Run the
actual test with the unchanged upstream Fab binary and identified EMOS image.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pty
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
import yaml

TASK=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(args):
    root=TASK.parents[2]
    output=args.output.resolve()
    if not output.is_relative_to(root/'.emulator'):raise ValueError('Profile must be inside .emulator')
    output.mkdir(parents=True)
    media=output/'sdcard';target=media/'extender/fscheck';target.mkdir(parents=True)
    manifests=[yaml.safe_load((b/'build-manifest.yaml').read_text()) for b in (args.bundle,args.emos_bundle)]
    outputs=[]
    for bundle,manifest in zip((args.bundle,args.emos_bundle),manifests):
        for item in manifest['outputs']:
            if sha(bundle/item['filename'])!=item['sha256']:raise ValueError('Bundle mismatch')
        outputs.append({item['role']:bundle.resolve()/item['filename'] for item in manifest['outputs']})
    shutil.copy2(outputs[0]['bin'],target/'FSCHECK.BIN')
    (media/'autoexec.txt').write_bytes(b'VDU 22 3\r\nLOAD /extender/fscheck/FSCHECK.BIN\r\nRUN\r\n')
    symbols={name:int(address,16) for address,name in re.findall(
        r'^\s*(0x[0-9a-f]+)\s+(_fs_done|_fs_exit_status)\s*$',outputs[0]['map'].read_text(),re.M)}
    config=dict(backend=args.backend,done=symbols['_fs_done'],status=symbols['_fs_exit_status'],
                fixture=manifests[0]['build'],emos=manifests[1]['build'],mcopy=str(args.mcopy.absolute()),
                mcopy_sha256=sha(args.mcopy))
    mutable=tuple('extender/fscheck/R00001/'+n for n in ('CREATE.DAT','SYNC.DAT','RESULT.TXT'))
    if args.backend=='image':
        image=media/'sd.img'
        with image.open('wb') as stream:stream.truncate(32*1024*1024)
        subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
        subprocess.run([config['mcopy'],'-i',str(image),'-s',str(media/'autoexec.txt'),str(media/'extender'),'::/'],check=True)
        config['image_sha256']=sha(image);mutable=('sd.img',)
    (media/'review.json').write_text(json.dumps(config,indent=2)+'\n')
    peer=media/'review.py';shutil.copy2(Path(__file__),peer)
    # The canonical generator expects a runtime manifest for a peer. This
    # record identifies the unchanged upstream runtime, not a custom build.
    runtime=output/'runtime';runtime.mkdir()
    (runtime/'runtime-inputs.json').write_text(json.dumps(dict(
        executable=str(args.fab_root.resolve()/'target/release/fab-agon-emulator'),
        sha256=sha(args.fab_root/'target/release/fab-agon-emulator')))+'\n')
    (runtime/'target/release').mkdir(parents=True)
    (runtime/'target/release/fab-agon-emulator').symlink_to(args.fab_root.resolve()/'target/release/fab-agon-emulator')
    sys.path.insert(0,str(root.parent/'agon-emos/scripts'))
    from review_boot import make_profile
    make_profile(output/'profile',outputs[1]['firmware'],outputs[1]['firmware_map'],media,
                 args.fab_root.resolve(),runtime=runtime,peer=peer,mutable_names=mutable)
    print(output/'profile')


def run(args):
    media=args.sdcard.resolve();config=json.loads((media/'review.json').read_text())
    if sha(Path(config['mcopy']))!=config['mcopy_sha256']:raise ValueError('Changed mcopy')
    image=media/'sd.img'
    if config['backend']=='image' and sha(image)!=config['image_sha256']:raise ValueError('Changed image')
    record=dict(outcome='fail',scope=__doc__,config=config)
    transcript=bytearray();debug=''
    with tempfile.TemporaryDirectory(prefix='fatfs-review-') as tmp:
        master,slave=pty.openpty()
        env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        command=[str(args.emulator),'--mos',str(args.firmware),'--vdp',str(args.vdp),'--renderer','sw','--zero',
                 '--debugger','--breakpoint',hex(config['done'])]
        command+=['--sdcard-img',str(image)] if config['backend']=='image' else ['--sdcard',str(media)]
        proc=subprocess.Popen(command,cwd=tmp,env=env,stdin=slave,stdout=slave,stderr=slave);os.close(slave)
        def receive():
            nonlocal debug
            end=time.monotonic()+90
            while '>> ' not in debug:
                if time.monotonic()>end:raise TimeoutError('Filesystem probe did not finish')
                if select.select([master],[],[],.1)[0]:
                    data=os.read(master,65536);transcript.extend(data);debug+=data.decode(errors='replace')
            result,debug=debug.split('>> ',1);return result
        try:
            receive()
            os.write(master,f'mem {hex(config["status"])} 3\n'.encode());record['status_dump']=receive()
            target=args.output.parent/'RESULT.TXT'
            if config['backend']=='image':
                subprocess.run([config['mcopy'],'-i',str(image),'::/extender/fscheck/R00001/RESULT.TXT',str(target)],check=True)
            else:shutil.copy2(media/'extender/fscheck/R00001/RESULT.TXT',target)
            text=target.read_text();record['result']=text
            expected={'setup':0,'create_existing':8 if config['backend']=='image' else 0,
                      'original_contents':0,'sync_open_written':0 if config['backend']=='image' else 9,
                      'close':0,'reopened_contents':0}
            actual={name:int(value) for name,value in re.findall(r'^(\w+)=(\d+)',text,re.M)}
            if actual!=expected:raise ValueError('Unexpected reproducer results: '+repr(actual))
            record['outcome']='pass' if config['backend']=='image' else 'reproduced'
            print(config['backend']+': '+record['outcome']+'\n'+text,flush=True)
        finally:
            proc.terminate();proc.wait(timeout=5);os.close(master)
            args.output.write_text(json.dumps(record,indent=2)+'\n')
            args.output.with_suffix('.log').write_bytes(transcript)


if __name__=='__main__':
    sys.dont_write_bytecode=True
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('output','bundle','emos-bundle','fab-root','mcopy','emulator','firmware','sdcard','vdp'):
        parser.add_argument('--'+name,type=Path)
    parser.add_argument('--backend',choices=('directory','image'))
    parser.add_argument('--graphical',action='store_true')
    args=parser.parse_args()
    if args.emulator:run(args)
    else:prepare(args)
