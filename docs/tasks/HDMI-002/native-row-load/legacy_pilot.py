"""Collect one 60-second mode-20 drawing reference on the reserved Legacy arm."""
import argparse
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def read(path):
    return json.loads(path.read_bytes())


def pinned_json(spec):
    data = Path(spec['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != spec['sha256']:
        raise ValueError('Binding hash mismatch: ' + spec['path'])
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binding', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    packet = args.binding.resolve().parent
    binding = read(args.binding)
    root = Path(binding['runner_checkout'])
    out = args.out.resolve()
    if subprocess.check_output(['git', '-C', root, 'rev-parse', 'HEAD'], text=True).strip() != binding['runner_revision']:
        raise RuntimeError('Operator checkout mismatch')
    config = pinned_json(binding['config'])
    job = pinned_json(binding['arms']['legacy']['job'])
    fixture = job['fixtures'][0]
    owner = binding['operator_chat']
    preload = read(packet / 'evidence/legacy/preload/preload.json')
    if (owner != read(packet / 'evidence/slot-open.json')['operator'] or
            preload['operator'] != owner or preload['route'] != 'Legacy' or
            preload['mode'] != 0 or preload['sha256'] != fixture['agon']['sha256']):
        raise RuntimeError('Reservation or preload mismatch')

    sys.path.insert(0, str(root / 'scripts'))
    from olimex_bench import (Bench, Client, Observer, PARALLEL_LISTENER, RemoteError,
                              StagedClient, bench_process, open_passive_serial)

    out.mkdir(exist_ok=False)
    bench = Bench(config, job, out)
    def record(label, **fields):
        bench_process.record(out / (label + '.json'), dict(epoch=time.time(), **fields))
        print(label, flush=True)

    def key(label, *action):
        bench.own()
        bench.keyboard()
        record(label, action=action)
        subprocess.run([sys.executable, str(root / 'scripts/keyboard.py'),
                        '--url', bench.url, '--state', str(out / ('keys-' + label + '.json')),
                        *action], check=True, timeout=16)

    def collect(label, optional=False):
        bench.start_listener('listener-' + label, PARALLEL_LISTENER)
        remote = fixture['cwd'] + '/rowload.csv'
        client = Client(bench.url, out / ('stat-' + label + '.json'), timeout=12)
        try:
            client.connect(require_fast=True)
            try:
                size, _ = client.stat_entry(remote)
            except RemoteError as error:
                if not optional or error.status != 6 or error.detail not in (b'\x04', b'\x05'):
                    raise
                size = None
        finally:
            client.lock.close()
        data = b''
        if size is not None:
            dest = out / (label + '.csv')
            staged = StagedClient(bench.url, out / ('transfer-' + label + '.json'))
            try:
                result = staged.begin('get', remote, destination=dest, require_parallel=True)
            finally:
                staged.close()
            record('receipt-' + label, result=result)
            data = dest.read_bytes()
            if (len(data) != size or result['bytes'] != size or
                    result['payload_carrier'] != 'parlio' or result['error'] or result['remote_status']):
                raise RuntimeError('CSV collection differs from STAT or PARLIO receipt')
        bench.exit_staged_listener(label)
        record('csv-' + label, present=size is not None, size=size, sha256=hashlib.sha256(data).hexdigest())
        return data

    def until(observer, label, marker, seconds=15):
        def match(raw):
            if b'Row test failed.' in raw or b'Start at a mode 0 prompt.' in raw:
                raise RuntimeError('rowload refused or failed during ' + label)
            return marker in raw
        observer.receive(label, bytearray(), match, seconds)

    with Path(config['operation_lock']).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        bench.lock = lock
        bench.validate_ports()
        bench.idle()
        bench.keyboard()
        port = bench.c['ports'][0]
        with open_passive_serial(port, timeout=0.15) as reader, (out / 'mos.bin').open('xb') as raw:
            o = Observer(reader, raw, bench.type_line)
            # A first Escape can close a selected case or cancel a partial mode entry.
            # A second Escape leaves the menu. At a blank MOS prompt it enters no command.
            for index in (1, 2):
                key(f'exit-interactive-{index}', 'hold', 'escape', '--seconds', '0.20')
                time.sleep(2)
            bench.type_line('enable-mirror', 'VDU 2')
            prompt = o.witness('takeover-prompt')
            if prompt.lower() != (fixture['cwd'] + ' *').lower().encode():
                raise RuntimeError('Unexpected entry directory: ' + repr(prompt))
            o.mirror_off(prompt, 'mirror-off-before-collection')
            before = collect('before', optional=True)
            bench.type_line('mirror-on-test', 'VDU 2')
            if o.witness('reload-prompt') != prompt:
                raise RuntimeError('Listener exit changed the MOS prompt')
            o.quiet_load('LOAD rowload.bin &040000', prompt)
            menu = b'T transitions, Q exit.'
            bench.type_line('invoke', 'RUN &040000')
            until(o, 'menu', menu)
            key('draw', 'type', 'r')
            until(o, 'mode-entry', b'Mode number then Enter:')
            key('mode', 'type', '20', '--enter')
            until(o, 'entered', b'Mode 20 test R, Escape ends window')
            start = time.monotonic()
            record('entered', mode=20, case='R', monotonic=start)
            subprocess.run([sys.executable, str(Path(__file__).with_name('observe.py')),
                            '--binding', str(args.binding.resolve()), '--arm', 'legacy',
                            '--seconds', '60', '--hz', '1', '--output', str(out / 'observer')],
                           check=True, timeout=85)
            dispatch = time.monotonic()
            key('end-window', 'hold', 'escape', '--seconds', '0.20')
            until(o, 'returned-menu', menu)
            key('close', 'type', 'q')
            until(o, 'closed', b'Row test closed.')
            if o.witness('completed-prompt') != prompt:
                raise RuntimeError('Unexpected final MOS prompt')
            o.mirror_off(prompt, 'mirror-off-after-window')
            after = collect('after')
            bench.type_line('mirror-on-final', 'VDU 2')
            if o.witness('collected-prompt') != prompt:
                raise RuntimeError('Unexpected prompt after CSV collection')
            o.mirror_off(prompt)
        bench.validate_ports()
        bench.idle()
        bench.keyboard()
        if not after.startswith(before):
            raise RuntimeError('Prior CSV data changed')
        rows = list(csv.reader(after[len(before):].decode('ascii').splitlines()))
        if len(rows) != 1 or len(rows[0]) != 7 or rows[0][:2] != ['20', 'R']:
            raise RuntimeError(f'Expected one appended mode-20 R row, got {rows!r}')
        begin, end, loops, sd_bytes, ok = map(int, rows[0][2:])
        ticks = (end - begin) % (1 << 32)
        if not ticks or loops <= 0 or sd_bytes != 0 or ok != 1:
            raise RuntimeError(f'Invalid workload result {rows[0]!r}')
        samples = [json.loads(line) for line in (out / 'observer/observations.jsonl').read_text().splitlines()]
        if (samples[0].get('event') != 'start' or samples[-1].get('event') != 'end'
                or samples[-1]['elapsed_s'] < 60 or any('error' in s for s in samples)):
            raise RuntimeError('Nominal service observation incomplete')
        record('result', row=rows[0], mos_ticks=ticks, seconds_menu_to_escape_dispatch=dispatch-start,
               service_window_s=samples[-1]['elapsed_s'], status_reads=sum('data' in s for s in samples),
               prompt=prompt.decode(), mirror='on during drawing', slot='held')


if __name__ == '__main__':
    main()
