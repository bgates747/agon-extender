#!/usr/bin/env python3
"""Build the deterministic canonical compatibility qualification join."""

from __future__ import annotations

import argparse
from pathlib import Path

from qualification_model import REVIEWED, build_matrix, dump_yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewed", type=Path, default=REVIEWED)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix(args.reviewed)
    args.output.write_text(dump_yaml(matrix), encoding="utf-8")
    print(f"wrote {args.output}: {len(matrix['interfaces'])} interfaces, {len(matrix['obligations'])} obligations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
