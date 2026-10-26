#!/usr/bin/env python3
"""Finite deterministic controller source. Measures Oryx send/ACK timing only.

Uses the existing admitted UDP protocol; no input device, firmware installation,
Agon commands, automatic takeover or reconnect. Logs are buffered during a run
and flushed/fsynced on close; that logging cost is included in host scheduling.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import secrets
import select
import signal
import socket
import struct
import time
from types import SimpleNamespace

from controller_udp import OPEN, InputFault, control, decode_ack, encode, endpoint

NS = 1_000_000_000


def pattern(slot, hz, name='step'):
    """Six repeatable raw8 channels, based on scheduled time, never wall time.

    Step switches every half second. Triangle traverses its range in one second.
    Triangle phases help reveal swapped axes; step alternates two banks.
    No buttons or hat edges.
    """
    if name == 'step':
        raw = [255 if ((slot * 2 // hz) + i) % 2 else 0 for i in range(6)]
    elif name == 'triangle':
        phase = slot % (2 * hz)
        raw = []
        for i in range(6):
            x = (phase + i * hz // 3) % (2 * hz)
            raw.append(min(x, 2 * hz - x) * 255 // hz)
    else:
        raise ValueError('Unknown pattern')
    values = {k: v * 257 - 32768 for k, v in zip((0, 1, 3, 4), raw[:4])}
    values.update({2: raw[4], 5: raw[5], 16: 0, 17: 0})
    return SimpleNamespace(values=values, pressed=set()), raw


def due_slot(start_ns, now_ns, hz, next_slot):
    """Latest scheduled slot: skip missed slots; never send catch-up bursts."""
    return max(next_slot, (now_ns - start_ns) * hz // NS)


def stats(values):
    if not values:
        return dict(count=0, min=None, median=None, p95=None, max=None)
    ordered = sorted(values)
    n = len(ordered)
    return dict(count=n, min=ordered[0], median=(ordered[(n-1)//2]+ordered[n//2])/2,
                p95=ordered[math.ceil(.95*n)-1], max=ordered[-1])


def summarize(events):
    sends = {e['sequence']: e for e in events if e['event'] == 'send'}
    acks = {}
    for event in events:
        if event['event'] == 'ack':
            acks.setdefault(event['sequence'], event)
    ordered = list(sends.values())
    intervals = [(b['send_ns']-a['send_ns'])/1e6 for a, b in zip(ordered, ordered[1:])]
    elapsed = (ordered[-1]['send_ns']-ordered[0]['send_ns'])/NS if len(ordered)>1 else 0
    return dict(sent=len(sends), acknowledged=len(acks), unacknowledged=len(sends)-len(acks),
                skipped_slots=sum(e['skipped'] for e in ordered),
                effective_hz=(len(ordered)-1)/elapsed if elapsed else None,
                send_interval_ms=stats(intervals),
                schedule_lateness_ms=stats([(e['send_ns']-e['deadline_ns'])/1e6 for e in ordered]),
                send_call_ms=stats([(e['send_done_ns']-e['send_ns'])/1e6 for e in ordered]),
                ack_round_trip_ms=stats([(e['receive_ns']-sends[k]['send_ns'])/1e6
                                         for k, e in acks.items()]),
                scope='Host pre-send to host post-recv ACK; not one-way or EMOS/display latency')


class Journal:
    def __init__(self, path):
        self.file = path.open('x', encoding='utf-8')
        self.events = []

    def put(self, kind, **fields):
        row = dict(event=kind, **fields)
        self.file.write(json.dumps(row, separators=(',', ':'))+'\n')
        self.events.append(row)

    def close(self):
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def run(url, output, *, hz=120, seconds=30, timeout_ms=250, name='step', stop=None):
    if isinstance(hz, bool) or not isinstance(hz, int) or not 1 <= hz <= 240:
        raise ValueError('Rate must be an integer 1..240 Hz')
    if not math.isfinite(seconds) or not 0 < seconds <= 3600:
        raise ValueError('Duration must be finite, positive and at most 3600 seconds')
    if not 50 <= timeout_ms <= 2000 or hz * timeout_ms < 2000:
        raise ValueError('Timeout must be 50..2000 ms and allow two publication periods')
    pattern(0, hz, name)  # Validate before creating evidence or admitting input.
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    journal = Journal(output/'events.jsonl')
    begin = time.monotonic_ns()
    stamp = datetime.now(timezone.utc).isoformat()
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (Path(__file__), Path(__file__).with_name('controller_udp.py'),
                         Path(__file__).with_name('controller_input.py'))}
    write_json(output/'run.json', dict(schema=1, status='experimental',
               started_utc=stamp, host=platform.node(), pid=os.getpid(), python=platform.python_version(),
               hz=hz, seconds=seconds, timeout_ms=timeout_ms, pattern=name, source_sha256=sources,
               clock='time.monotonic_ns', clock_resolution_seconds=time.get_clock_info('monotonic').resolution,
               clock_accuracy='uncalibrated; local clock only', endpoint=url, buttons='none',
               scope='Controller UDP source / ACK; no Agon app or display measurement'))
    udp = None
    base = instance = session = None
    error = None
    cancelled = False
    last_new_ack = 0
    sent = 0
    sends = {}
    acknowledged = set()
    sending_start = sending_end = None
    try:
        base, address = endpoint(url)
        info = control(base, '/controller/status')
        if info.get('protocol') != 1:
            raise InputFault('Receiver does not advertise controller protocol 1')
        if info.get('active'):
            raise InputFault('Controller source already active; no takeover attempted')
        instance = int(info['instance'], 16)
        if not 0 < instance < 2**64 or not 0 < info['udp_port'] < 65536:
            raise InputFault('Invalid controller receiver identity/port')
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(('0.0.0.0', 0))
        udp.connect((address, info['udp_port']))
        udp.setblocking(False)
        opened = control(base, '/controller/open', OPEN.pack(instance, secrets.randbits(64) or 1,
                         udp.getsockname()[1], timeout_ms, 0))
        session = int(opened['session'], 16)
        if not 0 < session < 2**64:
            raise InputFault('Invalid admitted controller session')
        journal.put('admitted', instance=instance, session=session, time_ns=time.monotonic_ns(),
                    udp_port=info['udp_port'])
        start = time.monotonic_ns()
        sending_start = start
        end = start + round(seconds * NS)
        last_fresh = start
        next_slot = 0
        drain_end = None
        while True:
            now = time.monotonic_ns()
            if stop and stop():
                cancelled = True
                break
            # Timestamp immediately after recv; Python dispatch/logging follows.
            for _ in range(256):
                try:
                    data = udp.recv(256)
                except BlockingIOError:
                    break
                received = time.monotonic_ns()
                packet, edge = decode_ack(data, instance, session)
                if packet not in sends or edge:
                    raise InputFault('ACK claims an unsent packet or axes-only transition')
                duplicate = packet in acknowledged
                journal.put('ack', sequence=packet, receive_ns=received, duplicate=duplicate)
                acknowledged.add(packet)
                if packet > last_new_ack:
                    last_new_ack = packet
                    last_fresh = received
            now = time.monotonic_ns()
            if now >= end:
                if drain_end is None:
                    drain_end = now + timeout_ms * 1_000_000
                    sending_end = now
                    journal.put('send_end', time_ns=now)
                if len(acknowledged) == sent or now >= drain_end:
                    break
                select.select([udp], [], [], min(.05, (drain_end-now)/NS))
                continue
            if now - last_fresh >= timeout_ms * 1_000_000:
                raise InputFault('No fresh receiver ACK within timeout; no reconnect')
            deadline = start + (next_slot * NS + hz - 1) // hz
            if now >= deadline:
                slot = due_slot(start, now, hz, next_slot)
                skipped = slot - next_slot
                deadline = start + (slot * NS + hz - 1) // hz
                state, raw = pattern(slot, hz, name)
                sent += 1
                data = encode(instance, session, sent, state)
                before = time.monotonic_ns()
                if udp.send(data) != len(data):
                    raise InputFault('Partial UDP send')
                after = time.monotonic_ns()
                sends[sent] = before
                # Encoding/send can itself cross a deadline. Do not replay
                # those slots on the following iteration either.
                next_slot = max(slot+1, (after-start)*hz//NS+1)
                journal.put('send', sequence=sent, slot=slot, deadline_ns=deadline, send_ns=before,
                            send_done_ns=after, skipped=skipped+next_slot-slot-1,
                            axes_raw8=raw, bytes=len(data))
            wake = min(start + (next_slot * NS + hz - 1) // hz, end,
                       last_fresh + timeout_ms * 1_000_000)
            select.select([udp], [], [], max(0, (wake-time.monotonic_ns())/NS))
    except (OSError, ValueError, KeyError, TypeError, InputFault) as exc:
        error = str(exc)
        journal.put('failure', time_ns=time.monotonic_ns(), error=error)
    finally:
        if udp is not None:
            udp.close()
        if session and base and instance:
            try:
                closed = control(base, '/controller/close', struct.pack('<QQ', instance, session))
                if closed.get('closed') is not True:
                    raise InputFault('Close response is unconfirmed')
                journal.put('closed', time_ns=time.monotonic_ns())
            except (OSError, ValueError, InputFault) as exc:
                error = error or 'Close unconfirmed; receiver timeout required: '+str(exc)
                journal.put('close_failure', time_ns=time.monotonic_ns(), error=str(exc))
        finish = time.monotonic_ns()
        result = summarize(journal.events)
        result.update(error=error, cancelled=cancelled, started_utc=stamp,
                      finished_utc=datetime.now(timezone.utc).isoformat(),
                      total_seconds=(finish-begin)/NS,
                      sending_seconds=((sending_end or finish)-sending_start)/NS if sending_start else 0,
                      outcome='fail' if error else 'aborted' if cancelled else 'pass')
        # Missing final ACKs are a measurement, not proof of a healthy receiver.
        if result['unacknowledged'] and not error and not cancelled:
            result.update(outcome='partial')
        journal.put('finished', time_ns=finish, outcome=result['outcome'])
        journal.close()
        write_json(output/'summary.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', required=True, type=Path, help='New evidence directory; never overwritten')
    parser.add_argument('--hz', type=int, default=120)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--timeout-ms', type=int, default=250)
    parser.add_argument('--pattern', choices=('step', 'triangle'), default='step')
    args = parser.parse_args()
    stopped = False

    def cancel(_signum, _frame):
        nonlocal stopped
        stopped = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, cancel)
    try:
        result = run(args.url, args.output, hz=args.hz, seconds=args.seconds,
                     timeout_ms=args.timeout_ms, name=args.pattern, stop=lambda: stopped)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    return 0 if result['outcome'] == 'pass' else 130 if result['outcome'] == 'aborted' else 1


if __name__ == '__main__':
    raise SystemExit(main())
