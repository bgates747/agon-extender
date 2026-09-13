#!/usr/bin/env python3
"""Qualify an already running mainboard SD service in its isolated test root.

No serial opens, reset, firmware flashing, arbitrary command execution or changes
to existing game files. Keep the output directory after any failure: its client
state retains uncertain requests. Results distinguish host-injected lost replies
from physical link interruption. This program never declares hardware acceptance.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import secrets
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zlib

from sdcard import Client, RemoteError, path_payload, record

ROOT = Path(__file__).resolve().parents[1]
SIZES = (0, 1, 211, 212, 213, 4096, 65535, 65536, 65537, 131731)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class AuditedClient(Client):
    def __init__(self, url, state, audit, timeout):
        super().__init__(url, state, timeout)
        self.audit = audit
        self.drop_next_write = False
        self.injected_loss = False
        self.recovered_losses = 0
        self.last_request = None

    def event(self, kind, **data):
        self.audit.write(json.dumps(dict(event=kind, monotonic=time.monotonic(), **data))+'\n')
        self.audit.flush()

    def exchange(self, request):
        self.last_request = request
        self.event('request', record=request.hex())
        start = time.monotonic()
        status, data = super().exchange(request)
        self.event('response', status=status, payload=data.hex(), seconds=time.monotonic()-start)
        if self.drop_next_write and request[12] == 6 and status == 0:
            # The physical request completed. Withhold its response from the
            # durable client, then retry the exact saved request. P4 may answer
            # from its cache; this is not a claim of physical UART ACK loss.
            self.drop_next_write = False
            self.injected_loss = True
            self.event('injected_host_response_loss')
            raise TimeoutError('Deliberately discarded successful WRITE response')
        return status, data

    def rpc(self, op, payload=b''):
        try:
            return super().rpc(op, payload)
        except TimeoutError:
            if not self.injected_loss:
                raise
            self.injected_loss = False
            saved = json.loads(self.state_path.read_text())
            require(saved == self.state, 'Uncertain client state was not durable')
            pending = self.state['pending']
            result = self.resolve()
            require(self.last_request.hex() == pending, 'Retry changed the saved request')
            self.recovered_losses += 1
            self.event('durable_retry_pass')
            return result


def expect_error(client, op, payload, status):
    try:
        client.rpc(op, payload)
    except RemoteError as error:
        require(error.status == status, f'Expected service error {status}, got {error!r}')
        client.event('expected_error', operation=op, status=status, detail=error.detail.hex())
        return
    raise RuntimeError(f'Operation {op} unexpectedly succeeded')


def raw_http_error(client, data, expected):
    req = urllib.request.Request(client.url+'/sd/rpc', data=data,
                                 headers={'Content-Type': 'application/octet-stream'})
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    require(status == expected, f'Expected HTTP {expected}, got {status}')
    client.event('expected_http_error', status=status, request=data.hex())


def error_checks(client, path):
    name = path_payload(path)
    require(client.rpc(10, b'\0'+name) == b'\0', 'Test target already exists; refusing to reuse it')
    expect_error(client, 255, b'', 2)
    expect_error(client, 2, path_payload('/outside-port017'), 1)
    expect_error(client, 2, path_payload('/extender/sdtest/../outside'), 1)
    expect_error(client, 9, struct.pack('<I', 1), 1)
    expect_error(client, 2, name, 6)
    expect_error(client, 5, struct.pack('<III', 1, 0, 0)+
                 path_payload('/extender/sdtest/SDserve.BIN'), 1)
    damaged = bytearray(record(client.state['session'], client.state['sequence']+1, 2, name))
    damaged[-1] ^= 1
    raw_http_error(client, bytes(damaged), 400)
    last = client.last_request
    conflict = record(client.state['session'], client.state['sequence'], 255, b'conflict')
    raw_http_error(client, conflict, 409)
    require(last is not None, 'Missing request trace')
    status, _ = client.exchange(record(client.state['session'] ^ 0x17000000,
                                       1, 2, name))
    require(status == 4, 'An unknown session was not rejected')
    status, _ = client.exchange(record(client.state['session'],
                                       client.state['sequence']+2, 2, name))
    require(status == 5, 'A skipped sequence was not rejected')

    data = b'\0\xff\x81~'
    tid = secrets.randbelow(0xffffffff)+1
    begin = struct.pack('<III', tid, len(data), zlib.crc32(data))+name
    require(client.rpc(5, begin) == struct.pack('<II', tid, 0), 'BEGIN identity differs')
    expect_error(client, 5, begin, 3)
    expect_error(client, 6, struct.pack('<II', tid, 1)+data, 1)
    require(client.rpc(6, struct.pack('<II', tid, 0)+data[:2]) ==
            struct.pack('<II', tid, 2), 'WRITE offset differs')
    expect_error(client, 7, struct.pack('<I', tid), 7)
    expect_error(client, 11, b'', 3)
    client.rpc(9, struct.pack('<I', tid))
    require(client.rpc(10, b'\0'+name) == b'\0', 'CANCEL left journal siblings')

    # Valid wire CRC, deliberately wrong file contents: FINISH must reject it.
    client.rpc(5, begin)
    client.rpc(6, struct.pack('<II', tid, 0)+b'bad!')
    expect_error(client, 7, struct.pack('<I', tid), 7)
    require(client.rpc(10, b'\0'+name) == b'\x06', 'Failed verification did not retain stage/journal')
    require(client.rpc(10, b'\x02'+name) == b'\0', 'Explicit orphan abandonment failed')


def exercise(client, target, sizes=SIZES, results=None):
    results = [] if results is None else results
    name = path_payload(target)
    require(client.rpc(10, b'\0'+name) == b'\0', 'Cycle target exists; refusing to overwrite')
    previous = None
    for cycle, size in enumerate(sizes, 1):
        data = random.Random(0x17000000+cycle).randbytes(size)
        start = time.monotonic()
        # Exercise a durable retry during the first nonempty cycle only.
        client.drop_next_write = cycle == 2
        transfer = client.upload(target, data, activate=True)
        info = client.rpc(2, name)
        require(len(info) == 5 and struct.unpack_from('<I', info)[0] == size,
                'Activated target STAT differs')
        if previous is not None:
            require(client.download(target+'.p17bak') == previous, 'Previous target was not preserved')
        require(client.rpc(10, b'\x03'+name) == b'\x01', 'Verified backup cleanup failed')
        result = {'cycle': cycle, 'size': size, 'transfer': transfer,
                  'sha256': hashlib.sha256(data).hexdigest(), 'seconds': time.monotonic()-start}
        results.append(result)
        client.event('cycle_pass', **result)
        print(f'Cycle {cycle}/{len(sizes)} PASS: {size} bytes, {result["seconds"]:.3f}s', flush=True)
        previous = data
    require(client.recovered_losses == 1, 'Required lost-response recovery was not exercised')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True, help='New evidence directory; never reused')
    parser.add_argument('--timeout', type=float, default=30, help='Seconds per uncertain request')
    args = parser.parse_args()
    require(args.timeout > 0, 'Timeout must be positive')
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    run_id = 'PORT-017-'+now.strftime('%Y-%m-%d-%H-%M-%SZ')
    # New names under the pre-provisioned isolated root; no MKDIR capability.
    stem = '/extender/sdtest/p17-'+now.strftime('%Y%m%d-%H%M%S')
    result = {'run_id': run_id, 'started_at': now.isoformat(), 'outcome': 'fail',
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
              'source_sha256': {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                                for n in ('scripts/qualify_sdcard.py', 'scripts/sdcard.py')},
              'target': stem+'.bin', 'error_target': stem+'-err.bin', 'cycles': [],
              'limits': ['Host-injected response loss; no physical cable or power interruption.',
                         'No induced physical disk-full, media fault or power loss.',
                         'Keyboard observation and user acceptance recorded separately.',
                         'Times include multiple readbacks, sync and host audit/state writes.']}
    client = None
    try:
        with (output/'requests.jsonl').open('x') as audit:
            client = AuditedClient(args.url, output/'client-state.json', audit, args.timeout)
            result['initial_status'] = client.status()
            client.connect()
            result['boot'] = client.state['boot']
            error_checks(client, result['error_target'])
            result['error_checks'] = 'pass'
            exercise(client, result['target'], results=result['cycles'])
            result['durable_retry_count'] = client.recovered_losses
            result['final_status'] = client.status()
            require(result['final_status']['online'] and result['final_status']['boot'] == result['boot'],
                    'Service stopped or restarted during the sequence')
            result['outcome'] = 'pass'
    except Exception as error:
        result['error'] = repr(error)
        raise
    finally:
        if client:
            client.lock.close()
        result['ended_at'] = datetime.now(timezone.utc).isoformat()
        (output/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: ten unattended physical-path cycles and bounded error/recovery cases.', flush=True)
    print('Service remains running. Hardware acceptance is still separate.', flush=True)


if __name__ == '__main__':
    main()
