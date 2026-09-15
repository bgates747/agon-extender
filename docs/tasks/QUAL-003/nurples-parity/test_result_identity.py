"""Reject stale runs and malformed NP04 results before comparing timings."""
import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('np_analyze',Path(__file__).with_name('analyze.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class IdentityTests(unittest.TestCase):
 def test_identity_and_clock_wrap(self):
  nonce=bytes(range(8));b=bytearray(b'NP04'+(600).to_bytes(3,'little')+bytes([0,0,1])+(600).to_bytes(3,'little')+bytes([12])+nonce+bytes(2))
  for i in range(600):b+=((0xffff00+2*i)&0xffffff).to_bytes(3,'little')+bytes(8)+bytes([3])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'result.bin';p.write_bytes(b)
   r=a.parse(p,'fenced-sw',nonce,600)
   self.assertEqual(r['completed_fps'],60);self.assertEqual(r['live_sprites_max'],3)
   self.assertEqual(r['provenance'],'nonce_verified')
   for n,v,c in [(bytes(8),'fenced-sw',600),(nonce,'fenced-hw',600),(nonce,'fenced-sw',2400),(None,'fenced-sw',600)]:
    with self.assertRaises(AssertionError):a.parse(p,v,n,c)
   for offset,value in [(7,1),(8,3),(9,3),(13,11),(22,1)]:
    bad=bytearray(b);bad[offset]=value;p.write_bytes(bad)
    with self.assertRaises(AssertionError):a.parse(p,'fenced-sw',nonce,600)
   p.write_bytes(b[:-1])
   with self.assertRaises(AssertionError):a.parse(p,'fenced-sw',nonce,600)
if __name__=='__main__':unittest.main()
