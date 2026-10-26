"""Deterministic source integration: real localhost sockets, no bench or clocks set."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from controller_probe import NS, due_slot, pattern, run, summarize
from controller_udp import HEADER, OPEN, encode


@contextmanager
def peer(*, acknowledge=True, corrupt=False, active=False, tick_ms=0, drop=(), reverse=False):
    """Protocol reflector only. Its Python scheduling is NOT a physical P4 model."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('127.0.0.1', 0))
    udp.settimeout(.05)
    ended = threading.Event()
    state = dict(opened=0, closed=0, received=[], error=None)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def answer(self, body, status=200):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.answer(dict(protocol=1, instance='7b', active=active, udp_port=udp.getsockname()[1]))

        def do_POST(self):
            data = self.rfile.read(int(self.headers['Content-Length']))
            if self.path == '/controller/open':
                epoch, nonce, port, timeout, reserved = OPEN.unpack(data)
                if epoch != 123 or not nonce or not port or reserved or not 50 <= timeout <= 2000:
                    self.answer(dict(error='bad open'), 400)
                    return
                state['opened'] += 1
                self.answer(dict(session='1c8', timeout_ms=timeout))
            elif self.path == '/controller/close' and data == struct.pack('<QQ', 123, 456):
                state['closed'] += 1
                self.answer(dict(closed=True))
            else:
                self.answer(dict(error='bad request'), 400)

    def receive():
        try:
            while not ended.is_set():
                if tick_ms:
                    ended.wait(tick_ms/1000)
                packets = []
                try:
                    data, address = udp.recvfrom(256)
                    packets.append((data, address))
                    if reverse:
                        udp.settimeout(.02)
                        try:
                            packets.append(udp.recvfrom(256))
                        except socket.timeout:
                            pass
                        udp.settimeout(.05)
                except socket.timeout:
                    continue
                for data, address in reversed(packets):
                    magic, version, kind, length, epoch, token, seq, zero = HEADER.unpack_from(data)
                    if (magic, version, kind, length, epoch, token, zero) != (b'AGCP', 1, 1, 44, 123, 456, 0):
                        raise AssertionError('Unexpected STATE wire framing')
                    state['received'].append(data)
                    if acknowledge and seq not in drop:
                        ack = HEADER.pack(b'AGCP', 1, 2, 40, 123, 999 if corrupt else 456, seq, 0)
                        udp.sendto(ack+struct.pack('<II', seq, 0), address)
        except Exception as exc:
            state['error'] = str(exc)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    web = threading.Thread(target=server.serve_forever, kwargs=dict(poll_interval=.01), daemon=True)
    worker = threading.Thread(target=receive, daemon=True)
    web.start()
    worker.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', state
    finally:
        ended.set()
        server.shutdown()
        worker.join(timeout=1)
        udp.close()
        server.server_close()
        web.join(timeout=1)
        if state['error']:
            raise AssertionError(state['error'])


