"""Host client against the real session engine, including an accepted lost reply."""
import ctypes as C
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from keyboard import Client,KeyboardError,text_events,packet

class KeyboardClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.path=Path(cls.tmp.name)
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',
                        '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/remote_keyboard_peer.cpp'),
                        '-o',str(cls.path/'peer.so')],check=True)
        cls.lib=C.CDLL(str(cls.path/'peer.so'))
        cls.lib.key_post.argtypes=[C.c_char_p,C.c_uint,C.c_uint]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_all_printable_mapping_and_prevalidation(self):
        # Exhaustive printable ASCII, both layouts, through the real C++ map.
        for locale in (0,1):
            self.lib.key_begin(42);self.lib.key_admit(locale)
            data=packet(1,43,77,1);self.assertEqual(self.lib.key_post(data,len(data),0),200)
            text=''.join(chr(i) for i in range(32,127))
            events=text_events(text,locale);out=[];seq=1;now=0;buf=C.create_string_buffer(6)
            for offset in range(0,len(events),96):
                seq+=1;data=packet(2,43,77,seq,events[offset:offset+96]);self.assertEqual(self.lib.key_post(data,len(data),now),200)
                for _ in events[offset:offset+96]:
                    self.assertEqual(self.lib.key_take(buf,now),6);now+=20
                    if buf.raw[5] and buf.raw[2]:out.append(chr(buf.raw[2]))
            self.assertEqual(''.join(out),text)
        with self.assertRaises(ValueError):text_events('run\n🎹',1)

    def test_lost_reply_no_duplicate_command_and_stale_session(self):
        lock=threading.RLock();self.lib.key_begin(800);self.lib.key_admit(1)
        lib=self.lib;started=time.monotonic();observed=[];stop=threading.Event();lost=[]
        def now():return int((time.monotonic()-started)*1000)
        def status():
            b=C.create_string_buffer(450);lib.key_status(b,450,now());return b.value
        class HTTP(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                with lock:b=status()
                self.send_response(200);self.end_headers();self.wfile.write(b)
            def do_POST(self):
                data=self.rfile.read(int(self.headers['Content-Length']))
                with lock:code=lib.key_post(data,len(data),now());b=status()
                if code==200 and data[3]==2 and not lost:
                    lost.append(data);self.close_connection=True;return
                self.send_response(code);self.end_headers();self.wfile.write(b)
        server=ThreadingHTTPServer(('127.0.0.1',0),HTTP)
        def pump():
            while not stop.is_set():
                b=C.create_string_buffer(6)
                with lock:
                    if lib.key_take(b,now()):observed.append(b.raw)
                time.sleep(.003)
        threads=[threading.Thread(target=server.serve_forever),threading.Thread(target=pump)]
        for t in threads:t.start()
        c=Client(f'http://127.0.0.1:{server.server_port}',self.path/'client.json')
        try:
            c.open();c.send(text_events('run\n',1));c.cancel()
            self.assertEqual(bytes(p[2] for p in observed if p[5] and p[2]),b'run\r')
            self.assertEqual(len(lost),1)
            c.open();c.send([(4,1)])
            with lock:lib.key_physical(5,1)
            with self.assertRaises(KeyboardError):c.wait()
            time.sleep(.05)
            self.assertEqual(observed[-1][5],0)
            c.cancel()
            with lock:lib.key_physical(5,0)
            c.open()
            with lock:lib.key_admit(0)
            with self.assertRaises(KeyboardError):c.send(text_events('x',1))
            self.assertTrue(c.state['pending'])
        finally:
            c.lock.close();stop.set();server.shutdown();server.server_close()
            for t in threads:t.join()

if __name__=='__main__':unittest.main()
