import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import summarize
class AnalyzeTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)/'run.csv'
 def tearDown(self):self.tmp.cleanup()
 def write(self,overflow=0,missing=False):
  fields='source frame active_prt logic_prt submit_prt pacing_prt total_prt overflow mos_ticks run_ticks submitted_us completed_us drain_us'.split()
  with self.p.open('w') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for i in range(119 if missing else 120):w.writerow(dict(zip(fields,[0,i,1152,576,576,64383 if overflow else 18048,65535 if overflow else 19200,overflow,2,240,100,200,100])))
 def test_units(self):
  self.write();r=summarize(self.p);self.assertEqual(r['active_ms_per_update'],1);self.assertEqual(r['active_percent'],6);self.assertEqual(r['updates_per_second'],60)
 def test_saturation_not_short_frames(self):
  self.write(overflow=1);r=summarize(self.p);self.assertIsNone(r['active_ms_per_update']);self.assertEqual(r['overflow_rows'],120)
 def test_divider64(self):
  self.write();r=summarize(self.p,64);self.assertEqual(r["active_ms_per_update"],4);self.assertEqual(r["prt_counts_per_second_nominal"],288000)
 def test_incomplete(self):
  self.write(missing=True)
  with self.assertRaises(ValueError):summarize(self.p)
if __name__=='__main__':unittest.main()
