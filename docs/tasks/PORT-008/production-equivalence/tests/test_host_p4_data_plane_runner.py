"""Fail-closed timeout tests for the PORT-008 P4 host-test runner."""

from __future__ import annotations

from contextlib import redirect_stderr
import importlib.util
from io import StringIO
from pathlib import Path
import subprocess
import unittest
from unittest import mock


TASK_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = TASK_ROOT / "scripts/run-host-p4-data-plane-tests.py"
SPEC = importlib.util.spec_from_file_location("port008_p4_host_runner", SCRIPT)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class HostP4DataPlaneRunnerTests(unittest.TestCase):
    def test_compile_timeout_fails_closed(self) -> None:
        stderr = StringIO()
        with mock.patch.object(
            runner.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["synthetic-cxx"], 120),
        ), redirect_stderr(stderr):
            result = runner.main()
        self.assertEqual(runner.TIMEOUT_EXIT_STATUS, result)
        self.assertIn("host compile timed out", stderr.getvalue())

    def test_test_binary_timeout_fails_closed(self) -> None:
        compile_result = subprocess.CompletedProcess(
            ["synthetic-cxx"], 0, stdout="", stderr=""
        )
        stderr = StringIO()
        with mock.patch.object(
            runner.subprocess,
            "run",
            side_effect=[
                compile_result,
                subprocess.TimeoutExpired(["synthetic-test"], 30),
            ],
        ), redirect_stderr(stderr):
            result = runner.main()
        self.assertEqual(runner.TIMEOUT_EXIT_STATUS, result)
        self.assertIn("host test timed out", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
