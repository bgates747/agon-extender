"""Verify frozen campaign recovery/control semantics without touching a bench."""
import json,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qualification'))
from render_load_campaign import campaign,recover,mark_exception
sys.path.insert(0,str(Path(__file__).parent))
from generate import cases
CATALOG=list(cases())

class FakeBench:
 def __init__(self,evidence,warm_failure=False,missing_window=None,empty_warm_failures=()):
  self.evidence=evidence;self.calls=[];self.warm_failure=warm_failure;self.missing_window=missing_window;self.empty_warm_failures=empty_warm_failures
 def run(self,mode,endpoint,first,end,wait,deadline,variant,interval,**options):
  call=dict(mode=mode,endpoint=endpoint,first=first,end=end,wait=wait,interval=interval,**options);self.calls.append(call)
  name=f'BENCH-009-fixture-{len(self.calls):03}';folder=self.evidence/name;folder.mkdir()
  failed=self.warm_failure and len(self.calls)==1;last=72 if failed else end
  if endpoint=='mainboard' and first in self.empty_warm_failures and not options.get('disable_timing'):
   failed=True;last=first
  items=[]
  for i in range(first,last):
   c=CATALOG[i];flags=int(c['timing'] and not options.get('disable_timing'))|int(c['marker'])<<1
   items.append(dict(id=i,error=0,truncated=False,total_frames=64,flags=flags,frames=[dict(status=0)]*64))
  metadata=dict(run_id=name,first=first,end=end,endpoint=endpoint,mode=mode,tag=len(self.calls),case_interval_seconds=interval,outcome='fail' if failed else 'pass',**options)
  (folder/'run.json').write_text(json.dumps(metadata));(folder/'decoded.json').write_text(json.dumps(dict(cases=items)))
  if failed:
   failure=bytearray(128);failure[19]=4;(folder/'failure.bin').write_bytes(failure)
  if endpoint=='p4':
   windows=[dict(tag=len(self.calls),id=c['id'],flags=c['flags'],start_us=1,end_us=2) for c in items if c['id']!=self.missing_window or options.get('disable_timing')]
   (folder/'telemetry.json').write_text(json.dumps(dict(output=variant,overflow=False,windows=windows)))
  return folder

