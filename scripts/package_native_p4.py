#!/usr/bin/env python3
"""Preserve an accepted native P4 application update; no build/install or selection.

The historical hybrid installation packager remains unchanged. This recipe
packages only the exact tested application and matched viewer, with its existing
native source snapshot. It deliberately omits untested replacement bootloaders,
factory images, mutable flash, startup and full-device backups. Feature
acceptance is separate from canonical qualification and production selection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(folder):
    return {str(p.relative_to(folder)): {'sha256': sha(p), 'size_bytes': p.stat().st_size}
            for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS'}


def checksums(folder):
    (folder / 'SHA256SUMS').write_text(''.join(
        value['sha256'] + '  ' + name + '\n' for name, value in inventory(folder).items()))


def verify(folder):
    if any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('Symlink in package')
    expected = {}
    for line in (folder / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = folder / name
        if (name in expected or Path(name).is_absolute() or '..' in Path(name).parts
                or path.is_symlink() or not path.is_file() or folder.resolve() not in path.resolve().parents):
            raise ValueError('Invalid package member: ' + name)
        expected[name] = digest
        if sha(path) != digest:
            raise ValueError('Package digest mismatch: ' + name)
    actual = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
    if actual != set(expected) | {'SHA256SUMS'}:
        raise ValueError('Unlisted/missing package file')
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--build-output', type=Path)
    parser.add_argument('--viewer', type=Path)
    parser.add_argument('--viewer-manifest', type=Path)
    parser.add_argument('--acceptance', type=Path)
    parser.add_argument('--installed-readback', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.verify:
        print(json.dumps({'verified_files': verify(args.verify)}))
        return
    if not all((args.build_output, args.viewer, args.viewer_manifest, args.acceptance, args.installed_readback, args.output)):
        parser.error('All packaging inputs are required')
    if subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain']).strip():
        parser.error('Commit packaging inputs first')
    accepted = yaml.safe_load(args.acceptance.read_text())
    build = json.loads((args.build_output / 'manifest.json').read_text())
    app = args.build_output / 'build/agon_extender.bin'
    pin = accepted['p4']
    if (accepted['acceptance']['status'] != 'accepted' or build['source_dirty']
            or not build['source_snapshot_verified'] or build['source_commit'] != pin['source_commit']
            or build['build_id'] != pin['build_id'] or sha(app) != pin['sha256']
            or app.stat().st_size != pin['size_bytes']):
        raise ValueError('Accepted application identity differs')
    if (sha(args.viewer) != accepted['viewer']['sha256']
            or args.viewer.stat().st_size != accepted['viewer']['size_bytes']):
        raise ValueError('Matched viewer differs')
    viewer_manifest = json.loads(args.viewer_manifest.read_text())
    if (viewer_manifest['source_dirty'] or viewer_manifest['git_commit'] != accepted['viewer']['source_commit']
            or viewer_manifest['build_id'] != accepted['viewer']['build_id']):
        raise ValueError('Viewer provenance differs')
    for name, digest in viewer_manifest['inputs'].items():
        raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', viewer_manifest['git_commit'] + ':' + name])
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('Viewer source differs: ' + name)
    readback = args.installed_readback.read_bytes()
    if (len(readback) != 0x1000000 or hashlib.sha256(readback).hexdigest() != accepted['installed_readback_sha256']
            or readback[0x20000:0x20000 + pin['size_bytes']] != app.read_bytes()):
        raise ValueError('Independent installed readback differs')
    for artifact in build['artifacts']:
        path = Path(artifact['path'])
        if path.stat().st_size != artifact['bytes'] or sha(path) != artifact['sha256']:
            raise ValueError('Build input/artifact differs: ' + path.name)
    source_inventory = json.loads((args.build_output / 'source-inputs.json').read_text())['files']
    with tarfile.open(args.build_output / 'source.tar.gz') as archive:
        members = [x for x in archive if x.isfile()]
        pins = {x['path']: x for x in source_inventory}
        if len(members) != len(pins) or {x.name for x in members} != set(pins):
            raise ValueError('Source inventory differs')
        for member in members:
            raw = archive.extractfile(member).read()
            if len(raw) != pins[member.name]['bytes'] or hashlib.sha256(raw).hexdigest() != pins[member.name]['sha256']:
                raise ValueError('Source bytes differ: ' + member.name)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    runtime = out / pin['build_id']
    support = out / (pin['build_id'] + '-sources')
    runtime.mkdir(); support.mkdir()
    def copy(src, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    copy(app, runtime / 'p4/firmware.bin')
    copy(args.viewer, runtime / 'sd/extender/controller/ctrlview.bin')
    for src, dst in ((args.acceptance, runtime / 'acceptance.yaml'),
                     (ROOT / 'production/native-p4-update.md', runtime / 'INSTALL.md'),
                     (ROOT / 'production/native-p4-notices.md', runtime / 'NOTICES.md'),
                     (ROOT / 'LICENSE', runtime / 'licenses/agon-extender-LICENSE')):
        copy(src, dst)
    for name in ('source.tar.gz', 'source-inputs.json', 'manifest.json', 'validation.json', 'sdkconfig', 'dependencies.lock'):
        copy(args.build_output / name, support / name)
    copy(args.viewer_manifest, support / 'viewer-manifest.json')
    with (support / 'viewer-source.tar.gz').open('wb') as stream:
        subprocess.run(['git', '-C', str(ROOT), 'archive', '--format=tar.gz',
                        viewer_manifest['git_commit'], '--', 'LICENSE', *viewer_manifest['inputs']],
                       stdout=stream, check=True)
    copy(ROOT / 'scripts/package_native_p4.py', support / 'package_native_p4.py')
    copy(ROOT / 'production/native-p4-notices.md', support / 'NOTICES.md')
    copy(ROOT / 'LICENSE', support / 'licenses/agon-extender-LICENSE')
    checksums(runtime); checksums(support)
    verify(runtime); verify(support)
    archives = []
    for folder in (runtime, support):
        path = out / (folder.name + '.tar.gz')
        with tarfile.open(path, 'w:gz', compresslevel=1) as archive:
            archive.add(folder, arcname=folder.name)
        archives.append({'filename': path.name, 'sha256': sha(path), 'size_bytes': path.stat().st_size})
    (out / 'SHA256SUMS').write_text(''.join(x['sha256'] + '  ' + x['filename'] + '\n' for x in archives))
    record = dict(accepted, kind='native_p4_application_update', selection='unselected',
                  packaging_commit=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                  publication='local only; private reset endpoint embedded; no public binary publication',
                  archives=archives, runtime_files=inventory(runtime), source_support_files=inventory(support))
    (out / 'bundle-record.yaml').write_text(yaml.safe_dump(record, sort_keys=False))
    print(json.dumps({'archives': archives, 'runtime_files': verify(runtime), 'source_support_files': verify(support)}, indent=2))


if __name__ == '__main__':
    main()
