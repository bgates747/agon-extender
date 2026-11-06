#!/usr/bin/env python3
"""Finite actual Wi-Fi core/adapter host checks; no device or emulator access.

Run only in an admitted compiler tranche. Output is an ignored evidence path.
"""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0')
flags = ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-g',
         '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-Itools/wifi-setup/include', '-Itests/wifi-setup/include']
core = ['tools/wifi-setup/src/config.c', 'tools/wifi-setup/src/setup.c']
def run(args):
    result = subprocess.run(args, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    with (out / 'host-checks.log').open('a') as f:
        f.write('$ ' + ' '.join(map(str, args)) + '\n' + result.stdout)
    if result.returncode:
        raise SystemExit(result.stdout or f'Command failed: {result.returncode}')
for name, source in [('diagnostic-core', 'tests/wifi-setup/test_core.c'),
                     ('startup-core', 'tests/wifi-start/test_start.c')]:
    target = str(out / name)
    run(flags + [source] + core + ['-o', target])
    run([target])
for name, source, test, define in [
    ('diagnostic-adapter', 'tools/wifi-setup/src/main.c', 'tests/wifi-setup/test_platform.c', '-Dmain=ws_native_main'),
    ('startup-adapter', 'tools/wifi-start/src/main.c', 'tests/wifi-start/test_platform.c', '-DWS_START_ENTRY=ws_start_native_main')]:
    obj, target = str(out / (name + '.o')), str(out / name)
    run(flags + [define, '-c', source, '-o', obj])
    run(flags + [obj, test] + core + ['-o', target])
    run([target, str(out)])
print('PASS: both actual cores and both native adapters with ASan/UBSan. No hardware or emulator.')
