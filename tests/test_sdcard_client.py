import ctypes as C
import contextlib
import io
import subprocess
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

class RealEngineUploadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory();root=ROOT.parent/'agon-emos'
        lib=Path(cls.build.name)/'sd.so'
        subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror',
            '-Wno-misleading-indentation','-fsanitize=undefined','-fPIC','-shared',
            '-I'+str(root/'tests/sdserve_host'),str(root/'projects/sdserve/src/service.c'),
            str(root/'tests/sdserve_host/fs.c'),'-o',str(lib)],check=True)
        cls.lib=C.CDLL(str(lib))
        cls.lib.service_request.argtypes=[C.c_char_p,C.c_uint,C.c_void_p]
    @classmethod
    def tearDownClass(cls):cls.build.cleanup()
    def exercise(self,listener_fast,client_fast,size=4096):
        with tempfile.TemporaryDirectory() as temp:
            disk=Path(temp);(disk/'test').mkdir()
            self.lib.fs_root(str(disk).encode())
            self.assertEqual(self.lib.service_init_mode(b'/test',101,listener_fast),1)
            c=sd.Client('http://fixture',disk/'state.json');ops=[]
            def exchange(request):
                ops.append(request[12]);out=C.create_string_buffer(240)
                n=self.lib.service_request(request,len(request),out)
                return sd.response(out.raw[:n],request)
            c.exchange=exchange;data=bytes(i%256 for i in range(size));output=io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    if listener_fast!=client_fast:
                        with self.assertRaisesRegex(sd.RemoteError,'mode mismatch'):
                            c.upload('/test/game.bin',data,True,fast=client_fast)
                        self.assertEqual(ops,[1]);self.assertEqual(list((disk/'test').iterdir()),[])
                        return
                    c.upload('/test/game.bin',data,True,fast=client_fast)
                self.assertEqual((disk/'test/game.bin').read_bytes(),data)
                self.assertEqual(self.lib.fs_read_bytes(),20+(0 if client_fast else 4*size))
                self.assertEqual(ops.count(4),0 if client_fast else 2*max(1,(size+215)//216))
                if client_fast:self.assertNotIn('SHA256',output.getvalue())
                else:self.assertIn('Verified stage SHA256',output.getvalue())
            finally:c.lock.close();self.lib.service_stop()
    def test_readbacks_omitted_only_when_both_ends_opt_in(self):
        for fast in (False,True):
            for size in (0,213,4096):
                with self.subTest(fast=fast,size=size):self.exercise(fast,fast,size)
    def test_mismatch_refused_before_begin(self):
        for fast in (False,True):self.exercise(fast,not fast)

if __name__=='__main__':unittest.main()
