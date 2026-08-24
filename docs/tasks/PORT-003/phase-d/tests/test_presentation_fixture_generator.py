from pathlib import Path
import importlib.util
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data  # noqa: E402


SCRIPT = ROOT / "docs/tasks/PORT-003/phase-d/scripts/generate-presentation-fixtures.py"
FIXTURES = ROOT / "docs/tasks/PORT-003/phase-d/fixtures/presentation.yaml"
spec = importlib.util.spec_from_file_location("phase_d_fixture_generator", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class PresentationFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data(FIXTURES)

    def test_all_case_ids_and_hashes_are_unique_and_valid(self):
        cases = self.data["palette_cases"] + self.data["composition_cases"] + self.data["allocation_cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            expected = case["content_sha256"]
            payload = dict(case)
            del payload["content_sha256"]
            self.assertEqual(expected, module.payload_hash(payload))

    def test_fixture_matrix_covers_every_format_and_buffering_state(self):
        composition_formats = {case["format"] for case in self.data["composition_cases"]}
        self.assertEqual(composition_formats, set(module.FORMATS))
        self.assertTrue(any(case["double_buffered"] for case in self.data["composition_cases"]))
        self.assertTrue(any(not case["double_buffered"] for case in self.data["composition_cases"]))

    def test_required_palette_and_copper_edges_are_present(self):
        encoded = json.dumps(self.data["palette_cases"], sort_keys=True)
        for token in ('"index": 5', '"palette_id": 65535', '"pairs": []', '"pairs": [[0, 5]'):
            self.assertIn(token, encoded)
        self.assertIn("unknown-zero-row", encoded)

    def test_overlay_fixture_covers_order_alpha_xor_and_clipping(self):
        case = next(item for item in self.data["composition_cases"] if item["id"] == "overlay-order-alpha-xor-clipping")
        roles = {item["role"] for item in case["overlays"]}
        self.assertEqual(roles, {"text", "hardware", "software", "mouse"})
        self.assertTrue(any(item.get("paint") == "XOR" for item in case["overlays"]))
        self.assertTrue(any(item["x"] < 0 for item in case["overlays"]))
        self.assertTrue(any(0 in item["data"] for item in case["overlays"]))

    def test_oracle_does_not_import_or_invoke_production(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("extender/display", text)
        self.assertNotIn("subprocess", text)


if __name__ == "__main__":
    unittest.main()
