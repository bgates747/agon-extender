#!/usr/bin/env python3
"""Compatibility entry point for the canonical native P4 console build.

New automation should call ``scripts/build_p4.py`` directly. This wrapper
retains the former routine console command name without retaining PlatformIO as
a second maintained build authority. It never flashes hardware or edits SD.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--reset-url")
    parser.add_argument("--admission-probe", action="store_true")
    parser.add_argument("--lcd", action="store_true")
    parser.add_argument("--lcd-pattern", action="store_true")
    parser.add_argument("--lcd-framebuffer-pattern", action="store_true")
    parser.add_argument("--lcd-legacy-timing", action="store_true")
    parser.add_argument("--lcd-hphase", type=int, default=0)
    parser.add_argument(
        "--staged-webdav", action="store_true",
        help="accepted for compatibility; the console profile already enables it",
    )
    args = parser.parse_args()
    obsolete = [
        name for name in (
            "admission_probe", "lcd", "lcd_pattern", "lcd_framebuffer_pattern",
            "lcd_legacy_timing", "lcd_hphase",
        ) if getattr(args, name)
    ]
    if obsolete:
        parser.error(
            "the native pre-LCD console profile does not support historical "
            "diagnostic switches: " + ", ".join(obsolete)
        )
    build_id = "native-console-b" + datetime.now(timezone.utc).strftime(
        "%Y-%m-%d-%H-%M-%SZ"
    )
    command = [
        sys.executable, str(ROOT / "scripts/build_p4.py"),
        "--profile", "p4-console", "--output", str(args.output),
        "--build-id", build_id,
    ]
    if args.reset_url:
        command += ["--reset-url", args.reset_url]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
