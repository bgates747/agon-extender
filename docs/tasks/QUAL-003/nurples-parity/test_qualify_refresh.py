import json,tempfile,unittest
from pathlib import Path
from qualify_refresh import qualify
class QualificationTests(unittest.TestCase):
 def fixture(self,root,interval):
  cases=[]
  for i in range(8):
   target='mainboard' if i<4 else 'p4';variant='unfenced-hw' if i%4>=2 else 'unfenced-sw';nonce=i.to_bytes(8,'little')
   b=bytearray(b'NP04'+(2400).to_bytes(3,'little')+bytes([0,0,2 if variant.endswith('hw') else 0])+(2400).to_bytes(3,'little')+bytes([12])+nonce+bytes(2))
   for j in range(2400):b+=(2*j).to_bytes(3,'little')+bytes(9)
   (root/f'{i}.bin').write_bytes(b);text=f'NPTRACE begin {nonce.hex()} 2400 2400 1 0\n';t=0
   for j in range(2400):
    t+=interval(j) if target=='p4' else 16667;text+=f'NPTRACE row {j} {t} {t+100}\n'
   (root/f'{i}.log').write_text(text+f'NPTRACE end {nonce.hex()}\n')
   cases.append(dict(label=str(i),target=target,variant=variant,nonce=nonce.hex(),file=f'{i}.bin',trace_file=f'{i}.log'))
  p=root/'cases.json';p.write_text(json.dumps(cases));return p
 def test_all_baseline_pairs_and_separate_limits(self):
  with tempfile.TemporaryDirectory() as d:
   p=self.fixture(Path(d),lambda j:16667);r=qualify(p);self.assertTrue(r['timing_pass']);self.assertEqual(len(r['comparisons']),8)
   p=self.fixture(Path(d),lambda j:26000 if j%16==0 else 16667);r=qualify(p);self.assertFalse(r['timing_pass']);self.assertTrue(all(c['mean_pass'] and not c['p95_pass'] for c in r['comparisons']))
   p=self.fixture(Path(d),lambda j:17501);r=qualify(p);self.assertFalse(r['timing_pass']);self.assertTrue(all(not c['mean_pass'] and c['p95_pass'] for c in r['comparisons']))
   cases=json.loads(p.read_text());p.write_text(json.dumps(cases[1:]));
   with self.assertRaises(AssertionError):qualify(p)
if __name__=='__main__':unittest.main()
