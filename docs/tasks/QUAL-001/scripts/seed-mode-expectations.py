#!/usr/bin/env python3
"""One-time Gate 2 seed of accepted mode expectations.

Legacy/cooperative VDU ownership comes from ADR-0014. EDP-exclusive ownership
comes from the accepted SETUP-004 disposition; unresolved input, RTC, and
carve-out behavior remains blocked by its exact SETUP-005 decision.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "docs" / "qualification" / "scripts"))

from qualification_model import dump_yaml  # noqa: E402


def exclusive_expectation(interface: dict) -> tuple[str, list[str], list[str]]:
    disposition = interface["disposition"]
    interface_id = interface["id"]
    if disposition == "unsupported":
        return "unsupported", ["SETUP-005"], ["SETUP-005-D006"]
    if disposition == "accepted-noop":
        return "accepted-noop", ["PORT-003"], []
    if disposition == "unresolved":
        return "unresolved", ["SETUP-005"], ["SETUP-005-D008"]
    if disposition == "mode-dependent":
        return "unresolved", ["PORT-005", "SETUP-005"], ["SETUP-005-D007"]
    if interface_id == "interface:agon-vdp:vdu-23-0-x80":
        return "extender-required", ["PORT-008"], ["PORT-003-PHASE-E", "SETUP-005-D003"]
    if interface_id == "interface:agon-vdp:vdu-7" or interface_id.startswith("interface:agon-vdp:vdu-23-0-x85"):
        return "extender-required", ["PORT-004"], []
    return "extender-required", ["PORT-003"], []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interfaces", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    interfaces = yaml.safe_load(args.interfaces.read_text(encoding="utf-8"))["interfaces"]
    records = []
    for interface in interfaces:
        stem = interface["id"].replace("interface:", "mode-expectation:", 1)
        records.append({
            "id": stem + ":legacy",
            "interface_id": interface["id"],
            "mode_id": "mode:extender:legacy",
            "expectation": "stock-vdp",
            "owner_task_ids": [],
            "blocker_refs": [],
        })
        expectation, owners, blockers = exclusive_expectation(interface)
        records.append({
            "id": stem + ":edp-exclusive",
            "interface_id": interface["id"],
            "mode_id": "mode:extender:edp-exclusive",
            "expectation": expectation,
            "owner_task_ids": owners,
            "blocker_refs": blockers,
        })
        records.append({
            "id": stem + ":cooperative",
            "interface_id": interface["id"],
            "mode_id": "mode:extender:cooperative",
            "expectation": "stock-vdp",
            "owner_task_ids": [],
            "blocker_refs": [],
        })
    document = {
        "schema_version": "1.0.0",
        "artifact_kind": "qualification_mode_expectations",
        "mode_expectations": sorted(records, key=lambda record: record["id"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dump_yaml(document), encoding="utf-8")
    print(f"wrote {args.output}: {len(records)} complete interface/mode tuples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
