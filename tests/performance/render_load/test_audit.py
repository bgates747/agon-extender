"""Verify evidence identity and distinguish failed work from unperformed work."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qualification'))
from render_load_audit import audit
sys.path.insert(0,str(Path(__file__).parent))
from codec import decode

def fixture(root):
 evidence=root/'evidence';evidence.mkdir();folder=evidence/'BENCH-009-evidence';folder.mkdir();analysis=root/'analysis';analysis.mkdir()
 header=bytearray(128);header[:5]=b'B9R2\2';header[5]=8;header[6:8]=(320).to_bytes(2,'little');header[8:10]=(240).to_bytes(2,'little');header[10]=64;header[12:15]=(123).to_bytes(3,'little');header[22:26]=b'test'
 case=bytearray(24);case[:4]=b'B9C2';case[7]=3;case[11:14]=(120).to_bytes(3,'little');case[14:17]=(64).to_bytes(3,'little');case[17:20]=(64).to_bytes(3,'little');case[20]=1
 frames=b''.join(bytes([(i+8)%40,0])+bytes(10) for i in range(64));raw=header+case+frames
 meta=dict(run_id=folder.name,suite='render-load-contract-r04',mode=8,endpoint='mainboard',variant='normal',pass_number=1,first=0,end=94,tag=123,outcome='fail',fixture={'build_id':'test'},result_sha256=hashlib.sha256(raw).hexdigest())
 (folder/'run.json').write_text(json.dumps(meta));(folder/'results.bin').write_bytes(raw);(folder/'decoded.json').write_text(json.dumps(decode(raw)))
 failure=bytearray(header);failure[19]=4;(folder/'failure.bin').write_bytes(failure)
 (analysis/'cases.json').write_text(json.dumps([dict(run=folder.name,case=0,pass_number=1,**{'pass':1},disable_timing=False)]))
 return evidence,analysis,folder

class AuditTests(unittest.TestCase):
 def test_failed_boundary_is_accounted_without_claiming_remaining_work(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);evidence,analysis,folder=fixture(root);result=audit(evidence,analysis,root/'audit.json')
   self.assertTrue(result['raw_provenance_complete'])
   self.assertEqual((result['executions_accounted'],result['valid_measurements'],result['failed_or_invalid_executions']),(2,1,1))
   group=next(g for g in result['groups'] if (g['output'],g['mode'],g['endpoint'],g['pass_number'])==('normal',8,'mainboard',1))
   self.assertEqual(group['valid_cases'],[0]);self.assertEqual(group['failed_or_invalid_cases'],[1]);self.assertEqual(group['unperformed_cases'],list(range(2,94)))
   self.assertFalse(result['execution_coverage_complete'])
 def test_derived_record_tampering_cannot_supply_valid_coverage(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);evidence,analysis,folder=fixture(root)
   result=json.loads((folder/'decoded.json').read_text());result['cases'][0]['id']=2;(folder/'decoded.json').write_text(json.dumps(result))
   audited=audit(evidence,analysis,root/'audit.json')
   self.assertFalse(audited['raw_provenance_complete']);self.assertEqual(audited['executions_accounted'],0)
   self.assertIn('derived decoded records differ',audited['issues'][0]['failure'])

if __name__=='__main__':unittest.main()
