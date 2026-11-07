"""One isolated async UART1 appliance; no installation/reset/retry.

Adapted from the retained NET-004 parent without changing its frozen source.

Run only after an owner-local stage/readback and current component admission.
All application/carrier code stays in Extender. No MechAgon import, game schema,
module, asset loader or private EMOS RAM address is used. An uncertain failure
retains custody for normal recovery and RAM preservation before any later LOAD.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
from keyboard import Client as Keyboard, text_events
from passive_serial import open_passive_serial

TASK = 'NET004-U1RX-ISOLATION'
CASES = ('async-rx',)
SIZES = [0, 1, 2, 17, 63, 64, 65, 75, 79, 127, 128]
FIXTURE = '7ad4c8915a6f0a2ed721f5ab8ac080ca526d92ce3b30a1febc74567fb037fa1e'
P4 = 'd9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e'
EMOS = 'd43150a05293dabaecc2599922bc8cd8a6ee7453f0ff0a6577aaa84457eb90d7'
UNCHANGED = dict(native_vdp_sha256='5d65797e53a70db8716cc3bc31dc936e431aea975ffad8efb76d5d7e8c1e3d07',
 startup_sha256='ed403e17f90a22c634afa0de3cad65451bc52da86bde6da084abe42fac3b7c64',
 listener_sha256='0566e17f18747c2e625d2450ce5324a2b1097bce323a5e4d70fad6dcb41cdff2')
BUILD_ID = 'netasync-r01-b2026-11-07-09-46-17Z'

def save(path, value):
    with Path(path).open('x') as file:
        json.dump(value, file, indent=2)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())


def validate_binding(context, grant, prepared):
    """A new exact owner case, never historical lease/fixture compatibility."""
    if not (grant.get('owner') == 'linux-extender' and grant.get('task') == TASK
            and isinstance(grant.get('generation'), int) and grant['generation'] > 77
            and isinstance(grant.get('lease'), str) and len(grant['lease']) == 32
            and grant.get('request') and context.get('operator') == 'linux-extender'
            and context.get('central_owner') == 'linux-extender'
            and context.get('phase') == 'async-isolation'
            and all(context.get(key) == grant.get(key) for key in ('request', 'generation', 'lease'))
            and not context.get('released') and not context.get('pending_commands')):
        raise RuntimeError('Fresh exclusive owner/task/token required')
    if not (prepared.get('schema') == 'extender-u1rx-prepared-v1'
            and prepared.get('case') == 'async-rx' and prepared.get('carrier') == 'uart1-async'
            and prepared.get('sessions') == 4 and prepared.get('records') == 176
            and prepared.get('full_fixture_readback_match') is True
            and prepared.get('installed_components') == context.get('components')
            and context.get('components',{}).get('p4_app_sha256') == P4
            and context.get('components',{}).get('emos_rom_sha256') == EMOS
            and prepared.get('actual_cli') is True and prepared.get('callback_zero') is True
            and prepared.get('legacy_zero') is True and prepared.get('entry_mode') == 0
            and re.fullmatch(r'[0-9a-f]{64}', context.get('source_pins_sha256', ''))
            and prepared.get('source_pins_sha256') == context.get('source_pins_sha256')
            and prepared.get('fixture_sha256') == FIXTURE
            and all(context.get('components',{}).get(k)==v for k,v in UNCHANGED.items())):
        raise RuntimeError('Exact new ROM/P4/fixture and clean CLI required')
    for key,prefix,name in (('fixture_remote','/extender/network/uart1-async-rx/','netasync.bin'),
                            ('result_remote','/agents/extender/results/uart1-async-rx/','result.txt')):
        if prepared.get(key) != prefix+grant['request']+'/'+name:
            raise RuntimeError('Fresh owner SD path required')


def validate_peer_report(report):
    """The real peer compares bytes; reject partial/reordered metadata too."""
    expected = [dict(session=s, index=i, bytes=SIZES[i % len(SIZES)])
                for s in range(4) for i in range(44)]
    if not (report.get('passed') is True and report.get('closed_sessions') == 4
            and report.get('records') == expected and 'first_error' not in report):
        raise RuntimeError('Incomplete or failed four-session byte witness')
    return True


def validate_durable_result(text, case='async-rx'):
    if case != 'async-rx':raise RuntimeError('Unknown owner case')
    lines=text.splitlines()
    if len(lines)!=5:raise RuntimeError('Missing session retirement evidence')
    for session,line in enumerate(lines[:4]):
        if line != 'session=%d records=%d first_error=0 source_phase=0 close=0' % (session,(session+1)*44):
            raise RuntimeError('Incomplete/failed session retirement')
    words=lines[4].split()
    if not words or words[0]!=BUILD_ID:raise RuntimeError('Wrong native identity')
    fields={}
    for word in words[1:]:
        key,value=word.split('=',1)
        if key in fields:raise RuntimeError('Duplicate native field')
        fields[key]=value
    wanted=dict(result='PASS',first_error='0',records='176/176',opened='4/4',closed='4/4',
                release='0',restore='1',tick_hz_nominal='120',carrier='uart1-async',irq_complete='0')
    if any(fields.get(key)!=value for key,value in wanted.items()):
        raise RuntimeError('Native exact-byte/close/mode matrix incomplete')
    if not 0<=int(fields['elapsed_ticks'])<14400:raise RuntimeError('Native case bound')
    return fields


def run(context_path, prepared_path, output):
    context_path, prepared_path, output = map(Path, (context_path, prepared_path, output))
    context = json.loads(context_path.read_text())
    grant = json.loads(Path(context['grant']).read_text())
    prepared = json.loads(prepared_path.read_text())
    validate_binding(context, grant, prepared)
    pins_path = Path(context['source_pins'])
    if hashlib.sha256(pins_path.read_bytes()).hexdigest() != context['source_pins_sha256']:
        raise RuntimeError('Owner source freeze differs')
    pins = json.loads(pins_path.read_text())
    for name, pin in pins['inputs'].items():
        data = Path(name).read_bytes()
        if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
            raise RuntimeError('Changed frozen input: ' + name)
    fixture = Path(prepared['fixture_local']).read_bytes()
    if hashlib.sha256(fixture).hexdigest() != prepared['fixture_sha256']:
        raise RuntimeError('Selected local fixture differs')
    output.mkdir(parents=True, exist_ok=False)
    lease_helper = ROOT.parent / 'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'
    interpreter = ROOT.parent / 'agon-dev-env/.venv/bin/python'

    def own():
        current = json.loads(context_path.read_text())
        validate_binding(current, grant, prepared)
        subprocess.run([str(interpreter), str(lease_helper), 'assert-owner',
                        '--owner', 'linux-extender', '--lease', grant['lease']],
                       check=True, stdout=subprocess.DEVNULL, timeout=5)

    def line(label, command):
        own()
        save(output / (label + '-issued.json'), dict(epoch=time.time(), command=command, once=True))
        client = Keyboard(context['url'], output / (label + '-keys.json'))
        try:
            state = client.status()
            if not (state['ready'] and state['physical_neutral'] and not state['held'] and not state['pending']):
                raise RuntimeError('Input not ready and neutral; no command emitted')
            client.open(state)
            for char in command:
                client.send(text_events(char, state['locale'], state['caps']))
            client.send([(40, 1), (40, 0)])
            if not client.state.get('pending'):
                client.cancel()
        finally:
            client.lock.close()

    own()
    for port in context['ports']:
        if subprocess.run(['fuser', str(Path(port).resolve())], capture_output=True, timeout=3).returncode != 1:
            raise RuntimeError('USB port occupied; no actor launched')
    ip, port = context['echo_bind'], 7671
    with socket.socket() as probe:
        probe.bind((ip, port))
    save(output / 'manifest.json', dict(epoch=time.time(), grant=grant, prepared=prepared,
        prepared_path=str(prepared_path), source_pins=str(pins_path),
        observation_seconds=150, sizes=SIZES, sessions=4, records=176, no_reset_or_install=True))
    raw, p4raw = bytearray(), bytearray()
    stop = threading.Event()
    errors, threads = [], []
    peer = None
    requested = invoked = cli = passed = False
    failure = None

    def wait(predicate, deadline, label):
        while not predicate():
            if errors:
                raise RuntimeError(str(errors))
            if time.monotonic() >= deadline:
                raise TimeoutError(label + ': original bound expired; no replay')
            time.sleep(.025)

    def capture(serial, path, data):
        try:
            with path.open('xb') as file:
                while not stop.is_set():
                    part = serial.read(8192)
                    if part:
                        file.write(part)
                        file.flush()
                        data.extend(part)
                        if len(data) > 4 * 1024 * 1024:
                            raise RuntimeError('Serial evidence cap')
        except BaseException as exc:
            errors.append(repr(exc))

    def interrupted(signum, _):
        raise SystemExit(128 + signum)

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, interrupted)
    try:
        with open_passive_serial(context['ports'][0], baudrate=115200, timeout=.1) as main, \
             open_passive_serial(context['ports'][1], baudrate=115200, timeout=.1) as p4:
            for handle, name, data in ((main, 'mainboard.bin', raw), (p4, 'p4.bin', p4raw)):
                thread = threading.Thread(target=capture, args=(handle, output / name, data))
                thread.start()
                threads.append(thread)
            try:
                line('mirror-on', 'VDU 2')
                sentinel = b'Extender async UART1 observer'
                line('actual-cli', 'VDU ' + ' '.join(map(str, sentinel + b'\r\n')))
                wait(lambda: sentinel in raw, time.monotonic() + 15, 'Actual CLI')
                mark = len(raw)
                line('load-once', 'LOAD ' + prepared['fixture_remote'])
                prompt = lambda data: re.search(rb'(?:^|[\r\n])/[^\r\n]{0,96} \*', bytes(data))
                wait(lambda: prompt(raw[mark:]), time.monotonic() + 20, 'LOAD CLI')
                if any(error in raw[mark:] for error in (b'Error', b'not found', b'Invalid parameter')):
                    raise RuntimeError('LOAD failed; no old-image RUN')
                with (output / 'peer.log').open('x') as log:
                    peer = subprocess.Popen([str(ROOT / '.venv/bin/python'),
                        str(ROOT / 'tests/fixtures/network/repeat_peer.py'), '--bind', ip, '--port', str(port),
                        '--output', str(output / 'peer')],
                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    wait(lambda: peer.poll() is not None or (output / 'peer/ready.json').exists(),
                         time.monotonic() + 5, 'Echo readiness')
                    if peer.poll() is not None:
                        raise RuntimeError('Echo peer refused before RUN')
                    own()
                    requested = True
                    began = time.monotonic()
                    mark = len(raw)
                    line('run-once', 'RUN . ' + ip + ':' + str(port) + ' ' + prepared['result_remote'])
                    invoked = True
                    wait(lambda: (b'Async UART1 probe PASS' in raw[mark:] or
                                  b'Async UART1 probe FAIL' in raw[mark:] or b'Close refused' in raw[mark:])
                                  and prompt(raw[mark:]), began + 150, 'Native terminal CLI')
                    cli = True
                    passed = b'Async UART1 probe PASS' in raw[mark:] and b'Async UART1 probe FAIL' not in raw[mark:]
                    peer.wait(timeout=10)
                    report = json.loads((output / 'peer/run.json').read_text())
                    passed = passed and peer.returncode == 0 and validate_peer_report(report)
                    if not passed:
                        raise RuntimeError('Native/echo result failed; preserve RAM before later LOAD')
            finally:
                stop.set()
                for thread in threads:
                    thread.join(3)
    except BaseException as exc:
        failure = repr(exc)
        passed = False
        raise
    finally:
        stop.set()
        for thread in threads:
            thread.join(3)
        if peer is not None and peer.poll() is None:
            peer.terminate()
            try:
                peer.wait(timeout=5)
            except subprocess.TimeoutExpired:
                peer.kill()
                peer.wait(timeout=3)
        save(output / 'actors.json', dict(epoch=time.time(), run_requested=requested, run_delivery_returned=invoked, native_invoked_once=invoked,
            actual_native_cli=cli, serial_readers_joined=all(not thread.is_alive() for thread in threads),
            peer_joined=peer is None or peer.poll() is not None, passed=passed, error=failure,
            collection_pending=True, full_handback_pending=True,
            durable_repeat_verification_pending=True,
            preserve_RAM_before_LOAD=requested and not passed, no_replay=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True, type=Path)
    parser.add_argument('--prepared', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.context, args.prepared, args.output)
