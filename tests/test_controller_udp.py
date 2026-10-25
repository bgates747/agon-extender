"""Python wire/sender versus the actual portable C++ P4 receiver; no hardware."""
import ctypes as c
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import random
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from controller_input import State, Axis, EV_KEY, EV_ABS, EV_SYN
from controller_udp import (encode,decode_ack,Transitions,InputFault,run,OPEN,
                            HEADER,MAX_PACKET,held_mask)


def state():
    axes={k:Axis(-32768,32767) for k in (0,1,3,4)}
    axes.update({k:Axis(0,255) for k in (2,5)})
    axes.update({k:Axis(-1,1) for k in (16,17)})
    values={k:128 for k in (0,1,3,4)}
    values.update({k:0 for k in (2,5,16,17)})
    return State(axes,values)


class NativeReceiver:
    def __init__(self,lib):self.lib=lib;self.ptr=lib.cr_new()
    def open(self,nonce=1,now=0,port=2,timeout=250,token=456):
        return self.lib.cr_open(self.ptr,1,port,timeout,nonce,now,token)
    def receive(self,data,now=1,port=2):
        out=c.create_string_buffer(40)
        count=self.lib.cr_receive(self.ptr,data,len(data),1,port,now,out)
        return out.raw if count==40 else count
    def field(self,k,now=1):return self.lib.cr_field(self.ptr,k,now)
    def drain(self):
        result=[];out=(c.c_uint*3)()
        while self.lib.cr_consume(self.ptr,out):result.append(tuple(out))
        return result
    def close(self):return self.lib.cr_close(self.ptr)
    def delete(self):self.lib.cr_delete(self.ptr)


class ReplayObserver:
    """Sub-tick press and release; uses the real State report semantics."""
    def __init__(self,selected):
        self.device=True;self.session='synthetic';self.state=state()
        self.on_frame=self.on_gap=None;self.record_error='';self.message='synthetic'
        self.n=0
    def poll(self):
        self.n+=1
        if self.n in (4,5):
            self.state.feed(EV_KEY,304,int(self.n==4),time.monotonic_ns())
            self.state.feed(EV_SYN,0,0,time.monotonic_ns())
            if self.on_frame:self.on_frame(self.state)
    def close(self):self.device=False


class WireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        library=Path(cls.temp.name)/'receiver.so'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',
                        '-I',str(ROOT/'vdp/video'),str(ROOT/'tests/controller/native.cpp'),'-o',str(library)],check=True)
        cls.lib=c.CDLL(str(library))
        cls.lib.cr_new.restype=c.c_void_p
        cls.lib.cr_delete.argtypes=[c.c_void_p]
        cls.lib.cr_open.argtypes=[c.c_void_p,c.c_uint,c.c_uint,c.c_uint,c.c_ulonglong,c.c_ulonglong,c.c_ulonglong]
        cls.lib.cr_receive.argtypes=[c.c_void_p,c.c_char_p,c.c_uint,c.c_uint,c.c_uint,c.c_ulonglong,c.c_void_p]
        cls.lib.cr_field.argtypes=[c.c_void_p,c.c_uint,c.c_ulonglong]
        cls.lib.cr_consume.argtypes=[c.c_void_p,c.c_void_p]
        cls.lib.cr_close.argtypes=[c.c_void_p]
        cls.lib.cr_link.argtypes=[c.c_void_p]
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):self.receiver=NativeReceiver(self.lib);self.receiver.open()
    def tearDown(self):self.receiver.delete()

    def test_raw8_exact_lattice_and_native_fallback(self):
        s=state();s.values.update({0:-32768,1:32767,2:255})
        data=encode(123,456,1,s)
        self.assertEqual(len(data),44)
        self.assertEqual(decode_ack(self.receiver.receive(data),123,456),(1,0))
        self.assertEqual(self.receiver.field(7),32768)
        self.assertEqual(self.receiver.field(8),255)
        s.values[0]=1234
        data=encode(123,456,2,s)
        self.assertEqual(len(data),48)
        self.receiver.receive(data)
        self.assertEqual(self.receiver.field(7),1234)

    def test_http_ipv4_and_mapped_peer_admission(self):
        executable=Path(self.temp.name)/'http-peer'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                        '-I',str(ROOT/'vdp/video'),str(ROOT/'tests/controller/http_peer.cpp'),
                        '-o',str(executable)],check=True)
        subprocess.run([str(executable)],check=True,timeout=5)

    def test_loss_duplicate_gap_reorder_and_tap_retention(self):
        s=state();q=Transitions(s)
        s.last_edges=[(304,True),(304,False)];q.report(s)
        lost=encode(123,456,1,s,q.batch())
        self.assertEqual(len(lost),60)
        # First transmission lost. Exact edges travel in new snapshot.
        packet=encode(123,456,2,s,q.batch())
        ack=self.receiver.receive(packet,now=10)
        self.assertEqual(decode_ack(ack,123,456),(2,2))
        self.assertEqual(self.receiver.receive(packet,now=11),ack)
        self.assertEqual(self.receiver.receive(lost,now=12),0)
        self.assertEqual(self.receiver.drain(),[(1,0,1),(2,0,0)])
        q.ack(2);self.assertFalse(q.pending)
        # Missing prefix does not block axis snapshots or generate false edges.
        s.values[0]=32767
        ack=self.receiver.receive(encode(123,456,3,s,[(4,0,0)]),now=13)
        self.assertEqual(decode_ack(ack,123,456),(3,2))
        self.assertEqual(self.receiver.field(7,13),32767)
        self.receiver.receive(encode(123,456,4,s,[(3,0,1),(4,0,0)]),now=14)
        self.assertEqual(self.receiver.drain(),[(3,0,1),(4,0,0)])

    def test_timeout_checks_before_late_packet_and_new_session(self):
        s=state()
        self.receiver.receive(encode(123,456,1,s),now=10)
        self.assertEqual(self.receiver.receive(encode(123,456,2,s),now=260),0)
        self.assertEqual(self.receiver.field(1,260),0)
        self.assertEqual(self.receiver.open(nonce=1,now=260),410)
        self.assertEqual(self.receiver.open(nonce=2,now=260,token=789),200)
        self.assertEqual(self.receiver.receive(encode(123,456,3,s),now=261),0)
        self.assertIsInstance(self.receiver.receive(encode(123,789,1,s),now=262),bytes)

    def test_duplicate_and_idempotent_open_do_not_refresh_lease(self):
        s=state();p=encode(123,456,1,s)
        self.receiver.receive(p,now=0)
        self.assertEqual(self.receiver.open(now=200),200)
        self.receiver.receive(p,now=249)
        self.assertEqual(self.receiver.field(0,250),0)

    def test_peer_epoch_and_malformed_packets_rejected(self):
        p=encode(123,456,1,state())
        self.assertEqual(self.receiver.receive(p,port=9),0)
        self.assertEqual(self.receiver.receive(encode(999,456,1,state())),0)
        for offset in (0,4,5,6,28,36,37):
            data=bytearray(p);data[offset]^=0xff
            self.assertEqual(self.receiver.receive(bytes(data)),-1)
        self.assertEqual(self.receiver.receive(p+b'\0'),-1)
        self.assertEqual(self.receiver.receive(p[:30]),-1)

    def test_source_age_link_and_busy_owner(self):
        self.assertEqual(self.receiver.open(nonce=99),409)
        p=bytearray(encode(123,456,1,state()));struct.pack_into('<H',p,34,51)
        self.assertEqual(self.receiver.receive(bytes(p)),0)
        self.lib.cr_link(self.receiver.ptr)
        self.assertEqual(self.receiver.receive(encode(123,456,1,state())),0)
        self.assertEqual(self.receiver.field(1),0)

    def test_bounded_receiver_and_sender_queues(self):
        s=state()
        for batch in range(8):
            edges=[(batch*16+i+1,0,int(i%2==0)) for i in range(16)]
            self.receiver.receive(encode(123,456,batch+1,s,edges),now=batch)
        self.assertEqual(self.receiver.field(4,8),128)
        fault=self.receiver.receive(encode(123,456,9,s,[(129,0,1)]),now=9)
        with self.assertRaisesRegex(InputFault,'reason 4'):decode_ack(fault,123,456)
        self.assertEqual(self.receiver.field(0,9),0)
        q=Transitions(s)
        for i in range(128):q.push(0,i%2)
        with self.assertRaises(InputFault):q.push(0,1)

    def test_many_short_edges_not_limited_by_ui_history(self):
        s=state();q=Transitions(s)
        for i in range(20):s.feed(EV_KEY,304,int(i%2==0),i)
        s.feed(EV_SYN,0,0,21);q.report(s)
        self.assertEqual(len(s.history),12)
        self.assertEqual(len(q.pending),20)
        s.last_edges=[];s.values[16]=-1;q.report(s)
        s.values[16]=1;q.report(s)
        self.assertEqual(list(q.pending)[-3:],[(21,11,1),(22,11,0),(23,12,1)])

    def test_bad_ack_cannot_discard_unsent_transitions(self):
        q=Transitions(state());q.push(0,1)
        with self.assertRaises(InputFault):q.ack(1)
        q.batch();q.ack(1);self.assertFalse(q.pending)
        ack=self.receiver.receive(encode(123,456,1,state()))
        with self.assertRaises(InputFault):decode_ack(ack,123,999)

    def test_socket_sender_retries_tap_after_loss(self):
        self.loopback(drop_tap=True,acknowledge=True)

    def test_socket_sender_stops_on_missing_acks(self):
        self.loopback(drop_tap=False,acknowledge=False)

    def loopback(self,drop_tap,acknowledge):
        native=NativeReceiver(self.lib);guard=threading.Lock();collected=[]
        udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);udp.bind(('127.0.0.1',0));udp.settimeout(.01)
        stop=threading.Event();dropped=[]
        now=lambda:int(time.monotonic()*1000)
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def reply(self,code,data):
                b=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
            def do_GET(self):self.reply(200,dict(instance='000000000000007b',udp_port=udp.getsockname()[1]))
            def do_POST(self):
                data=self.rfile.read(int(self.headers['Content-Length']))
                with guard:
                    if self.path.endswith('/open'):
                        epoch,nonce,port,timeout,reserved=OPEN.unpack(data)
                        code=native.open(nonce=nonce,now=now(),port=port,timeout=timeout)
                        self.reply(code,dict(session='00000000000001c8'))
                    else:native.close();self.reply(200,dict(closed=True))
        http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        http_thread=threading.Thread(target=http.serve_forever,daemon=True);http_thread.start()
        def worker():
            while not stop.is_set():
                try:data,peer=udp.recvfrom(MAX_PACKET+1)
                except socket.timeout:continue
                if drop_tap and data[37] and not dropped:dropped.append(True);continue
                with guard:
                    ack=native.receive(data,now=now(),port=peer[1]);collected.extend(native.drain())
                if acknowledge and isinstance(ack,bytes):udp.sendto(ack,peer)
        thread=threading.Thread(target=worker,daemon=True);thread.start()
        try:
            with patch('controller_udp.Observer',ReplayObserver),redirect_stdout(io.StringIO()):
                result=run(f'http://127.0.0.1:{http.server_port}',seconds=.25,timeout_ms=100)
            if acknowledge:
                self.assertIsNone(result['error'])
                self.assertEqual(collected,[(1,0,1),(2,0,0)])
                self.assertTrue(dropped)
            else:self.assertIn('No fresh',result['error'])
        finally:
            stop.set();thread.join(1);udp.close();http.shutdown();http.server_close();http_thread.join(1);native.delete()

if __name__=='__main__':unittest.main()
