#!/usr/bin/env python3
"""Explicit development client for P4-staged, checksum-free mainboard files.

One HTTP upload/download per file. The P4 worker owns all UART record exchanges.
Resume observes an existing job; it never resubmits a possibly executed upload.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

QUOTA = 32 * 1024 * 1024


class TransferError(RuntimeError):
    pass


class Client:
    def __init__(self, url, state, timeout=300):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'http' or not parsed.netloc or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
            raise ValueError('Use the P4 http:// origin without a path')
        self.url = url.rstrip('/')
        self.path = Path(state)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = self.path.with_name(self.path.name + '.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise TransferError('Another client owns this state file') from None
        self.timeout = timeout
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {'url': self.url, 'job': None}
        if self.state['url'] != self.url:
            self.lock.close()
            raise TransferError('State belongs to another endpoint')

    def close(self):
        self.lock.close()

    def save(self):
        temp = self.path.with_name(self.path.name + '.tmp')
        with temp.open('w') as f:
            json.dump(self.state, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        temp.replace(self.path)
        # Persist the replacement itself, once per job boundary, not UART chunk.
        fd = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def request(self, method='GET', suffix='', data=None, headers=None):
        request = urllib.request.Request(self.url + '/sd/fast' + suffix, data=data,
                                         headers=headers or {}, method=method)
        # No automatic POST retry: an exception can mean the P4 accepted it.
        return urllib.request.urlopen(request, timeout=self.timeout)

    def status(self):
        with self.request() as response:
            result = json.load(response)
        if result.get('protocol') != 1:
            raise TransferError('Unsupported P4 staged transfer service')
        return result

    def headers(self):
        job = self.state['job']
        return {'X-Extender-Job': f"{job['id']:08x}",
                'X-Extender-Boot': f"{job['boot']:08x}"}

    def begin(self, operation, remote, *, source=None, destination=None, activate=False):
        if self.state['job']:
            raise TransferError('Existing job retained; use resume/status before another transfer')
        if operation not in ('put', 'get') or (operation == 'put' and not activate) or (operation == 'get' and activate):
            raise ValueError('Staged put requires --activate; use sdcard.py for stage-only transactions')
        try:
            remote.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError('Agon paths must be ASCII') from None
        if (not remote.startswith('/') or len(remote) > (112 if operation == 'put' else 120)
                or any(ord(c) < 32 or ord(c) > 126 or c in ':\\*?' for c in remote)
                or any(p in ('', '.', '..') or p.endswith(('.', ' ')) for p in remote[1:].split('/'))):
            raise ValueError('Invalid absolute Agon file path')
        if operation == 'put' and Path(source).stat().st_size > QUOTA:
            raise ValueError('P4 staged transfers are limited to 32 MiB per file')
        payload = Path(source).read_bytes() if operation == 'put' else b''
        if len(payload) > QUOTA:
            raise ValueError('P4 staged transfers are limited to 32 MiB per file')
        if destination and Path(destination).exists():
            raise FileExistsError(destination)
        before = self.status()
        if before['phase'] != 0:
            raise TransferError('P4 has a retained job; inspect it before submitting another')
        self.state['job'] = {'id': secrets.randbelow(0xffffffff)+1, 'boot': before['boot'],
                             'operation': operation, 'remote': remote, 'activate': activate,
                             'size': len(payload), 'destination': str(Path(destination).absolute()) if destination else None,
                             'started': time.time(), 'result': None, 'delivered': False}
        self.save()  # durable BEFORE any possibly mutating HTTP submission
        headers = self.headers() | {'X-Extender-Operation': operation, 'X-Extender-Path': remote,
                                   'Content-Type': 'application/octet-stream'}
        if activate:
            headers['X-Extender-Activate'] = '1'
        started = time.monotonic()
        with self.request('POST', data=payload, headers=headers) as response:
            if response.status != 202:
                raise TransferError('Admission uncertain; use resume, never resubmit')
        self.state['job']['http_upload_s'] = time.monotonic() - started
        return self.resume()

    def resume(self):
        job = self.state['job']
        if not job:
            raise TransferError('No retained job')
        if job.get('result') and job.get('delivered'):
            self.release()
            return job['result']
        deadline = time.monotonic() + self.timeout
        while True:
            current = self.status()
            if current['boot'] != job['boot'] or current['id'] != job['id']:
                raise TransferError('P4 lost/replaced this job; state retained. No automatic resubmission.')
            if current['phase'] == 5:
                raise TransferError(f"P4 job failed: error={current['error']}, remote={current['remote_status']}, "
                                    f"filesystem={current['filesystem']}; stages retained")
            if current['phase'] == 4:
                if current['error'] or current['bytes'] != current['size']:
                    raise TransferError('Invalid terminal byte count; job retained')
                if job['operation'] == 'put' and current['size'] != job['size']:
                    raise TransferError('Upload length mismatch; job retained')
                job['result'] = current
                break
            if current['phase'] not in (1, 2, 3):
                raise TransferError('Unknown job state; retained without resubmission')
            if time.monotonic() >= deadline:
                raise TimeoutError('Job still pending; use resume to observe it. No reset or replay.')
            time.sleep(.25)  # observation only: P4 UART progress never waits here
        if job['operation'] == 'get':
            self.download(job)
        job['delivered'] = True
        job['finished'] = time.time()
        job['result']['host_elapsed_s'] = job['finished'] - job['started']
        if 'http_upload_s' in job:
            job['result']['http_upload_s'] = job['http_upload_s']
        self.save()  # retain confirmed completion BEFORE deleting P4 staging
        if job['operation'] == 'get':
            self.partial(job).unlink(missing_ok=True)
        result = job['result']
        self.release()
        return result

    def download(self, job):
        destination = Path(job['destination'])
        part = self.partial(job)
        if destination.exists():
            # A crash after publishing the hard link but before the completion
            # journal is recoverable without trusting an unrelated equal-size file.
            if part.exists() and os.path.samefile(part, destination) and part.stat().st_size == job['result']['size']:
                return
            raise FileExistsError(f'{destination}: preserve existing output; P4 job retained')
        # A deliberate resume may restart this job's own partial HTTP download.
        # UART/Agon transfer is already complete and is never repeated.
        mode = 'wb' if job.get('partial_owned') else 'xb'
        started = time.monotonic()
        with self.request(suffix='/data', headers=self.headers()) as response, part.open(mode) as out:
            if not job.get('partial_owned'):
                job['partial_owned'] = True
                self.save()
            received = 0
            while True:
                data = response.read(65536)
                if not data:
                    break
                received += len(data)
                if received > job['result']['size']:
                    raise TransferError('Oversized HTTP snapshot; P4 job retained')
                out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if received != job['result']['size']:
            raise TransferError('Truncated HTTP snapshot; resume can fetch the same P4 file')
        job['result']['http_download_s'] = time.monotonic() - started
        # link creates the destination without replacing a file created meanwhile.
        os.link(part, destination)
        fd = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def partial(job):
        destination = Path(job['destination'])
        return destination.with_name(destination.name + f".{job['id']:08x}.p4part")

    def release(self, *, discard=False):
        job = self.state['job']
        if not job:
            raise TransferError('No retained job')
        if not discard and not job.get('delivered'):
            raise TransferError('Delivery not confirmed; use resume, or explicit discard')
        current = self.status()
        # A lost DELETE response can be resolved from a previously durable
        # delivery receipt plus the same P4 boot now reporting idle.
        if current['boot'] == job['boot'] and current['phase'] == 0 and job.get('delivered'):
            pass
        elif current['boot'] != job['boot'] or current['id'] != job['id']:
            raise TransferError('Job identity changed; preserve local receipt')
        else:
            headers = self.headers()
            if discard:
                headers['X-Extender-Discard'] = '1'
            with self.request('DELETE', headers=headers) as response:
                response.read()
        self.state['last'] = job
        self.state['job'] = None
        self.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=300)
    commands = parser.add_subparsers(dest='command', required=True)
    put = commands.add_parser('put')
    put.add_argument('source', type=Path)
    put.add_argument('remote')
    put.add_argument('--activate', action='store_true', required=True,
                     help='Complete the file replacement; stage-only transactions use sdcard.py')
    get = commands.add_parser('get')
    get.add_argument('remote')
    get.add_argument('destination', type=Path)
    for name in ('status', 'resume', 'release', 'discard'):
        commands.add_parser(name)
    args = parser.parse_args()
    client = Client(args.url, args.state, args.timeout)
    try:
        if args.command == 'put':
            result = client.begin('put', args.remote, source=args.source, activate=args.activate)
        elif args.command == 'get':
            result = client.begin('get', args.remote, destination=args.destination)
        elif args.command == 'status':
            result = client.status()
        elif args.command == 'resume':
            result = client.resume()
        else:
            result = client.release(discard=args.command == 'discard')
        print(json.dumps(result, indent=2))
    finally:
        client.close()


if __name__ == '__main__':
    main()
