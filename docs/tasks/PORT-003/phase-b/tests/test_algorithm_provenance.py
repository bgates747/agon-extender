"""Unit tests for the Phase B source-span extractor."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/extract-algorithm-provenance.py"
SPEC = importlib.util.spec_from_file_location("phase_b_provenance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CallableSpanTests(unittest.TestCase):
    def end_line(self, text: str, start: int = 1) -> int:
        cleaned = MODULE.clean_cpp(text)
        return MODULE.callable_end_line(cleaned, MODULE.line_offsets(text), start)

    def test_multiline_declaration(self) -> None:
        self.assertEqual(self.end_line("void f(\n  int value\n);\n"), 3)

    def test_nested_body_and_literal_braces(self) -> None:
        text = 'void f() {\n  if (true) { call("}"); }\n}\n'
        self.assertEqual(self.end_line(text), 3)

    def test_comment_does_not_end_declaration(self) -> None:
        text = "void f( /* ; { } */\n int value);\n"
        self.assertEqual(self.end_line(text), 2)

    def test_unterminated_body_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "unterminated"):
            self.end_line("void f() {\n")


class ClassificationTests(unittest.TestCase):
    def test_depth_operation_is_adapted(self) -> None:
        self.assertEqual(
            MODULE.classify("src/dispdrivers/vga4controller.cpp", "rawFillRow")[0],
            "adapt-depth-algorithm",
        )

    def test_physical_isr_is_excluded(self) -> None:
        self.assertEqual(
            MODULE.classify("src/dispdrivers/vga64controller.cpp", "ISRHandler")[0],
            "exclude-physical",
        )

    def test_common_template_is_retained(self) -> None:
        self.assertEqual(
            MODULE.classify("src/displaycontroller.h", "genericDrawEllipse")[0],
            "retain-common",
        )

    def test_sprite_and_background_scopes_are_deferred(self) -> None:
        self.assertEqual(
            MODULE.classify("src/displaycontroller.cpp", "moveTo", "fabgl::Sprite")[0],
            "defer-phase-d",
        )
        self.assertEqual(
            MODULE.classify(
                "src/displaycontroller.h",
                "enableBackgroundPrimitiveTimeout",
                "fabgl::BitmappedDisplayController",
            )[0],
            "defer-phase-c",
        )


class GeneratedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[5]
        cls.source_root = cls.root / "vdp/vendor/vdp-gl"
        cls.artifact = yaml.safe_load(
            (cls.root / "docs/tasks/PORT-003/phase-b/evidence/algorithm-provenance.yaml").read_text(
                encoding="utf-8"
            )
        )

    def test_fixed_pinned_scope_and_unique_records(self) -> None:
        self.assertEqual(self.artifact["source"]["commit"], MODULE.EXPECTED_COMMIT)
        self.assertEqual(self.artifact["summary"]["file_count"], 17)
        ids = [item["id"] for item in self.artifact["algorithms"]]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(any("__anon" in item["symbol"] for item in self.artifact["algorithms"]))

    def test_narrow_geometry_utility_closure_is_retained(self) -> None:
        utility = {
            item["symbol"]: item
            for item in self.artifact["algorithms"]
            if item["family"] == "common-geometry"
        }
        self.assertEqual(set(utility), MODULE.PHASE_B_UTILITY_NAMES)
        self.assertTrue(all(item["disposition"] == "retain-common" for item in utility.values()))

    def test_every_source_and_span_fingerprint_matches(self) -> None:
        for item in self.artifact["scope"]["files"]:
            self.assertEqual(MODULE.sha256_file(self.source_root / item["path"]), item["sha256"])
        for item in self.artifact["algorithms"]:
            span = item["span"]
            path = self.source_root / span["path"]
            self.assertEqual(MODULE.sha256_file(path), span["file_sha256"])
            self.assertEqual(
                MODULE.source_span(
                    MODULE.SOURCE_ID,
                    self.source_root,
                    span["path"],
                    span["start_line"],
                    span["end_line"],
                    span["symbol"],
                ),
                span,
            )

    def test_each_native_depth_has_required_algorithm_families(self) -> None:
        required = {
            "setPixelAt",
            "rawFillRow",
            "rawCopyRow",
            "clear",
            "VScroll",
            "HScroll",
            "drawGlyph",
            "copyRect",
            "readScreen",
            "rawDrawBitmap_Native",
            "rawDrawBitmap_RGBA2222",
            "rawDrawBitmap_RGBA8888",
            "rawCopyToBitmap",
        }
        for depth in MODULE.DEPTHS:
            observed = {
                item["symbol"]
                for item in self.artifact["algorithms"]
                if item["family"] == f"native-depth-{depth}"
                and item["role"] == "definition"
            }
            self.assertEqual(required - observed, set(), f"native depth {depth}")

    def test_common_generic_algorithms_and_boundary_examples(self) -> None:
        records = {
            (item["family"], item["symbol"], item["role"]): item["disposition"]
            for item in self.artifact["algorithms"]
        }
        for name in {
            "genericDrawEllipse",
            "genericFillRowScan",
            "genericFloodFill",
            "genericDrawGlyph",
            "genericRawDrawBitmap_Native",
            "genericRawCopyToBitmap",
            "genericVScroll",
            "genericHScroll",
        }:
            self.assertEqual(records[("common-renderer", name, "definition")], "retain-common")
        self.assertEqual(
            records[("classic-vga-base", "allocateViewPort", "definition")],
            "replace-platform",
        )
        self.assertEqual(
            records[("classic-vga-base", "swapBuffers", "definition")],
            "defer-phase-c",
        )
        self.assertEqual(
            records[("classic-vga-base", "packHVSync", "definition")],
            "adapt-depth-algorithm",
        )
        self.assertEqual(
            records[("native-depth-64", "ISRHandler", "definition")],
            "exclude-physical",
        )


if __name__ == "__main__":
    unittest.main()
