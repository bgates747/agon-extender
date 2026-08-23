"""Invariants for the generated Phase C target-run index."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file  # noqa: E402


class TargetRunIndexTests(unittest.TestCase):
    def test_manifests_exist_match_hashes_and_are_unique(self):
        index = load_data(
            ROOT / "docs/tasks/PORT-003/phase-c/evidence/target-runs.yaml"
        )
        run_ids = [run["run_id"] for run in index["runs"]]
        self.assertEqual(len(run_ids), len(set(run_ids)))
        for run in index["runs"]:
            manifest = ROOT / run["manifest"]
            self.assertTrue(manifest.is_file())
            self.assertEqual(run["manifest_sha256"], sha256_file(manifest))
            self.assertEqual(load_data(manifest)["run"]["run_id"], run["run_id"])


if __name__ == "__main__":
    unittest.main()
