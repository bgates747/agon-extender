#!/usr/bin/env python3
"""Build and run the offline stock-depth/P4 pixel comparison."""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GL = ROOT / "vdp/vendor/vdp-gl/src"
FIXTURES = ROOT / "docs/tasks/PORT-003"
COMPAT = FIXTURES / "stock-backend-r1/compat"


def main():
    depths = ("vga2", "vga4", "vga8", "vga16", "vga64", "vgapaletted", "vgabase")
    sources = [GL / "dispdrivers" / (d + "controller.cpp") for d in depths]
    sources.extend(GL / (s + ".cpp") for s in ("canvas", "displaycontroller", "codepages", "fabfonts"))
    sources.extend((ROOT / "vdp/video/extender/port/stock_render_utils.cpp",
                    ROOT / "vdp/video/extender/display/stock_scanline.cpp",
                    Path(__file__).with_suffix(".cpp")))
    with tempfile.TemporaryDirectory(prefix="p4-native-pixels-") as temp:
        binary = Path(temp) / "pixels"
        subprocess.run(["g++", "-std=c++17", "-O2", "-ffunction-sections", "-fdata-sections",
                        "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_ROWS_PROOF",
                        "-DAGON_EXTENDER_NATIVE_SCANOUT", "-include", COMPAT / "host_preinclude.hpp",
                        "-I", COMPAT, "-I", FIXTURES / "phase-b/tests/compat", "-I", GL,
                        "-I", ROOT / "vdp/video", *sources, "-Wl,--gc-sections", "-o", binary],
                       cwd=ROOT, check=True)
        subprocess.run([binary], check=True)


if __name__ == "__main__":
    main()
