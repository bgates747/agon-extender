"""Exercise acquisition failures without involving a P4 or serial port."""
import importlib.util
import json
from pathlib import Path
import socket
import unittest

spec = importlib.util.spec_from_file_location('recorder', Path(__file__).parents[1]/'scripts/record.py')
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


class Reply:
    status = 200
    def __init__(self, body): self.body = body
    def read(self, size): return self.body[:size]


class Connection:
    def __init__(self, body=None, error=None):
        self.body, self.error, self.closed = body, error, False
    def request(self, *args):
        assert args == ('GET', '/diagnostics/frame-timing')
        if self.error: raise self.error
    def getresponse(self): return Reply(self.body)
    def close(self): self.closed = True


class AcquisitionTests(unittest.TestCase):
    def test_preserves_raw_response_and_connection(self):
        body = json.dumps({'schema': 1, 'phases': [{'name': name} for name in (
            'frame', 'queue', 'sprites', 'snapshot', 'suspend', 'parser',
            'tx_enqueue', 'tx_complete')]}).encode()
        c = Connection(body); result = recorder.fetch(c)
        self.assertTrue(result['valid']); self.assertFalse(c.closed)
        self.assertEqual(result['body'], body.decode())
        self.assertGreaterEqual(result['request_duration_ns'], 0)

    def test_failures_close_connection_and_remain_records(self):
        for c in (Connection(error=socket.timeout('timed out')),
                  Connection(b'not json'), Connection(b'{"schema":2}'),
                  Connection(b'[]'), Connection(b'{"schema":1,"phases":[null]}'),
                  Connection(b'x'*65537)):
            with self.subTest(body=c.body[:30] if c.body else None):
                result = recorder.fetch(c)
                self.assertFalse(result['valid']); self.assertTrue(c.closed)
                self.assertIn('error', result); self.assertIn('host_at', result)
                self.assertGreaterEqual(result['request_duration_ns'], 0)


if __name__ == '__main__': unittest.main()
