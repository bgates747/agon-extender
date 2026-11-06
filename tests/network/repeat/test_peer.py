"""Actual peer byte protocol and cross-language matrix, no device/emulator."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('repeat_peer',ROOT/'tests/fixtures/network/repeat_peer.py')
peer=importlib.util.module_from_spec(spec);spec.loader.exec_module(peer)

class CountedServer:
    def __init__(self,sock):self.sock=sock;self.accepts=0
    def settimeout(self,value):self.sock.settimeout(value)
    def accept(self):self.accepts+=1;return self.sock.accept()

def exact(sock,n):
    data=bytearray()
    while len(data)<n:
        part=sock.recv(n-len(data))
        if not part:raise RuntimeError('Test client short reply')
        data.extend(part)
    return bytes(data)

class PeerTests(unittest.TestCase):
    def test_native_matrix_matches_peer_for_all176_records(self):
        raw=subprocess.check_output([os.environ['PROBE_REPEAT_MATRIX_DUMP']],timeout=3)
        at=0;coverage=0
        for s in range(4):
            for i in range(44):
                n=peer.SIZES[i%len(peer.SIZES)]
                self.assertEqual(raw[at:at+3],bytes((s,i,n)));at+=3
                data=raw[at:at+n];at+=n
                self.assertEqual(data,peer.payload(s,i,n))
                for value in data:coverage|=value
        self.assertEqual(at,len(raw));self.assertEqual(coverage,255)

    def run_case(self,fault=None):
        errors=[];returned=0
        with tempfile.TemporaryDirectory() as temp,socket.socket() as server:
            server.bind(('127.0.0.1',0));server.listen(1);counted=CountedServer(server)
            def worker():
                try:peer.serve(counted,Path(temp),seconds=5,progress=.3)
                except BaseException as exc:errors.append(exc)
            thread=threading.Thread(target=worker);thread.start()
            try:
                for s in range(4 if fault is None else 1):
                    with socket.create_connection(server.getsockname(),timeout=1) as client:
                        client.settimeout(1)
                        if fault=='short-header':client.sendall(b'\0\0');break
                        for i in range(44):
                            n=peer.SIZES[i%len(peer.SIZES)];data=peer.payload(s,i,n)
                            if fault=='length' and i==1:
                                client.sendall(struct.pack('<I',129));break
                            if fault=='data' and i==1:
                                client.sendall(struct.pack('<I',n)+bytes([data[0]^1]));break
                            if fault=='short-data' and i==2:
                                client.sendall(struct.pack('<I',n)+data[:1]);break
                            client.sendall(struct.pack('<I',n)+data)
                            self.assertEqual(struct.unpack('<I',exact(client,4))[0],n)
                            self.assertEqual(exact(client,n),data);returned+=1
                        if fault=='extra':client.sendall(b'!')
                thread.join(2)
                self.assertFalse(thread.is_alive(),'Peer must retire after its first failure')
            finally:
                server.close();thread.join(1)
            report=json.loads((Path(temp)/'run.json').read_text())
            self.assertEqual(report['passed'],fault is None)
            self.assertEqual(counted.accepts,4 if fault is None else 1)
            self.assertEqual(len(errors),0 if fault is None else 1)
            self.assertEqual(len(report['records']),returned)
            if fault:self.assertIn('first_error',report)
            else:self.assertEqual(report['closed_sessions'],4);self.assertEqual(returned,176)

    def test_four_positive_closed_sessions(self):self.run_case()
    def test_wrong_length_stops(self):self.run_case('length')
    def test_changed_byte_stops(self):self.run_case('data')
    def test_short_header_stops(self):self.run_case('short-header')
    def test_short_payload_stops(self):self.run_case('short-data')
    def test_extra_record_stops(self):self.run_case('extra')
    def test_original_whole_deadline_stops_without_client(self):
        with tempfile.TemporaryDirectory() as temp,socket.socket() as sock:
            sock.bind(('127.0.0.1',0));sock.listen(1)
            with self.assertRaises(TimeoutError):peer.serve(sock,Path(temp),seconds=.02,progress=1)
            report=json.loads((Path(temp)/'run.json').read_text())
            self.assertFalse(report['passed']);self.assertEqual(report['records'],[])

if __name__=='__main__':unittest.main()
