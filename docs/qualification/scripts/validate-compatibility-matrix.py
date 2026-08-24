#!/usr/bin/env python3
"""Validate canonical qualification structure, semantics, and authority joins."""

from __future__ import annotations

import argparse
from pathlib import Path

from qualification_model import GENERATED, load_yaml, validate_matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", nargs="?", type=Path, default=GENERATED / "compatibility-matrix.yaml")
    parser.add_argument("--skip-inventory-check", action="store_true")
    args = parser.parse_args()
    matrix = load_yaml(args.matrix)
    errors = validate_matrix(matrix, verify_inventory=not args.skip_inventory_check)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        f"valid: {len(matrix['interfaces'])} interfaces, "
        f"{len(matrix['mode_expectations'])} mode expectations, "
        f"{len(matrix['obligations'])} obligations, "
        f"{len(matrix['evidence_links'])} evidence links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
