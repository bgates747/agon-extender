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
    parser.add_argument('--emos-source', type=Path, help='Native EMOS owner worktree for matched endpoint checks')
    parser.add_argument('--parallel-emos-source', type=Path, help='NET-004 owner worktree for actual foreground endpoint checks')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    inputs = sorted((root/'vdp/video/extender/network/messages').glob('*.*'))
    inputs += sorted((root/'tests/network/messages').glob('*.*'))
    inputs += [root/'include/agon/net.h', root/'include/agon/net_parallel.h']
    start = time.monotonic_ns()
    report = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'clock': 'host monotonic nanoseconds; elapsed, not calibrated performance',
              'scope': 'actual core and ephemeral IPv4 loopback; optional actual EMOS/P4 peer/C-client fake-transport pipeline; no physical target',
              'inputs': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in inputs if p.is_file()}, 'steps': [], 'passed': False}
    flags = ['-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer', '-no-pie', '-I', 'vdp/video']
    try:
        with tempfile.TemporaryDirectory(prefix='net003-') as temp:
            cases = [('core', ['tests/network/messages/channel_test.cpp']),
                     ('parallel-mailbox', ['tests/network/messages/parallel_mailbox_test.cpp']),
                     ('parallel-service', ['tests/network/messages/parallel_service_test.cpp',
                                           'vdp/video/extender/transport/p4_parallel_handover.cpp']),
                     ('tcp', ['tests/network/messages/tcp_test.cpp',
                              'vdp/video/extender/network/messages/tcp_client.cpp'])]
            if args.parallel_emos_source:
                emos = args.parallel_emos_source.resolve()
                fake = Path(temp)
                (fake/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
                (fake/'ez80f92.h').write_text('/* Physical owner injected by host check. */\n')
                command = ['cc','-std=c17','-Wall','-Wextra','-Werror',
                           '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',
                           '-Wno-endif-labels','-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast',
                           '-DMOS_DEFINES_H','-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35',
                           '-DEMOS_NETWORK_PARALLEL=1',
                           '-include',str(root.parent/'agon-emos/tests/host/defines.h'),
                           '-I'+temp,'-I'+str(root.parent/'agon-emos/tests/host'),'-I'+str(emos/'src'),
                           '-c',str(emos/'src/emos_netp.c'),'-o',str(fake/'netp.o')]
                report['inputs']['component:emos_netp.c'] = hashlib.sha256((emos/'src/emos_netp.c').read_bytes()).hexdigest()
                started = time.monotonic_ns()
                with (output/'netp-compile.log').open('w') as log:
                    result = subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=180)
                report['steps'].append({'name':'netp','phase':'compile','command':command,
                                        'returncode':result.returncode,'duration_ns':time.monotonic_ns()-started})
                if result.returncode: raise RuntimeError('Actual EMOS netp endpoint compile failed')
                common=command.copy();common[common.index(str(emos/'src/emos_netp.c'))]=str(emos/'src/emos_app_span.c');common[-1]=str(fake/'span.o')
                report['inputs']['component:emos_app_span.c']=hashlib.sha256((emos/'src/emos_app_span.c').read_bytes()).hexdigest()
                with (output/'span-compile.log').open('w') as log:
                    subprocess.run(common,cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
                cases.append(('parallel-pipeline',['tests/network/messages/parallel_pipeline_test.cpp',str(fake/'netp.o'),str(fake/'span.o')]))
                flags += ['-I',str(root/'include')]
            if args.emos_source:
                emos = args.emos_source.resolve()
                wire = (root/'vdp/video/extender/network/messages/wire.h').read_text()
                assert wire == (emos/'src/emos_net_wire.h').read_text()
                public = (root/'include/agon/net.h').read_text()
                assert public.split('// BEGIN canonical messages/wire.h\n')[1].split('// END canonical messages/wire.h')[0] == wire
                fake = Path(temp)
                (fake/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
                (fake/'ez80f92.h').write_text('/* No hardware registers used by this endpoint. */\n')
                command = ['cc','-std=c17','-Wall','-Wextra','-Werror',
                           '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',
                           '-Wno-endif-labels','-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast',
                           '-DMOS_DEFINES_H','-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35',
                           '-include',str(root.parent/'agon-emos/tests/host/defines.h'),
                           '-I'+temp,'-I'+str(root.parent/'agon-emos/tests/host'),'-I'+str(emos/'src'),
                           '-c',str(emos/'src/emos_net.c'),'-o',str(fake/'emos.o')]
                report['inputs']['component:emos_net.c'] = hashlib.sha256((emos/'src/emos_net.c').read_bytes()).hexdigest()
                started = time.monotonic_ns()
                with (output/'emos-compile.log').open('w') as log:
                    result = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT, timeout=180)
                report['steps'].append({'name':'emos','phase':'compile','command':command,
                                        'returncode':result.returncode,'duration_ns':time.monotonic_ns()-started})
                if result.returncode: raise RuntimeError('Actual EMOS C endpoint compile failed')
                cases.append(('peer', ['tests/network/messages/peer_test.cpp',str(fake/'emos.o')]))
                flags += ['-I',str(root/'include')]
            for name, sources in cases:

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
