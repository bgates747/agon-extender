"""Synthetic private framing: no real keyring, modem or bench access."""
import importlib.util,unittest,zlib
from pathlib import Path
spec=importlib.util.spec_from_file_location('modem_join',Path(__file__).resolve().parents[1]/'scripts/modem_join.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def packet(ssid=b'fake-network',password=b'fake-password'):
 data=bytearray(b'MWJ1'+bytes([len(ssid),len(password)])+ssid+password);data.extend(zlib.crc32(data).to_bytes(4,'little'));return data
class PrivateFraming(unittest.TestCase):
 def test_exact_private_wire(self):
  p=packet();self.assertEqual(m.wire_packet(p),bytes([12,13])+b'fake-networkfake-password');m.wipe(p);self.assertFalse(any(p))
 def test_corrupt_crc(self):
  p=packet();p[-1]^=1
  with self.assertRaisesRegex(ValueError,'checksum'):m.wire_packet(p)
 def test_lengths_and_controls(self):
  for p in [packet(b''),packet(b'a'*33),packet(b'a',b'b'*65),packet(b'bad\n'),packet(b'a',b'\x80')]:
   with self.assertRaises(ValueError):m.wire_packet(p)
 def test_empty_password(self):self.assertEqual(m.wire_packet(packet(b'x',b'')),b'\x01\x00x')
if __name__=='__main__':unittest.main()
