from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
RESULTS = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-facade-matrix-results.yaml"


class ModeFacadeMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(RESULTS.read_text(encoding="utf-8"))

    def test_every_mode_variant_passes(self):
        self.assertEqual(len(self.data["cases"]), 58)
        self.assertEqual(self.data["summary"], {"passed": 58, "failed": 0})
        self.assertFalse(self.data["failures"])

    def test_one_stable_facade_restarts_and_releases(self):
        teardown = self.data["teardown"]
        self.assertEqual(teardown["service_starts"], 58)
        self.assertEqual(teardown["service_stops"], 57)
        self.assertEqual(teardown["live_allocations"], 0)


if __name__ == "__main__":
    unittest.main()
