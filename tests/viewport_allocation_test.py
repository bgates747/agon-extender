"""Run AUDIT-010 RP05 checked viewport-allocation regressions."""

from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ViewportAllocationTests(unittest.TestCase):
    def test_every_allocation_failure_is_atomic_and_leak_free(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "viewport-allocation-test"
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
                    str(ROOT / "tests/viewport_allocation_test.cpp"),
                    "-o",
                    str(binary),
                ],
                check=True,
            )
            subprocess.run([str(binary)], check=True)

    def test_selected_controllers_stop_before_viewport_dereference(self):
        base = (ROOT / "vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp").read_text()
        paletted = (ROOT / "vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp").read_text()
        screen = (ROOT / "vdp/video/agon_screen.h").read_text()
        self.assertIn("if (!allocateViewPort())\n    return;", base)
        self.assertIn("if (!isViewPortAllocated())\n    return;", paletted)
        self.assertIn("if (!vga.isViewPortAllocated()", screen)
        self.assertLess(
            screen.index("if (!vga.isViewPortAllocated()"),
            screen.index("service.startClock"),
        )


if __name__ == "__main__":
    unittest.main()
