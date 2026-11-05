#!/usr/bin/env python3
"""Build generic echo appliance only; no SD deployment, invocation or emulator."""
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
    parser.add_argument('--toolchain-bin', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    work = output/'work'
    source = work/'src'
    (source/'agon').mkdir(parents=True)
    inputs = {
        'main.cpp':'tests/fixtures/network/main.cpp',
        'mode_lifecycle.hpp':'tests/fixtures/scroll/mode_lifecycle.hpp',
        'mos_io.asm':'tests/fixtures/controller/mos_io.asm',
        'net_callback.asm':'include/agon/net_callback.asm',
        'agon/net.h':'include/agon/net.h',
    }
    for name, path in inputs.items():
        shutil.copyfile(root/path, source/name)
    (work/'Makefile').write_text('NAME=netprobe\nLDHAS_ARG_PROCESSING=1\nLDHAS_EXIT_HANDLER=0\n'
                               'include $(shell agondev-config --makefile)\n'
                               'CXXFLAGS += -Isrc -std=c++17 -fno-exceptions -fno-rtti -Wall -Wextra -Werror\n')
    env = dict(os.environ, PATH=str(args.toolchain_bin.resolve())+os.pathsep+os.environ['PATH'])
    start = time.monotonic_ns()
    report = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='native Agon compile/link only; no invocation',
                  inputs={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs.values()})
    try:
        with (output/'build.log').open('w') as log:
            result = subprocess.run(['make','-j1','-C',str(work)], env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=180)
        report['returncode'] = result.returncode
        if result.returncode:
            raise RuntimeError('Native fixture build failed; see build.log')
        shutil.copyfile(work/'bin/netprobe.bin', output/'netprobe.bin')
        report['binary'] = dict(bytes=(output/'netprobe.bin').stat().st_size,
                               sha256=hashlib.sha256((output/'netprobe.bin').read_bytes()).hexdigest())
    finally:
        report['duration_ns'] = time.monotonic_ns()-start
        report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (output/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
