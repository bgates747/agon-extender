#!/usr/bin/env python3
"""Read P4 frame timing for one bounded manual game reproduction; no resets."""
import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import select
import sys
import time
from urllib.parse import urlsplit


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(connection):
    start = time.monotonic_ns()
    record = {'kind': 'sample', 'host_at': stamp(), 'host_monotonic_ns': start}
    try:
        connection.request('GET', '/diagnostics/frame-timing')
        response = connection.getresponse()
        body = response.read(65537)
        record.update(status=response.status, body=body.decode('utf-8', errors='replace'))
        if len(body) > 65536:
            raise ValueError('response exceeds bounded diagnostic size')
        parsed = json.loads(body)
        if response.status != 200 or not isinstance(parsed, dict) or parsed.get('schema') != 1:
            raise ValueError('unexpected HTTP status or timing schema')
        phases = parsed.get('phases', [])
        if [p['name'] for p in phases] != [
                'frame', 'queue', 'sprites', 'snapshot', 'suspend', 'parser',
                'tx_enqueue', 'tx_complete']:
            raise ValueError('unexpected phase set')
        record['valid'] = True
    except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException) as error:
        record.update(valid=False, error=str(error))
        connection.close()
    record['request_duration_ns'] = time.monotonic_ns() - start
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True,
                        help='ignored local endpoint and exact deployment binding')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    url = urlsplit(config['base_url'])
    if url.scheme != 'http' or not url.hostname or url.path not in ('', '/'):
        parser.error('expected a bare local HTTP origin')
    # Verify every local binding file before recording. The endpoint itself
    # deliberately exposes no mutable identity command; the verified deployment
    # receipt binds this observation to the image installed by the bench tool.
    for item in config['binding_files']:
        if sha(Path(item['path'])) != item['sha256']:
            parser.error('deployment binding file changed: '+item['path'])
    connection = http.client.HTTPConnection(url.hostname, url.port or 80, timeout=2)
    check = fetch(connection)
    if not check.get('valid'):
        connection.close()
        raise SystemExit('P4 timing endpoint is not ready: '+check.get('error', 'unknown response'))
    print('Keep browser video connected. The recorder does not reset either board.')
    print('After starting, reset Agon and run Nurples in ExCom with joystick disabled.')
    print('During capture: Enter marks a hang; q then Enter finishes. Five-minute limit.')
    input('Press Enter to start recording: ')
    run = datetime.now(timezone.utc).strftime('AUDIT-006-%Y-%m-%d-%H-%M-%SZ')
    folder = Path(config['output_root'])/run
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'binding.json').write_text(json.dumps(config, indent=2)+'\n')
    deadline = time.monotonic()+300
    next_sample = time.monotonic()
    samples = failed = markers = 0
    reason = 'five-minute limit'
    with (folder/'records.jsonl').open('x') as out:
        def write(record):
            out.write(json.dumps(record, separators=(',', ':'))+'\n')
            out.flush()
            os.fsync(out.fileno())
        write({'kind': 'start', 'host_at': stamp(), 'run_id': run,
               'interval_seconds': 1, 'http_timeout_seconds': 2,
               'limit_seconds': 300, 'preflight': check})
        print('Recording. Start the game when ready.')
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([sys.stdin], [], [], max(0, min(
                    next_sample-time.monotonic(), deadline-time.monotonic())))
                if ready:
                    line = sys.stdin.readline()
                    if not line or line.strip().lower() == 'q':
                        reason = 'operator finished'; break
                    markers += 1
                    write({'kind': 'operator_marker', 'host_at': stamp(),
                           'host_monotonic_ns': time.monotonic_ns(),
                           'note': line.strip() or 'hang noticed'})
                    print('Hang marker saved.' if not line.strip() else 'Note saved.')
                if time.monotonic() >= next_sample:
                    sample = fetch(connection); write(sample)
                    samples += 1; failed += not sample.get('valid', False)
                    # Never burst requests to catch up after an HTTP stall.
                    next_sample = time.monotonic()+1
        except KeyboardInterrupt:
            reason = 'operator interrupt'
        finally:
            connection.close()
            write({'kind': 'end', 'host_at': stamp(), 'reason': reason,
                   'samples': samples, 'failed_requests': failed, 'markers': markers})
    files = {p.name: sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
    (folder/'checksums.json').write_text(json.dumps(files, indent=2)+'\n')
    print(f'Saved {samples} timing samples; {failed} failed requests; {markers} markers.')
    print('Evidence: '+str(folder))
    print('HTTP failures alone do not identify the cause of a game hang.')


if __name__ == '__main__':
    main()
