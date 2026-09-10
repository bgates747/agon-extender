#!/usr/bin/env python3
"""Freeze an isolated functional benchmark review; never touch physical media."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import yaml
from build import ROOT, TASK, sha, with_filesystem_probe


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--emos-bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--fab-root',type=Path,required=True)
    parser.add_argument('--mcopy',type=Path,required=True)
    parser.add_argument('--trace',nargs=2,choices=('byte','count','delimiter','cli-putch','null','points'))
    parser.add_argument('--probe-response', choices=('normal','late','absent'), default='normal')
    parser.add_argument('--fault-pixel-number',type=int,default=1)
    parser.add_argument('--fs-bundle',type=Path,help='Run this verified filesystem probe before the benchmark')
    args=parser.parse_args()
    if args.fault_pixel_number<1: parser.error('Pixel ordinal starts at one')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'.emulator'):
        parser.error('Review profile must be below .emulator')
    bundles=[args.bundle.resolve(),args.emos_bundle.resolve()]
    manifests=[yaml.safe_load((p/'build-manifest.yaml').read_text()) for p in bundles]
    outputs=[]
    for bundle,manifest in zip(bundles,manifests):
        for item in manifest['outputs']:
            if sha(bundle/item['filename'])!=item['sha256']: raise ValueError('Bundle hash mismatch')
        outputs.append({item['role']:bundle/item['filename'] for item in manifest['outputs']})
    runtime=args.runtime.resolve(strict=True)
    for name,digest in json.loads((runtime/'runtime-inputs.json').read_text())['files'].items():
        if sha(runtime/name)!=digest: raise ValueError('Runtime hash mismatch')
    output.mkdir(parents=True)
    media=output/'sdcard'
    shutil.copytree(bundles[1]/'emos-sdcard',media)
    target=media/'extender/uartbench'
    (target/'results').mkdir(parents=True)
    (target/'results/00000001.CSV').write_text('Prior result must survive.\n')
    shutil.copy2(outputs[0]['bin'],target/'UPBENCH.BIN')
    startup=outputs[0]['autoexec'].read_bytes()
    if args.fs_bundle:
        fs_bundle=args.fs_bundle.resolve(strict=True)
        fs_manifest=yaml.safe_load((fs_bundle/'build-manifest.yaml').read_text())
        if fs_manifest['build']['artifact_id']!='fatfs-file-probe': parser.error('Wrong filesystem probe')
        for item in fs_manifest['outputs']:
            source=fs_bundle/item['filename']
            if sha(source)!=item['sha256']: raise ValueError('Filesystem bundle changed')
            if item['role']=='bin':
                folder=media/'extender/fscheck';folder.mkdir(parents=True)
                shutil.copy2(source,folder/'FSCHECK.BIN')
        startup=with_filesystem_probe(startup)
    probe=b'RUN . probe\r\n' in startup
    if probe and args.trace: parser.error('Probe and trace are separate invocations')
    if args.trace:
        if args.trace[0] not in ('byte','count','delimiter','cli-putch') or args.trace[1] not in ('null','points'):
            parser.error('Expected --trace ENTRY PAYLOAD')
        startup=startup.removesuffix(b'RUN\r\n')+('RUN . trace '+' '.join(args.trace)+'\r\n').encode()
    (media/'autoexec.txt').write_bytes(startup)
    symbols={name:int(address,16) for address,name in re.findall(
        r'^\s*(0x[0-9a-f]+)\s+(_bench_done|_bench_exit_status)\s*$',outputs[0]['map'].read_text(),re.M)}
    offset=symbols['_bench_done']-0x40000
    # Fab hostfs does not implement f_sync and treats CREATE_NEW as create-or-open
    # (selected runtime fbb7d7c + pinned UART peer adapter). Use its existing raw
    # SD image backend instead: real MOS FatFS, no storage-success substitution.
    # Retain this until hostfs implements those contracts and is separately tested.
    image=media/'sd.img'
    with image.open('wb') as stream: stream.truncate(32*1024*1024)
    subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
    mcopy=args.mcopy.absolute()  # preserve multicall executable's mcopy basename
    if not mcopy.is_file(): parser.error('mcopy executable is missing')
    subprocess.run([str(mcopy),'-i',str(image),'-s',str(media/'autoexec.txt'),
                    str(media/'bin'),str(media/'emos-boot'),str(media/'extender'),'::/'],check=True)
    (media/'review.json').write_text(json.dumps(dict(done=symbols['_bench_done'],status=symbols['_bench_exit_status'],
        done_bytes=outputs[0]['bin'].read_bytes()[offset:offset+20].hex(),
        image_sha256=sha(image),mcopy=str(mcopy),mcopy_sha256=sha(mcopy),
        probe=probe,probe_response=args.probe_response,fault_pixel_number=args.fault_pixel_number,
        filesystem_probe=bool(args.fs_bundle)))+'\n')
    for source in (TASK/'scripts/review_peer.py',TASK/'scripts/analyze.py',TASK/'scripts/benchmark_framer.py',
                   ROOT/'scripts/console_peer.py',ROOT/'docs/tasks/QUAL-003/scripts/vdu_framer.py'):
        shutil.copy2(source,media/source.name)
    subprocess.run(['c++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror',
                    '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/console_session_peer.cpp'),
                    '-o',str(media/'console-session.so')],check=True)
    sys.path.insert(0,str(ROOT.parent/'agon-emos/scripts'))
    from review_boot import make_profile
    make_profile(output/'profile',outputs[1]['firmware'],outputs[1]['firmware_map'],media,
                 args.fab_root.resolve(),runtime=runtime,peer=media/'review_peer.py',
                 mutable_names=('sd.img',))
    print(output/'profile')


if __name__=='__main__':
    main()
