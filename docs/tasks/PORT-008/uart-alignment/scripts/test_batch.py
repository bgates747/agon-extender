#!/usr/bin/env python3
"""Independent scope/quantization controls for the symmetric return analyzer."""
import csv,io,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ANALYZER=Path(__file__).with_name('analyze_batch.py')
class Batch(unittest.TestCase):
 def invoke(self,rounds,change=None,scope=None):
  rows=[]
  for repeat in range(6):
   for route in range(2):
    rows.append(dict(repeat=repeat,route=route,direction='reverse-batch',pattern=3,length=256,send_ticks=0,reply_ticks=(10 if route==0 else 8)*rounds,elapsed_us=0,expected_bytes=2048*rounds,actual_bytes=2048*rounds,errors=0,status=0))
  terminal='# terminal,status=0,saved=12,recovery=0'
  if change:terminal=change(rows,terminal)
  text=io.StringIO();writer=csv.DictWriter(text,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
  with tempfile.TemporaryDirectory() as tmp:
   src=Path(tmp)/'input.csv';out=Path(tmp)/'result.json';src.write_text(text.getvalue()+terminal+'\n')
   p=subprocess.run([sys.executable,str(ANALYZER),str(src),'--transfers',str(rounds if scope is None else scope),'--output',str(out)],capture_output=True,text=True)
   return p.returncode,json.loads(out.read_text()) if out.exists() else None
 def test_supported_scopes(self):
  for n in (16,31,128):
   with self.subTest(n=n):
    rc,d=self.invoke(n);self.assertEqual(rc,0);self.assertEqual(d['exact_useful_bytes'],12*n*2048);self.assertAlmostEqual(d['per_transfer_uncertainty_ms'],1000/60/n);self.assertTrue(d['conservative_parity_pass'])
 def test_wrong_scope(self):self.assertNotEqual(self.invoke(128,scope=16)[0],0)
 def test_reject_corrupt_or_incomplete(self):
  def modify(field,value):
   def change(rows,t):rows[0][field]=value;return t
   return change
  changes=[modify('actual_bytes',1),modify('errors',1),modify('status',1),modify('reply_ticks',3),modify('elapsed_us',1),lambda rows,t:t.replace('recovery=0','recovery=1')]
  for change in changes:
   with self.subTest(change=change):self.assertNotEqual(self.invoke(128,change)[0],0)
 def test_overlapping_bounds_do_not_pass(self):
  def close(rows,t):
   for r in rows:r['reply_ticks']=1280
   return t
  rc,d=self.invoke(128,close);self.assertEqual(rc,0);self.assertFalse(d['conservative_parity_pass'])
if __name__=='__main__':unittest.main()
