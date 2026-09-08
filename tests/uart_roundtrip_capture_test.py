"""A request PASS alone must never imply an acknowledged round trip."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('roundtrip', ROOT / 'scripts/capture_uart_roundtrip.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
BUILD = 'uart-roundtrip-probe-r01-b2026-09-08-00-00-00Z'
PASS = ('UART FORWARD PASS received=18 expected=18 '
        'hex=454D4F53205541525431202D3E2050340D0A reason=none build=' + BUILD + '\r\n').encode()
ACK = ('UART RETURN SENT count=5 hex=41434B0D0A build=' + BUILD + '\r\n').encode()


class RoundtripCaptureTests(unittest.TestCase):
    def test_complete_reply_and_request_are_required(self):
        self.assertTrue(capture.verdict(ACK + PASS + PASS, BUILD)[0])
        for log in (PASS, ACK, b'', PASS + ACK[:-1]):
            self.assertFalse(capture.verdict(log, BUILD)[0])

    def test_wrong_or_duplicate_reply_is_rejected(self):
        for bad in (ACK.replace(b'count=5', b'count=4'),
                    ACK.replace(b'4143', b'0043'),
                    ACK.replace(b'r01-b', b'r02-b'), ACK + ACK,
                    ACK + b'UART RETURN SENT malformed\n'):
            self.assertFalse(capture.verdict(PASS + bad, BUILD)[0])

    def test_later_failure_or_restart_invalidates_ack(self):
        for bad in (b'UART FORWARD FAIL\n', b'UART event type=3\n',
                    b'UART FORWARD RECEIVER ' + BUILD.encode() + b'\n'):
            self.assertFalse(capture.verdict(PASS + ACK + bad, BUILD)[0])

    def test_operator_cue_still_requires_empty_wait(self):
        wait = ('UART FORWARD WAIT received=0 expected=18 hex= reason=none build=' + BUILD + '\r\n').encode()
        self.assertTrue(capture.receiver_ready(wait, BUILD))
        self.assertFalse(capture.receiver_ready(wait[:-1], BUILD))
        with self.assertRaises(RuntimeError):
            capture.receiver_ready(PASS, BUILD)


if __name__ == '__main__':
    unittest.main()
