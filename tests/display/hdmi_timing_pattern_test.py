#!/usr/bin/env python3
"""Build/run the standalone timing pattern with address/undefined sanitizers."""
from argparse import ArgumentParser
from pathlib import Path
import os
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "vdp/hdmi-timing-test"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--ppm", type=Path, help="Optional 848x480 RGB preview output")
    args = parser.parse_args()
    # Verify that the deliberately small portable font remains an exact subset
    # of the already-vendored upstream font; no silently redrawn glyphs.
    upstream = (ROOT / "vdp/vendor/vdp-gl/src/fonts/font_6x8.h").read_text()
    rows = upstream.split("static const uint8_t FONT_6x8_DATA[] = {", 1)[1].split("};", 1)[0]
    expected = re.findall(r"0x[0-9a-fA-F]{2}", rows)[32 * 8:127 * 8]
    actual = (SOURCE / "pattern.c").read_text().split("font_6x8[95][8] = {", 1)[1].split("};", 1)[0]
    assert re.findall(r"0x[0-9a-fA-F]{2}", actual) == expected
    with tempfile.TemporaryDirectory(prefix="hdmi-pattern-") as directory:
        binary = Path(directory) / "check"
        subprocess.run([
            "cc", "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
            "-I" + str(SOURCE), str(SOURCE / "pattern.c"),
            str(Path(__file__).with_suffix(".c")), "-o", str(binary)
        ], check=True)
        # The agent sandbox uses ptrace, which LeakSanitizer cannot inspect.
        # Keep address/undefined checks enabled; this is a bounds test.
        env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0")
        subprocess.run([str(binary), *([str(args.ppm)] if args.ppm else [])],
                       check=True, timeout=15, env=env)


if __name__ == "__main__":
    main()
