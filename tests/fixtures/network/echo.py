#!/usr/bin/env python3
"""Finite generic echo peer for one explicitly admitted bench appliance.

No game server, firmware install, reset, runner or automatic application launch.
"""
import argparse
import datetime
import json
from pathlib import Path
import socket
import struct
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True, help='Explicit admitted Pi LAN IPv4')
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--sizes', default='0,1,56,128', help='Exactly four fixture lengths; parallel uses0,1,127,128')
    args = parser.parse_args()
    try:
        sizes=tuple(int(n) for n in args.sizes.split(','))
        if len(sizes)!=4 or any(n<0 or n>128 for n in sizes):raise ValueError()
    except ValueError:parser.error('sizes must be four integers in0..128')
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic_ns()
    report = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  clock='host monotonic ns, not synchronized with Agon', records=[], passed=False)
    def exact(peer, n):
        data = bytearray()
        while len(data) < n:
            chunk = peer.recv(n-len(data))
            if not chunk:
                raise RuntimeError('Peer closed mid-record')
            data.extend(chunk)
        return bytes(data)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((args.bind, args.port))
            server.listen(1)
            server.settimeout(60)
            print('Ready: one client, four records; no app invoked', flush=True)
            peer, _ = server.accept()
            with peer:
                peer.settimeout(5)
                for index, size in enumerate(sizes):
                    got = struct.unpack('<I', exact(peer, 4))[0]
                    if got != size:
                        raise RuntimeError('Unexpected record length')
                    payload = exact(peer, got)
                    if payload != bytes((j*37+index) & 255 for j in range(size)):
                        raise RuntimeError('Unexpected record bytes')
                    peer.sendall(struct.pack('<I', got)+payload)
                    report['records'].append(dict(index=index, bytes=got))
                # Keep TCP live until application RELEASE/lease close; do not
                # race the final echo with an unexplained forced EOF.
                peer.settimeout(5)
                if peer.recv(1):
                    raise RuntimeError('Unexpected fifth record')
        report['passed'] = True
    finally:
        report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['duration_ns'] = time.monotonic_ns()-start
        (args.output/'run.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
