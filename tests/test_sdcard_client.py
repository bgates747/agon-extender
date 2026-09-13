import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sdcard',ROOT/'scripts/sdcard.py')
sd=importlib.util.module_from_spec(spec);spec.loader.exec_module(sd)

class ClientTests(unittest.TestCase):
    def test_uncertain_request_is_durable_and_retried_exactly(self):
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)/'state.json';c=sd.Client('http://fixture',state)
            def lost(request):raise TimeoutError('lost response')
            c.exchange=lost
            with self.assertRaises(TimeoutError):c.rpc(6,b'write payload')
            pending=json.loads(state.read_text())['pending']
            self.assertTrue(pending);self.assertEqual(c.state['sequence'],0)
            def recovered(request):
                self.assertEqual(request.hex(),pending);return 0,b'result'
            c.exchange=recovered
            self.assertEqual(c.resolve(),b'result')
            self.assertEqual(c.state['sequence'],1);self.assertIsNone(c.state['pending'])
            c.lock.close()
    def test_concurrent_state_owner_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)/'state.json';a=sd.Client('http://fixture',state)
            with self.assertRaises(sd.RemoteError):sd.Client('http://fixture',state)
            a.lock.close()
    def test_bad_response_identity_crc_and_size(self):
        request=sd.record(17,1,4,b'')
        h=sd.HEADER.pack(b'SD',1,2,17,1,4,0,3);reply=h+struct.pack('<I',zlib.crc32(h+b'abc'))+b'abc'
        self.assertEqual(sd.response(reply,request),(0,b'abc'))
        for bad in (reply[:-1],reply+b'a',reply[:20]+b'abd'):
            with self.assertRaises(sd.RemoteError):sd.response(bad,request)
        with self.assertRaises(sd.RemoteError):sd.response(reply,sd.record(18,1,4))
    def test_busy_hello_does_not_advance_session(self):
        with tempfile.TemporaryDirectory() as temp:
            c=sd.Client('http://fixture',Path(temp)/'state.json');c.exchange=lambda p:(3,b'')
            with self.assertRaises(sd.RemoteError):c.rpc(1)
            self.assertEqual(c.state['sequence'],0);self.assertTrue(c.state['pending']);c.lock.close()
    def test_long_write_path_rejected_before_request(self):
        with tempfile.TemporaryDirectory() as temp:
            c=sd.Client('http://fixture',Path(temp)/'state.json')
            with self.assertRaises(ValueError):c.upload('/'+('a'*112),b'')
            self.assertIsNone(c.state['pending']);c.lock.close()

if __name__=='__main__':unittest.main()
