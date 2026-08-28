#!/usr/bin/env python3
"""Validate and render the frozen PORT-003 Phase F boot closure."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def inline(value: object) -> str:
    return "—" if value is None else str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.project_root.resolve()
    source = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    ids: set[str] = set()
    missing: list[str] = []
    for group in ("lifecycle", "subsystems"):
        for record in source[group]:
            if record["id"] in ids:
                raise ValueError(f"duplicate closure id: {record['id']}")
            ids.add(record["id"])
            for path in record.get("paths", []):
                # Planned project adapters are allowed to be absent until the
                # implementation item that owns them. All retained/vendored
                # inputs must already exist.
                candidate = root / "vdp" / path
                if not candidate.is_file() and "/extender/" not in path:
                    missing.append(path)
    if missing:
        raise FileNotFoundError("missing closure inputs: " + ", ".join(missing))

    lines = [
        "# PORT-003 Phase F boot closure",
        "",
        "Generated from `boot-closure.yaml` by `scripts/render-boot-closure.py`; do not edit.",
        "",
        "## Claim boundary",
        "",
    ]
    lines.extend(f"{index}. {claim}" for index, claim in enumerate(source["claims"], 1))
    lines.extend(
        [
            "",
            "## Lifecycle",
            "",
            "| ID | Disposition | Actor | Phase F operation | Failure rule |",
            "|---|---|---|---|---|",
        ]
    )
    for item in source["lifecycle"]:
        lines.append(
            f"| `{item['id']}` | {item['disposition']} | {item['actor']} | "
            f"{item['operation']} | {item['failure']} |"
        )
    lines.extend(
        [
            "",
            "## Subsystem closure",
            "",
            "| ID | Disposition | Owner | Phase F binding | Later owner |",
            "|---|---|---|---|---|",
        ]
    )
    for item in source["subsystems"]:
        lines.append(
            f"| `{item['id']}` | {item['disposition']} | {item['owner']} | "
            f"{item['phase_f_binding']} | {inline(item['later_owner'])} |"
        )
    lines.extend(["", "## Nonclaims", ""])
    lines.extend(f"{index}. {claim}" for index, claim in enumerate(source["nonclaims"], 1))
    lines.append("")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
