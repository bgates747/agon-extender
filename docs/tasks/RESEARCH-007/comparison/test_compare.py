"""Synthetic guards against comparing different workloads/installed firmware."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('comparison', HERE/'compare.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.plan = {'campaign':'synthetic', 'clock':{}, 'fixture_build':'synthetic-fixture',
                     'firmware':{}, 'cases':[]}
        for label, active in (('baseline',200), ('candidate',100)):
            directory = self.base/label
            directory.mkdir()
            identity = {'build_id':'synthetic-'+label,
                        'segments':[{'path':'agon_extender.bin','sha256':'0'*64}]}
            self.plan['firmware'][label] = identity
            (directory/'run.json').write_text(json.dumps({'installed_build_id':identity['build_id'], 'application_sha256':'0'*64}))
            windows = {'open':False,'overflow':False,'windows':[]}
            for case in (3,7,8,9):
                self.plan['cases'].append({'variant':label,'case':case,'frames':2,'warmup':0,'window_tag':77})
                header = bytearray(128)
                header[:8] = b'SCANR01!'
                header[8:10] = bytes([case,24])
                for offset, value in ((10,77),(16,2),(22,4),(35,2)):
                    header[offset:offset+3] = value.to_bytes(3,'little')
                header[41] = 4 | int(case==9)
                header[42:42+17] = b'synthetic-fixture'
                rows = b''
                for update in (1,2):
                    rows += b''.join(v.to_bytes(3,'little') for v in (update,active,300,1000,2,5)) + bytes([0,1,2,3,4,5])
                (directory/f't{case:02}.bin').write_bytes(header+rows)
                windows['windows'].append({'tag':77,'id':case,'start_us':1,'end_us':100001,
                     'updates':5,'scanouts':6,'phases':[{'calls':1,'us':100} for _ in range(6)]})
            (directory/'windows.json').write_text(json.dumps(windows))
        self.plan_path = self.base/'plan.json'
        self.plan_path.write_text(json.dumps(self.plan))

    def run_comparison(self):
        return comparison.compare(ROOT,self.plan_path,self.base/'baseline',self.base/'candidate')

    def test_compares_costs_without_claiming_fenced_game_completion(self):
        result = self.run_comparison()
        self.assertEqual(result['deltas'][0]['metrics']['active']['median_cost_reduction_percent'],50)
        self.assertNotIn('complete', result['deltas'][-1]['metrics'])

    def test_rejects_different_installed_bytes(self):
        path = self.base/'candidate/run.json'
        meta = json.loads(path.read_text());meta['application_sha256'] = 'f'*64
        path.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError,'firmware identity'):
            self.run_comparison()

    def test_rejects_different_state_trajectory(self):
        path = self.base/'candidate/t09.bin'
        raw = bytearray(path.read_bytes());raw[128+15] ^= 1
        path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'workloads differ'):
            self.run_comparison()

    def test_rejects_unclosed_window(self):
        path = self.base/'candidate/windows.json'
        data = json.loads(path.read_text());data['open'] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'open or overflowed'):
            self.run_comparison()

    def test_rejects_faulted_record(self):
        path = self.base/'candidate/t07.bin'
        raw = bytearray(path.read_bytes());raw[128+18] = 1
        path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'faulted record'):
            self.run_comparison()

    def test_rejects_truncated_record(self):
        path = self.base/'candidate/t03.bin'
        path.write_bytes(path.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError,'truncated'):
            self.run_comparison()


if __name__=='__main__':
    unittest.main()