class ProbeTests(unittest.TestCase):
    def test_pattern_repeats_and_raw8_codec(self):
        for name, period in [('step', 120), ('triangle', 240)]:
            for slot in range(period):
                a, raw = pattern(slot, 120, name)
                b, repeated = pattern(slot+period, 120, name)
                self.assertEqual(raw, repeated)
                self.assertEqual(encode(123, 456, 1, a), encode(123, 456, 1, b))
                packet = encode(123, 456, 1, a)
                self.assertEqual(packet[36:38], b'\x01\x00')
                self.assertEqual(list(packet[38:44]), raw)
        self.assertNotEqual(pattern(0, 120)[1], pattern(60, 120)[1])

    def test_skip_missed_slots(self):
        self.assertEqual(due_slot(10*NS, 10*NS+45_000_000, 120, 1), 5)
        # A scheduler does not repeat slots, even if called immediately again.
        self.assertEqual(due_slot(10*NS, 10*NS+45_000_000, 120, 6), 6)

    def test_socket_timing_and_exact_wire_state(self):
        with tempfile.TemporaryDirectory() as temp, peer() as (url, p):
            result = run(url, Path(temp)/'run', seconds=.22)
            self.assertEqual(result['outcome'], 'pass')
            self.assertGreater(result['sent'], 5)
            self.assertEqual(result['sent'], result['acknowledged'])
            self.assertEqual((p['opened'], p['closed']), (1, 1))
            directory = Path(temp)/'run'
            events = [json.loads(line) for line in (directory/'events.jsonl').read_text().splitlines()]
            send = [e for e in events if e['event'] == 'send']
            wire = {HEADER.unpack_from(data)[6]: data for data in p['received']}
            for row in send:
                self.assertEqual(list(wire[row['sequence']][38:44]), row['axes_raw8'])
                self.assertGreaterEqual(row['send_ns'], row['deadline_ns'])
            self.assertEqual(json.loads((directory/'summary.json').read_text()), result)
            with self.assertRaises(FileExistsError):
                run(url, directory, seconds=.01)

    def test_no_takeover(self):
        with tempfile.TemporaryDirectory() as temp, peer(active=True) as (url, p):
            result = run(url, Path(temp)/'run', seconds=.1)
            self.assertEqual(result['outcome'], 'fail')
            self.assertIn('no takeover', result['error'])
            self.assertEqual((p['opened'], p['closed']), (0, 0))

    def test_slow_encoding_skips_deadlines_instead_of_replaying(self):
        first = True

        def slow_encode(*args, **kwargs):
            nonlocal first
            if first:
                first = False
                time.sleep(.04)
            return encode(*args, **kwargs)

        with tempfile.TemporaryDirectory() as temp, peer() as (url, _), \
                patch('controller_probe.encode', slow_encode):
            folder = Path(temp)/'run'
            result = run(url, folder, seconds=.12)
            self.assertEqual(result['outcome'], 'pass')
            self.assertGreaterEqual(result['skipped_slots'], 4)
            events = [json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
            slots = [e['slot'] for e in events if e['event'] == 'send']
            self.assertGreaterEqual(slots[1], 5)

    def test_timeout_closes_without_reconnect(self):
        with tempfile.TemporaryDirectory() as temp, peer(acknowledge=False) as (url, p):
            result = run(url, Path(temp)/'run', seconds=.3, timeout_ms=50)
            self.assertEqual(result['outcome'], 'fail')
            self.assertIn('No fresh', result['error'])
            self.assertEqual((p['opened'], p['closed']), (1, 1))
            self.assertLess(result['total_seconds'], 1)

    def test_wrong_session_ack_is_fault(self):
        with tempfile.TemporaryDirectory() as temp, peer(corrupt=True) as (url, p):
            result = run(url, Path(temp)/'run', seconds=.2)
            self.assertEqual(result['outcome'], 'fail')
            self.assertIn('ACK identity', result['error'])
            self.assertEqual(p['closed'], 1)

    def test_loss_reorder_and_final_drain(self):
        with tempfile.TemporaryDirectory() as temp, peer(drop=(1,), reverse=True) as (url, p):
            result = run(url, Path(temp)/'run', seconds=.15)
            self.assertEqual(result['outcome'], 'partial')
            self.assertEqual(result['unacknowledged'], 1)
            self.assertEqual(p['closed'], 1)

    def test_signal_stop_requests_close(self):
        with tempfile.TemporaryDirectory() as temp, peer() as (url, p):
            deadline = time.monotonic()+.08
            result = run(url, Path(temp)/'run', seconds=30, stop=lambda: time.monotonic()>=deadline)
            self.assertEqual(result['outcome'], 'aborted')
            self.assertEqual(p['closed'], 1)

    def test_invalid_configuration_has_no_effect(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'run'
            for kwargs in [dict(hz=0), dict(hz=120.5), dict(seconds=float('nan')),
                           dict(seconds=0), dict(timeout_ms=5), dict(name='noise')]:
                with self.assertRaises(ValueError):
                    run('http://127.0.0.1:1', path, **kwargs)
                self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
