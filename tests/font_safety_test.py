"""Run AUDIT-010 A10-VP07 font bounds/lifetime regressions under ASan/UBSan."""

from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FontSafetyTests(unittest.TestCase):
    def test_managed_font_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "font-safety-test"
            subprocess.run(
                [
                    "c++",
                    "-std=c++17",
                    "-O1",
                    "-g",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fsanitize=address,undefined",
                    "-fno-sanitize-recover=all",
                    "-I" + str(ROOT / "vdp/video"),
                    str(ROOT / "tests/font_safety_test.cpp"),
                    "-o",
                    str(binary),
                ],
                check=True,
            )
            result = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            self.assertIn("font safety checks passed", result.stdout)

    def test_fixed_scratch_and_double_height_have_no_alloca(self):
        context = (ROOT / "vdp/video/context/fonts.h").read_text()
        renderer = (ROOT / "vdp/vendor/vdp-gl/src/displaycontroller.h").read_text()
        self.assertNotIn("charData[charSize]", context)
        self.assertIn("std::bitset<256> candidates", context)
        self.assertNotIn("alloca(glyphSize)", renderer)
        self.assertIn("doubleHeightOffset + (y >> 1)", renderer)


if __name__ == "__main__":
    unittest.main()
