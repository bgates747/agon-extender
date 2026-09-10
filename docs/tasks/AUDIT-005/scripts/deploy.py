#!/usr/bin/env python3
"""Install only the benchmark application and autoexec on an explicit mounted SD.

Back up replaced files first. Preserve all results and unrelated applications.
This does not flash, reset, access serial, or install any MOS/VDP firmware.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import yaml
from build import sha, with_filesystem_probe


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--mount',type=Path,required=True)
    parser.add_argument('--backup',type=Path,required=True)
    parser.add_argument('--fs-bundle',type=Path)
    parser.add_argument('--fs-first',action='store_true',help='Run the independent filesystem check before the benchmark')
    parser.add_argument('--trace', action='store_true', help='Run the existing counted-point trace instead of the full suite')
    args=parser.parse_args()
    if args.fs_first and not args.fs_bundle: parser.error('--fs-first requires --fs-bundle')
    bundle=args.bundle.resolve(strict=True)
    mount=args.mount.absolute()
    if mount.resolve(strict=True)!=mount: parser.error('Mount must not be a symlink')
    info=json.loads(subprocess.check_output(['findmnt','--json','--target',str(mount),
                    '--output','TARGET,SOURCE,FSTYPE,OPTIONS'],text=True))['filesystems']
    if len(info)!=1 or info[0]['target']!=str(mount) or info[0]['fstype'] not in ('vfat','msdos'):
        parser.error('Expected the exact mounted FAT SD root')
    if 'rw' not in info[0]['options'].split(','): parser.error('SD is not writable')
    manifest=yaml.safe_load((bundle/'build-manifest.yaml').read_text())
    for item in manifest['outputs']:
        if sha(bundle/item['filename'])!=item['sha256']: raise ValueError('Bundle changed')
    outputs={item['role']:bundle/item['filename'] for item in manifest['outputs']}
    if not (mount/'bin/EMBOOT.BIN').is_file(): parser.error('Existing boot smoke is missing')
    relative=['autoexec.txt','extender/uartbench/UPBENCH.BIN','extender/uartbench/build-manifest.yaml']
    fs_copies=[]
    if args.fs_bundle:
        fs_bundle=args.fs_bundle.resolve(strict=True)
        fs_manifest=yaml.safe_load((fs_bundle/'build-manifest.yaml').read_text())
        if fs_manifest['build']['artifact_id']!='fatfs-file-probe': parser.error('Wrong filesystem fixture')
        for item in fs_manifest['outputs']:
            if sha(fs_bundle/item['filename'])!=item['sha256']:raise ValueError('Filesystem bundle changed')
            if item['role']=='bin':fs_copies.append((fs_bundle/item['filename'],'extender/fscheck/FSCHECK.BIN'))
        fs_copies.append((fs_bundle/'build-manifest.yaml','extender/fscheck/build-manifest.yaml'))
        relative += [name for _,name in fs_copies]
    for name in relative+['extender/uartbench/results','bin/EMBOOT.BIN']:
        path=mount/name
        if path.resolve()!=path: parser.error('SD target contains a symlink')
    backup=args.backup.resolve()
    backup.mkdir(parents=True,exist_ok=False)
    old={}
    for name in relative:
        path=mount/name
        if path.exists():
            if not path.is_file(): parser.error('Unexpected non-file target: '+name)
            dest=backup/name; dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,dest); old[name]=sha(dest)
    (mount/'extender/uartbench/results').mkdir(parents=True,exist_ok=True)
    if fs_copies: (mount/'extender/fscheck').mkdir(parents=True,exist_ok=True)
    # Commit startup last, so a partially copied bundle is never auto-launched.
    startup=outputs['autoexec']
    if args.trace:
        original=startup.read_bytes()
        if not original.endswith(b'RUN\r\n'):
            parser.error('Trace requires the unchanged full-suite bundle')
        startup=backup/'trace-autoexec.txt'
        startup.write_bytes(original.removesuffix(b'RUN\r\n')+b'RUN . trace count points\r\n')
    if args.fs_first:
        # Keep the frozen bundle unchanged. Record the composed startup as an
        # explicit deployment input; its exact bytes/hash live in the receipt.
        original=startup.read_bytes()
        startup=backup/'prepared-autoexec.txt'
        startup.write_bytes(with_filesystem_probe(original))
    copies=[(outputs['bin'],'extender/uartbench/UPBENCH.BIN'),
            (bundle/'build-manifest.yaml','extender/uartbench/build-manifest.yaml'),
            *fs_copies,(startup,'autoexec.txt')]
    for source,name in copies:
        destination=mount/name
        with tempfile.NamedTemporaryFile(dir=destination.parent,delete=False) as stream:
            pending=Path(stream.name)
            try:
                stream.write(source.read_bytes()); stream.flush(); os.fsync(stream.fileno())
            except BaseException:
                pending.unlink(missing_ok=True); raise
        os.replace(pending,destination)
    os.sync()
    (backup/'deployment.json').write_text(json.dumps(dict(
        deployed_at=datetime.now(timezone.utc).isoformat(),build=manifest['build'],
        deploy_script_sha256=sha(Path(__file__)),
        mount=str(mount),source=info[0]['source'],previous_sha256=old,
        boot_smoke_sha256=sha(mount/'bin/EMBOOT.BIN'),
        installed={name:sha(source) for source,name in copies}),indent=2)+'\n')
    print('SD ready: '+manifest['build']['build_id'])
    print('Saved original files in '+str(backup))
    print('Autoexec invocation: '+startup.read_text().splitlines()[-1])


if __name__=='__main__':
    main()
