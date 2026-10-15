import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
import test_master_runner
spec=importlib.util.spec_from_file_location('card_collect',ROOT/'scripts/collect_render_qualification.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class CardCollectionTests(unittest.TestCase):
    def prepare(self,root):
        run=root/'run';run.mkdir();card=root/'card';card.mkdir()
        plan=test_master_runner.MasterRunnerTests().plan(root)
        package=root/'package.json'
        jobs=[];rows=[]
        for job in plan['jobs']:
            folder=run/job['id'];folder.mkdir()
            remote='/agents/extender/results/example/'+job['id']+'/records.bin'
            frozen=dict(job,result=remote)
            jobs.append(frozen)
            source=card/remote.lstrip('/');source.parent.mkdir(parents=True)
            source.write_bytes(b'raw')
            for name,value in [('invocation.json',dict(job=frozen,identity='selected-image')),
                               ('windows.json',{}),('before-display.json',{}),('after-display.json',{})]:
                c.dump(folder/name,value)
            receipt={k:job[k] for k in ('id','renderer','mode','case','repeat')}
            receipt.update(validated=False,collection_pending=True,bench_idle=True,
                           identity='selected-image',result_remote=remote,
                           sidecar_sha256={name:c.sha((folder/name).read_bytes()) for name in
                               ('invocation.json','windows.json','before-display.json','after-display.json')})
            c.dump(folder/'receipt.json',receipt)
            rows.append(dict(id=job['id'],receipt_sha256=c.sha((folder/'receipt.json').read_bytes())))
        c.dump(package,dict(jobs=jobs))
        plan['inputs'][str(package)]=c.sha(package.read_bytes())
        plan['collection']=dict(method='physical-card',park=['park'],package_plan=str(package))
        c.dump(run/'plan.json',plan)
        c.dump(run/'summary.json',dict(state='awaiting_collection',park_returncode=0,jobs=rows))
        return run,card

    def test_invalid_raw_is_retained_as_error_and_disqualifies_its_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,card=self.prepare(Path(tmp))
            calls=0
            def validate(*args):
                nonlocal calls
                calls+=1
                if calls==1:raise ValueError('bad raw')
                return dict(trajectory_sha256='same')
            with patch.object(c,'validate_records',side_effect=validate):
                self.assertEqual(c.collect(run,card),240)
            summary=json.loads((run/'summary.json').read_text())
            self.assertEqual(summary['state'],'collected_with_errors_awaiting_notification')
            self.assertEqual(summary['failed'],2)
            calls=[]
            def notify(argv,log,cwd):
                calls.append(argv);log.write_text('mock\n');return 0
            self.assertEqual(test_master_runner.m.notify_collected(run,notify),1)
            self.assertEqual(calls,[['red']])

    def test_changed_sidecar_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,card=self.prepare(Path(tmp))
            job=json.loads((run/'plan.json').read_text())['jobs'][0]
            (run/job['id']/'windows.json').write_text('{} altered')
            with self.assertRaisesRegex(ValueError,'sidecar changed'):c.collect(run,card)

    def test_collection_finishes_offline_with_notification_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,card=self.prepare(Path(tmp))
            with patch.object(c,'validate_records',return_value=dict(trajectory_sha256='same')):
                self.assertEqual(c.collect(run,card),240)
            summary=json.loads((run/'summary.json').read_text())
            self.assertEqual(summary['state'],'validated_awaiting_notification')
            self.assertEqual(summary['passed'],240)
            self.assertEqual(summary['pending_collection'],0)
            calls=[]
            def notify(argv,log,cwd):
                calls.append(argv);log.write_text('mock\n');return 0
            self.assertEqual(test_master_runner.m.notify_collected(run,notify),0)
            self.assertEqual(calls,[['green']])
            with self.assertRaises(ValueError):test_master_runner.m.notify_collected(run,notify)

    def test_changed_collected_raw_prevents_notification(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,card=self.prepare(Path(tmp))
            with patch.object(c,'validate_records',return_value=dict(trajectory_sha256='same')):
                c.collect(run,card)
            job=json.loads((run/'plan.json').read_text())['jobs'][0]
            (run/job['id']/'records.bin').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'evidence changed'):
                test_master_runner.m.notify_collected(run)


if __name__=='__main__':unittest.main()
