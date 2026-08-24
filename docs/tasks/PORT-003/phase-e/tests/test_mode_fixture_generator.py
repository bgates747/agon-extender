from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / "docs/tasks/PORT-003/phase-e/scripts/generate-mode-fixtures.py"
FIXTURES = ROOT / "docs/tasks/PORT-003/phase-e/fixtures/modes-and-lifecycle.yaml"
PROVENANCE = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("phase_e_fixtures", SCRIPT)
    loaded = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(loaded)
    return loaded


class ModeFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))

    def test_generator_reproduces_fixture(self):
        generated = load_module().build()
        self.assertEqual(generated, self.data)

    def test_mode_contract_is_complete_and_independent(self):
        modes = self.data["mode_cases"]
        self.assertEqual(len(modes), 58)
        self.assertEqual(len({entry["id"] for entry in modes}), 58)
        self.assertEqual({entry["native_format"] for entry in modes}, {"PALETTE2", "PALETTE4", "PALETTE16", "SBGR2222"})
        self.assertEqual({entry["refresh_hz"] for entry in modes}, {60, 70, 75})
        self.assertTrue(any(entry["teletext"] for entry in modes))
        self.assertTrue(any(entry["double_buffered"] for entry in modes))

    def test_independent_modes_match_source_provenance(self):
        provenance = yaml.safe_load(PROVENANCE.read_text(encoding="utf-8"))
        expected = {
            (entry["mode"], str(entry["legacy_modes"]).lower()):
            (entry["width"], entry["height"], entry["colours"], entry["refresh_hz"], entry["double_buffered"])
            for entry in self.data["mode_cases"]
        }
        observed = {
            (entry["mode"], str(entry["legacy_modes"]).lower()):
            (entry["width"], entry["height"], entry["colours"], entry["refresh_hz"], entry["double_buffered"])
            for entry in provenance["mode_table"]
        }
        self.assertEqual(observed, expected)

    def test_lifecycle_covers_fallback_and_observable_order(self):
        cases = self.data["lifecycle_cases"]
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertTrue(any(len(case["attempts"]) == 3 for case in cases))
        self.assertTrue(any(case["result"]["double_buffered"] for case in cases))
        self.assertTrue(any(case["initial"]["mouse_visible"] for case in cases))
        for case in cases:
            self.assertEqual(
                case["expected_events"][-3:],
                [
                    "callbacks.call-mode-change",
                    "callbacks.call-sending-mode-packet",
                    "packet.send-mode",
                ],
            )
            self.assertEqual(len(case["expected_mode_packet"]), 8)
            self.assertEqual(case["expected_mode_packet"][-1], case["result"]["video_mode"])


if __name__ == "__main__":
    unittest.main()
