import unittest
from analyze_native_wait import read

class NativeAnalysis(unittest.TestCase):
 def fixture(self):
  n='0123456789abcdef';count=122
  text=f'NPTRACE begin {n} {count} {count} 1 0\n'
  text+=''.join(f'NPTRACE row {i} {i*16667} {i*16667+100}\n' for i in range(count))
  text+=f'NPTRACE end {n}\nNPNATIVE begin {n} {count} 0\n'
  text+=''.join(f'NPNATIVE row {i} 300 200 2 400\n' for i in range(count))
  return n,text+f'NPNATIVE end {n}\n'
 def test_valid(self):
  n,t=self.fixture();r,rows=read(t,n,122)
  self.assertEqual(r['native_wait_ms']['mean'],.3)
  self.assertEqual(r['rx_buffered_bytes_at_enqueue']['p95'],400)
  self.assertEqual(len(rows),122)
 def test_missing_record(self):
  n,t=self.fixture()
  with self.assertRaises(AssertionError):read(t.replace('NPNATIVE row 4 300 200 2 400\n',''),n,122)
 def test_wrong_nonce(self):
  n,t=self.fixture()
  with self.assertRaises(AssertionError):read(t,'fedcba9876543210',122)
 def test_impossible_wait(self):
  n,t=self.fixture()
  with self.assertRaises(AssertionError):read(t.replace('row 4 300 200 2 400','row 4 100 200 2 400'),n,122)
if __name__=='__main__':unittest.main()
