import dataclasses
import io
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from comms_accuracy import CrcError, Frame, Journal, ProtocolError, case_frames, inspect_journal
from comms_accuracy_peer import exact, receive, serve_client

PLAN = dict(run=0x12345678, case=7, tx=1, rx=2, pattern=5, seed=0xfedcba98, total=169)


class AccuracyTests(unittest.TestCase):
    def test_independent_native_wire_and_patterns(self):
        raw = subprocess.check_output([os.environ['COMMS_ACCURACY_BINARY'], '--dump'], timeout=5)
        stream, count = io.BytesIO(raw), 0
        for pattern in range(6):
            for tx in (1, 2):
                for rx in (1, 2):
                    for total in (0, 1, 17, 84):
                        n = struct.unpack('<I', stream.read(4))[0]
                        packet = stream.read(n)
                        expected = next(case_frames(dict(PLAN, tx=tx, rx=rx, pattern=pattern, total=total)))
                        self.assertEqual(packet, expected.encode())
                        self.assertEqual(Frame.decode(packet), expected)
                        self.assertTrue(Frame.decode(packet).pattern_matches())
                        count += 1
        self.assertEqual(count, 96)
        self.assertEqual(stream.read(), b'')

    def test_every_wire_bit_is_protected(self):
        frame = next(case_frames(PLAN))
        packet = frame.encode()
        for at in range(len(packet)):
            for bit in range(8):
                bad = bytearray(packet)
                bad[at] ^= 1 << bit
                with self.assertRaises(CrcError):
                    Frame.decode(bad)

    def test_crc_vectors_and_cross_block_offsets(self):
        self.assertEqual(zlib.crc32(b'123456789'), 0xcbf43926)
        fs = list(case_frames(PLAN))
        self.assertEqual([len(f.payload) for f in fs], [84, 84, 1])
        self.assertEqual([f.offset for f in fs], [0, 84, 168])
        self.assertTrue(all(f.pattern_matches() for f in fs))

    def test_bad_header_with_recomputed_crc(self):
        f = next(case_frames(PLAN))
        for at, value in ((0, 0), (4, 9), (5, 0), (7, 6), (32, 6), (33, 2), (37, 2), (38, 1)):
            bad = bytearray(f.encode())
            bad[at] = value
            bad[-4:] = struct.pack('<I', zlib.crc32(bad[:-4]))
            with self.assertRaises(ProtocolError):
                Frame.decode(bad)

    def test_short_extra_and_span_refusal(self):
        f = next(case_frames(PLAN))
        for bad in (f.encode()[:-1], f.encode() + b'x', b''):
            with self.assertRaises(ProtocolError):
                Frame.decode(bad)
        for changes in (dict(offset=169), dict(run=0), dict(run=True), dict(attempt=0), dict(total=17*1024*1024)):
            with self.assertRaises(ProtocolError):
                dataclasses.replace(f, **changes).encode()

    def test_corruption_with_good_crc_still_fails_oracle(self):
        f = next(case_frames(PLAN))
        changed = dataclasses.replace(f, payload=b'\xff' + f.payload[1:])
        self.assertFalse(Frame.decode(changed.encode()).pattern_matches())

    def test_journal_exclusive_and_pending_tail(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log'
            with Journal(path) as j:
                j.append(dict(event='run'))
                j.append(dict(event='intent', case=1, attempt=1))
                with self.assertRaises(FileExistsError):
                    Journal(path)
            result = inspect_journal(path)
            self.assertFalse(result['complete'])
            self.assertEqual(result['pending'], [(1, 1)])
            with path.open('ab') as f:
                f.write(b'{"partial":')
            self.assertTrue(inspect_journal(path)['incomplete_tail'])

    def test_short_write_and_sync_error_stop_logging(self):
        class Short:
            def __init__(self, wrapped): self.wrapped = wrapped
            def write(self, raw): return self.wrapped.write(raw[:5])
            def close(self): self.wrapped.close()
        with tempfile.TemporaryDirectory() as d:
            with Journal(Path(d) / 'short') as j:
                j.append(dict(event='run'))
                j.file = Short(j.file)
                with self.assertRaises(OSError): j.append(dict(event='intent', case=1, attempt=1))
                with self.assertRaises(OSError): j.append(dict(event='stop'))
                self.assertTrue(j.failed)
            self.assertTrue(inspect_journal(Path(d) / 'short')['incomplete_tail'])
            with Journal(Path(d) / 'sync') as j:
                with patch('comms_accuracy.os.fsync', side_effect=OSError('Injected sync failure')):
                    with self.assertRaises(OSError): j.append(dict(event='run'))
                self.assertTrue(j.failed)

    def test_journal_order_and_record_bound(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log'
            with Journal(path) as j:
                j.append(dict(event='run'))
                j.append(dict(event='outcome', case=1, attempt=1))
            with self.assertRaises(ProtocolError): inspect_journal(path)
            with Journal(Path(d) / 'big') as j:
                with self.assertRaises(ValueError): j.append(dict(event='x', value='x'*4096))

    def exercise_tcp(self, change=None, extra=False, split=False, truncate=False):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'journal'
            listener = socket.socket()
            listener.bind(('127.0.0.1', 0))
            listener.listen(1)
            errors, outcome = [], []
            def worker():
                with listener, Journal(path) as journal:
                    journal.append(dict(event='run'))
                    try:
                        listener.settimeout(3)
                        conn, _ = listener.accept()
                        with conn:
                            outcome.append(serve_client(conn, PLAN, journal, time.monotonic() + 4))
                    except (OSError, ValueError, EOFError) as error:
                        errors.append(error)
                    journal.append(dict(event='stop', passed=bool(outcome and outcome[0])))
            address = listener.getsockname()
            thread = threading.Thread(target=worker)
            thread.start()
            try:
                with socket.create_connection(address, timeout=3) as conn:
                    for index, f in enumerate(case_frames(PLAN)):
                        raw = f.encode()
                        if index == 0 and change:
                            raw = change(f)
                        packet = struct.pack('<I', len(raw)) + raw
                        if truncate:
                            conn.sendall(packet[:9]);conn.shutdown(socket.SHUT_WR)
                            break
                        if split:
                            for value in packet: conn.sendall(bytes([value]))
                        else:
                            conn.sendall(packet)
                        reply = Frame.decode(receive(conn, time.monotonic() + 3))
                        if change:
                            self.assertEqual(reply.kind, 3)
                            self.assertEqual(reply.flags, 0)  # Pi cannot prove hardware retirement.
                            break
                        self.assertEqual(reply, dataclasses.replace(f, kind=2, direction=1))
                    if extra:
                        conn.sendall(b'X')
                    if not truncate:
                        conn.shutdown(socket.SHUT_WR)
                    while conn.recv(128): pass
            finally:
                thread.join(6)
                self.assertFalse(thread.is_alive())
            return outcome, errors, inspect_journal(path)

    def test_real_tcp_fragmented_complete(self):
        outcome, errors, journal = self.exercise_tcp(split=True)
        self.assertEqual(outcome, [True]);self.assertFalse(errors);self.assertTrue(journal['complete'])

    def test_real_tcp_crc_refusal(self):
        def changed(f):
            packet = bytearray(f.encode());packet[40] ^= 1;return bytes(packet)
        outcome, errors, journal = self.exercise_tcp(change=changed)
        self.assertEqual(outcome, [False]);self.assertFalse(errors)
        self.assertEqual([r['reason'] for r in journal['records'] if r['event'] == 'error'], [1])

    def test_real_tcp_pattern_and_case_refusal(self):
        for change, reason in ((lambda f: dataclasses.replace(f, payload=b'\xff' + f.payload[1:]).encode(), 2),
                               (lambda f: dataclasses.replace(f, case=f.case+1).encode(), 3)):
            outcome, errors, journal = self.exercise_tcp(change=change)
            self.assertEqual(outcome, [False]);self.assertFalse(errors)
            self.assertEqual([r['reason'] for r in journal['records'] if r['event'] == 'error'], [reason])

    def test_real_tcp_extra_and_short_stop_incomplete(self):
        for kwargs in (dict(extra=True), dict(truncate=True)):
            outcome, errors, journal = self.exercise_tcp(**kwargs)
            self.assertFalse(outcome);self.assertTrue(errors);self.assertFalse(journal['complete'])

    def test_original_whole_deadline(self):
        a, b = socket.socketpair()
        with a, b:
            with self.assertRaises(TimeoutError): exact(a, 1, time.monotonic() - 1)


if __name__ == '__main__':
    unittest.main()
