#!/usr/bin/env python3
"""Finite actual-core build checks; caller owns the Pi compile reservation."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    inputs = sorted((root/'vdp/video/extender/network/messages').glob('*.*'))
    inputs += sorted((root/'tests/network/messages').glob('*.*'))
    start = time.monotonic_ns()
    report = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'clock': 'host monotonic nanoseconds; elapsed, not calibrated performance',
              'scope': 'actual core/fake I/O and ephemeral IPv4 loopback; no LAN/P4/EMOS',
              'inputs': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in inputs if p.is_file()}, 'steps': [], 'passed': False}
    flags = ['-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer', '-no-pie', '-I', 'vdp/video']
    try:
        with tempfile.TemporaryDirectory(prefix='net003-') as temp:
            for name, sources in [('core', ['tests/network/messages/channel_test.cpp']),
                                  ('tcp', ['tests/network/messages/tcp_test.cpp',
                                           'vdp/video/extender/network/messages/tcp_client.cpp'])]:
                executable = str(Path(temp)/name)
                for phase, command, limit in [('compile', [os.environ.get('CXX', 'g++'), *flags,
                                                           *sources, '-o', executable], 180),
                                               ('check', [executable], 20)]:
                    step_start = time.monotonic_ns()
                    step = {'name': name, 'phase': phase, 'command': command}
                    report['steps'].append(step)
                    with (output/f'{name}-{phase}.log').open('w') as log:
                        try:
                            result = subprocess.run(command, cwd=root, stdout=log,
                                                    stderr=subprocess.STDOUT, timeout=limit)
                            step['returncode'] = result.returncode
                            if result.returncode:
                                raise RuntimeError(f'{name} {phase} failed; see {log.name}')
                        finally:
                            step['duration_ns'] = time.monotonic_ns() - step_start
        report['passed'] = True
    finally:
        report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['duration_ns'] = time.monotonic_ns() - start
        (output/'run.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': True, 'duration_ns': report['duration_ns'], 'output': str(output)}))


if __name__ == '__main__':
    main()
