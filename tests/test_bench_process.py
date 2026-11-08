"""Host-only process evidence regressions; never opens a bench connection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import bench_process as bench


class BenchProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)/'operation'

    def launch(self, code, seconds=2):
        argv = [sys.executable, '-c', code]
        status = bench.run(argv, self.out, seconds, grace=.1, owner='test',
                           lease='test-only', phase='host', next_action='Inspect original journal; no replay')
        return status, argv

    def mutate(self, name, key, value):
        path = self.out/name
        record = bench.read(path)
        record[key] = value
        path.write_text(json.dumps(record))

    def test_success_records_actual_wait_and_refuses_reuse(self):
        status, argv = self.launch('print("done")')
        self.assertEqual(status, 0)
        self.assertEqual(bench.verify_child(self.out, argv)['actual_returncode'], 0)
        self.assertFalse((self.out/'blocked.json').exists())
        with self.assertRaises(FileExistsError):
            self.launch('pass')

    def test_nonzero_never_certified_and_block_is_actionable(self):
        status, argv = self.launch('raise SystemExit(17)')
        self.assertEqual(status, 1)
        self.assertEqual(bench.read(self.out/'child-terminal.json')['returncode'], 17)
        self.assertTrue(bench.read(self.out/'blocked.json')['notification_required'])
        self.assertIn('journal', bench.read(self.out/'blocked.json')['next_action'])
        with self.assertRaises(ValueError):
            bench.verify_child(self.out, argv)

    def test_timeout_joins_and_preserves_timeout(self):
        status, argv = self.launch('import time; time.sleep(30)', seconds=.05)
        self.assertEqual(status, 1)
        end = bench.read(self.out/'child-terminal.json')
        self.assertTrue(end['timed_out'])
        self.assertTrue(end['group_terminal'])
        with self.assertRaises(ValueError):
            bench.verify_child(self.out, argv)

    def test_exit_zero_with_leftover_child_is_failure(self):
        status, _ = self.launch('import subprocess,sys; subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"])')
        self.assertEqual(status, 1)
        self.assertIn('descendants', bench.read(self.out/'blocked.json')['reason'])
        self.assertTrue(bench.read(self.out/'child-terminal.json')['group_terminal'])

    def test_missing_terminal_refused(self):
        _, argv = self.launch('pass')
        (self.out/'child-terminal.json').unlink()
        with self.assertRaises(FileNotFoundError):
            bench.verify_child(self.out, argv)

    def test_mismatched_pid_and_namespace_and_argv_refused(self):
        _, argv = self.launch('pass')
        with self.assertRaises(ValueError):
            bench.verify_child(self.out, argv+['extra'])
        original = bench.read(self.out/'child-terminal.json')['pid']
        self.mutate('child-terminal.json', 'pid', original+1)
        with self.assertRaises(ValueError):
            bench.verify_child(self.out, argv)
        self.mutate('child-terminal.json', 'pid', original)
        self.mutate('child-started.json', 'pid_namespace', 'different')
        with self.assertRaises(ValueError):
            bench.verify_child(self.out, argv)

    def test_cancellation_writes_terminal_and_block(self):
        script = Path(bench.__file__)
        argv = [sys.executable, str(script), 'run', '--out', str(self.out),
                '--seconds', '30', '--owner', 'test', '--lease', 'test-only',
                '--phase', 'host', '--next-action', 'Inspect original journal',
                '--', sys.executable, '-c', 'import time; time.sleep(30)']
        child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: child.poll() is None and child.kill())
        deadline = time.monotonic()+5
        while not (self.out/'child-started.json').exists():
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.01)
        child.terminate()
        child.communicate(timeout=8)
        self.assertEqual(child.returncode, 1)
        self.assertTrue(bench.read(self.out/'child-terminal.json')['cancelled'])
        self.assertTrue(bench.read(self.out/'child-terminal.json')['group_terminal'])
        self.assertTrue((self.out/'blocked.json').exists())

    def test_unattended_refuses_to_start_without_notification(self):
        with self.assertRaises(ValueError):
            bench.run([sys.executable,'-c','pass'],self.out,1,owner='test',lease='test',
                      phase='host',next_action='Reconcile',unattended=True)
        self.assertFalse(self.out.exists())

    def test_unattended_failure_notifies_once_and_retains_block(self):
        notice = Path(self.tmp.name)/'notice'
        argv = [sys.executable,'-c','raise SystemExit(7)']
        notify = [sys.executable,'-c','from pathlib import Path; import sys; Path(sys.argv[1]).write_text("notice")',str(notice)]
        rc = bench.run(argv,self.out,2,grace=.1,owner='test',lease='test',phase='host',
                       next_action='Inspect original journal',unattended=True,notify_argv=notify)
        self.assertEqual(rc,1)
        self.assertTrue(notice.exists())
        self.assertTrue(bench.read(self.out/'notification-result.json')['helper_completed'])
        self.assertEqual(bench.status(self.out)['state'],'blocked')

    def test_failed_notification_is_visible(self):
        rc = bench.run([sys.executable,'-c','raise SystemExit(3)'],self.out,2,grace=.1,
                       owner='test',lease='test',phase='host',next_action='Inspect original journal',
                       unattended=True,notify_argv=[sys.executable,'-c','raise SystemExit(5)'])
        self.assertEqual(rc,1)
        self.assertFalse(bench.status(self.out)['notification']['helper_completed'])

    def test_status_does_not_confuse_process_and_physical_completion(self):
        self.launch('pass')
        value=bench.status(self.out)
        self.assertEqual(value['state'],'process-completed')
        self.assertEqual(value['physical_release'],'separate verification required')
        (self.out/'complete.json').unlink()
        self.mutate('supervisor-started.json','start','0')
        self.assertEqual(bench.status(self.out)['state'],'interrupted-unreconciled')

    def test_completion_verification_fault_is_a_visible_block(self):
        with patch.object(bench,'verify_child',side_effect=ValueError('bad proof')):
            status,_=self.launch('pass')
        self.assertEqual(status,1)
        self.assertIn('verification failed',bench.status(self.out)['reason'])

    def test_spawn_failure_is_a_visible_block_without_invented_terminal(self):
        status=bench.run(['/definitely-missing-bench-test-program'],self.out,1,
                         owner='test',lease='test',phase='host',next_action='Correct selected executable')
        self.assertEqual(status,1)
        self.assertEqual(bench.status(self.out)['state'],'blocked')
        self.assertFalse((self.out/'child-terminal.json').exists())

    def test_status_reports_wrong_namespace_without_false_completion(self):
        self.launch('pass')
        self.mutate('child-started.json','pid_namespace','different')
        result=bench.status(self.out)
        self.assertEqual(result['state'],'evidence-unverified')
        self.assertIn('native execution namespace',result['next_action'])


if __name__ == '__main__':
    unittest.main()
