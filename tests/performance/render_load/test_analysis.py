"""Check benchmark tail/budget aggregation and presentation scope off-bench."""
import contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qualification'))
from render_load_analyse import analyse

class AnalysisTests(unittest.TestCase):
 def test_matched_pass_tails_and_aborted_output_are_separate(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);evidence=root/'evidence';evidence.mkdir()
   for endpoint,counts in (('mainboard',(576,720,864)),('p4',(1440,1152,1440))):
    for number,count in enumerate(counts,1):
     folder=evidence/f'BENCH-009-{endpoint}-{number}';folder.mkdir()
     meta=dict(run_id=folder.name,suite='render-load-contract-r04',mode=8,endpoint=endpoint,variant='normal',first=0,end=1,pass_number=number,tag=number,outcome='pass',disable_timing=False)
     case=dict(id=0,flags=3,error=0,truncated=False,total_frames=64,raw_start=0,raw_end=120,frames=[dict(status=0,submit_counts=72,complete_counts=count,total_counts=count)]*64)
     result=dict(mode=8,tag=number,width=320,height=240,colours=64,build_id='host-test',cases=[case])
     (folder/'run.json').write_text(json.dumps(meta));(folder/'decoded.json').write_text(json.dumps(result))
     if endpoint=='p4':
      phases=[dict(calls=100,us=100000,max_us=2000,boundary_drops=0) for _ in range(5)]
      phases.append(dict(calls=4,us=120000,max_us=40000,boundary_drops=1))
      window=dict(tag=number,id=0,flags=3,start_us=1000000,end_us=2000000,phases=phases,updates=0 if number==1 else 2,scanouts=60,marker_valid=0 if number==1 else 2,marker_invalid=0,last_frame=0)
      (folder/'telemetry.json').write_text(json.dumps(dict(output='normal',overflow=False,windows=[window])))
   output=root/'output'
   with contextlib.redirect_stdout(io.StringIO()):analyse(evidence,output)
   comparison=json.loads((output/'comparison.json').read_text())[0]
   self.assertEqual(comparison['paired_passes'],[1,2,3])
   self.assertEqual(comparison['mainboard_completion_median_ms'],10)
   self.assertEqual(comparison['p4_completion_median_ms'],20)
   self.assertEqual(comparison['p4_vs_mainboard_percent'],100)
   self.assertEqual(comparison['p4_completion_range_ms'],[16,20])
   self.assertEqual(comparison['p4_p95_ms'],20)
   self.assertEqual(comparison['p4_completion_over_16_667_ms_percent'],100)
   self.assertEqual(comparison['mainboard_completion_over_16_667_ms_percent'],0)
   zero=json.loads((output/'zero-submissions.json').read_text())
   self.assertEqual([(r['pass'],r['hdmi_submissions'],r['conversion_calls']) for r in zero],[(1,0,4)])
   phase=json.loads((output/'phase-summary.json').read_text())[0]
   self.assertEqual(phase['conversion_wall_mean_ms'],30)
   self.assertEqual(phase['zero_submission_passes'],[1])
   self.assertEqual(phase['completed_submissions_per_second'],2)
   self.assertIn('attempt including aborted publication',(output/'report.md').read_text())

if __name__=='__main__':unittest.main()
