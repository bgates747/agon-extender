from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
RESULTS = ROOT / "docs/tasks/PORT-003/phase-e/evidence/host-mode-results.yaml"


class HostModeResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(RESULTS.read_text(encoding="utf-8"))

    def test_complete_host_matrix_passes(self):
        self.assertEqual(self.data["summary"], {"passed": 8, "failed": 0})
        self.assertEqual(len(self.data["results"]), 8)
        self.assertTrue(all(result["status"] == "pass" for result in self.data["results"]))

    def test_cross_phase_evidence_is_hash_bound(self):
        paths = {entry["path"] for entry in self.data["evidence_inputs"]}
        self.assertTrue(
            {
                "docs/tasks/PORT-003/phase-b/evidence/host-fixture-results.yaml",
                "docs/tasks/PORT-003/phase-c/evidence/host-frame-results.yaml",
                "docs/tasks/PORT-003/phase-d/evidence/host-presentation-results.yaml",
            }
            <= paths
        )


if __name__ == "__main__":
    unittest.main()
