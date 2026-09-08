#!/usr/bin/env python3
"""Build the P4 retained-parser General Poll diagnostic locally; never flash or edit SD media.

EMOS is built/reviewed through its own wrappers. This bundle's autoexec is for
that reviewed firmware only; both endpoints must select the same baud.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_embedded_identity(path, source_identity, build_id, status):
    # Manifest metadata cannot prove that an incremental build recompiled the
    # boot identity consumer. Reject stale outputs before publishing a bundle.
    data = path.read_bytes()
    for value in (source_identity, build_id, status):
        if value.encode('ascii') + b'\0' not in data:
            raise ValueError(f'{path.name}: missing embedded identity {value}')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def snapshot():
    # Include new maintained inputs before their first commit; ignored bench
    # records and build outputs are excluded by Git's normal rules.
    names = git('ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0')
    return {name: sha(ROOT / name) for name in sorted(set(names)) if name}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error('output directory already exists')
    identity = json.loads((ROOT / 'vdp/pio/p4-general-poll-identity.json').read_text())
    source_identity, status = identity['source_identity'], identity['status']
    if status not in ('draft', 'experimental', 'candidate'):
        parser.error('unsupported lifecycle status')
    if source_identity is not None and not re.fullmatch(r'uart-general-poll-probe-r(?:0[1-9]|[1-9][0-9]+)', source_identity):
        parser.error('invalid General Poll fixture identity')
    before = {'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain')),
              'source_sha256': snapshot()}
    if status != 'draft' and (not source_identity or before['dirty']):
        parser.error('deployable builds require an approved identity and clean committed inputs')
    now = datetime.now(timezone.utc)
    build_id = source_identity + now.strftime('-b%Y-%m-%d-%H-%M-%SZ') if source_identity else 'UNVERSIONED-DO-NOT-DEPLOY'
    output.mkdir(parents=True)
    import os
    build_environment = dict(os.environ, AGON_EXTENDER_BUILD_ID=build_id)
    with (output / 'p4-build.log').open('w') as log:
        result = subprocess.run([str(ROOT / '.venv/bin/pio'), 'run', '-d', str(ROOT / 'vdp'),
                                 '-e', 'p4-general-poll'], cwd=ROOT, env=build_environment, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit('P4 build failed; see ' + str(output / 'p4-build.log'))
    after = {'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain')),
             'source_sha256': snapshot()}
    if before != after:
        raise SystemExit('source state changed during build; no bundle frozen')
    files = []
    for suffix in ('bin', 'elf', 'factory.bin'):
        source = ROOT / ('vdp/.pio/build/p4-general-poll/firmware.' + suffix)
        verify_embedded_identity(source, source_identity, build_id, status)
        target = output / (build_id + '.' + suffix)
        shutil.copyfile(source, target)
        files.append({'filename': target.name, 'sha256': sha(target), 'size_bytes': target.stat().st_size})
    (output / 'autoexec.txt').write_bytes(b'VDU 22 3\r\nEMOS VDPPOLL\r\n')
    manifest = {'schema_version': 1, 'build': {'artifact_id': identity['artifact_id'],
                'source_identity': source_identity, 'build_id': build_id, 'status': status,
                'created_at': now.isoformat()}, 'provenance': before, 'outputs': files,
                'baud_rate': 1152000, 'request_hex': '170080A5', 'reply_hex': '8001A5',
                'requires': 'separately built and reviewed EMOS providing EMOS VDPPOLL',
                'notes': ['Local build only; no hardware or emulator qualification.']}
    (output / 'build-manifest.yaml').write_text(yaml.safe_dump(manifest, sort_keys=False))
    print('P4 build PASS; bundle: ' + str(output))


if __name__ == '__main__':
    main()
