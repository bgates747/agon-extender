"""Browser-off condition must be explicit and cannot start before confirmation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run_trace
from capture_trace import sha


class ConditionTest(unittest.TestCase):
    def test_stock_drain_requires_image_and_deployment_binding(self):
        cfg=dict(browser_condition='disconnected',procedure_identity='uart-path-capture-r03',
                 drawing_policy='stock-drain-until-empty-or-suspended',
                 p4_build='uart-excom-console-r08-b2026-09-10-00-00-00Z',
                 p4_factory_sha256='a'*64,p4_manifest_sha256='b'*64,
                 p4_deployment_record_sha256='c'*64)
        self.assertEqual(run_trace.condition_settings(cfg),('disconnected','uart-path-capture-r03'))
        for field in ('drawing_policy','p4_build','p4_factory_sha256','p4_manifest_sha256','p4_deployment_record_sha256'):
            incomplete=dict(cfg);del incomplete[field]
            with self.subTest(field=field),self.assertRaises(ValueError):
                run_trace.condition_settings(incomplete)
        with self.assertRaises(ValueError):
            run_trace.condition_settings(dict(cfg,browser_condition='connected'))

    def test_condition_identity(self):
        self.assertEqual(run_trace.condition_settings({}),('connected','uart-path-capture-r01'))
        self.assertEqual(run_trace.condition_settings({'browser_condition':'disconnected',
                         'procedure_identity':'uart-path-capture-r02'}),('disconnected','uart-path-capture-r02'))
        for cfg in ({'browser_condition':'unknown'}, {'browser_condition':'disconnected',
                    'procedure_identity':'uart-path-capture-r01'}):
            with self.assertRaises(ValueError):run_trace.condition_settings(cfg)

    def test_cancel_before_confirmation(self):
        self.cancel(EOFError(),None)

    def test_cancel_during_settlement(self):
        self.cancel(None,KeyboardInterrupt())

    def cancel(self,input_error,sleep_error):
        with tempfile.TemporaryDirectory() as folder:
            cfg=Path(folder)/'bench.json'
            cfg.write_text(json.dumps(dict(browser_condition='disconnected',
                procedure_identity='uart-path-capture-r02',
                capture_helper_sha256=sha(Path(run_trace.__file__).with_name('capture_trace.py')))))
            with patch('sys.argv',['run_trace','--bench',str(cfg)]), \
                 patch('builtins.input',side_effect=input_error,return_value=''), \
                 patch('builtins.print'), patch('run_trace.time.sleep',side_effect=sleep_error), \
                 patch('run_trace.subprocess.check_output') as remote, \
                 patch('run_trace.subprocess.Popen') as acquisition:
                with self.assertRaises(SystemExit):run_trace.main()
                remote.assert_not_called();acquisition.assert_not_called()


if __name__=='__main__':unittest.main()
