"""Device-free admission/result negative controls for the actual owner runner."""
from pathlib import Path
import copy,importlib.util,unittest
R=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('rx_control',R/'docs/tasks/NET-004/scripts/async_rx_control.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RxControl(unittest.TestCase):
 def setUp(self):
  self.g=dict(owner='linux-extender',task=m.TASK,generation=78,lease='a'*32,request='newrequest')
  self.c=dict(self.g,operator='linux-extender',central_owner='linux-extender',phase='async-isolation',
    components=dict(m.UNCHANGED,p4_app_sha256=m.P4,emos_rom_sha256=m.EMOS),source_pins_sha256='b'*64)
  self.p=dict(schema='extender-u1rx-prepared-v1',case='async-rx',carrier='uart1-async',sessions=4,records=176,
    full_fixture_readback_match=True,installed_components=self.c['components'],actual_cli=True,callback_zero=True,
    legacy_zero=True,entry_mode=0,source_pins_sha256='b'*64,fixture_sha256=m.FIXTURE,
    fixture_remote='/extender/network/uart1-async-rx/newrequest/netasync.bin',
    result_remote='/agents/extender/results/uart1-async-rx/newrequest/result.txt')
 def test_binding_and_mutations(self):
  m.validate_binding(self.c,self.g,self.p)
  for label,mutate in [
    ('oldlease',lambda c,g,p:g.update(generation=77)),
    ('otheroperator',lambda c,g,p:c.update(operator='mechagon')),
    ('pendingcommand',lambda c,g,p:c.update(pending_commands=True)),
    ('unsafe_callback',lambda c,g,p:p.update(callback_zero=False)),
    ('stale_fixture',lambda c,g,p:p.update(fixture_sha256='0'*64)),
    ('oldROM',lambda c,g,p:c['components'].update(emos_rom_sha256='0'*64)),
    ('differentnative',lambda c,g,p:c['components'].update(native_vdp_sha256='0'*64)),
    ('oldresult',lambda c,g,p:p.update(result_remote='/agents/extender/results/old/result.txt')),
    ('unverifiedwrite',lambda c,g,p:p.update(full_fixture_readback_match=False)),
    ('partialmatrix',lambda c,g,p:p.update(records=175)),
    ('freeze',lambda c,g,p:p.update(source_pins_sha256='c'*64))]:
   with self.subTest(label=label):
    c,g,p=copy.deepcopy((self.c,self.g,self.p));mutate(c,g,p)
    with self.assertRaises(RuntimeError):m.validate_binding(c,g,p)
 def test_durable_and_partial_retirement(self):
  text='\n'.join('session=%d records=%d first_error=0 source_phase=0 close=0'%(s,(s+1)*44) for s in range(4))
  text+='\n'+m.BUILD_ID+' result=PASS first_error=0 records=176/176 opened=4/4 closed=4/4 release=0 restore=1 elapsed_ticks=500 tick_hz_nominal=120 carrier=uart1-async irq_complete=0\n'
  m.validate_durable_result(text)
  for bad in (text.replace('closed=4/4','closed=3/4'),text.replace('source_phase=0','source_phase=3'),
              text.replace('elapsed_ticks=500','elapsed_ticks=14400'),text.replace('restore=1','restore=0'),
              text.replace('records=176/176','records=175/176'),text+'extra\n'):
   with self.assertRaises(RuntimeError):m.validate_durable_result(bad)
 def test_peer_must_be_complete(self):
  p=dict(passed=True,closed_sessions=4,records=[dict(session=s,index=i,bytes=m.SIZES[i%11]) for s in range(4) for i in range(44)])
  m.validate_peer_report(p);p['records'].pop()
  with self.assertRaises(RuntimeError):m.validate_peer_report(p)
if __name__=='__main__':unittest.main()