class CampaignTests(unittest.TestCase):
 def run_scenario(self,warm_failure=False,missing_window=None):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
  contract=root/'contract.json';contract.write_text(json.dumps(dict(identity='host-validation',endpoint_order=[['mainboard','p4']],automated_case_seconds=10)))
  b=FakeBench(root,warm_failure,missing_window)
  result=campaign(b,'normal',contract,[20],1,1,root/'campaign.json')
  return b,result
 def test_warm_failure_keeps_prior_cases_and_replays_prefix(self):
  b,r=self.run_scenario(warm_failure=True)
  self.assertEqual(r['marked'][0]['case'],72)
  self.assertEqual((b.calls[1]['first'],b.calls[1]['end']),(73,94))
  control=b.calls[-1]
  self.assertTrue(control['disable_timing'])
  self.assertEqual((control['first'],control['end'],control['interval']),(0,73,10))
  self.assertEqual(control['control_context']['marked_case'],72)
  self.assertEqual(control['control_context']['original_run'],r['runs'][0])
 def test_missing_p4_window_requires_a_control(self):
  b,r=self.run_scenario(missing_window=85)
  self.assertEqual([(x['endpoint'],x['case']) for x in r['marked']],[('p4',85)])
  control=b.calls[-1]
  self.assertTrue(control['disable_timing'])
  self.assertEqual((control['endpoint'],control['first'],control['end'],control['interval']),('p4',0,86,10))
 def test_recovery_escape_waits_for_fixture_callback_window(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);out=root/'failed';out.mkdir()
   (out/'run.json').write_text(json.dumps(dict(endpoint='p4',tag=123)))
   clock=[0];sent=[]
   class RecoveryBench:
    sd=None;state={};config={'p4':'http://test'};evidence=root
    def confirm_p4_fixture_cli(self,out):return False
    def save(self):pass
    def reset(self):pass
    def request(self,*args,**options):return 503,b''
    def fast_start(self):raise AssertionError('CLI was never observed')
    def fast_connect(self):pass
   def observed(b,path):
    if path=='/sd/status':return {'online':bool(sent)}
    if path=='/keyboard/status':return {'ready':True}
    if path=='/diagnostics/render-benchmark':
     started=clock[0]>=15
     return {'open':int(started),'windows':[dict(tag=123,id=0,end_us=0)] if started else []}
    raise AssertionError(path)
   def send(*args,**options):
    self.assertGreaterEqual(clock[0],15)
    sent.append(clock[0])
   with patch('render_load_campaign.status',side_effect=observed),patch('render_load_campaign.subprocess.run',side_effect=send),patch('render_load_campaign.time.monotonic',side_effect=lambda:clock[0]),patch('render_load_campaign.time.sleep',side_effect=lambda n:clock.__setitem__(0,clock[0]+n)):
    recover(RecoveryBench(),out,'/results/failed')
   self.assertEqual(len(sent),1)
   receipt=json.loads((out/'recovery.json').read_text())
   self.assertEqual(receipt['outcome'],'pass')
   self.assertEqual(receipt['escape_window']['tag'],123)
   self.assertTrue(receipt['fresh_fixture_invocation'])
 def test_recovered_warm_failures_continue_independent_cases(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);contract=root/'contract.json'
   contract.write_text(json.dumps(dict(identity='host-validation',endpoint_order=[['mainboard','p4']],automated_case_seconds=10)))
   b=FakeBench(root,empty_warm_failures=(0,1,2))
   result=campaign(b,'normal',contract,[20],1,1,root/'campaign.json')
   regular=[c for c in b.calls if c['endpoint']=='mainboard' and not c.get('disable_timing')]
   self.assertEqual([c['first'] for c in regular],[0,1,2,3])
   self.assertNotIn('unperformed',result)
 def test_explicit_continuation_does_not_repeat_completed_prefix(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);contract=root/'contract.json'
   contract.write_text(json.dumps(dict(identity='host-validation',endpoint_order=[['mainboard','p4']],automated_case_seconds=10)))
   b=FakeBench(root)
   result=campaign(b,'normal',contract,[136],1,1,root/'campaign.json',72,94,'mainboard')
   self.assertEqual([(c['endpoint'],c['first'],c['end']) for c in b.calls],[('mainboard',72,94)])
   self.assertEqual(result['selection']['first_case'],72)
 def test_post_reset_checkpoint_is_not_an_original_measurement(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);out=root/'BENCH-009-interrupted';out.mkdir()
   (out/'run.json').write_text(json.dumps(dict(run_id=out.name,endpoint='p4',tag=123)))
   class RecoveryOnlyBench:
    evidence=root;config={'results_root':'/results'}
    def fast_read(self,path):
     if path.endswith('/results.bin'):return b'post-reset-checkpoint'
     raise FileNotFoundError(path)
   def recovered(b,folder,remote):
    (folder/'recovery.json').write_text(json.dumps(dict(outcome='pass',fresh_fixture_invocation=True)))
   with patch('render_load_campaign.recover',side_effect=recovered),patch('render_load_campaign.decode',return_value={'cases':[{'id':0}]}):
    result=mark_exception(RecoveryOnlyBench(),set(),RuntimeError('input not admitted'),'host-validation',2)
   self.assertEqual(result,out)
   self.assertFalse((out/'results.bin').exists())
   self.assertFalse((out/'decoded.json').exists())
   self.assertEqual((out/'results-recovery-only.bin').read_bytes(),b'post-reset-checkpoint')
   self.assertTrue(json.loads((out/'run.json').read_text())['recovery_started_fresh_fixture'])
 def test_deferred_failure_recovery_never_downloads_checkpoint_bytes(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);out=root/'BENCH-009-deferred';out.mkdir()
   (out/'run.json').write_text(json.dumps(dict(run_id=out.name,endpoint='p4',tag=123)))
   class DeferredBench:
    evidence=root;config={'results_root':'/results','defer_result_retrieval':True}
    def fast_read(self,path):raise AssertionError('Bulk retrieval is deferred')
    def fast_connect(self):return self
    def stat_entry(self,path):return (7208,32)
   def recovered(b,folder,remote):
    (folder/'recovery.json').write_text(json.dumps(dict(outcome='pass',fresh_fixture_invocation=True)))
   with patch('render_load_campaign.recover',side_effect=recovered):
    mark_exception(DeferredBench(),set(),RuntimeError('missing window'),'host-validation',1)
   meta=json.loads((out/'run.json').read_text())
   self.assertEqual(meta['outcome'],'fail')
   self.assertEqual(meta['recovery_result_suffix'],'-recovery-only')
   self.assertEqual(meta['sd_files']['results.bin']['bytes'],7208)
   self.assertFalse((out/'results.bin').exists())
if __name__=='__main__':unittest.main()
