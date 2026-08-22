"""Tests for the implementation-independent Phase B fixture oracle."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate-fixtures.py"
SPEC = importlib.util.spec_from_file_location("phase_b_fixtures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[5]


class OracleTests(unittest.TestCase):
    def test_known_packed_bit_orders(self) -> None:
        self.assertEqual(MODULE.encode_pixels([[1, 0, 1]], 1), [0xA0])
        self.assertEqual(MODULE.encode_pixels([[1, 2, 3, 0]], 2), [0x6C])
        self.assertEqual(MODULE.encode_pixels([[0, 1, 2, 3, 4, 5, 6, 7]], 3), [0x05, 0x39, 0x77])
        self.assertEqual(MODULE.encode_pixels([[0xA, 0x5, 0xF]], 4), [0xA5, 0xF0])
        self.assertEqual(MODULE.encode_pixels([[0x00, 0x3F, 0x7F]], 8), [0x00, 0x3F, 0x3F])

    def test_generated_metadata_and_hashes(self) -> None:
        for relative in (
            "docs/tasks/PORT-003/phase-b/fixtures/native-codecs.yaml",
            "docs/tasks/PORT-003/phase-b/fixtures/primitives.yaml",
        ):
            data = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(data["oracle_class"], "independent mathematical model")
            self.assertTrue(data["implementation_output_prohibited"])
            self.assertEqual(data["fixture_set_sha256"], MODULE.payload_hash(data["fixtures"]))
            for fixture in data["fixtures"]:
                expected_hash = fixture.pop("content_sha256")
                self.assertEqual(expected_hash, MODULE.payload_hash(fixture))
                fixture["content_sha256"] = expected_hash

    def test_native_matrix_is_exhaustive_and_boundary_bounded(self) -> None:
        data = yaml.safe_load(
            (ROOT / "docs/tasks/PORT-003/phase-b/fixtures/native-codecs.yaml").read_text(
                encoding="utf-8"
            )
        )
        cases = {fixture["id"]: fixture for fixture in data["fixtures"]}
        for format_name, (_, maximum) in MODULE.FORMATS.items():
            for width in (1, 2, 3, 7, 8, 9, 15, 16, 17):
                case = cases[f"codec-{format_name.lower()}-{width}x3"]
                self.assertEqual({op["value"] for op in case["operations"]}, set(range(maximum + 1)))
            for value in range(maximum + 1):
                self.assertIn(f"clear-{format_name.lower()}-{value}", cases)

    def test_primitive_matrix_has_every_format_and_operation_family(self) -> None:
        data = yaml.safe_load(
            (ROOT / "docs/tasks/PORT-003/phase-b/fixtures/primitives.yaml").read_text(
                encoding="utf-8"
            )
        )
        for format_name in MODULE.FORMATS:
            cases = [case for case in data["fixtures"] if case["format"] == format_name]
            operation_names = {op["op"] for case in cases for op in case["operations"]}
            self.assertEqual(len(cases), 23)
            self.assertTrue({
                "set_pixel", "line", "fill_row", "copy_rect", "vscroll", "hscroll",
                "set_origin", "set_clip", "fill_rect", "invert_rect", "paint_pixel",
                "clear", "glyph", "flood_fill", "ellipse", "arc", "segment", "sector",
                "bitmap_mask", "bitmap_native", "bitmap_rgba2222", "bitmap_rgba8888",
                "bitmap_transform_rgba2222",
            } <= operation_names)
            self.assertEqual(
                sum(bool(case.get("double_buffered")) for case in cases), 1
            )


if __name__ == "__main__":
    unittest.main()
