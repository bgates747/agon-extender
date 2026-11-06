#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Package only reviewed Wi-Fi utility inputs; never glob private cfg/log files."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    identity = manifest['build_id']
    if not re.fullmatch(r'wifi-setup-b\d{4}-\d\d-\d\d-\d\d-\d\d-\d\dZ', identity):
        raise ValueError('Explicit UTC build identity required')
    # Fixed public whitelist; real .cfg, logs and ignored operator records
    # cannot enter this package even when adjacent to the build outputs.
    names = ['tools/wifi-setup/' + name for name in (
        'Makefile', 'README.md', 'NOTICES.md', 'wifi-setup.cfg.example',
        'include/setup.h', 'src/config.c', 'src/setup.c', 'src/main.c', 'src/uart.src')]
    names += ['tests/wifi-setup/' + name for name in (
        'test_core.c', 'test_platform.c', 'include/agon/mos.h')]
    names += ['scripts/build_wifi_setup_package.py']
    if set(manifest['inputs']) != set(names):
        raise ValueError('Exact reviewed source whitelist differs')
    payload = {}
    for name in names:
        data = (ROOT / name).read_bytes()
        if digest(data) != manifest['inputs'][name]:
            raise ValueError('Source changed after build: ' + name)
        payload['source/' + name] = data
    binary = (ROOT / 'tools/wifi-setup/bin/wifi-setup.bin').read_bytes()
    if len(binary) != manifest['binary']['bytes'] or digest(binary) != manifest['binary']['sha256']:
        raise ValueError('Native binary differs from exact build')
    payload['wifi-setup.bin'] = binary
    for name in ('README.md', 'NOTICES.md', 'wifi-setup.cfg.example'):
        payload[name] = (ROOT / 'tools/wifi-setup' / name).read_bytes()
    payload['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    payload['build-manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    inventory = {name: {'bytes': len(data), 'sha256': digest(data)} for name, data in sorted(payload.items())}
    payload['inventory.json'] = (json.dumps(inventory, indent=2) + '\n').encode()
    directory = args.output / identity
    directory.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    archive = args.output / (identity + '.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(payload):
            z.writestr(name, payload[name])
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or set(z.namelist()) != set(payload):
            raise ValueError('Archive structure failed')
        for name, data in payload.items():
            if z.read(name) != data or (directory / name).read_bytes() != data:
                raise ValueError('Extracted/archive mismatch: ' + name)
    result = {'build_id': identity, 'package': str(directory), 'archive': str(archive),
              'archive_sha256': digest(archive.read_bytes()), 'files_verified': len(payload),
              'private_cfg_or_logs_packaged': False, 'hardware_pass': False}
    (args.output / (identity + '-verification.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
