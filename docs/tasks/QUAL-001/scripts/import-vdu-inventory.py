#!/usr/bin/env python3
"""One-time QUAL-001 importer for the accepted SETUP-004 VDU inventory.

The durable validator retains the same exact-import check until Review Gate 2;
this task-local command only materializes the candidate reviewed file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "docs" / "qualification" / "scripts"))

from qualification_model import dump_yaml, parse_vdu_inventory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    document = {
        "schema_version": "1.0.0",
        "artifact_kind": "qualification_interfaces",
        "interfaces": parse_vdu_inventory(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dump_yaml(document), encoding="utf-8")
    print(f"wrote {args.output}: {len(document['interfaces'])} exact inventory entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
