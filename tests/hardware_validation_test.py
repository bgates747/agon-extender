#!/usr/bin/env python3
"""Structural tests for commit-pinned flash and hardware regression tools."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


shared = load("hardware_validation", ROOT / "scripts/hardware_validation.py")
runner = load("hardware_regression", ROOT / "scripts/run_hardware_regression.py")


class HardwareValidationTests(unittest.TestCase):
    def test_repair_manifest_is_explicit_and_valid(self):
        document = json.loads((ROOT / "tests/hardware-repair-suite.json").read_text())
        runner.validate_repair_manifest(document)
        self.assertEqual([case["id"] for case in document["cases"]],
                         ["a10-rp04-raw-sd-write"])
        self.assertTrue(document["cases"][0]["destructive"])

    def test_physical_result_requires_complete_restore_oracle(self):
        record = (
            b"schema=1\ncase=a10-rp04-raw-sd-write\nstatus=pass\nsector=2\n"
            b"test_rc=0\nrestore_rc=0\nrestore_verify_rc=0\n"
            b"before_crc32=12345678\npattern_crc32=87654321\n"
            b"observed_crc32=87654321\nrestored_crc32=12345678\n"
        )
        self.assertEqual(runner.parse_result(record)["status"], "pass")
        with self.assertRaisesRegex(ValueError, "wrong schema"):
            runner.parse_result(record.replace(b"restore_rc=0\n", b""))

    def test_config_requires_exact_p4_identity_even_for_shared_tool(self):
        document = json.loads((ROOT / "tests/hardware-validation.example.json").read_text())
        document["p4"].pop("usb_serial")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "p4.usb_serial"):
                shared.load_config(path)

    def test_commit_resolution_returns_full_identity(self):
        commit = shared.resolve_commit(ROOT, "HEAD")
        self.assertEqual(len(commit), 40)
        self.assertTrue(all(character in "0123456789abcdef" for character in commit))


if __name__ == "__main__":
    unittest.main()
