#!/usr/bin/env python3
"""Compile new objects with retained actual P4/IDF headers; never link/install."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-output', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, help='Explicit matching compiler for this host; retained build unchanged')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    database = (args.build_output/'build/compile_commands.json').resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    entry = next(row for row in json.loads(database.read_text())
                 if row['file'].endswith('/wired_network_service.cpp'))
    original = entry.get('arguments') or shlex.split(entry['command'])
    # Never leave dependency/output flags pointing into the retained build.
    command = []
    i = 0
    while i < len(original):
        value = original[i]
        if value in ('-MF', '-MT', '-MQ'):
            i += 2
            continue
        if value in ('-MD', '-MMD', '-MP') or value.startswith(('-MF', '-MT', '-MQ')):
            i += 1
            continue
        command.append(value)
        i += 1
    if args.compiler:
        command[0] = str(args.compiler.resolve())
    start = time.monotonic_ns()
    report = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'objects only, retained build headers/config; no firmware link or execution',
              'database_sha256': hashlib.sha256(database.read_bytes()).hexdigest(),
              'clock': 'host monotonic nanoseconds, not calibrated performance',
              'inputs': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted((root/'vdp/video/extender/network/messages').glob('*.*'))
                         if p.is_file()}, 'steps': [], 'passed': False}
    try:
        for name, source in [('tcp', 'vdp/video/extender/network/messages/tcp_client.cpp'),
                             ('core', 'tests/network/messages/target_compile.cpp')]:
            invocation = command.copy()
            invocation[invocation.index('-o') + 1] = str(output/f'{name}.o')
            invocation[invocation.index('-c') + 1] = str(root/source)
            invocation += ['-std=c++17', '-I'+str(root/'vdp/video'), '-include', 'sdkconfig.h']
            step = {'name': name, 'command': invocation,
                    'source_sha256': hashlib.sha256((root/source).read_bytes()).hexdigest()}
            report['steps'].append(step)
            with (output/f'{name}.log').open('w') as log:
                result = subprocess.run(invocation, cwd=entry['directory'], stdout=log,
                                        stderr=subprocess.STDOUT, timeout=180)
            step['returncode'] = result.returncode
            if result.returncode:
                raise RuntimeError(f'{name}: target compile failed; see {output}')
        nm = str(Path(command[0]).with_name(Path(command[0]).name.replace('g++', 'nm')))
        result = subprocess.run([nm, '-S', str(output/'core.o')], capture_output=True,
                                text=True, check=True, timeout=20)
        (output/'symbols.txt').write_text(result.stdout)
        report['sizes'] = {line.split()[-1]: int(line.split()[1],16)
                           for line in result.stdout.splitlines() if line.endswith(('_small_size','_large_size'))}
        report['passed'] = True
    finally:
        report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['duration_ns'] = time.monotonic_ns()-start
        (output/'run.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': True, 'sizes': report['sizes'], 'duration_ns': report['duration_ns']}))


if __name__ == '__main__':
    main()
