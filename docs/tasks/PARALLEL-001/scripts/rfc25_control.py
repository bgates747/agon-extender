"""One guarded-RFC25 parallel appliance; no installation/reset/retry.

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

TASK = 'PARALLEL-001-RFC25'
CASES = ('rfc25',)
SIZES = [0, 1, 127, 128]
FIXTURES = {'rfc25': 'd04442f1af37bbf06c253f155caf9a684961d74e8d74bf1c0ce8bb4fd23de952'}
UNFILTERED_P4 = '02addd547f3af3a00cf4fb975ef9d259f2e48d0ded64ef80a053f9b4de10ccf9'
PARALLEL_EMOS = '8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281'


def save(path, value):
    with Path(path).open('x') as file:
        json.dump(value, file, indent=2)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())


def validate_binding(context, grant, prepared):
    """Pure gate; the central assert-owner remains mandatory at every call."""
    if not (grant.get('owner') == 'linux-extender' and grant.get('task') == TASK
            and isinstance(grant.get('generation'), int) and grant['generation'] > 58
            and isinstance(grant.get('lease'), str) and len(grant['lease']) == 32
            and grant.get('request') and context.get('operator') == 'linux-extender'
            and context.get('central_owner') == 'linux-extender'
            and all(context.get(key) == grant.get(key) for key in ('request', 'generation', 'lease'))
            and not context.get('released') and not context.get('pending_commands')):
        raise RuntimeError('Fresh exclusive independent owner/task/token required')
    if not (prepared.get('schema') == 'extender-parallel-rfc25-prepared-v1'
            and prepared.get('case') in CASES and prepared.get('carrier') == 'parallel'
            and prepared.get('guarded_rfc25') is True
            and prepared.get('rfc25_packet_bytes') == 67
            and prepared.get('full_fixture_readback_match') is True
            and prepared.get('installed_components') == context.get('components')
            and prepared.get('installed_components')
            and prepared.get('actual_cli') is True and prepared.get('callback_zero') is True
            and prepared.get('legacy_zero') is True
            and prepared.get('entry_mode') == 0
            and prepared.get('source_pins_sha256') == context.get('source_pins_sha256')):
        raise RuntimeError('Exact staged fixture/current pair and clean CLI required')
    for key, prefix in (('fixture_remote', '/extender/network/parallel001-rfc25/'),
                        ('result_remote', '/agents/extender/results/parallel001-rfc25/')):
        path = prepared.get(key, '')
        if not isinstance(path, str) or not path.startswith(prefix) or '..' in path.split('/'):
            raise RuntimeError('Owned SD path required: ' + key)
    digest = prepared.get('fixture_sha256', '')
    if digest != FIXTURES[prepared['case']]:
        raise RuntimeError('Exact fixture hash required')
    wanted = UNFILTERED_P4
    if (context['components'].get('p4_app_sha256') != wanted or
            context['components'].get('emos_rom_sha256') != PARALLEL_EMOS):
        raise RuntimeError('Exact selected baseline/filter pair required')


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
        observation_seconds=150, sizes=SIZES, no_reset_or_install=True))
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
                sentinel = b'Extender RFC25 parallel observer'
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
                        str(ROOT / 'tests/fixtures/network/echo.py'), '--bind', ip, '--port', str(port),
                        '--sizes', ','.join(map(str, SIZES)), '--output', str(output / 'peer')],
                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    wait(lambda: peer.poll() is not None or 'Ready: one client' in (output / 'peer.log').read_text(),
                         time.monotonic() + 5, 'Echo readiness')
                    if peer.poll() is not None:
                        raise RuntimeError('Echo peer refused before RUN')
                    own()
                    requested = True
                    began = time.monotonic()
                    mark = len(raw)
                    line('run-once', 'RUN &040000 ' + ip + ':' + str(port) + ' ' + prepared['result_remote'])
                    invoked = True
                    wait(lambda: (b'Network echo probe PASS' in raw[mark:] or
                                  b'Network echo probe FAIL' in raw[mark:] or b'close refused' in raw[mark:])
                                  and prompt(raw[mark:]), began + 150, 'Native terminal CLI')
                    cli = True
                    passed = b'Network echo probe PASS' in raw[mark:] and b'Network echo probe FAIL' not in raw[mark:]
                    peer.wait(timeout=10)
                    report = json.loads((output / 'peer/run.json').read_text())
                    passed = passed and peer.returncode == 0 and report['passed'] and [item['bytes'] for item in report['records']] == SIZES
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
            rfc25_SD_cycle_verification_pending=True,
            preserve_RAM_before_LOAD=requested and not passed, no_replay=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True, type=Path)
    parser.add_argument('--prepared', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.context, args.prepared, args.output)
