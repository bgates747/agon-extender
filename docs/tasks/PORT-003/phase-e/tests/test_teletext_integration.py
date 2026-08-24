from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
RESULTS = ROOT / "docs/tasks/PORT-003/phase-e/evidence/teletext-integration-results.yaml"


class TeletextIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(RESULTS.read_text(encoding="utf-8"))

    def test_retained_teletext_cases_pass(self):
        self.assertEqual(self.data["summary"], {"passed": 2, "failed": 0})
        self.assertEqual(
            [result["id"] for result in self.data["results"]],
            ["success", "failure"],
        )
        self.assertTrue(all(result["status"] == "pass" for result in self.data["results"]))

    def test_no_classic_physical_source_is_in_host_closure(self):
        paths = [entry["path"] for entry in self.data["production_and_harness_sources"]]
        forbidden = ("vga", "cvbs", "scene", "ps2", "soundgen", "network")
        self.assertFalse(any(any(token in path.lower() for token in forbidden) for path in paths))

    def test_retained_official_headers_are_hash_bound(self):
        self.assertEqual(
            [entry["path"] for entry in self.data["retained_header_inputs"]],
            [
                "vdp/video/agon_screen.h",
                "vdp/video/agon_ttxt.h",
                "vdp/video/ttxtfont.h",
                "vdp/video/agon_palette.h",
            ],
        )
        self.assertTrue(
            all(len(entry["sha256"]) == 64 for entry in self.data["retained_header_inputs"])
        )


if __name__ == "__main__":
    unittest.main()
