"""Run and validate one stock rowload window on the reserved Legacy arm."""
import argparse
import csv
import fcntl
import hashlib
import json
import re
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


def check_mirror(raw, mode, case, pilot):
    """Require an uninterrupted grammar between fixture banners, including cleanup."""
    if pilot:
        guard = re.search(rb'Copper check begin (-?\d+)[\r\n]+Copper check end \1[\r\n]+K Copper check', raw)
        if not guard:
            raise RuntimeError('Copper self-check leaked operands or changed its entry setting')
    banner = f'Mode {mode} test {case}, Escape ends window'.encode()
    if case in 'RB':
        pattern = rb'Copper entry (-?\d+)[\r\n]+' + banner + rb'[\r\n]+Copper restored \1[\r\n]+K Copper check'
    else:
        allowed = rb'[\r\n\x0c]+' if case == 'C' else rb'[\r\n]+'
        pattern = banner + allowed + b'K Copper check'
    matched = re.search(pattern, raw)
    if not matched:
        raise RuntimeError('Unexpected printer bytes or missing state restoration during ' + banner.decode())
    if case in 'RB':
        return int(matched[1])
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binding', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--mode', required=True, type=int, choices=(20,8,0,3,136))
    parser.add_argument('--case', required=True, choices=list('CRDB'))
    parser.add_argument('--previous', required=True, type=Path, help='Previous collected CSV')
    parser.add_argument('--pilot', action='store_true', help='Stage fresh corrected fixture and check Copper states')
    args = parser.parse_args()
    mode, case = args.mode, args.case
    if args.pilot and (mode, case) != (20, 'R'):
        parser.error('First window must be mode 20 draw')
    before = args.previous.read_bytes()
    binding = read(args.binding)
    root = Path(binding['runner_checkout'])
    out = args.out.resolve()
    if subprocess.check_output(['git', '-C', root, 'rev-parse', 'HEAD'], text=True).strip() != binding['runner_revision']:
        raise RuntimeError('Operator checkout mismatch')
    config = pinned_json(binding['config'])
    job = pinned_json(binding['arms']['legacy']['job'])
    fixture = job['fixtures'][0]
    owner = binding['operator_chat']
    parent = pinned_json(binding['parent_binding'])
    packet = Path(binding['parent_binding']['path']).parent
    preload = read(packet / 'evidence/legacy/preload/preload.json')
    if (owner != read(packet / 'evidence/slot-open.json')['operator'] or
            preload['operator'] != owner or preload['route'] != 'Legacy' or
            preload['mode'] != 0 or preload['sha256'] != parent['fixture']['sha256'] or parent['operator_chat'] != owner):
        raise RuntimeError('Reservation or preload mismatch')

    sys.path.insert(0, str(root / 'scripts'))
    from olimex_bench import (Bench, Observer, PARALLEL_LISTENER, RemoteError,
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

    def collect(label):
        bench.start_listener('listener-' + label, PARALLEL_LISTENER)
        remote = fixture['cwd'] + '/rowload.csv'
        dest = out / (label + '.csv')
        staged = StagedClient(bench.url, out / ('transfer-' + label + '.json'))
        try:
            result = staged.begin('get', remote, destination=dest, require_parallel=True)
        finally:
            staged.close()
        record('receipt-' + label, result=result)
        data = dest.read_bytes()
        if (result['bytes'] != len(data) or result['payload_carrier'] != 'parlio'
                or result['error'] or result['remote_status']):
            raise RuntimeError('CSV collection differs from PARLIO receipt')
        bench.exit_staged_listener(label)
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
            bench.type_line('enable-mirror', 'VDU 2')
            prompt = o.witness('entry-prompt')
            if prompt.lower() != (fixture['cwd'] + ' *').lower().encode():
                raise RuntimeError('Unexpected entry directory: ' + repr(prompt))
            if args.pilot:
                o.mirror_off(prompt, 'mirror-off-stage')
                image = Path(fixture['agon']['path']).read_bytes()
                if hashlib.sha256(image).hexdigest() != fixture['agon']['sha256']:
                    raise ValueError('Corrected program hash mismatch')
                def existing(client, target):
                    try:
                        return client.stat_entry(target)
                    except RemoteError as error:
                        if error.status == 6 and error.detail in (b'\x04', b'\x05'):
                            return None
                        raise
                bench.stage_parallel({fixture['sd_program']: image}, [], existing)
                bench.type_line('mirror-on-test', 'VDU 2')
                if o.witness('stage-prompt') != prompt:
                    raise RuntimeError('Staging changed the MOS prompt')
            o.quiet_load('LOAD ' + Path(fixture['sd_program']).name + ' &040000', prompt)
            menu = b'T transitions, Q exit.'
            bench.type_line('invoke', 'RUN &040000')
            until(o, 'menu', menu)
            if args.pilot:
                key('check', 'type', 'k')
                until(o, 'copper-test', menu, 30)
                if not re.search(rb'Copper check begin (-?\d+)[\r\n]+Copper check end \1[\r\n]+K Copper check', (out / 'mos.bin').read_bytes()):
                    raise RuntimeError('Copper preflight state or command-consumption failure')
            key('workload', 'type', case.lower())
            until(o, 'mode-entry', b'Mode number then Enter:')
            key('mode', 'type', str(mode), '--enter')
            until(o, 'entered', f'Mode {mode} test {case}, Escape ends window'.encode())
            start = time.monotonic()
            record('entered', mode=mode, case=case, monotonic=start)
            command = [sys.executable, str(Path(__file__).with_name('observe.py')),
                       '--binding', str(args.binding.resolve()), '--arm', 'legacy',
                       '--seconds', '60', '--hz', '1', '--output', str(out / 'observer')]
            with subprocess.Popen(command) as observer:
                try:
                    while observer.poll() is None:
                        if time.monotonic() - start > 85:
                            raise TimeoutError('Service observer exceeded window bound')
                        data = reader.read(min(8192, reader.in_waiting or 1))
                        if data:
                            o.capture(data)
                    if observer.returncode:
                        raise RuntimeError('Service observer failed')
                finally:
                    if observer.poll() is None:
                        observer.kill()
                        observer.wait()
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
        restored = check_mirror((out / 'mos.bin').read_bytes(), mode, case, args.pilot)
        if not after.startswith(before):
            raise RuntimeError('Prior CSV data changed')
        rows = list(csv.reader(after[len(before):].decode('ascii').splitlines()))
        if len(rows) != 1 or len(rows[0]) != 7 or rows[0][:2] != [str(mode), case]:
            raise RuntimeError(f'Expected one matching appended row, got {rows!r}')
        begin, end, loops, sd_bytes, ok = map(int, rows[0][2:])
        ticks = (end - begin) % (1 << 32)
        if not 5400 <= ticks <= 11000 or loops <= 0 or (sd_bytes > 0) != (case in 'DB') or ok != 1:
            raise RuntimeError(f'Invalid workload result {rows[0]!r}')
        samples = [json.loads(line) for line in (out / 'observer/observations.jsonl').read_text().splitlines()]
        if (samples[0].get('event') != 'start' or samples[-1].get('event') != 'end'
                or samples[-1]['elapsed_s'] < 60 or any('error' in s for s in samples)):
            raise RuntimeError('Nominal service observation incomplete')
        record('result', row=rows[0], mos_ticks=ticks, seconds_menu_to_escape_dispatch=dispatch-start,
               service_window_s=samples[-1]['elapsed_s'], status_reads=sum('data' in s for s in samples),
               prompt=prompt.decode(), copper_entry_and_exit=restored, clean_mirror=True,
               program_sha256=fixture['agon']['sha256'], slot='held')


if __name__ == '__main__':
    main()
