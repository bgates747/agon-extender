"""Reject partial/wrong-run completion dumps before any performance claim."""
import unittest
from analyze_refresh_trace import analyze
class RefreshAnalysisTests(unittest.TestCase):
 def setUp(self):
  self.nonce='0123456789abcdef'
  self.text=f'NPTRACE begin {self.nonce} 2400 2400 1 0\n'+''.join(
   f'NPTRACE row {i} {(0xffffff00+i*16667)&0xffffffff} {(0xffffff00+i*16667+100)&0xffffffff}\n'
   for i in range(2400))+f'NPTRACE end {self.nonce}\n'
 def test_clock_wrap_and_latency(self):
  r=analyze(self.text,self.nonce,2400)
  self.assertAlmostEqual(r['completed_fps'],60,places=2)
  self.assertEqual(r['enqueue_to_completion']['mean_ms'],0.1)
 def test_corruption_rejected(self):
  for bad in (self.text.replace('row 5 ','row 4 '),self.text.replace('2400 2400 1 0','2400 2399 1 0'),self.text.replace('2400 2400 1 0','2400 2400 1 1'),self.text[:self.text.index('NPTRACE end')],self.text+self.text):
   with self.subTest(bad=bad[:80]),self.assertRaises(AssertionError):analyze(bad,self.nonce,2400)
  with self.assertRaises(AssertionError):analyze(self.text,'0000000000000000',2400)
if __name__=='__main__':unittest.main()
