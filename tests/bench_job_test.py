#!/usr/bin/env python3
"""Focused tests for detached bench-job terminal notification hooks."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('bench_job', ROOT / 'scripts/bench_job.py')
BENCH_JOB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCH_JOB)


class BenchJobTest(unittest.TestCase):
    def test_rejects_shell_string_and_unknown_hook(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'hooks.json'
            path.write_text(json.dumps({'success': 'echo unsafe'}))
            with self.assertRaisesRegex(ValueError, 'argv string array'):
                BENCH_JOB.read_hooks(path)
            path.write_text(json.dumps({'always': ['true']}))
            with self.assertRaisesRegex(ValueError, 'unknown terminal hook'):
                BENCH_JOB.read_hooks(path)

    def test_failure_hook_runs_after_primary_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            marker = folder / 'hook.txt'
            request = {
                'argv': [sys.executable, '-c', 'raise SystemExit(7)'],
                'cwd': str(folder),
                'terminal_hooks': {
                    'success': [sys.executable, '-c', 'raise SystemExit(9)'],
                    'failure': [sys.executable, '-c',
                                f'from pathlib import Path; Path({str(marker)!r}).write_text("failure")'],
                },
            }
            (folder / 'request.json').write_text(json.dumps(request))
            with contextlib.redirect_stdout(io.StringIO()):
                BENCH_JOB.worker(folder)
            result = json.loads((folder / 'result.json').read_text())
            self.assertEqual(result['command_exit_code'], 7)
            self.assertEqual(result['terminal_hook'], 'failure')
            self.assertEqual(result['terminal_hook_exit_code'], 0)
            self.assertEqual(result['status'], 'failure')
            self.assertEqual(marker.read_text(), 'failure')

    def test_success_hook_failure_prevents_success_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            request = {
                'argv': [sys.executable, '-c', 'pass'],
                'cwd': str(folder),
                'terminal_hooks': {
                    'success': [sys.executable, '-c', 'raise SystemExit(6)'],
                },
            }
            (folder / 'request.json').write_text(json.dumps(request))
            with contextlib.redirect_stdout(io.StringIO()):
                BENCH_JOB.worker(folder)
            result = json.loads((folder / 'result.json').read_text())
            self.assertEqual(result['command_status'], 'success')
            self.assertEqual(result['terminal_hook_exit_code'], 6)
            self.assertEqual(result['status'], 'failure')

    def test_job_without_hooks_remains_supported(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            request = {
                'argv': [sys.executable, '-c', 'pass'],
                'cwd': str(folder),
                'terminal_hooks': {},
            }
            (folder / 'request.json').write_text(json.dumps(request))
            with contextlib.redirect_stdout(io.StringIO()):
                BENCH_JOB.worker(folder)
            result = json.loads((folder / 'result.json').read_text())
            self.assertEqual(result['exit_code'], 0)
            self.assertEqual(result['status'], 'success')
            self.assertIsNone(result['terminal_hook'])


if __name__ == '__main__':
    unittest.main()
