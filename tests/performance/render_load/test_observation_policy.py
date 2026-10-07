"""Keep unobserved ordinary-image controls outside scheduled comparisons."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qualification'))
from render_load import Bench

class PreparationReached(Exception):pass
class ObservationPolicyTests(unittest.TestCase):
 def bench(self,root,variant='ordinary-hdmi'):
  installed=root/'installed.json';installed.write_text(json.dumps(dict(variant=variant)))
  config=root/'config.json';config.write_text(json.dumps(dict(require_benchmark_telemetry=False,installation_record=str(installed),p4='http://test',results_root='/results')))
  return Bench(config,root/'evidence')
 def test_unobserved_windows_cannot_enter_scheduled_comparisons(self):
  with tempfile.TemporaryDirectory() as temp:
   b=self.bench(Path(temp))
   with self.assertRaises(ValueError):b.run(8,'p4',0,1,20,1100,'normal',suite='render-load-contract-r04')
   self.assertFalse(list(b.evidence.glob('BENCH-009-*')))
 def test_hook_free_control_requires_ordinary_image_and_absent_endpoint(self):
  with tempfile.TemporaryDirectory() as temp:
   b=self.bench(Path(temp),variant='normal')
   with self.assertRaisesRegex(RuntimeError,'ordinary HDMI'):b.run(8,'p4',0,1,20,1100,'normal',disable_timing=True,suite='presentation-no-hook-controls-r04')
  with tempfile.TemporaryDirectory() as temp:
   b=self.bench(Path(temp));b.fast_exit=lambda:(_ for _ in ()).throw(PreparationReached())
   with patch('render_load.urllib.request.urlopen',side_effect=HTTPError('http://test',404,'absent',{},None)):
    with self.assertRaises(PreparationReached):b.run(8,'p4',0,1,20,1100,'normal',disable_timing=True,suite='presentation-no-hook-controls-r04')

if __name__=='__main__':unittest.main()
