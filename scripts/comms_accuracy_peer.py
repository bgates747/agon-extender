#!/usr/bin/env python3
"""Bounded COMMS-001 single-attempt Pi TCP peer; no UART/device ownership.

Read one trusted case plan and check every framed record before returning ACK.
NACK is a network diagnostic for a future P4 UART-control adapter. It never
claims physical retirement. This peer does not retry/reconnect or restart a case.
"""
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
import time
import zlib
from comms_accuracy import CrcError, Frame, Journal, ProtocolError, case_frames


def publish_ready(path, value):
    """Publish complete readiness atomically and never overwrite a prior file."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.comms-ready-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as file:
            json.dump(value, file)
            file.write('\n')
            file.flush()
            os.fsync(file.fileno())
        os.link(temporary, path)  # Exclusive atomic link, unlike replace().
    finally:
        Path(temporary).unlink()


def exact(sock, count, deadline):
    result = bytearray()
    while len(result) < count:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Original whole-peer deadline')
        sock.settimeout(min(remaining, 5))
        part = sock.recv(count - len(result))
        if not part:
            raise EOFError('Truncated TCP record')
        result.extend(part)
    return bytes(result)


def receive(sock, deadline):
    n = struct.unpack('<I', exact(sock, 4, deadline))[0]
    if not 44 <= n <= 128:
        raise ProtocolError('Unbounded/invalid TCP record length')
    return exact(sock, n, deadline)


def send(sock, frame, deadline):
    packet = frame.encode()
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Original whole-peer deadline')
    sock.settimeout(min(remaining, 5))
    sock.sendall(struct.pack('<I', len(packet)) + packet)


def serve_client(sock, plan, journal, deadline, chunk=84):
    journal.append(dict(event='intent', case=plan['case'], attempt=plan.get('attempt', 1),
                        monotonic_ns=time.monotonic_ns()))
    for expected in case_frames(plan, chunk):
        packet = receive(sock, deadline)
        status = 0
        try:
            got = Frame.decode(packet)
            if replace(got, payload=expected.payload) != expected:
                status = 3
            elif not got.pattern_matches():
                status = 2
        except CrcError:
            status = 1
        except ProtocolError:
            status = 3
        if status:
            report = replace(expected, kind=3, direction=1, status=status, flags=0,
                             payload=struct.pack('<II', zlib.crc32(expected.encode()[:-4]),
                                                 zlib.crc32(packet[:-4])))
            journal.append(dict(event='error', case=expected.case, attempt=expected.attempt,
                                sequence=expected.sequence, reason=status, packet_hex=packet.hex(),
                                uart_delivery_verified=False, owner_retired=False,
                                monotonic_ns=time.monotonic_ns()))
            send(sock, report, deadline)
            journal.append(dict(event='outcome', case=expected.case, attempt=expected.attempt,
                                passed=False, reason=status, monotonic_ns=time.monotonic_ns()))
            return False
        send(sock, replace(expected, kind=2, direction=1), deadline)
        journal.append(dict(event='record', case=expected.case, attempt=expected.attempt,
                            sequence=expected.sequence, bytes=len(expected.payload),
                            received_crc=struct.unpack('<I', packet[-4:])[0],
                            monotonic_ns=time.monotonic_ns()))
    # Require clean peer close, not merely enough expected bytes.
    sock.settimeout(min(5, max(.001, deadline - time.monotonic())))
    if sock.recv(1):
        raise ProtocolError('Extra bytes after complete trusted case')
    journal.append(dict(event='outcome', case=plan['case'], attempt=plan.get('attempt', 1),
                        passed=True, positive_tcp_close=True, monotonic_ns=time.monotonic_ns()))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--journal', required=True)
    parser.add_argument('--duration', type=float, default=60)
    parser.add_argument('--ready', help='Exclusive host readiness JSON; optional, no device operation')
    args = parser.parse_args()
    if not 0 < args.duration <= 3600 or not 0 <= args.port <= 65535:
        parser.error('Finite duration/valid port required')
    with open(args.plan) as file:
        plan = json.load(file)
    next(case_frames(plan))  # Reject invalid trusted plan before listening.
    deadline = time.monotonic() + args.duration
    with Journal(args.journal) as journal:
        journal.append(dict(event='run', schema='comms-accuracy-peer-r01', plan=plan,
                            monotonic_ns=time.monotonic_ns(), physical_uart_adapter=False))
        try:
            with socket.socket() as listener:
                listener.bind((args.bind, args.port))
                listener.listen(1)
                if args.ready:
                    publish_ready(args.ready, dict(schema='comms-accuracy-peer-ready-r01',
                                  endpoint=listener.getsockname(), monotonic_ns=time.monotonic_ns()))
                listener.settimeout(min(args.duration, 30))
                sock, _ = listener.accept()
                with sock:
                    passed = serve_client(sock, plan, journal, deadline)
            journal.append(dict(event='stop', passed=passed, monotonic_ns=time.monotonic_ns()))
            return 0 if passed else 1
        except (OSError, ValueError, EOFError) as error:
            if not journal.failed:
                journal.append(dict(event='stop', passed=False, error=repr(error),
                                    monotonic_ns=time.monotonic_ns()))
            raise


if __name__ == '__main__':
    raise SystemExit(main())
