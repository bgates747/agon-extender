from pathlib import Path
import hashlib
import sys
import unittest


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file  # noqa: E402


ARTIFACT = ROOT / "docs/tasks/PORT-003/phase-d/evidence/presentation-provenance.yaml"


class PresentationProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data(ARTIFACT)

    def test_identity_tuples_are_unique(self):
        keys = [
            (item["owner"], item["span"]["path"], item["span"]["start_line"], item["symbol"])
            for item in self.data["records"]
        ]
        self.assertEqual(len(keys), len(set(keys)))

    def test_all_source_and_span_hashes_match(self):
        roots = {"agon-vdp": ROOT / "vdp", "vdp-gl": ROOT / "vdp/vendor/vdp-gl"}
        for item in self.data["sources"]:
            self.assertEqual(item["sha256"], sha256_file(roots[item["owner"]] / item["path"]))
        for item in self.data["records"]:
            span = item["span"]
            lines = (roots[item["owner"]] / span["path"]).read_bytes().splitlines(keepends=True)
            payload = b"".join(lines[span["start_line"] - 1 : span["end_line"]])
            self.assertEqual(span["span_sha256"], hashlib.sha256(payload).hexdigest())

    def test_critical_contracts_and_physical_exclusions_exist(self):
        dispositions = {}
        for item in self.data["records"]:
            dispositions.setdefault(item["symbol"], set()).add(item["disposition"])
        self.assertIn("retain-algorithm", dispositions["updateRGB2PaletteLUT"])
        self.assertIn("retain-common-contract", dispositions["showSprites"])
        self.assertIn("adapt-overlay-algorithm", dispositions["drawSpriteScanLine"])
        self.assertIn("exclude-physical-engine", dispositions["vga2-packed-signal-table"])

    def test_findings_preserve_logical_and_overlay_boundaries(self):
        findings = self.data["findings"]
        self.assertIn("readback", findings["logical_presentation_split"])
        self.assertIn("software sprites", findings["software_hardware_split"])
        self.assertEqual(findings["overlay_order"], "text cursor, ascending hardware sprites, then mouse cursor")
        self.assertIn("I2S", findings["excluded_mechanism"])


if __name__ == "__main__":
    unittest.main()
