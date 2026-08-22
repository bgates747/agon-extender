"""Unit tests for PORT-003 Phase A closure normalization."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate-phase-a.py"
spec = importlib.util.spec_from_file_location("phase_a_validator", SCRIPT)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

IMPORT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/import-baselines.py"
import_spec = importlib.util.spec_from_file_location("phase_a_importer", IMPORT_SCRIPT)
assert import_spec and import_spec.loader
importer = importlib.util.module_from_spec(import_spec)
import_spec.loader.exec_module(importer)


class PhaseAValidatorTests(unittest.TestCase):
    def test_loaded_application_objects_are_scope_limited(self) -> None:
        map_text = "\n".join(
            [
                "LOAD .pio/build/p4-display-contract-canary/selected-vdp-gl/canvas.o",
                "LOAD .pio/build/p4-display-contract-canary/video/extender/a.cpp.o",
                "LOAD .pio/build/p4-display-contract-canary/esp-idf/driver/libdriver.a",
            ]
        )
        self.assertEqual(
            ["selected-vdp-gl/canvas.o", "video/extender/a.cpp.o"],
            validator.loaded_application_objects(map_text),
        )

    def test_expected_objects_preserve_project_and_vendor_ownership(self) -> None:
        selection = {
            "project_translation_units": ["video/extender/a.cpp"],
            "vendored_translation_units": ["vendor/vdp-gl/src/canvas.cpp"],
        }
        self.assertEqual(
            {
                "video/extender/a.cpp": "video/extender/a.cpp.o",
                "vendor/vdp-gl/src/canvas.cpp": "selected-vdp-gl/canvas.o",
            },
            validator.expected_objects(selection),
        )

    def test_official_import_allows_extender_and_generated_cmake_only(self) -> None:
        old_video = importer.OFFICIAL_VIDEO_ROOT
        old_metadata = importer.OFFICIAL_METADATA_ROOT
        try:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                importer.OFFICIAL_VIDEO_ROOT = root / "video"
                importer.OFFICIAL_METADATA_ROOT = root / "release"
                (root / "video/extender").mkdir(parents=True)
                (root / "release").mkdir()
                (root / "video/official.h").write_text("official\n")
                (root / "video/extender/local.cpp").write_text("local\n")
                (root / "video/CMakeLists.txt").write_text("generated\n")
                (root / "release/platformio.ini").write_text("official\n")
                paths = ["video/official.h", "platformio.ini"]
                self.assertEqual([], importer.unexpected_official_files(paths))
                (root / "video/rogue.h").write_text("rogue\n")
                self.assertEqual(
                    ["video/rogue.h"], importer.unexpected_official_files(paths)
                )
        finally:
            importer.OFFICIAL_VIDEO_ROOT = old_video
            importer.OFFICIAL_METADATA_ROOT = old_metadata


if __name__ == "__main__":
    unittest.main()
