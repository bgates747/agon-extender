#!/usr/bin/env python3
"""Remove machine-local source paths from generated KiCad XML netlists.

KiCad 7 writes the invoking machine's absolute schematic path into the
top-level ``design/source`` element even when both command arguments are
repository-relative. Tracked HW-001 evidence must not disclose or depend on a
developer's filesystem layout, so every documented export pipeline runs this
bounded postprocessor before validation or commit.

Only the first ``design/source`` value is rewritten. All electrical netlist
content and the title-block source field remain byte-for-byte unchanged.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape, unescape


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DESIGN_SOURCE = re.compile(
    r"(?P<prefix><design>\s*<source>)(?P<source>[^<]+)(?P<suffix></source>)",
    re.MULTILINE,
)


def normalize(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    match = DESIGN_SOURCE.search(text)
    if match is None:
        raise ValueError(f"{path}: missing top-level design/source")

    source_text = unescape(match.group("source"))
    source = Path(source_text)
    if source.is_absolute():
        try:
            source = source.resolve().relative_to(REPOSITORY_ROOT)
        except ValueError as error:
            raise ValueError(
                f"{path}: KiCad source is outside repository: {source_text}"
            ) from error
    elif ".." in source.parts:
        raise ValueError(f"{path}: unsafe relative KiCad source: {source_text}")

    replacement = (
        match.group("prefix") + escape(source.as_posix()) + match.group("suffix")
    )
    normalized = text[: match.start()] + replacement + text[match.end() :]
    path.write_text(normalized, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("netlists", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.netlists:
        normalize(path.resolve())
        print(f"normalized {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
