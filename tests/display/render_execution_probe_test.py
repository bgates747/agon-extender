#!/usr/bin/env python3
"""Check real worker guard/wait accounting and bounded render-window storage.

Host elapsed times demonstrate exclusion semantics, not P4 performance.
"""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GL = ROOT / "vdp/vendor/vdp-gl/src"
RUNTIME = ROOT / "docs/tasks/PORT-003/stock-backend-r2/runtime"
ROW = ROOT / "docs/tasks/PORT-003/stock-backend-r1"


def main():
    sources = [GL / "dispdrivers" / (name + "controller.cpp")
               for name in ("vgabase", "vgapaletted", "vga2", "vga4",
                            "vga8", "vga16", "vga64")]
    sources += [GL / (name + ".cpp")
                for name in ("canvas", "displaycontroller", "codepages", "fabfonts")]
    sources += [ROOT / "vdp/video/extender/port/stock_render_utils.cpp"]
    sources += [ROOT / "vdp/video/extender/display" / (name + ".cpp")
                for name in ("stock_native_access", "stock_scanline",
                             "stock_runtime_controller", "p4_rgb888_controller",
                             "presentation_snapshot_pool")]
    sources.append(Path(__file__).with_suffix(".cpp"))
    includes = [HERE / "compat", RUNTIME / "compat", ROW / "compat",
                ROOT / "docs/tasks/PORT-003/phase-c/tests/compat",
                ROOT / "docs/tasks/PORT-003/phase-b/tests/compat",
                GL, ROOT / "vdp/video"]
    with tempfile.TemporaryDirectory(prefix="render-execution-") as directory:
        binary = Path(directory) / "check"
        subprocess.run([
            "g++", "-std=c++17", "-O1", "-g", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_RUNTIME",
            "-DAGON_EXTENDER_DIRECT_RGB888", "-DAGON_EXTENDER_RENDER_BENCHMARK=1",
            *["-I" + str(path) for path in includes],
            "-include", str(RUNTIME / "compat/host_preinclude.hpp"),
            *map(str, sources), "-o", str(binary)], check=True)
        completed = subprocess.run([str(binary)], check=True, capture_output=True,
                                   text=True, timeout=15)
    result = json.loads(completed.stdout)
    assert result["render_capacity"] == 16 and result["render_overflow"]
    assert len(result["windows"]) == 17
    assert all(len(window["phases"]) == 6 for window in result["windows"])
    assert result["windows"][16]["render"] is None
    print("PASS: actual recursive guard excludes native wait; rendering categories, "
          "empty/refused drains, closed-window drops and sidecar overflow validate")


if __name__ == "__main__":
    main()
