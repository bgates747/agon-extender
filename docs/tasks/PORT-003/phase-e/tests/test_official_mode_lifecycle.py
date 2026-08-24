from __future__ import annotations

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
FIXTURES = ROOT / "docs/tasks/PORT-003/phase-e/fixtures/modes-and-lifecycle.yaml"
PROVENANCE = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml"
RESULTS = ROOT / "docs/tasks/PORT-003/phase-e/evidence/official-mode-lifecycle-results.yaml"


class OfficialModeLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        cls.provenance = yaml.safe_load(PROVENANCE.read_text(encoding="utf-8"))
        cls.results = yaml.safe_load(RESULTS.read_text(encoding="utf-8"))

    def test_every_lifecycle_fixture_passes(self):
        expected = [case["id"] for case in self.fixtures["lifecycle_cases"]]
        observed = [case["id"] for case in self.results["cases"]]
        self.assertEqual(observed, expected)
        self.assertEqual(self.results["summary"], {"passed": len(expected), "failed": 0})
        self.assertTrue(all(case["status"] == "pass" for case in self.results["cases"]))

    def test_exact_official_source_regions_are_bound(self):
        expected = {
            record["function"]: record["sha256"]
            for record in self.provenance["source_regions"]
            if record["function"]
            in {
                "VDUStreamProcessor::vdu_mode",
                "VDUStreamProcessor::sendModeInformation",
            }
        }
        observed = {
            record["function"]: record["sha256"]
            for record in self.results["source_regions"]
        }
        self.assertEqual(observed, expected)

    def test_packet_callback_precedes_exact_packet(self):
        for case in self.results["cases"]:
            self.assertEqual(
                case["events"][-3:],
                [
                    "callbacks.call-mode-change",
                    "callbacks.call-sending-mode-packet",
                    "packet.send-mode",
                ],
            )
            self.assertEqual(len(case["mode_packet"]), 8)


if __name__ == "__main__":
    unittest.main()
