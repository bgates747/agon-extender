#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build the allowlisted TRS-80-002 source kits from this working tree.

No builds, installs, network access or Git mutation. Run with an existing
development virtual environment. ZIPs are byte-reproducible for identical
inputs and Git HEAD; all files use fixed metadata and stored compression.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
PREFIX = TASK.relative_to(ROOT).as_posix()
WEB = 'vdp/video/extender/web'
COMMON = {'LICENSE': 'LICENSE', 'LICENSING.md': 'LICENSING.md'}
PACKAGES = {
    'agon-extender-trs-net-probe-r01': {
        **COMMON,
        'README.md': f'{PREFIX}/sources/trs-net-probe-README.md',
        'trs_net_probe.py': f'{PREFIX}/sources/trs_net_probe.py',
    },
    'agon-extender-sd-lab-r01': {
        **COMMON,
        'README.md': f'{PREFIX}/sources/sd-lab-README.md',
        'examples/queue_demo.cpp': f'{PREFIX}/sources/queue_demo.cpp',
        **{p: p for p in (
            'vdp/video/extender/storage/sd_wire.h',
            'vdp/video/extender/storage/sd_service.hpp',
            'scripts/sdcard.py',
            'tests/test_sd_wire.py',
            'tests/test_sd_service.py',
            'tests/sd_service_test.cpp',
            'tests/test_sdcard_client.py',
        )},
    },
    'agon-extender-browser-demo-r01': {
        **COMMON,
        'README.md': f'{PREFIX}/sources/browser-demo-README.md',
        **{f'{WEB}/{name}': f'{WEB}/{name}' for name in (
            'index.html', 'style.css', 'app.js', 'frame_protocol.js',
            'webgl2_presenter.js',
        )},
        'tests/browser_video_ui_test.py': 'tests/browser_video_ui_test.py',
    },
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    head = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    output = TASK / 'bin'
    output.mkdir(exist_ok=True)
    sums = []
    for name, paths in PACKAGES.items():
        payload = {}
        entries = []
        for destination, source in sorted(paths.items()):
            path = ROOT / source
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'Expected a regular source file: {source}')
            data = path.read_bytes()
            baseline = subprocess.run(
                ['git', 'show', f'{head}:{source}'], cwd=ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
            state = ('added' if baseline.returncode else
                     'unchanged' if baseline.stdout == data else 'modified')
            entries.append({'path': destination, 'source_path': source,
                            'source_state_vs_head': state,
                            'bytes': len(data), 'sha256': sha(data)})
            payload[destination] = data
        manifest = {
            'schema': 1, 'package': name, 'task': 'TRS-80-002',
            'status': 'experimental-source-sample',
            'repository': 'https://github.com/bgates747/agon-extender',
            'source_head': head, 'files': entries,
            'note': 'HEAD is the comparison baseline, not a release identity. '
                    'The per-file entries identify this working-tree snapshot. '
                    'manifest.json is excluded from its own file hashes.',
        }
        payload['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
        archive = output / f'{name}.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as z:
            for destination, data in sorted(payload.items()):
                info = zipfile.ZipInfo(f'{name}/{destination}',
                                       date_time=(2026, 9, 13, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                z.writestr(info, data)
        sums.append(f'{sha(archive.read_bytes())}  {archive.name}')
        print(f'{archive.relative_to(ROOT)} ({archive.stat().st_size} bytes)')
    (output / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')


if __name__ == '__main__':
    main()
