#!/usr/bin/env python3
"""Compile/run the real stock swap with the established host-only substrate."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
GL = ROOT / "vdp/vendor/vdp-gl/src"
RUNTIME = ROOT / "docs/tasks/PORT-003/stock-backend-r2/runtime"
ROW = ROOT / "docs/tasks/PORT-003/stock-backend-r1"


def main():
    sources = [GL / "dispdrivers" / (name + "controller.cpp")
               for name in ("vgabase", "vgapaletted", "vga2", "vga4",
                            "vga8", "vga16", "vga64")]
    sources += [GL / (name + ".cpp")
                for name in ("displaycontroller", "codepages", "fabfonts")]
    sources += [ROOT / "vdp/video/extender/port/stock_render_utils.cpp",
                ROOT / "vdp/video/extender/display/stock_native_access.cpp",
                Path(__file__).with_suffix(".cpp")]
    includes = [RUNTIME / "compat", ROW / "compat",
                ROOT / "docs/tasks/PORT-003/phase-c/tests/compat",
                ROOT / "docs/tasks/PORT-003/phase-b/tests/compat",
                GL, ROOT / "vdp/video"]
    with tempfile.TemporaryDirectory(prefix="hdmi-visible-") as directory:
        binary = Path(directory) / "check"
        subprocess.run([
            "g++", "-std=c++17", "-O1", "-g", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_RUNTIME",
            "-DAGON_EXTENDER_HDMI", *["-I" + str(path) for path in includes],
            "-include", str(RUNTIME / "compat/host_preinclude.hpp"),
            *map(str, sources), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True, timeout=10)
    print("PASS: native swap updates aliases/generation atomically under row exclusion")


if __name__ == "__main__":
    main()
