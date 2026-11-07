#!/usr/bin/env python3
"""Compile two separate stopped eZ80 core self-checks; no deployment/invocation.

Caller must hold normal compiler custody. These are compile/link probes only,
not physical test appliances or evidence of any real carrier/timer operation.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain-bin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    args.output.mkdir(parents=True, exist_ok=False)
    report = dict(schema='comms-core-link-check-r01', scope='stopped core self-check compilation only',
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=False, builds=[])
    started = time.monotonic_ns()
    env = dict(os.environ, PATH=str(args.toolchain_bin.resolve()) + os.pathsep + os.environ['PATH'])
    try:
        for kind in ('accuracy', 'performance'):
            out = args.output / kind
            src = out / 'src'
            src.mkdir(parents=True)
            inputs = {}
            for source, target in (('core.hpp', 'core.hpp'), ('selfcheck.cpp', 'main.cpp')):
                p = root / 'tests/fixtures' / ('comms_' + kind) / source
                shutil.copyfile(p, src / target)
                inputs[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
            (out / 'Makefile').write_text('NAME=comms-' + kind + '-core\nLDHAS_ARG_PROCESSING=0\n'
                'LDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\n'
                'CXXFLAGS += -Isrc -std=c++17 -fno-exceptions -fno-rtti -Wall -Wextra -Werror\n')
            item = dict(kind=kind, inputs=inputs, passed=False)
            report['builds'].append(item)
            with (out / 'build.log').open('x') as log:
                result = subprocess.run(['make', '-j1', '-C', str(out.resolve())], env=env,
                                        stdout=log, stderr=subprocess.STDOUT, timeout=180)
            item['returncode'] = result.returncode
            if result.returncode:
                raise RuntimeError(kind + ' native compile/link failed')
            binary = out / 'bin' / ('comms-' + kind + '-core.bin')
            item.update(passed=True, bytes=binary.stat().st_size,
                        sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
        report['passed'] = True
    finally:
        report['elapsed_ns'] = time.monotonic_ns() - started
        report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (args.output / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
