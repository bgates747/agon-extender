#!/usr/bin/env python3
"""Exercise actual HDMI service scheduling with the existing host substrate."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GL = ROOT / "vdp/vendor/vdp-gl/src"
RUNTIME = ROOT / "docs/tasks/PORT-003/stock-backend-r2/runtime"
ROW = ROOT / "docs/tasks/PORT-003/stock-backend-r1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--indexed', action='store_true')
    parser.add_argument('--hdmi848', action='store_true')
    parser.add_argument('--hdmi684', action='store_true')
    parser.add_argument('--bitmap-fast', action='store_true')
    parser.add_argument('--bitmap-lut', action='store_true')
    parser.add_argument('--scroll-fast', action='store_true')
    parser.add_argument('--sanitize', action='store_true',
                        help='Run the actual controller goldens with address/undefined sanitizers')
    args = parser.parse_args()
    if args.bitmap_lut and not args.bitmap_fast:
        parser.error('Bitmap LUT requires the fast painter')
    if args.bitmap_lut and args.indexed:
        parser.error('Bitmap LUT expands BGR triples and cannot use indexed storage')
    if args.indexed and (args.hdmi848 or args.hdmi684):
        parser.error("Indexed test uses private logical rows, not borrowed panels")
    if args.hdmi848 and args.hdmi684:
        parser.error('Select only one output geometry')
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
    with tempfile.TemporaryDirectory(prefix="hdmi-scheduling-") as directory:
        binary = Path(directory) / "check"
        subprocess.run([
            "g++", "-std=c++17", "-O1", "-g", "-pthread",
            *(["-fsanitize=address,undefined", "-fno-omit-frame-pointer"] if args.sanitize else []),
            "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_RUNTIME",
            "-DAGON_EXTENDER_HDMI", "-DAGON_EXTENDER_DIRECT_RGB888",
            *(["-DAGON_EXTENDER_BITMAP_FAST=1"] if args.bitmap_fast else []),
            *(["-DAGON_EXTENDER_BITMAP_LUT=1"] if args.bitmap_lut else []),
            *(["-DAGON_EXTENDER_SCROLL_FAST=1"] if args.scroll_fast else []),
            *(["-DAGON_EXTENDER_INDEXED_PPA=1"] if args.indexed else []),
            *(["-DAGON_EXTENDER_HDMI_848X480=1"] if args.hdmi848 else []),
            *(["-DAGON_EXTENDER_HDMI_684X384=1"] if args.hdmi684 else []), *["-I" + str(path) for path in includes],
            "-include", str(RUNTIME / "compat/host_preinclude.hpp"),
            *map(str, sources), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True, timeout=15)
    print("PASS: RGB888 pixels/rasterizers, clipping, transparency, scroll/copy, overlays and double-buffer swap match native")


if __name__ == "__main__":
    main()
