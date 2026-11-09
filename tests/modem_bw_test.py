"""Test the actual codec/duplex peer, including faults and independent CRC vectors."""
from pathlib import Path
import os,socket,struct,subprocess,sys,tempfile,threading,time,unittest,zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from modem_bw_protocol import *
from modem_bw_peer import Peer
from modem_bw import evaluate
class Protocol(unittest.TestCase):
 def test_codec_faults(self):
  self.assertEqual(zlib.crc32(b'123456789'),0xcbf43926)
  b=frame(7,pattern(7,UP));self.assertEqual(check(b,7,UP),(7,pattern(7,UP)))
  for i in [0,5,9,13,16,500,1039]:
   broken=bytearray(b);broken[i]^=1
   with self.assertRaises(ValueError):check(broken,7,UP)
  with self.assertRaises(ValueError):check(b,8,UP)
  with self.assertRaises(ValueError):check(b[:-1],7,UP)
 def test_native_bytes(self):
  exe=Path(os.environ.get('NET008_NATIVE_CODEC','/tmp/net008-no-native-codec'))
  if not exe.exists():self.skipTest('Native codec binary supplied by compiler tranche')
  data=bytes.fromhex(subprocess.check_output([str(exe)],text=True).strip());self.assertEqual(data,frame(7,pattern(7,UP)))
 def test_acceptance_refuses_false_pass(self):
  n=dict(pass_=True,cleanup=True,uart_retired=True,uart_errors=0,crc_errors=0,frame_errors=0,tx_frames=10,rx_frames=10,tx_bytes=10240,rx_bytes=10240,rx_elapsed_us=61000000)
  n['pass']=n.pop('pass_');p=dict(tx_frames=10,rx_frames=10,tx_bytes=10240,rx_bytes=10240,rx_elapsed_seconds=61);p['pass']=True
  self.assertTrue(evaluate(n,p,60)['pass_case'])
  for field,value in [('rx_frames',9),('rx_bytes',10000),('uart_errors',1),('crc_errors',1),('rx_elapsed_us',59000000)]:
   bad=dict(n);bad[field]=value
   with self.assertRaises(ValueError):evaluate(bad,p,60)
 def test_actual_duplex_peer(self):
  with tempfile.TemporaryDirectory() as tmp:
   peer=Peer('127.0.0.1',Path(tmp)/'peer',17,115200,100)
   with socket.create_connection(('127.0.0.1',peer.port),timeout=3) as sock:
    sock.settimeout(3);sock.sendall(frame(0,struct.pack('<4I',17,115200,100,PAYLOAD)));self.assertEqual(check(receive(sock),0),(0,b'GO'))
    def tx():
     for seq in range(1,21):sock.sendall(frame(seq,pattern(seq,UP)))
     sock.sendall(frame(21))
    t=threading.Thread(target=tx);t.start();seq=1
    while True:
     _,data=check(receive(sock),seq,DOWN);seq+=1
     if not data:break
    t.join();self.assertTrue(peer.finished.wait(3));self.assertTrue(peer.result['pass']);self.assertEqual(peer.result['rx_frames'],20);peer.close()
if __name__=='__main__':unittest.main()
