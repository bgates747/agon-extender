from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / "docs/tasks/PORT-003/phase-e/scripts/extract-mode-provenance.py"
ARTIFACT = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml"


def module():
    spec = importlib.util.spec_from_file_location("phase_e_provenance", SCRIPT)
    loaded = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(loaded)
    return loaded


class ModeProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))

    def test_complete_mode_ids_and_variants(self):
        modes = self.data["mode_table"]
        ids = {entry["mode"] for entry in modes}
        self.assertEqual(ids, set(range(31)) | {129, 130, 132, 133, 134, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146, 149, 150, 151, 153, 154, 156, 157, 158})
        self.assertEqual(len([entry for entry in modes if entry["mode"] <= 3]), 8)
        self.assertEqual(len(modes), len(ids) + 4)

    def test_all_regions_are_unique_and_nonempty(self):
        records = self.data["source_regions"] + self.data["documentation_regions"]
        self.assertEqual(len({record["id"] for record in records}), len(records))
        for record in records:
            self.assertLessEqual(record["start_line"], record["end_line"])
            self.assertEqual(len(record["sha256"]), 64)
            self.assertEqual(len(record["file_sha256"]), 64)

    def test_critical_lifecycle_regions_present(self):
        ids = {record["id"] for record in self.data["source_regions"]}
        self.assertTrue({"screen-mode-table", "vdu-mode-lifecycle", "mode-information-packet", "context-mode-reset", "teletext-initialization", "mouse-positioner-reset"} <= ids)

    def test_parser_reproduces_tracked_artifact(self):
        parsed = module().mode_table(ROOT.parents[1] / "agon-vdp", ROOT / "vdp/vendor/vdp-gl")
        self.assertEqual(parsed, self.data["mode_table"])


if __name__ == "__main__":
    unittest.main()
