#!/usr/bin/env python3
"""Structural tests for the canonical offline qualification runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "qualification_offline", ROOT / "qualification/offline.py"
)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(runner)


class RegressionSuiteTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "qualification/manifests/offline.json").read_text())

    def test_manifest_is_valid_and_classifies_maintained_entry_points(self):
        runner.validate_manifest(self.manifest)
        included = set()
        for case in self.manifest["cases"]:
            included.update(item for item in case["argv"]
                            if item.startswith("tests/") and item.endswith(".py"))
        excluded = {item["path"] for item in self.manifest["excluded"]
                    if item["path"].endswith(".py")}
        entry_points = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "tests").glob("*test.py")
        }
        entry_points.update(
            str(path.relative_to(ROOT))
            for path in (ROOT / "tests").glob("test_*.py")
        )
        entry_points.update(
            str(path.relative_to(ROOT))
            for path in (ROOT / "tests/storage").glob("test_*.py")
        )
        self.assertEqual(entry_points, included | excluded)
        self.assertFalse(included & excluded)

    def test_unknown_placeholder_is_rejected(self):
        case = {"id": "bad", "argv": ["{missing}"]}
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "unknown placeholder"):
                runner.expand(case, Path(folder), Path("/python"), Path("/idf"))

    def test_atomic_json_replaces_complete_document(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "state.json"
            runner.atomic_json(target, {"status": "running"})
            runner.atomic_json(target, {"status": "success", "count": 2})
            self.assertEqual(json.loads(target.read_text()),
                             {"status": "success", "count": 2})
            self.assertFalse(target.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
