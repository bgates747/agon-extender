"""Device-free NET-009 serial framing and command boundaries."""
import io
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from modem_bw_protocol import UP, check, frame, pattern
from net009_pi_uart import command, read_frame, require_header_uart, write_all


class SerialFixture:
    def __init__(self, data=b'', short=False):
        self.data = data
        self.short = short
        self.in_waiting = 0

    def read(self, count):
        n = min(count, 7)
        data, self.data = self.data[:n], self.data[n:]
        return data

    def write(self, data):
        return len(data) - int(self.short)


class Net009(unittest.TestCase):
    def test_fragment_and_coalesced_next_frame(self):
        first, last = frame(1, pattern(1, UP)), frame(2)
        port, raw = SerialFixture(first + last), io.BytesIO()
        end = time.monotonic() + 1
        self.assertEqual(check(read_frame(port, end, raw), 1, UP)[1], pattern(1, UP))
        self.assertEqual(check(read_frame(port, end, raw), 2)[1], b'')
        self.assertEqual(raw.getvalue(), first + last)

    def test_corruption_remains_in_evidence(self):
        corrupt = frame(1, pattern(1, UP))[:-1] + b'\xff'
        raw = io.BytesIO()
        with self.assertRaisesRegex(ValueError, 'CRC'):
            check(read_frame(SerialFixture(corrupt), time.monotonic() + 1, raw), 1, UP)
        self.assertEqual(raw.getvalue(), corrupt)

    def test_truncation_is_not_a_frame(self):
        partial = frame(1, pattern(1, UP))[:150]
        raw = io.BytesIO()
        with self.assertRaises(TimeoutError):
            read_frame(SerialFixture(partial), time.monotonic() + .01, raw)
        self.assertEqual(raw.getvalue(), partial)

    def test_fragmented_response_and_refusal(self):
        self.assertIn(b'OK', command(SerialFixture(b'AT\r\r\nOK\r\n'), b'AT\r\n'))
        with self.assertRaises(RuntimeError):
            command(SerialFixture(b'\r\nERROR\r\n'), b'AT\r\n')

    def test_short_write_and_alias_refused(self):
        with self.assertRaises(IOError):
            write_all(SerialFixture(short=True), b'test')
        with self.assertRaises(ValueError):
            require_header_uart('/dev/serial0')


if __name__ == '__main__':
    unittest.main()
