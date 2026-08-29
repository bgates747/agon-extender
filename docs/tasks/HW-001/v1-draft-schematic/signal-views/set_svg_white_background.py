#!/usr/bin/env python3
"""Give generated KiCad SVG signal views an explicit white background."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BACKGROUND_ID = "explicit-white-background"
BACKGROUND = (
    f'  <rect id="{BACKGROUND_ID}" x="0" y="0" width="100%" height="100%" '
    'fill="#ffffff" stroke="none"/>\n'
)


def set_white_background(path: Path) -> None:
    """Insert a white background without changing KiCad drawing colors."""

    text = path.read_text(encoding="utf-8")
    if f'id="{BACKGROUND_ID}"' in text:
        return
    match = re.search(r"(<desc>.*?</desc>\s*)", text, re.DOTALL)
    if match is None:
        raise ValueError(f"{path}: SVG has no desc element insertion point")
    text = text[: match.end()] + BACKGROUND + text[match.end() :]
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Insert an explicit white background into generated SVG files."
    )
    parser.add_argument("svg", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        for path in args.svg:
            set_white_background(path)
            print(f"PASS: explicit white background: {path}")
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
